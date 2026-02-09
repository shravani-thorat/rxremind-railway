import os
import sqlite3
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "pharmacy.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicine_orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        medicine_name TEXT NOT NULL,
        quantity INTEGER,
        days INTEGER,
        start_date TEXT,
        end_date TEXT,
        reminder_date TEXT,
        is_active INTEGER DEFAULT 1,
        last_reminded_on TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    conn.commit()
    conn.close()

def calculate_dates(days):
    start_date = datetime.today().date()
    end_date = start_date + timedelta(days=days)
    reminder_date = end_date - timedelta(days=2)
    return start_date, end_date, reminder_date

# ADD CUSTOMER
def add_customer(name, phone):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO customers (name, phone) VALUES (?, ?)",
        (name, phone)
    )

    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()

    return customer_id

# ADD MEDICINE
def add_medicine(customer_id, medicine_name, quantity, days):
    start_date, end_date, reminder_date = calculate_dates(days)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO medicine_orders
        (customer_id, medicine_name, quantity, days,
         start_date, end_date, reminder_date,
         is_active, last_reminded_on)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1, NULL)
    """, (
        customer_id,
        medicine_name,
        quantity,
        days,
        start_date.isoformat(),
        end_date.isoformat(),
        reminder_date.isoformat()
    ))

    conn.commit()
    conn.close()

# GET REMINDERS 
def get_reminders():
    today = datetime.today().date()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            medicine_orders.order_id,
            customers.name,
            customers.phone,
            medicine_orders.medicine_name,
            medicine_orders.quantity,
            medicine_orders.days,
            medicine_orders.reminder_date,
            medicine_orders.is_active,
            medicine_orders.last_reminded_on
        FROM medicine_orders
        JOIN customers
        ON customers.customer_id = medicine_orders.customer_id
    """)

    rows = cursor.fetchall()
    conn.close()

    reminders = []

    for row in rows:
        order_id, name, phone, med, qty, days, reminder_date, is_active, last_reminded_on = row

        reminder_date_obj = datetime.fromisoformat(reminder_date).date()

        should_notify = False

        # Only notify if active
        if is_active == 1:

            # If reminder date reached
            if reminder_date_obj <= today:

                # If never reminded today
                if last_reminded_on != today.isoformat():
                    should_notify = True

        reminders.append({
            "order_id": order_id,
            "name": name,
            "phone": phone,
            "medicine": med,
            "quantity": qty,
            "reminder_date": reminder_date,
            "is_active": is_active,
            "should_notify": should_notify
        })

    return reminders


# MARK REMINDER AS SENT
def reminder_already_sent(order_id):
    today = datetime.today().date().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE medicine_orders
        SET last_reminded_on = ?
        WHERE order_id = ?
    """, (today, order_id))

    conn.commit()
    conn.close()

# TOGGLE REMINDER
def turn_on_reminder(order_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE medicine_orders
        SET is_active = 1,
            last_reminded_on = NULL
        WHERE order_id = ?
    """, (order_id,))

    conn.commit()
    conn.close()


def turn_off_reminder(order_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE medicine_orders
        SET is_active = 0
        WHERE order_id = ?
    """, (order_id,))

    conn.commit()
    conn.close()

# DELETE REMINDER
def delete_reminder(order_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM medicine_orders
        WHERE order_id = ?
    """, (order_id,))

    conn.commit()
    conn.close()