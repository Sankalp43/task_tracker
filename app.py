# Team Task Tracker - Full Structured Version with Features

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from supabase import create_client, Client
import hashlib
import yagmail
from datetime import datetime, time
import math
# --- SUPABASE CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# utils/email_utils.py


SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
APP_PASSWORD = st.secrets["APP_PASSWORD"]  # Keep this secure

yag = yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD)

def send_welcome_email(to_email, name):
    subject = f"Welcome to Team Task Tracker, {name}! 🎉"
    body = f"""
    Hi {name},

    Welcome aboard! We're excited to have you using the Team Task Tracker 🚀.

    You can start adding tasks, earning points, and tracking your daily wins.
    Let's get productive! 💪

    Cheers,  
    - Team Task Tracker
    """
    print(f"Sending email to {to_email}...")
    yag.send(to_email, subject, body)









# --- CONSTANTS ---
CATEGORY_COLORS = {
    "Work": "#4a90e2",
    "Personal": "#f39c12",
    "Health": "#27ae60",
    "Learning": "#8e44ad",
    "Other": "#95a5a6"
}

# --- PAGE CONFIG ---
st.set_page_config(page_title="Team Task Tracker", layout="wide")

# --- FUNCTIONS ---
def avatar_url(name):
    hashed = hashlib.md5(name.encode()).hexdigest()
    return f"https://robohash.org/{hashed}?set=set5"

def get_badges(points):
    badges = []
    if points >= 100: badges.append("Legend (100+ pts) 🏅")
    if points >= 50: badges.append("Gold (50+ pts) 🥇")
    if points >= 25: badges.append("Silver (25+ pts) 🥈")
    if points >= 10: badges.append("Bronze (10+ pts) 🥉")
    if points == 0: badges.append("Getting Started 🌱")
    return badges

@st.cache_data(ttl=60)
def load_tasks():
    data = supabase.table("tasks").select("*").execute()
    return pd.DataFrame(data.data) if data.data else pd.DataFrame(columns=[
        "id", "user", "task", "points", "status", "date", "completed_date", "category"])

DEADLINE_CATEGORIES = [
    "⏳ No Deadline",
    "⏰ Morning",
    "🌤️ Afternoon",
    "🌇 Evening",
    "🌌 End of Day"
]

DEADLINE_TIMES = {
    "⏰ Morning": time(10, 0),
    "🌤️ Afternoon": time(14, 0),
    "🌇 Evening": time(18, 0),
    "🌌 End of Day": time(23, 59),
    "⏳ No Deadline": None
}

def add_task(user, task, points, category, deadline_category):
    supabase.table("tasks").insert({
        "user": user,
        "task": task,
        "points": points,
        "status": False,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "completed_date": None,
        "category": category,
        "deadline_category": deadline_category
    }).execute()
    st.cache_data.clear()

def add_user(name, email):
    supabase.table("users").insert({
        "user": name,
        "mail": email,
        "created_at": datetime.now().isoformat()
    }).execute()
    st.cache_data.clear()


def complete_task(task_id):
    supabase.table("tasks").update({
        "status": True,
        "completed_date": datetime.now().strftime("%Y-%m-%d")
    }).eq("id", task_id).execute()
    st.cache_data.clear()

def edit_task(task_id, new_task, new_points, new_category):
    supabase.table("tasks").update({
        "task": new_task,
        "points": new_points,
        "category": new_category
    }).eq("id", task_id).execute()
    st.cache_data.clear()

# --- SIDEBAR ---
# def show_sidebar():
#     st.sidebar.title("Add New Task ➕")
#     with st.sidebar.form("add_task"):
#         user = st.text_input("👤 Your Name")
#         task = st.text_input("📝 Task Description")
#         points = st.slider("⭐ Points Value", 1, 10, 3)
#         category = st.selectbox("🏷️ Category", list(CATEGORY_COLORS.keys()))
#         deadline_category = st.selectbox("📅 Task Deadline", DEADLINE_CATEGORIES)
#         if st.form_submit_button("Add Task") and user and task:
#             add_task(user, task, points, category, deadline_category)
#             st.success("Task added successfully!💪")
#             st.rerun()
#     st.sidebar.markdown("---")
#     st.sidebar.title("View Options 🛠️")
#     dark_mode = st.sidebar.toggle("Dark Mode")
#     admin_mode = st.sidebar.checkbox("Admin Mode (View All Users)", value=True)
#     return dark_mode, admin_mode

