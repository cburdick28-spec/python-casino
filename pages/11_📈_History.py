import streamlit as st
from db import load_db, save_db, ensure_user_fields, DEV_ACCOUNTS

st.set_page_config(page_title="📈 History", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
db = load_db()

if user not in db["users"]:
    st.error("User not found.")
    st.stop()

user_data = ensure_user_fields(db["users"][user])
history = user_data.get("bet_history", [])

st.title("📈 Betting History")
st.caption("Your last 50 bets across all games.")
st.write(f"**Balance:** ${st.session_state.money:,}")

if not history:
    st.info("No betting history yet — go play some games!")
    st.stop()

# Summary stats from history
total_bets = len(history)
wins = sum(1 for h in history if h["outcome"] == "win")
losses = sum(1 for h in history if h["outcome"] == "loss")
pushes = sum(1 for h in history if h["outcome"] == "push")
total_wagered = sum(h["bet"] for h in history)
total_net = sum(h["net"] for h in history)

st.markdown("---")
st.subheader("📊 Summary")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("🎮 Total Bets", total_bets)
with col2:
    st.metric("✅ Wins", wins)
with col3:
    st.metric("❌ Losses", losses)
with col4:
    st.metric("💵 Wagered", f"${total_wagered:,}")
with col5:
    color = "normal" if total_net >= 0 else "inverse"
    st.metric("📈 Net", f"${total_net:,}", delta=f"${total_net:,}")

st.markdown("---")
st.subheader("🎲 Recent Bets")

# Filter options
game_filter = st.selectbox("Filter by game", ["All"] + sorted(set(h["game"] for h in history)))
outcome_filter = st.selectbox("Filter by outcome", ["All", "win", "loss", "push"])

filtered = list(reversed(history))  # newest first
if game_filter != "All":
    filtered = [h for h in filtered if h["game"] == game_filter]
if outcome_filter != "All":
    filtered = [h for h in filtered if h["outcome"] == outcome_filter]

if not filtered:
    st.info("No bets match your filters.")
else:
    for h in filtered:
        outcome = h["outcome"]
        net = h["net"]
        bet = h["bet"]
        game = h["game"]
        time_str = h.get("time", "")

        if outcome == "win":
            icon = "✅"
            color = "#1a4a1a"
            border = "#2ecc40"
            net_str = f"+${net:,}"
        elif outcome == "loss":
            icon = "❌"
            color = "#4a1a1a"
            border = "#cc2020"
            net_str = f"-${abs(net):,}"
        else:
            icon = "➡️"
            color = "#1a1a4a"
            border = "#4444cc"
            net_str = "Push"

        st.markdown(f"""
        <div style="background:{color};border-left:4px solid {border};
        border-radius:8px;padding:10px 16px;margin-bottom:8px;
        display:flex;justify-content:space-between;align-items:center;">
          <div>
            <span style="font-size:18px">{icon}</span>
            <span style="color:white;font-weight:bold;margin-left:8px">{game}</span>
            <span style="color:#aaa;font-size:12px;margin-left:12px">{time_str}</span>
          </div>
          <div style="text-align:right;">
            <div style="color:#aaa;font-size:12px">Bet: ${bet:,}</div>
            <div style="color:white;font-weight:bold;font-size:16px">{net_str}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# Clear history button
st.markdown("---")
if st.button("🗑️ Clear My History"):
    db = load_db()
    if user in db["users"]:
        db["users"][user]["bet_history"] = []
        save_db(db)
        st.success("History cleared!")
        st.rerun()
