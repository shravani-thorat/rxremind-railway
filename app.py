from flask import Flask, jsonify, render_template, request, redirect, flash
from database import (
    init_db,
    add_customer,
    add_medicine,
    get_reminders_for_today,
    mark_reminded
)
from datetime import date

app = Flask(__name__)
app.secret_key = "rxremind-secret"

# Initialize DB (Neon)
init_db()

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


@app.route("/reminders/<int:customer_id>")
def view_reminders(customer_id):
    today = date.today()
    reminders = get_reminders_for_today(customer_id, today)

    # Mark all shown reminders as reminded for today
    for r in reminders:
        mark_reminded(r['order_id'], today)

    return render_template("reminders.html", reminders=reminders)


@app.route("/api/reminders/<int:customer_id>")
def api_reminders(customer_id):
    today = date.today()
    reminders = get_reminders_for_today(customer_id, today)

    # Mark reminders as reminded
    for r in reminders:
        mark_reminded(r['order_id'], today)

    return jsonify(reminders)


@app.route("/toggle/<int:order_id>")
def toggle(order_id):
    from database import turn_on_reminder, turn_off_reminder, is_reminder_active
    if is_reminder_active(order_id):
        turn_off_reminder(order_id)
    else:
        turn_on_reminder(order_id)
    return "", 204


@app.route("/delete/<int:order_id>")
def delete(order_id):
    from database import delete_reminder
    delete_reminder(order_id)
    return redirect("/reminders")


if __name__ == "__main__":
    app.run(debug=True)