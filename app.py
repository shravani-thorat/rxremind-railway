from flask import Flask, render_template, request, redirect, flash, jsonify
from datetime import date
from database import (
    init_db,
    add_customer,
    add_medicine,
    get_all_reminders,
    get_today_reminders,
    mark_reminded,
    toggle_reminder,
    delete_reminder
)

app = Flask(__name__)
app.secret_key = "rxremind-secret"

# Initialize Neon DB tables
init_db()

# =========================
# HOME PAGE
# =========================
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


# =========================
# VIEW ALL REMINDERS
# =========================
@app.route("/reminders")
def reminders():
    reminders = get_all_reminders()
    return render_template("reminders.html", reminders=reminders)


# =========================
# TODAY'S REFILL REMINDERS
# =========================
@app.route("/today")
def today_reminders():
    today = date.today()
    reminders = get_today_reminders(today)

    # Mark shown reminders as reminded
    for r in reminders:
        mark_reminded(r["order_id"], today)

    return render_template("today.html", reminders=reminders)


# =========================
# TOGGLE ACTIVE / INACTIVE
# =========================
@app.route("/toggle/<int:order_id>")
def toggle(order_id):
    toggle_reminder(order_id)
    return "", 204


# =========================
# DELETE
# =========================
@app.route("/delete/<int:order_id>")
def delete(order_id):
    delete_reminder(order_id)
    return redirect("/reminders")


# =========================
# API (optional future use)
# # =========================
# @app.route("/api/today")
# def api_today():
#     today = date.today()
#     reminders = get_today_reminders(today)

#     for r in reminders:
#         mark_reminded(r["order_id"], today)

#     return jsonify(reminders)


if __name__ == "__main__":
    app.run(debug=True)