@st.cache_data(ttl=60)
def load_users():
    data = supabase.table("users").select("user").execute()
    # print(data)
    return sorted([user["user"] for user in data.data]) if data.data else []

def show_sidebar():
    st.sidebar.title("👤 Select or Create User")

    users = load_users()
    user_mode = st.sidebar.radio("Choose:", ["Existing User", "New User"])

    if user_mode == "Existing User" and users:
        selected_user = st.sidebar.selectbox("Select your name", users)
        st.session_state.user = selected_user
    elif user_mode == "New User":
        new_name = st.sidebar.text_input("Enter your name")
        new_email = st.sidebar.text_input("Enter your email")
        if st.sidebar.button("Create User") and new_name and new_email:
            existing = supabase.table("users").select("id").eq("mail", new_email).execute().data

            if existing:
                st.warning("A user with this email already exists. Please use a different email or choose 'Existing User'.")
            else:
                add_user(new_name, new_email)
                send_welcome_email(new_email, new_name)
                st.session_state.user = new_name
                st.success(f"Welcome, {new_name}!")
                st.rerun()

    if "user" not in st.session_state:
        st.sidebar.warning("Please select or create a user to continue.")
        return None, None

    st.sidebar.markdown(f"**Logged in as:** {st.session_state.user}")

    # --- Add Task Form ---
    st.sidebar.markdown("---")
    st.sidebar.title("➕ Add New Task")

    with st.sidebar.form("add_task"):
        task = st.text_input("📝 Task Description")
        points = st.slider("⭐ Points Value", 1, 10, 3)
        category = st.selectbox("🏷️ Category", list(CATEGORY_COLORS.keys()))
        deadline_category = st.selectbox("📅 Task Deadline", DEADLINE_CATEGORIES)
        if st.form_submit_button("Add Task") and task:
            add_task(st.session_state.user, task, points, category, deadline_category)
            st.success("Task added successfully! 💪")
            st.rerun()

    # --- View Options ---
    st.sidebar.markdown("---")
    st.sidebar.title("🛠️ View Options")
    dark_mode = st.sidebar.toggle("Dark Mode")
    admin_mode = st.sidebar.checkbox("Admin Mode", value=False)

    return dark_mode, admin_mode


# --- MAIN APP LAYOUT ---
def main():
    st.title("Team Task Tracker 🚀")
    dark_mode, admin_mode = show_sidebar()

    df = load_tasks()
    if df.empty:
        st.info("No tasks yet. Add some in the sidebar! 🌟")
        return

    df['date'] = pd.to_datetime(df['date'])
    df['completed_date'] = pd.to_datetime(df['completed_date'])

    user_filter = st.selectbox("Filter by user", ["All"] + sorted(df['user'].unique().tolist()))
    category_filter = st.selectbox("Filter by category", ["All"] + list(CATEGORY_COLORS.keys()))

    if user_filter != "All":
        df = df[df['user'] == user_filter]
    if category_filter != "All":
        df = df[df['category'] == category_filter]

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["📋 Active Tasks", "🏆 Leaderboard", "📈 Progress"])

    with tab1:
        show_tasks(df, admin_mode)

    with tab2:
        show_leaderboard(df)

    with tab3:
        show_progress_over_time(df)

    with st.expander("How to Use this App ❓"):
        st.write("""
        1. Use the sidebar to add new tasks with a category and point value.
        2. Check off tasks once they're done to earn points.
        3. Track progress with charts, badges, and a leaderboard.
        4. Use filters to focus on specific users or categories.
        """)

    with st.expander("🕒 Deadline Reference"):
        st.markdown("""
        **Here's what each deadline means:**

        - ☀️ **Morning Deadline** — Complete before **11:00 AM**
        - 🌤️ **Afternoon Deadline** — Complete before **5:00 PM**
        - 🌇 **Evening Deadline** — Complete before **8:00 PM**
        - 🌌 **End of Day** — Complete by **11:59 PM**

        Use these to set realistic expectations for when tasks should be completed.
        """)


