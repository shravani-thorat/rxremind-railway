from database import get_reminders, reminder_already_sent
from datetime import datetime

def run_reminder_check():

    reminders = get_reminders()

    for r in reminders:
        if r["should_notify"]:

            title = "RxRemind"
            body = f'{r["name"]} • {r["medicine"]} • Refill Due • 📞 {r["phone"]}'

            reminder_already_sent(r["order_id"])

if __name__ == "__main__":
    run_reminder_check()
