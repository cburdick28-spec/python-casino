import streamlit as st
from db import load_db, ensure_user_fields, get_vip_tier, get_next_tier, ACHIEVEMENTS, VIP_TIERS, DEV_ACCOUNTS

st.set_page_config(page_title="📊 Stats", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
db = load_db()
users = db["users"]

if user not in users:
    st.error("User not found.")
    st.stop()

user_data = ensure_user_fields(users[user])
money = st.session_state.money
stats = user_data["stats"]
achievements = user_data.get("achievements", [])
tier = get_vip_tier(money)
next_tier = get_next_tier(money)

# ---------------- VIP BANNER ----------------
st.markdown(f"""
<div style="background: linear-gradient(135deg, {tier['color']}33, {tier['color']}11);
border: 2px solid {tier['color']}; border-radius: 12px; padding: 20px; margin-bottom: 20px; text-align:center;">
<h1 style="color:{tier['color']}; margin:0">{tier['emoji']} {tier['name']} VIP</h1>
<h3 style="margin:5px 0">💰 ${money:,}</h3>
</div>
""", unsafe_allow_html=True)

if next_tier:
    progress = min((money - tier["min"]) / (next_tier["min"] - tier["min"]), 1.0)
    st.markdown(f"**Progress to {next_tier['emoji']} {next_tier['name']}:** ${money:,} / ${next_tier['min']:,}")
    st.progress(progress)
else:
    st.success("💠 You have reached the highest VIP tier — Diamond!")

st.markdown("---")

# ---------------- STATS ----------------
st.header("📊 Your Stats")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎮 Games Played", stats["games_played"])
with col2:
    win_rate = round(stats["games_won"] / stats["games_played"] * 100, 1) if stats["games_played"] > 0 else 0
    st.metric("✅ Win Rate", f"{win_rate}%")
with col3:
    st.metric("💵 Total Wagered", f"${stats['total_wagered']:,}")
with col4:
    st.metric("🏆 Biggest Win", f"${stats['biggest_win']:,}")

col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric("✅ Games Won", stats["games_won"])
with col6:
    st.metric("❌ Games Lost", stats["games_lost"])
with col7:
    st.metric("💰 Total Won", f"${stats['total_won']:,}")
with col8:
    net = stats["total_won"] - stats["total_wagered"]
    st.metric("📈 Net Profit", f"${net:,}", delta=f"${net:,}")

st.markdown("---")

# ---------------- VIP TIERS ----------------
st.header("💎 VIP Tiers")

cols = st.columns(len(VIP_TIERS))
for i, t in enumerate(VIP_TIERS):
    with cols[i]:
        unlocked = money >= t["min"]
        bg = f"{t['color']}22" if unlocked else "#33333322"
        border = t["color"] if unlocked else "#555"
        st.markdown(f"""
        <div style="background:{bg};border:2px solid {border};border-radius:10px;
        padding:15px;text-align:center;">
        <div style="font-size:30px">{t['emoji']}</div>
        <div style="color:{border};font-weight:bold">{t['name']}</div>
        <div style="font-size:12px;color:#aaa">${t['min']:,}+</div>
        <div style="font-size:20px">{"✅" if unlocked else "🔒"}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ---------------- ACHIEVEMENTS ----------------
st.header("🏆 Achievements")

cols = st.columns(4)
for i, ach in enumerate(ACHIEVEMENTS):
    with cols[i % 4]:
        unlocked = ach["id"] in achievements
        bg = "#2a2a2a" if unlocked else "#1a1a1a"
        opacity = "1" if unlocked else "0.4"
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {'#ffd700' if unlocked else '#444'};
        border-radius:10px;padding:12px;text-align:center;opacity:{opacity};margin-bottom:10px;">
        <div style="font-size:28px">{ach['emoji']}</div>
        <div style="font-weight:bold;font-size:13px">{ach['name']}</div>
        <div style="font-size:11px;color:#aaa">{ach['desc']}</div>
        <div style="font-size:18px;margin-top:5px">{"✅" if unlocked else "🔒"}</div>
        </div>
        """, unsafe_allow_html=True)
