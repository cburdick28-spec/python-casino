import streamlit as st
import random
import time
from db import load_db, save_progress, record_game, DEV_ACCOUNTS, MAX_SAFE_MONEY

st.set_page_config(page_title="🎲 Craps", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
db = load_db()
if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

money = st.session_state.money
st.title("🎲 Craps")
st.caption("Roll the dice! Classic casino craps rules.")
st.write(f"**Balance:** ${money:,}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

with st.expander("📋 How to Play"):
    st.markdown("""
**Come Out Roll (first roll):**
- Roll **7 or 11** → Instant Win! 🎉
- Roll **2, 3, or 12** → Craps — Instant Loss 💀
- Roll **anything else** → Sets your **Point** number

**Point Phase:**
- Roll your **Point** again → Win! 🎉
- Roll a **7** → Seven Out — Loss 💀
""")

for k, v in [("craps_phase","come_out"),("craps_point",None),
             ("craps_rolls",[]),("craps_result",None),("craps_bet",0)]:
    if k not in st.session_state:
        st.session_state[k] = v

bet = st.number_input("Bet", min_value=1, max_value=min(money, MAX_SAFE_MONEY), value=min(10,money), step=1)

if st.session_state.craps_result:
    outcome, msg, amount = st.session_state.craps_result
    if outcome=="win": st.success(f"🎉 {msg} +${amount:,}")
    else: st.error(f"💀 {msg} -${amount:,}")
    st.session_state.craps_result = None

phase = st.session_state.craps_phase
point = st.session_state.craps_point

if phase == "come_out":
    st.info("🎲 Come Out Roll — Roll the dice to set your point!")
    if st.session_state.craps_bet == 0:
        st.session_state.craps_bet = bet
else:
    st.warning(f"🎯 Point is **{point}** — Roll {point} to win, avoid 7!")

def dice_face(n):
    dots = {1:[(50,50)],2:[(25,25),(75,75)],3:[(25,25),(50,50),(75,75)],
            4:[(25,25),(75,25),(25,75),(75,75)],5:[(25,25),(75,25),(50,50),(25,75),(75,75)],
            6:[(25,20),(75,20),(25,50),(75,50),(25,80),(75,80)]}
    circles = "".join(f'<circle cx="{x}" cy="{y}" r="8" fill="#1a1a2e"/>' for x,y in dots.get(n,[]))
    return f'<svg width="80" height="80" viewBox="0 0 100 100"><rect width="100" height="100" rx="15" fill="white" stroke="#FFD700" stroke-width="4"/>{circles}</svg>'

roll_clicked = st.button("🎲 Roll Dice!")

if roll_clicked:
    if phase == "come_out":
        st.session_state.craps_bet = bet
    d1 = random.randint(1,6)
    d2 = random.randint(1,6)
    total = d1 + d2
    st.session_state.craps_rolls.append((d1,d2,total))
    locked_bet = st.session_state.craps_bet

    anim_placeholder = st.empty()
    for _ in range(10):
        a1,a2 = random.randint(1,6),random.randint(1,6)
        anim_placeholder.markdown(
            f'<div style="display:flex;gap:12px;justify-content:center;margin:10px 0">{dice_face(a1)}{dice_face(a2)}</div>',
            unsafe_allow_html=True)
        time.sleep(0.07)
    anim_placeholder.markdown(
        f'<div style="display:flex;gap:12px;justify-content:center;margin:10px 0">{dice_face(d1)}{dice_face(d2)}</div>',
        unsafe_allow_html=True)

    st.markdown(f"### 🎲 Rolled: **{d1} + {d2} = {total}**")

    if phase == "come_out":
        if total in (7,11):
            st.session_state.money += locked_bet
            st.session_state.craps_result = ("win", f"Natural {total}! You win!", locked_bet)
            record_game(user, True, locked_bet, locked_bet, "🎲 Craps")
            st.session_state.craps_phase = "come_out"
            st.session_state.craps_point = None
            st.session_state.craps_bet = 0
        elif total in (2,3,12):
            st.session_state.money -= locked_bet
            st.session_state.craps_result = ("lose", f"Craps! {total} — You lose.", locked_bet)
            record_game(user, False, locked_bet, 0, "🎲 Craps")
            st.session_state.craps_phase = "come_out"
            st.session_state.craps_point = None
            st.session_state.craps_bet = 0
        else:
            st.session_state.craps_point = total
            st.session_state.craps_phase = "point"
            st.info(f"🎯 Point set to **{total}**! Keep rolling!")
    elif phase == "point":
        if total == point:
            st.session_state.money += locked_bet
            st.session_state.craps_result = ("win", f"Hit your point {point}! You win!", locked_bet)
            record_game(user, True, locked_bet, locked_bet, "🎲 Craps")
            st.session_state.craps_phase = "come_out"
            st.session_state.craps_point = None
            st.session_state.craps_rolls = []
            st.session_state.craps_bet = 0
        elif total == 7:
            st.session_state.money -= locked_bet
            st.session_state.craps_result = ("lose", "Seven Out! You lose.", locked_bet)
            record_game(user, False, locked_bet, 0, "🎲 Craps")
            st.session_state.craps_phase = "come_out"
            st.session_state.craps_point = None
            st.session_state.craps_rolls = []
            st.session_state.craps_bet = 0
        else:
            st.info(f"Rolled {total} — keep rolling for {point}!")

    save_progress()
    st.write(f"**New Balance:** ${st.session_state.money:,}")

if st.session_state.craps_rolls and phase == "point":
    st.markdown("---")
    st.subheader("🎲 Roll History")
    history = ""
    for i,(d1,d2,t) in enumerate(st.session_state.craps_rolls):
        history += f"Roll {i+1}: {d1}+{d2}=**{t}** {'✅' if t==point else '⚠️' if t==7 else ''} | "
    st.markdown(history.rstrip(" | "))
