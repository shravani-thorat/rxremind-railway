import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not set in environment variables")

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


# =========================
# INITIALIZE TABLES
# =========================
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS medicine_orders (
            order_id SERIAL PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(customer_id) ON DELETE CASCADE,
            medicine TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            days INTEGER NOT NULL,
            start_date DATE DEFAULT CURRENT_DATE,
            last_reminded DATE,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# =========================
# ADD CUSTOMER
# =========================
def add_customer(name, phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO customers (name, phone) VALUES (%s, %s) RETURNING customer_id",
        (name, phone)
    )
    customer_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return customer_id


# =========================
# ADD MEDICINE
# =========================
def add_medicine(customer_id, medicine, quantity, days):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO medicine_orders
        (customer_id, medicine, quantity, days)
        VALUES (%s, %s, %s, %s)
    """, (customer_id, medicine, quantity, days))

    conn.commit()
    cur.close()
    conn.close()


# =========================
# GET ALL REMINDERS
# =========================
def get_all_reminders():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT m.*, c.name, c.phone
        FROM medicine_orders m
        JOIN customers c ON m.customer_id = c.customer_id
        ORDER BY m.order_id DESC
    """)

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


# =========================
# TODAY REFILL LOGIC
# =========================
def get_today_reminders(today):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT m.*, c.name, c.phone
        FROM medicine_orders m
        JOIN customers c ON m.customer_id = c.customer_id
        WHERE m.is_active = TRUE
        AND (m.last_reminded IS NULL OR m.last_reminded < %s)
        AND (m.start_date + (m.days - 1)) >= %s
    """, (today, today))

    reminders = cur.fetchall()
    cur.close()
    conn.close()
    return reminders


# =========================
# MARK AS REMINDED
# =========================
def mark_reminded(order_id, today):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE medicine_orders
        SET last_reminded = %s
        WHERE order_id = %s
    """, (today, order_id))

    conn.commit()
    cur.close()
    conn.close()


# =========================
# TOGGLE ACTIVE
# =========================
def toggle_reminder(order_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE medicine_orders
        SET is_active = NOT is_active
        WHERE order_id = %s
    """, (order_id,))

    conn.commit()
    cur.close()
    conn.close()


# =========================
# DELETE
# =========================
def delete_reminder(order_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM medicine_orders WHERE order_id = %s", (order_id,))
    conn.commit()

    cur.close()
    conn.close()