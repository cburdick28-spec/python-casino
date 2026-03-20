import streamlit as st
import random
import time
from db import load_db, save_progress, record_game, DEV_ACCOUNTS

st.set_page_config(page_title="🏇 Horse Racing", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
db = load_db()
if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

money = st.session_state.money

st.title("🏇 Horse Racing")
st.caption("Pick your horse and watch the race!")
st.write(f"**Balance:** ${money:,}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

# ---------------- HORSES ----------------
HORSES = [
    {"name": "Thunder Bolt",  "emoji": "🐎", "odds": 2.0,  "speed_range": (8, 14)},
    {"name": "Lucky Star",    "emoji": "🦄", "odds": 3.5,  "speed_range": (6, 15)},
    {"name": "Dark Shadow",   "emoji": "🐴", "odds": 5.0,  "speed_range": (5, 16)},
    {"name": "Golden Arrow",  "emoji": "🏅", "odds": 4.0,  "speed_range": (6, 14)},
    {"name": "Silver Wind",   "emoji": "💨", "odds": 2.5,  "speed_range": (7, 13)},
    {"name": "Iron Hooves",   "emoji": "⚡", "odds": 6.0,  "speed_range": (4, 17)},
]

TRACK_LENGTH = 30

# Session state
for k, v in [("race_result", None), ("race_running", False),
             ("race_bet", 0), ("race_horse", 0), ("race_positions", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

bet = st.number_input("Bet", min_value=1, max_value=money, value=min(10, money), step=1)

# Show last result
if st.session_state.race_result:
    outcome, msg, amount = st.session_state.race_result
    if outcome == "win":
        st.success(f"🏆 {msg} +${amount:,}")
    else:
        st.error(f"❌ {msg} -${amount:,}")
    st.session_state.race_result = None

# Horse selection
st.subheader("🐎 Pick Your Horse")
cols = st.columns(3)
selected_horse = st.session_state.race_horse

for i, horse in enumerate(HORSES):
    with cols[i % 3]:
        is_selected = (i == selected_horse)
        border = "3px solid #FFD700" if is_selected else "1px solid #333"
        bg = "#2a2a1a" if is_selected else "#1a1a2e"
        st.markdown(f"""
        <div style="background:{bg};border:{border};border-radius:10px;
        padding:12px;text-align:center;margin-bottom:8px;">
        <div style="font-size:32px">{horse['emoji']}</div>
        <div style="font-weight:bold;color:white">{horse['name']}</div>
        <div style="color:#FFD700;font-size:13px">Odds: {horse['odds']}x</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Select", key=f"horse_{i}"):
            st.session_state.race_horse = i
            st.rerun()

selected = HORSES[st.session_state.race_horse]
st.info(f"🐎 You selected **{selected['name']}** at **{selected['odds']}x** odds")

# Race button
if st.button("🏁 Start Race!", type="primary"):
    st.session_state.race_bet = bet
    st.session_state.race_running = True

    # Simulate full race positions for each step
    positions = [0] * len(HORSES)
    race_steps = []

    step = 0
    finished = [False] * len(HORSES)
    finish_order = []

    while len(finish_order) < len(HORSES):
        for i, horse in enumerate(HORSES):
            if not finished[i]:
                move = random.randint(*horse["speed_range"]) / 10
                positions[i] = min(positions[i] + move, TRACK_LENGTH)
                if positions[i] >= TRACK_LENGTH and not finished[i]:
                    finished[i] = True
                    finish_order.append(i)
        race_steps.append(list(positions))
        step += 1

    st.session_state.race_positions = race_steps

    # Animate the race
    st.subheader("🏁 Race in Progress!")
    track_placeholder = st.empty()

    for step_positions in race_steps[::2]:  # every 2 steps for speed
        track_html = "<div style='font-family:monospace;background:#1a3a1a;padding:16px;border-radius:10px;'>"
        track_html += "<div style='color:#FFD700;font-weight:bold;margin-bottom:8px'>🏁 RACE TRACK 🏁</div>"
        for i, horse in enumerate(HORSES):
            pos = step_positions[i]
            pct = min(int((pos / TRACK_LENGTH) * 100), 100)
            is_player = (i == st.session_state.race_horse)
            bar_color = "#FFD700" if is_player else "#4a9a4a"
            name_color = "#FFD700" if is_player else "#ffffff"
            track_html += f"""
            <div style='margin:6px 0;'>
              <span style='color:{name_color};font-size:12px;display:inline-block;width:130px'>
                {horse['emoji']} {horse['name'][:10]}
              </span>
              <span style='display:inline-block;width:{pct}%;max-width:60%;
                background:{bar_color};height:18px;border-radius:4px;
                vertical-align:middle;'></span>
              <span style='color:#aaa;font-size:11px;margin-left:4px'>{pct}%</span>
            </div>"""
        track_html += "</div>"
        track_placeholder.markdown(track_html, unsafe_allow_html=True)
        time.sleep(0.08)

    # Final positions (all at finish)
    final_html = "<div style='font-family:monospace;background:#1a3a1a;padding:16px;border-radius:10px;'>"
    final_html += "<div style='color:#FFD700;font-weight:bold;margin-bottom:8px'>🏁 FINISH! 🏁</div>"
    for place, hi in enumerate(finish_order):
        horse = HORSES[hi]
        is_player = (hi == st.session_state.race_horse)
        name_color = "#FFD700" if is_player else "#ffffff"
        medal = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣"][place]
        final_html += f"""
        <div style='margin:6px 0;color:{name_color};font-size:14px;'>
          {medal} {horse['emoji']} {horse['name']}{"  ← YOU" if is_player else ""}
        </div>"""
    final_html += "</div>"
    track_placeholder.markdown(final_html, unsafe_allow_html=True)

    # Calculate result
    winner_idx = finish_order[0]
    locked_bet = st.session_state.race_bet
    locked_horse = st.session_state.race_horse

    if winner_idx == locked_horse:
        payout = int(locked_bet * HORSES[locked_horse]["odds"])
        net = payout - locked_bet
        st.session_state.money += net
        st.session_state.race_result = ("win", f"{HORSES[locked_horse]['name']} wins the race!", net)
        record_game(user, True, locked_bet, payout)
    else:
        st.session_state.money -= locked_bet
        winner_name = HORSES[winner_idx]["name"]
        st.session_state.race_result = ("lose", f"{winner_name} won — your horse lost.", locked_bet)
        record_game(user, False, locked_bet, 0)

    save_progress()
    st.write(f"**New Balance:** ${st.session_state.money:,}")

# Odds table
st.markdown("---")
st.subheader("📋 Odds & Horses")
cols = st.columns(3)
for i, horse in enumerate(HORSES):
    with cols[i % 3]:
        st.markdown(f"""
        <div style="background:#1a1a2e;border:1px solid #333;border-radius:8px;
        padding:10px;text-align:center;margin-bottom:8px;">
        <div style="font-size:24px">{horse['emoji']}</div>
        <div style="color:white;font-weight:bold;font-size:13px">{horse['name']}</div>
        <div style="color:#FFD700;font-size:12px">Pays {horse['odds']}x</div>
        </div>
        """, unsafe_allow_html=True)
