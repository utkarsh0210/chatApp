import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Group Chat & Scheduler", layout="centered")

st.title("💬 Multi-User Chat & 🗓️ Meeting Scheduler")

# Tabs
tab1, tab2 = st.tabs(["📨 Chat", "📅 Schedule Meeting"])

# ---- TAB 1: CHAT ---- #
with tab1:
    st.subheader("Group Chat Room")

    with st.form("send_message_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        content = st.text_area("Message")

        submitted = st.form_submit_button("Send Message")

        if submitted:
            if name and email and content:
                res = requests.post(f"{API_URL}/message", json={
                    "name": name,
                    "email": email,
                    "content": content,
                    "timestamp": datetime.utcnow().isoformat()
                })

                if res.status_code == 200:
                    st.success("✅ Message sent!")
                else:
                    st.error("❌ Failed to send message.")
            else:
                st.warning("⚠️ All fields are required.")

    st.markdown("### 📜 Chat History")

    if st.button("🔄 Refresh Messages"):
        pass  # just to trigger rerun

    try:
        messages = requests.get(f"{API_URL}/messages").json()
        for msg in messages:
            st.write(f"🕒 {msg['timestamp']} - **{msg['name']}** ({msg['email']}): {msg['content']}")
    except:
        st.error("❌ Unable to fetch messages. Is backend running?")

# ---- TAB 2: SCHEDULING ---- #
with tab2:
    st.subheader("📅 Schedule a Meeting")

    with st.form("meeting_form"):
        title = st.text_input("Meeting Title")
        date = st.date_input("Date")
        time = st.time_input("Time")
        participants = st.text_area("Participants (comma-separated emails)")

        submit_meeting = st.form_submit_button("Schedule Meeting")

        if submit_meeting:
            if title and date and time and participants:
                participants_list = [p.strip() for p in participants.split(",") if p.strip()]
                payload = {
                    "title": title,
                    "date": str(date),
                    "time": str(time),
                    "participants": participants_list
                }
                res = requests.post(f"{API_URL}/schedule", json=payload)
                if res.status_code == 200:
                    st.success("✅ Meeting scheduled!")
                else:
                    st.error("❌ Failed to schedule meeting.")
            else:
                st.warning("⚠️ Fill all fields.")

    st.markdown("### 📅 Scheduled Meetings")
    try:
        meetings = requests.get(f"{API_URL}/meetings").json()
        for m in meetings:
            st.write(f"📌 **{m['title']}** at {m['date']} {m['time']} — Participants: {', '.join(m['participants'])}")
    except:
        st.error("❌ Unable to fetch meetings.")
