import streamlit as st
import random
import json
import os
import hashlib

DB_FILE = "casino_users.json"

# -----------------------
# DATABASE SETUP
# -----------------------

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------
# SESSION STATE
# -----------------------

if "username" not in st.session_state:
    st.session_state.username = None

if "money" not in st.session_state:
    st.session_state.money = 500

# -----------------------
# LOGIN / REGISTER
# -----------------------

if st.session_state.username is None:

    st.title("🎰 Python Casino")

    tab1, tab2 = st.tabs(["Login","Register"])

    users = load_users()

    # LOGIN
    with tab1:

        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if username in users:

                if users[username]["password"] == hash_password(password):

                    st.session_state.username = username
                    st.session_state.money = users[username]["money"]

                    st.success("Logged in!")
                    st.rerun()

                else:
                    st.error("Wrong password")

            else:
                st.error("User does not exist")

    # REGISTER
    with tab2:

        st.subheader("Create Account")

        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Register"):

            if new_user == "" or new_pass == "":
                st.error("Fill all fields")

            elif new_user in users:
                st.error("Username already exists")

            else:

                users[new_user] = {
                    "password": hash_password(new_pass),
                    "money": 500
                }

                save_users(users)

                st.success("Account created!")

    st.stop()

# -----------------------
# SAVE BALANCE
# -----------------------

def save_balance():

    users = load_users()

    users[st.session_state.username]["money"] = st.session_state.money

    save_users(users)

# -----------------------
# SIDEBAR
# -----------------------

st.sidebar.title("🎰 Casino")

st.sidebar.write("Player:", st.session_state.username)
st.sidebar.write("Balance: $", st.session_state.money)

if st.sidebar.button("Logout"):
    st.session_state.username = None
    st.rerun()

# -----------------------
# LEADERBOARD
# -----------------------

st.sidebar.markdown("---")
st.sidebar.header("🏆 Leaderboard")

users = load_users()

top = sorted(users.items(), key=lambda x: x[1]["money"], reverse=True)

for u in top[:10]:
    st.sidebar.write(u[0], "-", "$"+str(u[1]["money"]))

# -----------------------
# MAIN
# -----------------------

st.title("🎰 Python Casino")

game = st.selectbox(
    "Choose Game",
    ["Slots","Dice","Blackjack","Roulette"]
)

bet = st.number_input(
    "Bet Amount",
    min_value=1,
    max_value=max(1, st.session_state.money),
    value=10
)

# -----------------------
# SLOTS
# -----------------------

if game == "Slots":

    st.header("🎰 Slots")

    symbols = ["🍒","🍋","🍉","⭐","💎"]

    if st.button("Spin"):

        r = [random.choice(symbols) for _ in range(3)]

        st.write(" | ".join(r))

        if r[0]==r[1]==r[2]:

            win = bet*5
            st.success("JACKPOT +$"+str(win))
            st.session_state.money += win

        elif r[0]==r[1] or r[1]==r[2]:

            win = bet*2
            st.success("Win +$"+str(win))
            st.session_state.money += win

        else:

            st.error("Lost -$"+str(bet))
            st.session_state.money -= bet

        save_balance()

# -----------------------
# DICE
# -----------------------

if game == "Dice":

    st.header("🎲 Dice")

    if st.button("Roll"):

        player = random.randint(1,6)
        house = random.randint(1,6)

        st.write("You:",player)
        st.write("House:",house)

        if player > house:

            st.success("Win +$"+str(bet))
            st.session_state.money += bet

        elif player < house:

            st.error("Lose -$"+str(bet))
            st.session_state.money -= bet

        else:

            st.info("Draw")

        save_balance()

# -----------------------
# BLACKJACK
# -----------------------

if game == "Blackjack":

    st.header("🃏 Blackjack")

    def draw():
        return random.randint(1,11)

    if st.button("Deal"):

        player = draw()+draw()
        dealer = draw()+draw()

        st.write("Your hand:",player)
        st.write("Dealer:",dealer)

        if player>21:
            st.error("Bust -$"+str(bet))
            st.session_state.money -= bet

        elif dealer>21 or player>dealer:
            st.success("Win +$"+str(bet))
            st.session_state.money += bet

        elif player<dealer:
            st.error("Lose -$"+str(bet))
            st.session_state.money -= bet

        else:
            st.info("Push")

        save_balance()

# -----------------------
# ROULETTE
# -----------------------

if game == "Roulette":

    st.header("🎡 Roulette")

    choice = st.selectbox(
        "Bet on",
        ["Red","Black","Number"]
    )

    number = None

    if choice == "Number":
        number = st.number_input("Pick number 0-36",0,36)

    if st.button("Spin Wheel"):

        spin = random.randint(0,36)

        if spin == 0:
            color = "Green"
        elif spin % 2 == 0:
            color = "Red"
        else:
            color = "Black"

        st.write("Number:",spin)
        st.write("Color:",color)

        win = False

        if choice=="Red" and color=="Red":
            win=True

        if choice=="Black" and color=="Black":
            win=True

        if choice=="Number" and spin==number:

            st.success("HUGE WIN +$"+str(bet*10))
            st.session_state.money += bet*10
            save_balance()
            win=None

        if win==True:
            st.success("Win +$"+str(bet))
            st.session_state.money += bet

        elif win==False:
            st.error("Lose -$"+str(bet))
            st.session_state.money -= bet

        save_balance()

# -----------------------
# BANKRUPT
# -----------------------

if st.session_state.money <= 0:

    st.error("💀 You're broke!")

    if st.button("Reset to $500"):

        st.session_state.money = 500
        save_balance()
