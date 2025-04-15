import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from supabase import create_client, Client
import hashlib

# --- CONFIGURE YOUR SUPABASE ---
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CATEGORY COLORS ---
CATEGORY_COLORS = {
    "Work": "#4a90e2",
    "Personal": "#f39c12",
    "Health": "#27ae60",
    "Learning": "#8e44ad",
    "Other": "#95a5a6"
}

# --- BADGE LOGIC ---
def get_badges(points):
    badges = []
    if points >= 100:
        badges.append("🏅 Legend (100+ pts)")
    if points >= 50:
        badges.append("🥇 Gold (50+ pts)")
    if points >= 25:
        badges.append("🥈 Silver (25+ pts)")
    if points >= 10:
        badges.append("🥉 Bronze (10+ pts)")
    if points == 0:
        badges.append("🌱 Getting Started")
    return badges

# --- AVATAR GENERATOR ---
def avatar_url(name):
    # Use robohash for fun avatars
    hashed = hashlib.md5(name.encode()).hexdigest()
    return f"https://robohash.org/{hashed}?set=set5"

# --- LOAD TASKS FROM SUPABASE ---
@st.cache_data(ttl=60)
def load_tasks():
    data = supabase.table("tasks").select("*").execute()
    return pd.DataFrame(data.data) if data.data else pd.DataFrame(columns=[
        "id", "user", "task", "points", "status", "date", "completed_date", "category"
    ])

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

