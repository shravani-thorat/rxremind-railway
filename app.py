from flask import Flask, jsonify, render_template, request, redirect, flash
from database import (
    init_db,
    add_customer,
    add_medicine,
    get_all_reminders,
    reminder_already_sent,
    turn_on_reminder,
    turn_off_reminder,
    delete_reminder
)

app = Flask(__name__)
app.secret_key = "rxremind-secret"

init_db()


# ==============================
# HOME PAGE
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

    raw_reminders = get_all_reminders()

    # Prepare JSON-safe reminders
    notify_list = []

    for r in raw_reminders:
        notify_list.append({
            "order_id": r["order_id"],
            "name": r["name"],
            "medicine": r["medicine"],
            "phone": r["phone"],
            "should_notify": bool(r["should_notify"])
        })

        # Mark as reminded if due
        if r["should_notify"]:
            reminder_already_sent(r["order_id"])

    return render_template("index.html", reminders=notify_list)

# ==============================
# VIEW REMINDERS PAGE
# ==============================

@app.route("/reminders")
def reminders():
    data = get_all_reminders()
    return render_template("reminder.html", reminders=data)


# ==============================
# TOGGLE REMINDER
# ==============================

@app.route("/toggle/<int:order_id>", methods=["POST"])
def toggle(order_id):

    reminders = get_all_reminders()

    for r in reminders:
        if r["order_id"] == order_id:
            if r["is_active"]:
                turn_off_reminder(order_id)
            else:
                turn_on_reminder(order_id)
            break

    return "", 204


# ==============================
# DELETE REMINDER
# ==============================

@app.route("/delete/<int:order_id>", methods=["POST"])
def delete(order_id):
    delete_reminder(order_id)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)