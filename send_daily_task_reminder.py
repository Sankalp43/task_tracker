# send_daily_task_reminder.py
import yagmail
from datetime import datetime
from supabase import create_client
import os
import streamlit as st
import random

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# SUPABASE_URL = st.secrets["SUPABASE_URL"]
# SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


import random
TONE_GROUPS = {
    "motivational" : [
    # 🔥 Motivational / Uplifting
    "Every big goal starts with one small task. Add yours now!",
    "Remember: Consistency > Intensity. One task a day keeps the chaos away.",
    "If not now, then when? Your future self will thank you.",
    "Tiny tasks today, big wins tomorrow. Let’s go!",
    "You’re only one task away from feeling productive.",
    "Do it for Future You — they’ll be so proud!",
    "Momentum starts with a single checkbox.",
    "Productivity isn't a feeling, it’s a decision. Make it now.",
    "Tasks don’t complete themselves (unfortunately). You’ve got this."
    ],

    # 😏 Sarcastic / Teasing
    "sarcastic": [
    "No tasks yet? Wow. You're either done with life or just vibing too hard.",
    "At this rate, your task list is starting to look like a vacation brochure.",
    "Amazing! You’ve achieved nothing today. A true minimalist 👏",
    "We checked your task list — it’s emptier than a ghost town 🏜️",
    "Your tasks called. They miss you.",
    "Still waiting for that first task like it's a Marvel post-credit scene...",
    "Didn’t know *ignoring your goals* was your 2025 resolution. Bold.",
    "No tasks yet? Revolutionary. Who needs structure anyway?",
    "It's impressive how consistently inconsistent you're being.",
    "Remember your dreams? Yeah… they called. They’re worried.",
    "Still no tasks? You’re either enlightened or completely unbothered.",
    "Just winging the day again, huh? Respect."
    ],

    # 😂 Funny / Playful
    "playful":[
    "Hey, your task tracker is feeling lonely. Show it some love 💔",
    "Adding one task today could be the butterfly effect that saves the world. No pressure.",
    "Not doing anything today? Cool cool. Bold strategy.",
    "Your task list is starting to look like a vacation home — completely empty.",
    "Plot twist: today’s goal is to *add* a goal.",
    "Even your coffee wants you to be productive.",
    "Your tracker’s crying in the corner. Give it a purpose.",
    "Productivity ghosts have taken your tasks. Rescue them.",
    "Add a task. Or don’t. But just know we’ll judge you either way."
    ],

    # 🧠 Reverse Psychology / Mind Games
    "reverse_psychology":[
    "Honestly, don’t add any tasks today. You deserve to be overwhelmed tomorrow instead!",
    "Why be productive today when you can panic tomorrow?",
    "Sure, don’t add a task. Let Future You deal with the consequences. 😌",
    "Don’t add any tasks. Chaos is a totally acceptable life strategy.",
    "Stay task-less. It's worked so well so far, right?",
    "You know what’s better than a to-do list? Literally everything else. Don’t bother.",
    "Ignore this reminder. What’s the worst that could happen? 😬",
    "No tasks today? Cool. Hope you enjoy panic-working at 11:59 PM."
    ],

    # 🎯 Focused / Encouraging
    "focus":[
    "Your goals are valid. Let’s take the first step. Add a task.",
    "Come on, even Batman had a to-do list.",
    "Small steps > no steps. Start with one task.",
    "What’s one small thing you can do today? Write it down.",
    "Tasks turn intentions into action. Start with one.",
    "You don’t have to do it all. You just have to start.",
    "It’s not about perfection. It’s about progress. Begin now.",
    "Write it. Do it. Check it off. Repeat.",
     "Let’s get one thing done right today. Start with a task.",
    "A clear plan beats a busy mind. Add your first task.",
    "Start small. Stay consistent. Progress will follow.",
    "Even one task today can shift your momentum.",
    "Focus isn’t magic — it’s a habit. Let’s build it.",
    ],

    # 🎬 Pop Culture / Nerdy
    "nerdy":[
    "Task Tracker: 0 | Chaos: 1 — Wanna even the score?",
    "If you don't add a task, does your planner even exist? 🤔",
    "Even AI thinks you should write down your tasks. Just saying.",
    "Remember what Yoda said: 'Do or do not, there is no... forget to track.'",
    "Like Frodo with the ring, you must begin your journey. Start by adding a task.",
    "Even Tony Stark had a plan. What’s yours today?",
    "Be the Hermione of your day — organized and unstoppable.",
    "Even Thanos had a checklist. What's your excuse?",
    "Like Mario needs coins, you need completed tasks to level up.",
    "Wakanda had a plan. So should you."
    ]
}

