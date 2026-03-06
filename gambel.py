import streamlit as st
import random
import json
import os
import hashlib
import datetime

DB_FILE = "casino_users.json"

# -------------------------
# DATABASE
# -------------------------

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

# -------------------------
# SESSION
# -------------------------

if "username" not in st.session_state:
    st.session_state.username=None

if "money" not in st.session_state:
    st.session_state.money=500

if "wins" not in st.session_state:
    st.session_state.wins=0

if "losses" not in st.session_state:
    st.session_state.losses=0

# -------------------------
# SAVE USER
# -------------------------

def save_progress():

    users = load_users()

    users[st.session_state.username]["money"]=st.session_state.money
    users[st.session_state.username]["wins"]=st.session_state.wins
    users[st.session_state.username]["losses"]=st.session_state.losses

    save_users(users)

# -------------------------
# LOGIN / REGISTER
# -------------------------

if st.session_state.username is None:

    st.title("🎰 Ultimate Python Casino")

    tab1,tab2 = st.tabs(["Login","Register"])

    users = load_users()

    # LOGIN
    with tab1:

        user = st.text_input("Username")
        pw = st.text_input("Password",type="password")

        if st.button("Login"):

            if user in users:

                if users[user]["password"]==hash_password(pw):

                    st.session_state.username=user
                    st.session_state.money=users[user]["money"]
                    st.session_state.wins=users[user]["wins"]
                    st.session_state.losses=users[user]["losses"]

                    st.success("Welcome back!")
                    st.rerun()

                else:
                    st.error("Wrong password")

            else:
                st.error("User not found")

    # REGISTER
    with tab2:

        new_user = st.text_input("Create Username")
        new_pw = st.text_input("Create Password",type="password")

        if st.button("Register"):

            if new_user=="" or new_pw=="":
                st.error("Fill all fields")

            elif new_user in users:
                st.error("Username already exists")

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

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("🎰 Casino")

st.sidebar.write("👤 Player:",st.session_state.username)
st.sidebar.write("💰 Balance: $",st.session_state.money)
st.sidebar.write("🏆 Wins:",st.session_state.wins)
st.sidebar.write("💀 Losses:",st.session_state.losses)

if st.sidebar.button("Logout"):
    st.session_state.username=None
    st.rerun()

# -------------------------
# DAILY REWARD
# -------------------------

users = load_users()
today = str(datetime.date.today())

if users[st.session_state.username]["last_daily"] != today:

    if st.sidebar.button("🎁 Claim Daily $100"):

        st.session_state.money += 100
        users[st.session_state.username]["last_daily"]=today
        save_users(users)
        save_progress()

        st.sidebar.success("Daily claimed!")

# -------------------------
# LEADERBOARD
# -------------------------

st.sidebar.markdown("---")
st.sidebar.header("🏆 Leaderboard")

users = load_users()

top = sorted(users.items(),key=lambda x:x[1]["money"],reverse=True)

for u in top[:10]:
    st.sidebar.write(u[0],"- $"+str(u[1]["money"]))

# -------------------------
# MAIN
# -------------------------

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

# -------------------------
# SLOTS
# -------------------------

if game=="Slots":

    st.header("🎰 Slots")

    symbols=["🍒","🍋","🍉","⭐","💎","7️⃣"]

    if st.button("Spin"):

        r=[random.choice(symbols) for _ in range(3)]

        st.write(" | ".join(r))

        if r[0]==r[1]==r[2]:

            win=bet*6
            st.success("JACKPOT +$"+str(win))
            st.session_state.money+=win
            st.session_state.wins+=1

        elif r[0]==r[1] or r[1]==r[2]:

            win=bet*2
            st.success("Win +$"+str(win))
            st.session_state.money+=win
            st.session_state.wins+=1

        else:

            st.error("Lost -$"+str(bet))
            st.session_state.money-=bet
            st.session_state.losses+=1

        save_progress()

# -------------------------
# DICE
# -------------------------

if game=="Dice":

    st.header("🎲 Dice")

    if st.button("Roll"):

        player=random.randint(1,6)
        house=random.randint(1,6)

        st.write("You:",player)
        st.write("House:",house)

        if player>house:

            st.success("Win +$"+str(bet))
            st.session_state.money+=bet
            st.session_state.wins+=1

        elif player<house:

            st.error("Lose -$"+str(bet))
            st.session_state.money-=bet
            st.session_state.losses+=1

        else:

            st.info("Draw")

        save_progress()

# -------------------------
# BLACKJACK
# -------------------------

if game=="Blackjack":

    st.header("🃏 Blackjack")

    def draw():
        return random.randint(1,11)

    if st.button("Deal"):

        player=draw()+draw()
        dealer=draw()+draw()

        st.write("Your hand:",player)
        st.write("Dealer:",dealer)

        if player>21:

            st.error("Bust -$"+str(bet))
            st.session_state.money-=bet
            st.session_state.losses+=1

        elif dealer>21 or player>dealer:

            st.success("Win +$"+str(bet))
            st.session_state.money+=bet
            st.session_state.wins+=1

        elif player<dealer:

            st.error("Lose -$"+str(bet))
            st.session_state.money-=bet
            st.session_state.losses+=1

        else:

            st.info("Push")

        save_progress()

# -------------------------
# ROULETTE
# -------------------------

if game=="Roulette":

    st.header("🎡 Roulette")

    choice=st.selectbox(
        "Bet on",
        ["Red","Black","Number"]
    )

    number=None

    if choice=="Number":
        number=st.number_input("Pick 0-36",0,36)

    if st.button("Spin Wheel"):

        spin=random.randint(0,36)

        if spin==0:
            color="Green"
        elif spin%2==0:
            color="Red"
        else:
            color="Black"

        st.write("Number:",spin)
        st.write("Color:",color)

        win=False

        if choice=="Red" and color=="Red":
            win=True

        if choice=="Black" and color=="Black":
            win=True

        if choice=="Number" and spin==number:

            st.success("MEGA WIN +$"+str(bet*12))
            st.session_state.money+=bet*12
            st.session_state.wins+=1
            save_progress()
            win=None

        if win==True:

            st.success("Win +$"+str(bet))
            st.session_state.money+=bet
            st.session_state.wins+=1

        elif win==False:

            st.error("Lose -$"+str(bet))
            st.session_state.money-=bet
            st.session_state.losses+=1

        save_progress()

# -------------------------
# BANKRUPT
# -------------------------

if st.session_state.money<=0:

    st.error("💀 You're broke!")

    if st.button("Reset to $500"):

        st.session_state.money=500
        save_progress()
