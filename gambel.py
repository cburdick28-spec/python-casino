import streamlit as st
import datetime
import time
from db import load_db, save_db, save_progress, hash_password, DEV_ACCOUNTS, ensure_user_fields, get_vip_tier, check_vip_achievements, MAX_SAFE_MONEY

st.set_page_config(page_title="🎰 Ultimate Casino", layout="wide")

defaults = {
    "username": None,
    "money": 500,
    "bj_player": [],
    "bj_dealer": [],
    "bj_active": False,
    "bj_result": None,
    "bj_bet": 0,
    "jackpot_odds": 6
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

db = load_db()
if "users" not in db:
    db["users"] = {}
if "jackpot" not in db:
    db["jackpot"] = 1000
for u in db["users"]:
    db["users"][u] = ensure_user_fields(db["users"][u])
save_db(db)
users = db["users"]

# ---------------- LOGIN ----------------
if st.session_state.username is None:
    st.title("🎰 Ultimate Casino")
    tab1, tab2 = st.tabs(["Login", "Register"])
    db = load_db()
    users = db["users"]
    with tab1:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if user in users and users[user]["password"] == hash_password(pw):
                st.session_state.username = user
                st.session_state.money = min(users[user]["money"], MAX_SAFE_MONEY)
                st.rerun()
            else:
                st.error("Invalid login")
    with tab2:
        newu = st.text_input("New Username")
        newp = st.text_input("New Password", type="password")
        if st.button("Register"):
            if newu in users:
                st.error("User exists")
            elif not newu.strip():
                st.error("Username cannot be empty")
            elif not newp.strip():
                st.error("Password cannot be empty")
            else:
                users[newu] = ensure_user_fields({
                    "password": hash_password(newp),
                    "money": 500,
                    "last_daily": "",
                    "timeout": 0
                })
                db["users"] = users
                save_db(db)
                st.success("Account created! Please log in.")
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.title("🎰 Casino")

user = st.session_state.username
db = load_db()
users = db["users"]
for u in users:
    users[u] = ensure_user_fields(users[u])

now = time.time()
if users[user]["timeout"] > now:
    remaining = int(users[user]["timeout"] - now)
    st.error(f"⏳ You are timed out for {remaining // 60}m {remaining % 60}s")
    st.stop()

if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

money = st.session_state.money
tier = get_vip_tier(money)

st.sidebar.write("User:", user)
st.sidebar.markdown(f"**VIP:** <span style='color:{tier['color']}'>{tier['emoji']} {tier['name']}</span>", unsafe_allow_html=True)
st.sidebar.write("Role: 👑 Developer" if user in DEV_ACCOUNTS else "Role: 🎮 Player")
st.sidebar.write("Money: $", money)

if st.sidebar.button("Logout"):
    st.session_state.username = None
    st.rerun()

# ---------------- DEV PANEL ----------------
if user in DEV_ACCOUNTS:
    st.sidebar.markdown("---")
    st.sidebar.header("👑 Dev Panel")
    target = st.sidebar.selectbox("Select User", list(users.keys()))
    give = st.sidebar.number_input("Give Money", 0, 1000000)
    if st.sidebar.button("Give Money"):
        users[target]["money"] += give
        db["users"] = users
        save_db(db)
        st.sidebar.success("Money given")
    if st.sidebar.button("Reset All Money"):
        for u in users:
            users[u]["money"] = 500
        db["users"] = users
        save_db(db)
        st.sidebar.success("All balances reset")
    new_odds = st.sidebar.slider("Slot Jackpot Multiplier", 2, 20, st.session_state.jackpot_odds)
    st.session_state.jackpot_odds = new_odds
    st.sidebar.subheader("⏳ Timeout Player")
    timeout_user = st.sidebar.selectbox("Player to timeout", list(users.keys()), key="timeout_select")
    timeout_minutes = st.sidebar.number_input("Timeout minutes", 1, 10000, 5)
    if st.sidebar.button("Timeout Player"):
        users[timeout_user]["timeout"] = time.time() + timeout_minutes * 60
        db["users"] = users
        save_db(db)
        st.sidebar.success(f"{timeout_user} timed out for {timeout_minutes} minutes")
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔓 Remove Timeout")
    untimeout_user = st.sidebar.selectbox("Player to remove timeout", list(users.keys()), key="remove_timeout_select")
    if st.sidebar.button("Remove Timeout"):
        users[untimeout_user]["timeout"] = 0
        db["users"] = users
        save_db(db)
        st.sidebar.success(f"{untimeout_user} timeout removed")

# ---------------- DAILY ----------------
today = str(datetime.date.today())
if users[user]["last_daily"] != today:
    if st.sidebar.button("Claim $100 Daily"):
        st.session_state.money += 100
        users[user]["last_daily"] = today
        db["users"] = users
        save_db(db)
        save_progress()
        st.rerun()

# ---------------- LEADERBOARD ----------------
st.sidebar.markdown("---")
st.sidebar.header("🏆 Leaderboard")
top = sorted(
    [(u, v) for u, v in users.items() if u not in DEV_ACCOUNTS],
    key=lambda x: x[1]["money"],
    reverse=True
)
for u in top[:10]:
    t = get_vip_tier(u[1]["money"])
    st.sidebar.write(f"{t['emoji']} {u[0]} — ${u[1]['money']:,}")

# ---------------- MAIN PAGE ----------------
db = load_db()
st.title("🎰 Ultimate Casino")
st.header(f"💰 Progressive Jackpot: ${db['jackpot']:,}")

# VIP status banner
st.markdown(f"""
<div style="background: linear-gradient(135deg, {tier['color']}33, {tier['color']}11);
border: 2px solid {tier['color']}; border-radius: 12px; padding: 15px; margin-bottom: 20px;">
<b style="color:{tier['color']}">{tier['emoji']} {tier['name']} VIP</b> &nbsp;|&nbsp; Balance: <b>${money:,}</b>
</div>
""", unsafe_allow_html=True)

st.markdown("### Pick a game from the sidebar to play!")
st.markdown("""
| Game | Description |
|------|-------------|
| 🎰 Slots | Spin to match symbols and win the jackpot |
| 🃏 Blackjack | Beat the dealer without going over 21 |
| 🎡 Roulette | Pick red, black, or a number and spin |
| ♠️ Poker | Texas Hold'em vs the dealer |
| 📊 Stats | View your stats, VIP tier and achievements |
""")

if money <= 0:
    if users[user]["last_daily"] == today:
        if st.button("Play Again ($250)"):
            st.session_state.money = 250
            save_progress()
            st.rerun()
    else:
        st.warning("Claim your daily reward in the sidebar!")
