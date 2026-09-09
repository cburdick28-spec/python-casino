import random
import streamlit as st
from db import load_db, save_progress, record_game, DEV_ACCOUNTS, MAX_SAFE_MONEY

st.set_page_config(page_title="🔼 Higher Lower", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
_ = load_db()

if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

for k, v in [("hl_card", None), ("hl_bet", 0), ("hl_result", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

money = st.session_state.money
st.title("🔼 Higher Lower")
st.caption("Guess if the next card will be higher or lower.")
st.write(f"**Balance:** ${money:,}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

if st.session_state.hl_card is None:
    st.session_state.hl_card = random.randint(1, 13)

if "hl_bet_input" not in st.session_state:
    st.session_state.hl_bet_input = min(10, money)
else:
    st.session_state.hl_bet_input = min(st.session_state.hl_bet_input, min(money, MAX_SAFE_MONEY))

bet = st.number_input(
    "Bet",
    min_value=1,
    max_value=min(money, MAX_SAFE_MONEY),
    value=st.session_state.hl_bet_input,
    step=1,
    key="hl_bet_input",
)

st.subheader(f"Current card: {st.session_state.hl_card}")

c1, c2 = st.columns(2)
guess = None
with c1:
    if st.button("Higher"):
        guess = "higher"
with c2:
    if st.button("Lower"):
        guess = "lower"

if guess:
    next_card = random.randint(1, 13)
    current_card = st.session_state.hl_card
    st.subheader(f"Next card: {next_card}")

    if next_card == current_card:
        st.info("Push — cards matched, bet returned.")
    else:
        win = (guess == "higher" and next_card > current_card) or (guess == "lower" and next_card < current_card)
        if win:
            st.session_state.money += int(bet)
            st.success(f"Correct! +${int(bet):,}")
            record_game(user, True, int(bet), int(bet), "🔼 Higher Lower")
        else:
            st.session_state.money -= int(bet)
            st.error(f"Wrong guess. -${int(bet):,}")
            record_game(user, False, int(bet), 0, "🔼 Higher Lower")

    st.session_state.hl_card = next_card
    save_progress()
    st.write(f"**New Balance:** ${st.session_state.money:,}")
