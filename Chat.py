import streamlit as st
import datetime
from db import load_db, save_db, get_vip_tier, DEV_ACCOUNTS

st.set_page_config(page_title="💬 Chat", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username

def load_chat():
    db = load_db()
    if "chat" not in db:
        db["chat"] = []
        save_db(db)
    return db["chat"]

def send_message(username, message):
    if not message.strip():
        return
    db = load_db()
    if "chat" not in db:
        db["chat"] = []
    tier = get_vip_tier(db["users"].get(username, {}).get("money", 0))
    db["chat"].append({
        "user": username,
        "message": message.strip(),
        "time": datetime.datetime.now().strftime("%H:%M"),
        "vip": tier["emoji"],
        "dev": username in DEV_ACCOUNTS
    })
    # keep only last 50 messages
    db["chat"] = db["chat"][-50:]
    save_db(db)

def delete_message(index):
    db = load_db()
    if "chat" in db and 0 <= index < len(db["chat"]):
        db["chat"].pop(index)
        save_db(db)

# ---------------- UI ----------------
st.title("💬 Casino Chat")
st.caption("Chat with other players in real time! Refresh to see new messages.")

# Chat display
messages = load_chat()

if not messages:
    st.info("No messages yet — be the first to say something!")
else:
    for i, msg in enumerate(reversed(messages)):
        real_index = len(messages) - 1 - i
        is_me = msg["user"] == user
        is_dev = msg.get("dev", False)
        vip = msg.get("vip", "🥉")

        name_color = "#FFD700" if is_dev else "#00d4ff" if is_me else "#aaaaaa"
        bg_color = "#1e3a5f" if is_me else "#2a2a2a"
        align = "flex-end" if is_me else "flex-start"
        dev_badge = " 👑" if is_dev else ""

        st.markdown(f"""
        <div style="display:flex;justify-content:{align};margin:4px 0;">
          <div style="background:{bg_color};border-radius:12px;padding:10px 14px;
          max-width:70%;word-wrap:break-word;">
            <div style="font-size:12px;color:{name_color};font-weight:bold;margin-bottom:3px;">
              {vip} {msg['user']}{dev_badge} <span style="color:#666;font-weight:normal">{msg['time']}</span>
            </div>
            <div style="color:white;font-size:15px;">{msg['message']}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Dev can delete any message, users can delete their own
        if is_me or user in DEV_ACCOUNTS:
            if st.button("🗑️", key=f"del_{real_index}"):
                delete_message(real_index)
                st.rerun()

st.markdown("---")

# Message input
col1, col2 = st.columns([5, 1])
with col1:
    new_msg = st.text_input("Message", placeholder="Type a message...", label_visibility="collapsed", key="chat_input")
with col2:
    if st.button("Send 💬"):
        if new_msg.strip():
            send_message(user, new_msg)
            st.rerun()
        else:
            st.warning("Can't send empty message!")

if st.button("🔄 Refresh Chat"):
    st.rerun()

st.caption("Chat auto-keeps the last 50 messages.")
