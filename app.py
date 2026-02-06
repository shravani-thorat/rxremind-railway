from flask import Flask, jsonify, render_template, request, redirect, flash
from database import get_reminders , add_customer, add_medicine, turn_on_reminder, turn_off_reminder
import sqlite3
from database import init_db
init_db()

app = Flask(__name__)
app.secret_key = "rxremind-secret"

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]

        #accepting multiple medicine
        medicines = request.form.getlist("medicine[]")
        quantities = request.form.getlist("quantity[]")
        days_list =  request.form.getlist("days[]")

        customer_id = add_customer(name,phone)

        for i in range (len(medicines)):
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
    data = get_reminders()
    return jsonify(data)

@app.route("/toggle/<int:order_id>")
def toggle(order_id):
    conn = sqlite3.connect("pharmacy.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_active FROM medicine_orders WHERE order_id = ?",
        (order_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row["is_active"] == 1:
        turn_off_reminder(order_id)
    else:
        turn_on_reminder(order_id)

    return redirect("/reminders")

    
if __name__ == "__main__":
    app.run(debug=True)

    


