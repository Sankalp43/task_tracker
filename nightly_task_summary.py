import os
import random
import yagmail
from supabase import create_client
from datetime import datetime
from jinja2 import Template
import streamlit as st

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EMAIL_USER = os.getenv("SENDER_EMAIL")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# SUPABASE_URL = st.secrets["SUPABASE_URL"]
# SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
# EMAIL_USER = st.secrets["SENDER_EMAIL"]
# EMAIL_PASS = st.secrets["APP_PASSWORD"]



yag = yagmail.SMTP(user=EMAIL_USER, password=EMAIL_PASS)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Section 1: Quotes for Task Completion Status

# Quotes when all tasks are completed
COMPLETED_TASKS_QUOTES = [
    "Congratulations on completing your tasks today! You're on fire! 🔥 Keep it up and conquer tomorrow with the same energy! 💪",
    "All tasks checked off – you're crushing it! 🏆 Keep up the great work and stay on top of your goals! 🌟",
    "Victory is yours tonight! 🏅 You’ve finished all tasks – a true champion. 🏆 Keep this momentum going! 💥",
    "Well done! 🎉 All tasks completed, proving you're one step closer to greatness. 🌟 Take a well-earned break! 😌",
    "You did it! 🙌 All tasks are done. Now, recharge and get ready to take on tomorrow’s challenges. ⚡",
    "You're a task master! 🧑‍🏫 All done today. Rest up, and get ready for more achievements tomorrow. 🛌",
    "Mission complete! ✅ You've checked everything off the list. Well deserved relaxation ahead! 🌙",
    "You finished every task! 🎯 What a way to end the day. Keep pushing yourself forward. 🚀",
    "Success is the sum of small efforts, repeated day in and day out. 💪",
    "Discipline is the bridge between goals and accomplishment. 🌉",
    "Consistency is more important than perfection. 🔄",
    "Progress, not perfection. 📈",
    "The secret of your future is hidden in your daily routine. 🔑"
]

# Quotes when some tasks are pending
PENDING_TASKS_QUOTES = [
    "You’re so close! 😅 A few tasks left, and you’ll be on top of it. Tomorrow’s a new day to finish strong! 🌅",
    "Not quite there yet, but you're making progress! 💼 Tomorrow, let’s cross off those remaining tasks! ✅",
    "Almost finished! ⏳ With a little push tomorrow, you’ll wrap it all up. Keep going! 🚀",
    "Some tasks are still waiting for you, but don't worry – you’ve got this! One step at a time. 🦶",
    "Great progress today! 👍 A few tasks left to wrap up. Let’s finish strong tomorrow! 🏁",
    "You’re almost there! 🏃‍♂️ A little more effort and you’ll have it all done. Keep the momentum going! 🔥",
    "You’ve made fantastic progress. Just a few more steps, and you’ll be all set! 👏",
    "A few tasks left, but don’t fret – tomorrow's the perfect day to tackle them head-on! 💥",
    "Every day is a chance to get better. Don't give up! 🌱",
    "Stay focused and never give up on your dreams. 🌠",
    "Push yourself, because no one else is going to do it for you. 💪",
    "Great things never come from comfort zones. 🚀",
    "Keep going. Everything you need will come to you at the perfect time. ⏰"
]


PARTIAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Daily Summary</title>
  <style>
    body {
      font-family: "Segoe UI", sans-serif;
      background-color: #f3f4f6;
      color: #333;
      margin: 0;
      padding: 20px;
    }
    .container {
      background-color: #ffffff;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
      max-width: 600px;
      margin: 0 auto;
    }
    h2 {
      color: #3B82F6;
      font-size: 1.8em;
      text-align: center;
      margin-bottom: 20px;
    }
    p {
      font-size: 1.1em;
      color: #555;
      text-align: center;
      margin-bottom: 30px;
    }
    .task-list {
      margin-top: 20px;
      padding-left: 0;
    }
    .task {
      padding: 10px;
      border-radius: 8px;
      margin-bottom: 12px;
      font-size: 1.1em;
      transition: all 0.3s ease;
    }
    .task:hover {
      transform: scale(1.05);
    }
    .completed {
      background-color: #D1F7C4;
      color: #388E3C;
      border-left: 6px solid #388E3C;
    }
    .missed {
      background-color: #FFEBEE;
      color: #D32F2F;
      border-left: 6px solid #D32F2F;
    }
    .quote {
      margin-top: 30px;
      padding: 20px;
      background-color: #FFF8E1;
      border-left: 6px solid #FFB74D;
      font-style: italic;
      text-align: center;
      font-size: 1.2em;
    }
    .footer {
      font-size: 0.85em;
      color: #777;
      text-align: center;
      margin-top: 40px;
    }
    .footer strong {
      color: #6A5ACD;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>🌟 Hey {{ name }}, here’s your daily summary!</h2>
    <p>Here’s how your day went based on the tasks you had planned:</p>
    
    <h3> This is what you accomplished today. </h3>
    <p> You completed {{ completed_tasks | length }} tasks. </p>
    <div class="task-list">
      {% for task in completed_tasks %}
        <div class="task completed">✅ {{ task }}</div>
      {% endfor %}

    <h3> Tasks you missed: </h3>
    <p> You have {{ pending_tasks | length }} tasks left to complete. </p>
      {% for task in pending_tasks %}
        <div class="task missed">❌ {{ task }}</div>
      {% endfor %}
    </div>

    <div class="quote">
      “{{ quote }}”
    </div>

    <div class="footer">
      Task Tracker | Stay consistent, stay winning 💪<br>
      With 💡 from <strong>Team S.A.R.A ⚡</strong>
    </div>
  </div>
</body>
</html>
"""

CONGRATS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      font-family: "Segoe UI", sans-serif;
      background-color: #f0fff4;
      color: #2f855a;
      padding: 20px;
    }
    .container {
      background-color: #ffffff;
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    h2 {
      color: #38a169;
    }
    .message {
      font-size: 1.1em;
      margin-top: 10px;
    }
    .quote {
      margin-top: 20px;
      padding: 15px;
      background-color: #ebf8ff;
      border-left: 5px solid #63b3ed;
      font-style: italic;
    }
    .footer {
      font-size: 0.85em;
      color: #777;
      margin-top: 30px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>🎉 Great Job, {{ name }}!</h2>
    <p class="message">You've completed all your tasks for today. Keep up the amazing work!</p>

    <h3> This is what you accomplished today. </h3>
    <div class="task-list">
      {% for task in completed_tasks %}
        <div class="task completed">✅ {{ task }}</div>
      {% endfor %}

    <div class="quote">
      “{{ quote }}”
    </div>

    <div class="footer">
      Task Tracker | You crushed it today 🚀<br>
      With 💡 from <strong style='color: #2B6CB0;'>Team S.A.R.A ⚡</strong>
    </div>
  </div>
</body>
</html>
"""

def generate_task_summary_email_html(name, tasks, completed_tasks):
    complete_quote = random.choice(COMPLETED_TASKS_QUOTES)
    pending_quote = random.choice(PENDING_TASKS_QUOTES)

    all_completed = len(tasks) == len(completed_tasks)
    completed = [task['task'] for task in completed_tasks]

    if all_completed:
        template = Template(CONGRATS_TEMPLATE)
        return template.render(name=name, quote=complete_quote, completed_tasks=completed)
    else:
        pending = [task['task'] for task in tasks if task not in completed_tasks]
        template = Template(PARTIAL_TEMPLATE)
        return template.render(name=name, completed_tasks=completed, pending_tasks=pending, quote=pending_quote)

def send_nightly_summary():
    users = supabase.table("users").select("user, mail").execute().data
    for user in users:
        name = user["user"]
        email = user["mail"]

        today = datetime.today().strftime("%Y-%m-%d")
        tasks = supabase.table("tasks").select("task, status, date").eq("user", name).eq("date", today).execute().data
        completed = [task for task in tasks if task['status']]

        html = generate_task_summary_email_html(name, tasks, completed)
        subject = "🌙 Your Daily Task Summary"

        yag.send(to=email, subject=subject, contents=html)

if __name__ == "__main__":
    send_nightly_summary()
    print("Nightly task summary emails sent successfully!")