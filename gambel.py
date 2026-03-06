import streamlit as st
import random
import json
import os

# -----------------------------
# DATABASE
# -----------------------------

DB_FILE = "casino_users.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

def save_balance():
    users = load_users()
    users[st.session_state.username] = st.session_state.money
    save_users(users)

# -----------------------------
# LOGIN SYSTEM
# -----------------------------

users = load_users()

if "username" not in st.session_state:
    st.session_state.username = None

if "money" not in st.session_state:
    st.session_state.money = 500

if st.session_state.username is None:

    st.title("🎰 Python Casino")

    name = st.text_input("Enter Username")

    if st.button("Login"):

        if name == "":
            st.warning("Enter a username")

        else:

            users = load_users()

            if name not in users:
                users[name] = 500
                save_users(users)

            st.session_state.username = name
            st.session_state.money = users[name]

            st.rerun()

    st.stop()

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("🎰 Casino")

st.sidebar.write(f"👤 Player: **{st.session_state.username}**")
st.sidebar.write(f"💰 Balance: **${st.session_state.money}**")

# Leaderboard

st.sidebar.markdown("---")
st.sidebar.header("🏆 Leaderboard")

users = load_users()

sorted_players = sorted(
    users.items(),
    key=lambda x: x[1],
    reverse=True
)

for name, balance in sorted_players[:10]:
    st.sidebar.write(f"{name} — ${balance}")

# Logout

if st.sidebar.button("Logout"):
    st.session_state.username = None
    st.rerun()

# -----------------------------
# GAME MENU
# -----------------------------

st.title("🎰 Python Casino")

game = st.selectbox(
    "Choose a game",
    ["Slots", "Dice"]
)

bet = st.number_input(
    "Bet Amount",
    min_value=1,
    max_value=st.session_state.money,
    value=10
)

# -----------------------------
# SLOT MACHINE
# -----------------------------

if game == "Slots":

    st.header("🎰 Slot Machine")

    symbols = ["🍒", "🍋", "🍉", "⭐", "💎"]

    if st.button("Spin"):

        if bet > st.session_state.money:
            st.error("Not enough money")

        else:

            result = [
                random.choice(symbols),
                random.choice(symbols),
                random.choice(symbols)
            ]

            st.write(" | ".join(result))

            if result[0] == result[1] == result[2]:

                win = bet * 5
                st.success(f"JACKPOT! You win ${win}")

                st.session_state.money += win

            elif result[0] == result[1] or result[1] == result[2]:

                win = bet * 2
                st.success(f"You win ${win}")

                st.session_state.money += win

            else:

                st.error("You lost")

                st.session_state.money -= bet

            save_balance()

# -----------------------------
# DICE GAME
# -----------------------------

if game == "Dice":

    st.header("🎲 Dice")

    if st.button("Roll Dice"):

        if bet > st.session_state.money:
            st.error("Not enough money")

        else:

            player = random.randint(1, 6)
            house = random.randint(1, 6)

            st.write(f"You rolled: **{player}**")
            st.write(f"House rolled: **{house}**")

            if player > house:

                win = bet
                st.success(f"You win ${win}")

                st.session_state.money += win

            elif player < house:

                st.error("House wins")

                st.session_state.money -= bet

            else:

                st.info("Draw")

            save_balance()

# -----------------------------
# OUT OF MONEY
# -----------------------------

if st.session_state.money <= 0:

    st.error("💀 You are out of money!")

    if st.button("Reset to $500"):

        st.session_state.money = 500
        save_balance()