# --- ACTIVE TASKS ---
import math

def show_tasks(df, admin_mode):
    if df.empty:
        st.warning("No tasks found for the current user.")
        return  # Exit the function early
    users = df['user'].unique()
    if len(users) == 0:
        st.info("No users found with tasks.")
        return
    # Define number of users per row
    users_per_row = 3  # Or whatever you want as the max columns per row
    total_rows = math.ceil(len(users) / users_per_row)

    # Create each row of columns
    for row in range(total_rows):
        cols = st.columns(users_per_row)
        # Determine the range of users to show in this row
        for idx in range(users_per_row):
            user_idx = row * users_per_row + idx
            if user_idx < len(users):  # Check if user exists in the current row
                user = users[user_idx]
                with cols[idx]:
                    st.image(avatar_url(user), width=50)
                    st.markdown(f"**{user}**")
                    user_tasks = df[(df['user'] == user) & (~df['status'])]
                    for _, task in user_tasks.iterrows():
                        color = CATEGORY_COLORS.get(task['category'], "#ccc")
                        task_key = f"{task['id']}"
                        checked = st.checkbox(task['task'], key=task_key)
                        if checked and not task['status']:
                            complete_task(task['id'])
                            st.rerun()
                        deadline = task["deadline_category"]
                        if deadline:
                            st.markdown(f"⭐ {task['points']} pts | 🏷️ {task['category']} | {deadline} ")
                        else:
                            st.markdown(f"⭐ {task['points']} pts | 🏷️ {task['category']} | 📅 No Deadline")

                    if admin_mode:
                        with st.expander("Edit Task"):
                            new_task = st.text_input("Edit description", value=task['task'], key=f"edit_{task['id']}_task")
                            new_points = st.slider("Edit points", 1, 10, value=task['points'], key=f"edit_{task['id']}_points")
                            new_category = st.selectbox("Edit category", list(CATEGORY_COLORS.keys()), index=list(CATEGORY_COLORS.keys()).index(task['category']), key=f"edit_{task['id']}_cat")
                            if st.button("Save Changes", key=f"save_{task['id']}"):
                                edit_task(task['id'], new_task, new_points, new_category)
                                st.success("Task updated!")
                                st.rerun()
        # Add space after each row of users (to handle varying lengths of user task lists)
        st.write("")  # This will add some space after each row of columns

# def show_tasks(df, admin_mode):
#     if df.empty:
#         st.warning("No tasks found for the current user.")
#         return  # Exit the function early
#     users = df['user'].unique() 
#     # if len(users) == 0:
#     #     st.info("No users found with tasks.")
#     #     return
#     # cols = st.columns(min(len(users), 3))  # Max 5 columns per row
#     # for idx, user in enumerate(users):
#     if len(users) == 0:
#         st.info("No users found with tasks.")
#         return
#     # Define number of users per row
#     users_per_row = 3  # Or whatever you want as the max columns per row
#     total_rows = math.ceil(len(users) / users_per_row)

#     # Create each row of columns
#     for row in range(total_rows):
#         cols = st.columns(users_per_row)
#         # Determine the range of users to show in this row
#         for idx in range(users_per_row):
#             user_idx = row * users_per_row + idx
#             if user_idx < len(users):  # Check if user exists in the current row
#                 user = users[user_idx]
#         with cols[idx]:
#             st.image(avatar_url(user), width=50)
#             st.markdown(f"**{user}**")
#             user_tasks = df[(df['user'] == user) & (~df['status'])]
#             for _, task in user_tasks.iterrows():
#                 color = CATEGORY_COLORS.get(task['category'], "#ccc")
#                 task_key = f"{task['id']}"
#                 checked = st.checkbox(task['task'], key=task_key)
#                 if checked and not task['status']:
#                     complete_task(task['id'])
#                     st.rerun()
#                 deadline = task["deadline_category"]
#                 if deadline:
#                     st.markdown(f"⭐ {task['points']} pts| 🏷️ {task['category']} | {deadline} ")
#                 else:
#                     st.markdown(f"⭐ {task['points']} pts| 🏷️ {task['category']} | 📅 No Deadline")

