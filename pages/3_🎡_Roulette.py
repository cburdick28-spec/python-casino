import streamlit as st
import random
from db import load_db, save_db, save_progress, DEV_ACCOUNTS

st.set_page_config(page_title="🎡 Roulette", layout="wide")

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

st.title("🎡 Roulette")
st.write(f"**Balance:** ${money}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

bet = st.number_input("Bet", 1, money, min(10, money))

choice = st.selectbox("Bet on", ["Red", "Black", "Number"])
num = None
if choice == "Number":
    num = int(st.number_input("Pick 0-36", 0, 36))

if st.button("Spin"):
    spin = random.randint(0, 36)

    red_numbers = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

    if spin == 0:
        color = "Green"
    elif spin in red_numbers:
        color = "Red"
    else:
        color = "Black"

    st.write(f"🎡 Ball landed on: **{spin} {color}**")

    if choice == "Number" and spin == num:
        win = bet * 35
        st.success(f"🎉 Big Win! +${win}")
        st.session_state.money += win

    elif choice == color:
        st.success(f"Winner! +${bet}")
        st.session_state.money += bet

    else:
        st.error(f"No win. -{bet}")
        st.session_state.money -= bet

    save_progress()
    st.write(f"**New Balance:** ${st.session_state.money}")