GREETINGS = {
    "focus": [
    "📍 Time to focus, {name}.",
    "📋 Let's set the tone for your day, {name}.",
    "🧘‍♀️ One step at a time, {name}. Let’s begin.",
    "🕰️ The best moment to start is now, {name}.",
    "✅ Just one task to shift the day, {name}.",
    ],
    "motivational": [
        "🌞 Good morning, productivity warrior {name}!",
        "🎯 Let’s get focused, {name}!",
        "🚀 Rise and grind, {name}!"
    ],
    "sarcastic": [
        "😏 Look who still hasn’t added a task — {name}!",
        "🙄 Oh wow, it’s you again, {name}!",
        "🥴 Hey {name}, still chillin’, huh?",
        "👀 Guess who still hasn't done their homework?",
        "📅 Your task list is emptier than a Monday morning coffee pot.",
        "🪞 Mirror mirror on the wall, who’s avoiding their goals most of all?"
    ],
    "playful": [
        "👻 Boo! Task ghosts checking in, {name}!",
        "🎲 Random productivity check, {name}!",
        "🐢 Slow and steady doesn’t mean stopped, {name}!"
    ],
    "reverse_psychology": [
        "🤷‍♂️ Whatever, {name}. Just ignore this like always.",
        "🧨 Don’t read this. Seriously.",
        "😌 We both know you’re not gonna add anything, {name}."
    ],
    "nerdy": [
        "🧠 Activate productivity mode, {name}!",
        "🛸 Incoming data from Task HQ, {name}.",
        "📡 Productivity signal is weak… boost it, {name}?"
    ]
}

# 📝 Sign-offs per tone
SIGN_OFFS = {
    "motivational": [
        "🔥 Let’s crush it today.",
        "📈 Start strong. End stronger.",
        "💪 Small wins add up."
    ],
    "sarcastic": [
        "👏 Truly inspiring levels of inaction.",
        "😎 Keep it up. Or don’t. Who cares?",
        "🫠 At this point, even we’ve given up.",
        "😂 Come on, one task won’t kill you.",
        "⏳ Your goals are gathering dust.",
        "👈 Task button’s still right there. Just saying."
    ],
    "playful": [
        "🦥 We believe in you… slowly but surely.",
        "✨ Add a task — make your tracker sparkle.",
        "🎉 One task a day keeps the chaos away."
    ],
    "reverse_psychology": [
        "😅 But really… just don’t do it.",
        "🛋️ Just vibe today. You’ve earned it (maybe).",
        "🤡 What could go wrong, right?"
    ],
    "nerdy": [
        "📟 Log your mission for today.",
        "💾 Save your progress. Add a task.",
        "🎮 Don’t let life beat you — level up."
    ],
    "focus": [
    "🧩 Start with clarity. End with results.",
    "🎯 One task. One win.",
    "📌 Your focus moment starts here.",
    "🛠️ Let’s build your day one task at a time.",
    "🔒 Stay sharp. Stay on track.",
]
    
}

def build_message(name):
    name = name
    tone = random.choice(list(TONE_GROUPS.keys()))

    message = random.choice(TONE_GROUPS[tone])
    greeting = random.choice(GREETINGS[tone]).format(name=name)
    sign_off = random.choice(SIGN_OFFS[tone])
    app_link = "https://tasktrackertrail0.streamlit.app/"  # replace with your real link

    html_message = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background-color: #f4f4f4;
                color: #333;
                padding: 20px;
            }}
            .container {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                max-width: 500px;
                margin: auto;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }}
            h2 {{
                color: #444;
            }}
            h3 {{
                color: #666;
                }}
            p {{
                font-size: 18px;
                line-height: 1.6;
            }}
            .cta {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 14px;
                color: #888;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{greeting}</h2>
            <h3>{message}</h3>
            <a class="cta" href="{app_link}">🚀 Open Your Task Tracker</a>
            <p>Click the button above to add your tasks and get started!</p>
            <h3 class="footer">{sign_off}</h3>
            <h4 style="margin-top: 20px; font-weight: bold; color: #4CAF50;">— Team S.A.R.A</h4>
        </div>
    </body>
    </html>
    """
    return html_message



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
            html_message = build_message(name)
            yag.send(
            to=email,
            subject="⏰ Daily Task Reminder",
            contents=[html_message]
        )
        print(f"Sent reminder to {name} ({email})")

if __name__ == "__main__":
    send_reminders()
