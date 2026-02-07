import os
import sqlite3
from datetime import datetime, timedelta, date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "pharmacy.db")

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
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
""")

conn.commit()
conn.close()

#update in app 
def update_medicine_orders_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE medicine_orders ADD COLUMN is_active INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass   #if column already exit

    try:
        cursor.execute("ALTER TABLE medicine_orders ADD COLUMN last_reminded_on TEXT")
    except sqlite3.OperationalError:
        pass  

    conn.commit()
    conn.close()


print("Database and tables created successfully!")
#print("DB Location :", os.path.abspath("pharmacy.db"))

# helper function

def calculate_dates(days):
    start_date = datetime.today().date()
    end_date = start_date + timedelta(days=days)
    reminder_date = end_date - timedelta(days=2)
    return start_date, end_date, reminder_date

def add_customer(name, phone):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO customers(name, phone) VALUES (?,?)",
        (name, phone)
    )
    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()

    return customer_id

def add_medicine(customer_id,medicine_name,quantity,days):
    start_date, end_date, reminder_date = calculate_dates(days)

    conn =  sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
                   INSERT INTO medicine_orders
                   (customer_id, medicine_name,quantity,days,start_date,end_date,reminder_date,
                   is_active,last_reminded_on)
                   VALUES(?,?,?,?,?,?,?,?,?)
                   """,(
                       customer_id,
                       medicine_name,
                       quantity,
                       days,
                       start_date.isoformat(),
                       end_date.isoformat(),
                       reminder_date.isoformat(),
                       1,
                       None
                   ))
    conn.commit()
    conn.close()

def get_all_customers_medicine():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT
                     customers.customer_id,
                     customers.name,
                     customers.phone,
                     medicine_orders.order_id,
                     medicine_orders.medicine_name,
                     medicine_orders.quantity,
                     medicine_orders.days,
                     medicine_orders.start_date,
                     medicine_orders.end_date,
                     medicine_orders.reminder_date
                   FROM customers
                   JOIN medicine_orders
                   ON customers.customer_id = medicine_orders.customer_id
                   """
                   )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_reminders():
    today = datetime.today().date().isoformat()
    reminders=[]

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
                   WHERE medicine_orders.is_active = 1
                   """)
    
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        order_id,name,phone,med,qty,days,is_active,reminder_date, last_reminded_on = row

        if last_reminded_on is None:
            if isinstance(reminder_date, str):
                due_date = datetime.fromisoformat(reminder_date).date()
            elif isinstance(reminder_date, date):
                due_date = reminder_date
            else:
                continue   # skip broken record safely
        else:
            if isinstance(last_reminded_on, str):
                due_date= datetime.fromisoformat(last_reminded_on).date() + timedelta(days=days)
            elif isinstance(last_reminded_on, date):
                due_date = last_reminded_on + timedelta(days=days)
            else:
                continue

        #checking for today's reminder
        if due_date == today:
            reminders.append({
                "order_id": order_id,
                "name": name,
                "phone": phone,
                "medicine": med,
                "quantity": qty,
                "is_active": is_active
            })
    return reminders


#for keeping track on already sent reminders
def reminder_already_sent(order_id):
    today = datetime.today().date().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
                   UPDATE medicine_orders
                   SET last_reminded_on = ?
                   WHERE order_id = ?
                   """, (today,order_id))
    conn.commit()
    conn.close()

#for reminder on/off
def turn_on_reminder(order_id):
    today = datetime.today().date().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
                   UPDATE medicine_orders
                   SET is_active = 1,
                     last_reminded_on = ?
                   WHERE order_id = ?
                   """,(today,order_id))
    conn.commit()
    conn.close()

def turn_off_reminder(order_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
                   UPDATE medicine_orders
                   SET is_active = 0
                   WHERE order_id = ?
                   """,(order_id,))
    conn.commit()
    conn.close()

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

# if __name__ == "__main__":
#     update_medicine_orders_table()
#     print("Updated successfully")







