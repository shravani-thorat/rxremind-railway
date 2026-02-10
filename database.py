import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date

# ==============================
# DATABASE CONNECTION
# ==============================
DATABASE_URL = os.environ.get("psql 'postgresql://neondb_owner:npg_K3waOsTYWP6m@ep-ancient-darkness-a1glqwlu-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'")  # Set this in Railway
if not DATABASE_URL:
    raise Exception("DATABASE_URL not found! Set it in Railway environment variables.")

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# ==============================
# INIT DB
# ==============================
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # Customers
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    # Medicine Orders
    cur.execute("""
        CREATE TABLE IF NOT EXISTS medicine_orders (
            order_id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES customers(customer_id),
            medicine TEXT NOT NULL,
            quantity INT NOT NULL,
            days INT NOT NULL,
            start_date DATE DEFAULT CURRENT_DATE,
            last_reminded DATE,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# ==============================
# CUSTOMER & MEDICINE
# ==============================
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

def add_medicine(customer_id, medicine, quantity, days):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO medicine_orders (customer_id, medicine, quantity, days)
        VALUES (%s, %s, %s, %s)
        """,
        (customer_id, medicine, quantity, days)
    )
    conn.commit()
    cur.close()
    conn.close()

# ==============================
# REMINDERS
# ==============================
def get_reminders_for_today(customer_id, today):
    """Returns active reminders that should be notified today"""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT * FROM medicine_orders
        WHERE customer_id = %s
          AND is_active = TRUE
          AND (last_reminded IS NULL OR last_reminded < %s)
          AND (start_date + (days - 1) >= %s)
    """, (customer_id, today, today))

    reminders = cur.fetchall()
    cur.close()
    conn.close()
    return reminders

def mark_reminded(order_id, today):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE medicine_orders SET last_reminded = %s WHERE order_id = %s",
        (today, order_id)
    )
    conn.commit()
    cur.close()
    conn.close()

# ==============================
# TOGGLE REMINDER
# ==============================
def turn_on_reminder(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE medicine_orders SET is_active = TRUE WHERE order_id = %s",
        (order_id,)
    )
    conn.commit()
    cur.close()
    conn.close()

def turn_off_reminder(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE medicine_orders SET is_active = FALSE WHERE order_id = %s",
        (order_id,)
    )
    conn.commit()
    cur.close()
    conn.close()

def is_reminder_active(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT is_active FROM medicine_orders WHERE order_id = %s",
        (order_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else False

# ==============================
# DELETE REMINDER
# ==============================
def delete_reminder(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM medicine_orders WHERE order_id = %s", (order_id,))
    conn.commit()
    cur.close()
    conn.close()