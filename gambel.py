import streamlit as st
import random
import json
import os
import hashlib
import datetime
import time

DB_FILE = "casino_users.json"

# -----------------------
# DATABASE SETUP
# -----------------------

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(DB_FILE,"r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE,"w") as f:
        json.dump(users,f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------
# FIX OLD ACCOUNTS
# -----------------------

users = load_users()

for u in users:
    users[u].setdefault("password","")
    users[u].setdefault("money",500)
    users[u].setdefault("wins",0)
    users[u].setdefault("losses",0)
    users[u].setdefault("last_daily","")

save_users(users)

# -----------------------
# SESSION
# -----------------------

if "username" not in st.session_state:
    st.session_state.username=None

if "money" not in st.session_state:
    st.session_state.money=500

if "wins" not in st.session_state:
    st.session_state.wins=0

if "losses" not in st.session_state:
    st.session_state.losses=0

# -----------------------
# SAVE PROGRESS
# -----------------------

def save_progress():

    users = load_users()

    if st.session_state.username in users:
        users[st.session_state.username]["money"]=st.session_state.money
        users[st.session_state.username]["wins"]=st.session_state.wins
        users[st.session_state.username]["losses"]=st.session_state.losses

    save_users(users)

# -----------------------
# LOGIN / REGISTER
# -----------------------

if st.session_state.username is None:

    st.title("🎰 Ultimate Python Casino")

    tab1,tab2 = st.tabs(["Login","Register"])

    users = load_users()

    with tab1:

        user = st.text_input("Username")
        pw = st.text_input("Password",type="password")

        if st.button("Login"):

            if user in users:

                if users[user]["password"] == hash_password(pw):

                    st.session_state.username=user
                    st.session_state.money=users[user]["money"]
                    st.session_state.wins=users[user]["wins"]
                    st.session_state.losses=users[user]["losses"]

                    st.success("Login successful")
                    st.rerun()

                else:
                    st.error("Wrong password")

            else:
                st.error("User not found")

    with tab2:

        new_user = st.text_input("Create Username")
        new_pw = st.text_input("Create Password",type="password")

        if st.button("Register"):

            if new_user=="" or new_pw=="":
                st.error("Fill all fields")

            elif new_user in users:
                st.error("Username exists")

            else:

                users[new_user]={
                    "password":hash_password(new_pw),
                    "money":500,
                    "wins":0,
                    "losses":0,
                    "last_daily":""
                }

                save_users(users)

                st.success("Account created!")

    st.stop()

# -----------------------
# SIDEBAR
# -----------------------

st.sidebar.title("🎰 Casino")

st.sidebar.write("👤 Player:",st.session_state.username)
st.sidebar.write("💰 Balance:",st.session_state.money)
st.sidebar.write("🏆 Wins:",st.session_state.wins)
st.sidebar.write("💀 Losses:",st.session_state.losses)

if st.sidebar.button("Logout"):
    st.session_state.username=None
    st.rerun()

# -----------------------
# DAILY REWARD
# -----------------------

users = load_users()
today = str(datetime.date.today())

if users[st.session_state.username]["last_daily"] != today:

    if st.sidebar.button("🎁 Claim Daily $100"):

        st.session_state.money += 100
        users[st.session_state.username]["last_daily"]=today

        save_users(users)
        save_progress()

        st.sidebar.success("Daily reward claimed!")

# -----------------------
# LEADERBOARD (FIXED)
# -----------------------

st.sidebar.markdown("---")
st.sidebar.header("🏆 Leaderboard")

users = load_users()

top = sorted(
    users.items(),
    key=lambda x: x[1].get("money",0),
    reverse=True
)

for u in top[:10]:
    st.sidebar.write(f"{u[0]} - ${u[1].get('money',0)}")

# -----------------------
# MAIN
# -----------------------

st.title("🎰 Ultimate Python Casino")

game = st.selectbox(
    "Choose Game",
    ["Slots","Dice","Blackjack","Roulette"]
)

bet = st.number_input(
    "Bet Amount",
    min_value=1,
    max_value=max(1,st.session_state.money),
    value=10
)

# -----------------------
# SLOTS
# -----------------------

if game=="Slots":

    st.header("🎰 Slots")

    symbols=["🍒","🍋","🍉","⭐","💎","7️⃣"]

    display = st.empty()

    if st.button("Spin"):

        for i in range(15):
            r=[random.choice(symbols) for _ in range(3)]
            display.write(" | ".join(r))
            time.sleep(0.1)

        r=[random.choice(symbols) for _ in range(3)]
        display.write(" | ".join(r))

        if r[0]==r[1]==r[2]:

            win=bet*6
            st.success(f"🎉 JACKPOT +${win}")
            st.session_state.money+=win
            st.session_state.wins+=1

        elif r[0]==r[1] or r[1]==r[2]:

            win=bet*2
            st.success(f"Win +${win}")
            st.session_state.money+=win
            st.session_state.wins+=1

        else:

            st.error(f"Lose -${bet}")
            st.session_state.money-=bet
            st.session_state.losses+=1

        save_progress()

# -----------------------
# DICE
# -----------------------

if game=="Dice":

    st.header("🎲 Dice")

    display = st.empty()

    if st.button("Roll"):

        for i in range(10):

            p=random.randint(1,6)
            h=random.randint(1,6)

            display.write(f"You: {p} | House: {h}")
            time.sleep(0.1)

        player=random.randint(1,6)
        house=random.randint(1,6)

        display.write(f"You: {player} | House: {house}")

        if player>house:

            st.success(f"Win +${bet}")
            st.session_state.money+=bet
            st.session_state.wins+=1

        elif player<house:

            st.error(f"Lose -${bet}")
            st.session_state.money-=bet
            st.session_state.losses+=1

        else:
            st.info("Draw")

        save_progress()

# -----------------------
# BLACKJACK
# -----------------------

if game=="Blackjack":

    st.header("🃏 Blackjack")

    display = st.empty()

    def draw():
        return random.randint(1,11)

    if st.button("Deal"):

        total=0

        for i in range(3):
            c=draw()
            total+=c
            display.write(f"Drawing card: {c}")
            time.sleep(0.6)

        player=total
        dealer=draw()+draw()

        st.write("Your hand:",player)
        st.write("Dealer:",dealer)

        if player>21:

            st.error(f"Bust -${bet}")
            st.session_state.money-=bet
            st.session_state.losses+=1

        elif dealer>21 or player>dealer:

            st.success(f"Win +${bet}")
            st.session_state.money+=bet
            st.session_state.wins+=1

        elif player<dealer:

            st.error(f"Lose -${bet}")
            st.session_state.money-=bet
            st.session_state.losses+=1

        else:
            st.info("Push")

        save_progress()

# -----------------------
# ROULETTE
# -----------------------

if game=="Roulette":

    st.header("🎡 Roulette")

    choice=st.selectbox(
        "Bet on",
        ["Red","Black","Number"]
    )

    number=None

    if choice=="Number":
        number=st.number_input("Pick 0-36",0,36)

    display = st.empty()

    if st.button("Spin Wheel"):

        for i in range(20):
            spin=random.randint(0,36)
            display.write(f"🎡 Spinning... {spin}")
            time.sleep(0.05)

        spin=random.randint(0,36)

        if spin==0:
            color="Green"
        elif spin%2==0:
            color="Red"
        else:
            color="Black"

        display.write(f"Number: {spin} | Color: {color}")

        win=False

        if choice=="Red" and color=="Red":
            win=True

        if choice=="Black" and color=="Black":
            win=True

        if choice=="Number" and spin==number:

            st.success(f"MEGA WIN +${bet*12}")
            st.session_state.money+=bet*12
            st.session_state.wins+=1
            save_progress()
            win=None

        if win==True:

            st.success(f"Win +${bet}")
            st.session_state.money+=bet
            st.session_state.wins+=1

        elif win==False:

            st.error(f"Lose -${bet}")
            st.session_state.money-=bet
            st.session_state.losses+=1

        save_progress()

# -----------------------
# BANKRUPT
# -----------------------

if st.session_state.money <= 0:

    st.error("💀 You are broke!")

    if st.button("Reset to $500"):

        st.session_state.money=500
        save_progress()
