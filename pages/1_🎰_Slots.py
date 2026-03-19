import streamlit as st
import random
import time
from db import load_db, save_db, save_progress, DEV_ACCOUNTS

st.set_page_config(page_title="🎰 Slots", layout="wide")

# Guard: must be logged in
if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
db = load_db()
users = db["users"]

if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

money = st.session_state.money

st.title("🎰 Slots")
st.header(f"💰 Progressive Jackpot: ${db['jackpot']}")
st.write(f"**Balance:** ${money}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

bet = st.number_input("Bet", 1, money, min(10, money))

symbols = ["🍒", "🍋", "🍉", "⭐", "💎", "7️⃣"]
display = st.empty()

if st.button("Spin"):
    for i in range(15):
        r = [random.choice(symbols) for _ in range(3)]
        display.write(" | ".join(r))
        time.sleep(0.05)

    r = [random.choice(symbols) for _ in range(3)]
    display.write(" | ".join(r))

    db = load_db()
    jackpot = db["jackpot"]

    if r[0] == r[1] == r[2]:
        win = bet * st.session_state.jackpot_odds
        st.success(f"🎰 JACKPOT! +${win}")
        st.success(f"💰 Progressive Jackpot Won: ${jackpot}")
        st.session_state.money += win + jackpot
        db["jackpot"] = 1000

    elif r[0] == r[1] or r[1] == r[2]:
        win = bet * 2
        st.success(f"Winner! +${win}")
        st.session_state.money += win

    else:
        st.error(f"No match. -{bet}")
        st.session_state.money -= bet
        db["jackpot"] += int(bet * 0.25)

    save_db(db)
    save_progress()
    st.write(f"**New Balance:** ${st.session_state.money}")