# --- MAIN APP ---
st.set_page_config(page_title="Team Task Tracker", layout="wide")
st.markdown("""
<style>
.header { font-size: 2.5em; color: #4a90e2; text-align: center; }
.user-card { padding: 1.5rem; border-radius: 15px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.task-item { padding: 0.5rem; margin: 0.3rem 0; border-left: 4px solid #4a90e2; }
.points-badge { background: #4a90e2; color: white; padding: 0.2rem 0.8rem; border-radius: 15px; }
.category-badge { color: white; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.9em; margin-left: 0.5em;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="header">🚀 Team Task Tracker</p>', unsafe_allow_html=True)

# --- SIDEBAR: ADD TASK ---
with st.sidebar:
    st.subheader("➕ Add New Task")
    with st.form("task_form"):
        user = st.text_input("👤 Your Name")
        task = st.text_input("📝 Task Description")
        points = st.slider("⭐ Points Value", 1, 10, 3)
        category = st.selectbox("🏷️ Category", list(CATEGORY_COLORS.keys()))
        submitted = st.form_submit_button("Add Task")
        if submitted and user and task:
            add_task(user, task, points, category)
            st.success("Task added! 💪")
            st.rerun()

# --- LOAD DATA ---
df = load_tasks()
if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df['completed_date'] = pd.to_datetime(df['completed_date'])
else:
    st.info("No tasks yet. Add some in the sidebar! 🌟")

## NEW LEADERBOARD SECTION  
st.subheader("🏆 Leaderboard")
if not df.empty:
    totals = df[df['status']].groupby('user')['points'].sum().reset_index()
    totals = totals.sort_values(by="points", ascending=False)
    
    # Create two columns for leaderboard and achievements
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Team Members")
        for _, row in totals.iterrows():
            st.image(avatar_url(row['user']), width=40)
            st.markdown(f"**{row['user']}**")
            st.markdown(f"<span class='points-badge'>{row['points']} pts</span>", unsafe_allow_html=True)
            for badge in get_badges(row['points']):
                st.markdown(f"{badge}")
            st.markdown("---")
            
    with col2:
        st.subheader("🏅 Achievements")
        for _, row in totals.iterrows():
            st.image(avatar_url(row['user']), width=40)
            st.markdown(f"**{row['user']}**")
            for badge in get_badges(row['points']):
                st.markdown(f"{badge}")
            st.markdown("---")
    
    # Full-width chart below the columns
    st.subheader("📊 Team Progress")
    st.altair_chart(alt.Chart(totals).mark_bar().encode(
        x=alt.X('user', sort='-y'),
        y='points',
        color=alt.Color('user', legend=None)
    ), use_container_width=True)


# --- LEADERBOARD ---
# st.subheader("🏆 Leaderboard")
# if not df.empty:
#     totals = df[df['status']].groupby('user')['points'].sum().reset_index()
#     totals = totals.sort_values(by="points", ascending=False)
#     col1, col2, col3 = st.columns([2, 4, 2])
#     with col1:
#         for _, row in totals.iterrows():
#             st.image(avatar_url(row['user']), width=40)
#             st.markdown(f"**{row['user']}**")
#             st.markdown(f"<span class='points-badge'>{row['points']} pts</span>", unsafe_allow_html=True)
#             for badge in get_badges(row['points']):
#                 st.markdown(f"{badge}")
#             st.markdown("---")
#     with col2:
#         st.write("### Team Progress")
#         st.altair_chart(alt.Chart(totals).mark_bar().encode(
#             x=alt.X('user', sort='-y'),
#             y='points',
#             color=alt.Color('user', legend=None)
#         ), use_container_width=True)
#     with col3:
#         st.write("### Achievements")
#         for _, row in totals.iterrows():
#             st.markdown(f"**{row['user']}**")
#             for badge in get_badges(row['points']):
#                 st.markdown(f"{badge}")
#             st.markdown("---")
# else:
#     st.info("No points yet - add some tasks! ✨")

# --- WEEKLY/MONTHLY PROGRESS ---
st.subheader("📈 Progress Over Time")
if not df.empty:
    period = st.radio("View progress by:", ["Week", "Month"], horizontal=True)
    if period == "Week":
        df['week'] = df['completed_date'].dt.strftime('%Y-%U')
        progress = df[df['status']].groupby(['user', 'week'])['points'].sum().reset_index()
        x_axis = 'week'
    else:
        df['month'] = df['completed_date'].dt.strftime('%Y-%m')
        progress = df[df['status']].groupby(['user', 'month'])['points'].sum().reset_index()
        x_axis = 'month'
    if not progress.empty:
        st.altair_chart(
            alt.Chart(progress).mark_line(point=True).encode(
                x=x_axis,
                y='points',
                color='user'
            ).properties(width=700),
            use_container_width=True
        )
    else:
        st.info("No completed tasks yet for this period.")

# --- ACTIVE TASKS ---
st.subheader("📋 Active Tasks")
if not df.empty:
    users = df['user'].unique()
    cols = st.columns(len(users))
    for idx, user in enumerate(users):
        with cols[idx]:
            st.markdown(f'<div class="user-card" style="background-color: #f0f5ff">'
                        f'<img src="{avatar_url(user)}" width="60"/><br>'
                        f'<h3>👤 {user}</h3>', unsafe_allow_html=True)
            user_tasks = df[(df['user'] == user) & (~df['status'])]

            #####################
            for _, task in user_tasks.iterrows():
                color = CATEGORY_COLORS.get(task['category'], "#95a5a6")
                task_key = f"{user}-{task['task']}-{task['id']}"
                checked = st.checkbox(
                    task['task'],
                    key=task_key,
                    help=f"Added on {task['date'].strftime('%Y-%m-%d')}",
                    value=task['status']
                )
                    # complete_task(task['id'])
                    # st.rerun()
                st.markdown(
                    f"<span class='points-badge'>{task['points']}pts</span>"
                    f"<span class='category-badge' style='background:{color}'>{task['category']}</span>",
                    unsafe_allow_html=True
                )
                if checked and not task['status']:
                    complete_task(task['id'])
                    st.rerun()
#             st.markdown('</div>', unsafe_allow_html=True)
# else:
#     st.info("No tasks yet - add some in the sidebar! 🌟")

# --- HOW TO USE ---
st.markdown("---")
with st.expander("🚀 How to Use This App"):
    st.write("""
    1. **Add Tasks** using the sidebar form (choose category and points)
    2. **Check off tasks** when completed
    3. **Track progress** through the leaderboard and charts
    4. **Earn badges** as you accumulate points
    5. **See avatars** for each team member
    6. **All data is saved in the cloud (Supabase)**
    """)

st.caption("Made with ❤️ using Streamlit and Supabase")
