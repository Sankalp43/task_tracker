# send_daily_task_reminder.py
import yagmail
from datetime import datetime
from supabase import create_client
import os
import streamlit as st

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# SUPABASE_URL = st.secrets["SUPABASE_URL"]
# SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_users():
    users = supabase.table("users").select("*").execute().data
    return users or []

def get_today_tasks():
    today = datetime.now().strftime("%Y-%m-%d")
    tasks = supabase.table("tasks").select("user").eq("date", today).execute().data
    return set(task["user"] for task in tasks)

def send_reminders():
    today_users = get_today_tasks()
    print(f"Users with tasks today: {today_users}")
    all_users = get_users()
    print(f"All users: {all_users}")
    yag = yagmail.SMTP(user=os.getenv("SENDER_EMAIL"), password=os.getenv("EMAIL_PASS"))
    # yag = yagmail.SMTP(user=st.secrets["SENDER_EMAIL"], password=st.secrets["APP_PASSWORD"])
    for user in all_users:
        name, email = user["user"], user["mail"]
        if name not in today_users:
            yag.send(
                to=email,
                subject="⏰ Daily Task Reminder",
                contents=f"Hi {name},\n\nYou haven’t added any tasks today! Add a task now to stay on track.\n\n👉 Open your Task Tracker: [Your App Link]"
            )
            print(f"Sent reminder to {name} ({email})")

if __name__ == "__main__":
    send_reminders()