#                 if admin_mode:
#                     with st.expander("Edit Task"):
#                         new_task = st.text_input("Edit description", value=task['task'], key=f"edit_{task['id']}_task")
#                         new_points = st.slider("Edit points", 1, 10, value=task['points'], key=f"edit_{task['id']}_points")
#                         new_category = st.selectbox("Edit category", list(CATEGORY_COLORS.keys()), index=list(CATEGORY_COLORS.keys()).index(task['category']), key=f"edit_{task['id']}_cat")
#                         if st.button("Save Changes", key=f"save_{task['id']}"):
#                             edit_task(task['id'], new_task, new_points, new_category)
#                             st.success("Task updated!")
#                             st.rerun()
    # cols = st.columns(len(users))
    # for idx, user in enumerate(users):
    #     with cols[idx]:
    #         st.image(avatar_url(user), width=50)
    #         st.markdown(f"**{user}**")
    #         user_tasks = df[(df['user'] == user) & (~df['status'])]
    #         for _, task in user_tasks.iterrows():
    #             color = CATEGORY_COLORS.get(task['category'], "#ccc")
    #             task_key = f"{task['id']}"
    #             checked = st.checkbox(task['task'], key=task_key)
    #             if checked and not task['status']:
    #                 complete_task(task['id'])
    #                 st.rerun()
    #             deadline = task["deadline_category"]
    #             if deadline:
                #     st.markdown(f"⭐ {task['points']} pts| 🏷️ {task['category']} | {deadline} ")
                # else:
                #     st.markdown(f"⭐ {task['points']} pts| 🏷️ {task['category']} | 📅 No Deadline")

                # if admin_mode:
                #     with st.expander("Edit Task"):
                #         new_task = st.text_input("Edit description", value=task['task'], key=f"edit_{task['id']}_task")
                #         new_points = st.slider("Edit points", 1, 10, value=task['points'], key=f"edit_{task['id']}_points")
                #         new_category = st.selectbox("Edit category", list(CATEGORY_COLORS.keys()), index=list(CATEGORY_COLORS.keys()).index(task['category']), key=f"edit_{task['id']}_cat")
                #         if st.button("Save Changes", key=f"save_{task['id']}"):
                #             edit_task(task['id'], new_task, new_points, new_category)
                #             st.success("Task updated!")
                #             st.rerun()

# --- LEADERBOARD ---
def show_leaderboard(df):
    completed = df[df['status']]
    totals = completed.groupby('user')['points'].sum().reset_index().sort_values(by='points', ascending=False)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top Users 🧑‍🚀")
        for _, row in totals.iterrows():
            st.image(avatar_url(row['user']), width=40)
            st.markdown(f"**{row['user']}** — {row['points']} pts")
            st.markdown(", ".join(get_badges(row['points'])))
            progress = min(row['points'], 100)
            st.progress(progress / 100)
    with col2:
        st.markdown("### 📊 Total Points Bar Chart")
        chart = alt.Chart(totals).mark_bar().encode(
            x=alt.X('user', sort='-y'),
            y='points',
            color='user'
        )
        st.altair_chart(chart, use_container_width=True)

# --- PROGRESS OVER TIME ---
def show_progress_over_time(df):
    df = df[df['status']]
    view_by = st.radio("View progress by", ["Week", "Month"], horizontal=True)
    if view_by == "Week":
        df['period'] = df['completed_date'].dt.strftime('%Y-%U')
    else:
        df['period'] = df['completed_date'].dt.strftime('%Y-%m')

    progress = df.groupby(['user', 'period'])['points'].sum().reset_index()
    chart = alt.Chart(progress).mark_line(point=True).encode(
        x='period',
        y='points',
        color='user'
    )
    st.altair_chart(chart, use_container_width=True)

if __name__ == '__main__':
    main()
