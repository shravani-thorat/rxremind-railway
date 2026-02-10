from flask import Flask, jsonify, render_template, request, redirect, flash, send_from_directory
from database import (
    init_db,
    add_customer,
    add_medicine,
    get_reminders,
    reminder_already_sent,
    turn_on_reminder,
    turn_off_reminder,
    delete_reminder
)
from firebase_push import send_push
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import sqlite3
from database import DB_PATH


app = Flask(__name__)
app.secret_key = "rxremind-secret"

init_db()

# ==============================
# SCHEDULER
# ==============================

def check_reminders_daily():
    print("Running daily reminder check...")
    reminders = get_reminders()

    for r in reminders:
        if r["should_notify"]:
            title = "RxRemind"
            body = f'{r["name"]} • {r["medicine"]} • Refill Due • 📞 {r["phone"]}'
            send_push(title, body)
            reminder_already_sent(r["order_id"])


scheduler = BackgroundScheduler()
scheduler.add_job(check_reminders_daily, 'interval', minutes=5)
scheduler.start()

# ==============================
# ROUTES
# ==============================

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]

        medicines = request.form.getlist("medicine[]")
        quantities = request.form.getlist("quantity[]")
        days_list = request.form.getlist("days[]")

        customer_id = add_customer(name, phone)

        for i in range(len(medicines)):
            add_medicine(
                customer_id,
                medicines[i],
                int(quantities[i]),
                int(days_list[i])
            )

        flash("✅ Reminder saved successfully!")
        return redirect("/")

    return render_template("index.html")


@app.route("/reminders")
def reminders():
    data = get_reminders()
    return render_template("reminders.html", reminders=data)


@app.route("/api/reminders")
def api_reminders():
    return jsonify(get_reminders())


@app.route("/toggle/<int:order_id>")
def toggle(order_id):
    conn = sqlite3.connect("pharmacy.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_active FROM medicine_orders WHERE order_id = ?",
        (order_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row and row[0] == 1:
        turn_off_reminder(order_id)
    else:
        turn_on_reminder(order_id)

    return "", 204


@app.route("/delete/<int:order_id>")
def delete(order_id):
    delete_reminder(order_id)
    return redirect("/reminders")


@app.route("/save-token", methods=["POST"])
def save_token():
    data = request.json
    token = data.get("token")

    conn = sqlite3.connect("pharmacy.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fcm_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT
        )
    """)

    cursor.execute("INSERT INTO fcm_tokens(token) VALUES (?)", (token,))
    conn.commit()
    conn.close()

    return "", 204


@app.route('/firebase-messaging-sw.js')
def firebase_messaging_sw():
    return send_from_directory('static', 'firebase-messaging-sw.js')


# @app.route("/manual-check")
# def manual_check():
#     check_reminders_daily()
#     return "Manual check done", 200


if __name__ == "__main__":
    app.run(debug=True)
