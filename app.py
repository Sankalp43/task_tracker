# Team Task Tracker - Full Structured Version with Features

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from supabase import create_client, Client
import hashlib

# --- SUPABASE CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

def add_task(user, task, points, category):
    supabase.table("tasks").insert({
        "user": user,
        "task": task,
        "points": points,
        "status": False,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "completed_date": None,
        "category": category
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
def show_sidebar():
    st.sidebar.title("Add New Task ➕")
    with st.sidebar.form("add_task"):
        user = st.text_input("👤 Your Name")
        task = st.text_input("📝 Task Description")
        points = st.slider("⭐ Points Value", 1, 10, 3)
        category = st.selectbox("🏷️ Category", list(CATEGORY_COLORS.keys()))
        if st.form_submit_button("Add Task") and user and task:
            add_task(user, task, points, category)
            st.success("Task added successfully!💪")
            st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.title("View Options 🛠️")
    dark_mode = st.sidebar.toggle("Dark Mode")
    admin_mode = st.sidebar.checkbox("Admin Mode (View All Users)", value=True)
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

# --- ACTIVE TASKS ---
def show_tasks(df, admin_mode):
    if df.empty:
        st.warning("No tasks found for the current user.")
        return  # Exit the function early
    users = df['user'].unique() if admin_mode else [df['user'].iloc[0]]
    if len(users) == 0:
        st.info("No users found with tasks.")
        return
    cols = st.columns(len(users))
    for idx, user in enumerate(users):
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
                st.markdown(f"{task['points']} pts | 🏷️ {task['category']}")
                if admin_mode:
                    with st.expander("Edit Task"):
                        new_task = st.text_input("Edit description", value=task['task'], key=f"edit_{task['id']}_task")
                        new_points = st.slider("Edit points", 1, 10, value=task['points'], key=f"edit_{task['id']}_points")
                        new_category = st.selectbox("Edit category", list(CATEGORY_COLORS.keys()), index=list(CATEGORY_COLORS.keys()).index(task['category']), key=f"edit_{task['id']}_cat")
                        if st.button("Save Changes", key=f"save_{task['id']}"):
                            edit_task(task['id'], new_task, new_points, new_category)
                            st.success("Task updated!")
                            st.rerun()

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
