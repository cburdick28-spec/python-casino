import random
import streamlit as st
from db import load_db, save_progress, record_game, DEV_ACCOUNTS, MAX_SAFE_MONEY

st.set_page_config(page_title="🪙 Coin Flip", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
_ = load_db()

if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

money = st.session_state.money
st.title("🪙 Coin Flip")
st.caption("Call heads or tails and try your luck.")
st.write(f"**Balance:** ${money:,}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

if "coin_bet_input" not in st.session_state:
    st.session_state.coin_bet_input = min(10, money)
else:
    st.session_state.coin_bet_input = min(st.session_state.coin_bet_input, min(money, MAX_SAFE_MONEY))

bet = st.number_input(
    "Bet",
    min_value=1,
    max_value=min(money, MAX_SAFE_MONEY),
    value=st.session_state.coin_bet_input,
    step=1,
    key="coin_bet_input",
)

choice = st.radio("Pick a side", ["Heads", "Tails"], horizontal=True)

if st.button("Flip"):
    result = random.choice(["Heads", "Tails"])
    st.subheader(f"Result: {result}")

    if result == choice:
        st.session_state.money += int(bet)
        st.success(f"You won +${int(bet):,}!")
        record_game(user, True, int(bet), int(bet), "🪙 Coin Flip")
    else:
        st.session_state.money -= int(bet)
        st.error(f"You lost -${int(bet):,}.")
        record_game(user, False, int(bet), 0, "🪙 Coin Flip")

    save_progress()
    st.write(f"**New Balance:** ${st.session_state.money:,}")
