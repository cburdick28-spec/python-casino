import streamlit as st
import random
import json
import os
import hashlib
import datetime
import time

DB_FILE="casino_users.json"

# --------------------
# DATABASE
# --------------------

if not os.path.exists(DB_FILE):
    with open(DB_FILE,"w") as f:
        json.dump({},f)

def load_users():
    with open(DB_FILE,"r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE,"w") as f:
        json.dump(users,f)

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# --------------------
# LOAD USERS
# --------------------

users=load_users()

for u in users:
    users[u].setdefault("password","")
    users[u].setdefault("money",500)
    users[u].setdefault("wins",0)
    users[u].setdefault("losses",0)
    users[u].setdefault("last_daily","")
    users[u].setdefault("dev",False)

# --------------------
# DEV ACCOUNTS
# --------------------

devpass=hash_password("Dev")

users["Dev1"]={
    "password":devpass,
    "money":999999999,
    "wins":0,
    "losses":0,
    "last_daily":"",
    "dev":True
}

users["Dev2"]={
    "password":devpass,
    "money":999999999,
    "wins":0,
    "losses":0,
    "last_daily":"",
    "dev":True
}

save_users(users)

# --------------------
# SESSION
# --------------------

if "username" not in st.session_state:
    st.session_state.username=None

if "money" not in st.session_state:
    st.session_state.money=500

if "wins" not in st.session_state:
    st.session_state.wins=0

if "losses" not in st.session_state:
    st.session_state.losses=0

# --------------------
# SAVE PROGRESS
# --------------------

def save_progress():

    users=load_users()

    if st.session_state.username in users:

        if users[st.session_state.username].get("dev",False):
            st.session_state.money=999999999

        users[st.session_state.username]["money"]=st.session_state.money
        users[st.session_state.username]["wins"]=st.session_state.wins
        users[st.session_state.username]["losses"]=st.session_state.losses

    save_users(users)

# --------------------
# LOGIN
# --------------------

if st.session_state.username is None:

    st.title("🎰 Ultimate Casino")

    tab1,tab2=st.tabs(["Login","Register"])

    users=load_users()

    with tab1:

        user=st.text_input("Username")
        pw=st.text_input("Password",type="password")

        if st.button("Login"):

            if user in users and users[user]["password"]==hash_password(pw):

                st.session_state.username=user
                st.session_state.money=users[user]["money"]
                st.session_state.wins=users[user]["wins"]
                st.session_state.losses=users[user]["losses"]

                st.rerun()

            else:
                st.error("Invalid login")

    with tab2:

        newu=st.text_input("New Username")
        newp=st.text_input("New Password",type="password")

        if st.button("Register"):

            if newu=="" or newp=="":
                st.error("Fill all fields")

            elif newu in users:
                st.error("User exists")

            else:

                users[newu]={
                    "password":hash_password(newp),
                    "money":500,
                    "wins":0,
                    "losses":0,
                    "last_daily":"",
                    "dev":False
                }

                save_users(users)

                st.success("Account created")

    st.stop()

# --------------------
# SIDEBAR
# --------------------

st.sidebar.title("🎰 Casino")

st.sidebar.write("User:",st.session_state.username)
st.sidebar.write("Money:",st.session_state.money)
st.sidebar.write("Wins:",st.session_state.wins)
st.sidebar.write("Losses:",st.session_state.losses)

if st.sidebar.button("Logout"):
    st.session_state.username=None
    st.rerun()

# --------------------
# DAILY
# --------------------

users=load_users()
today=str(datetime.date.today())

if users[st.session_state.username]["last_daily"]!=today:

    if st.sidebar.button("Claim $100 Daily"):

        st.session_state.money+=100
        users[st.session_state.username]["last_daily"]=today

        save_users(users)
        save_progress()

        st.sidebar.success("Daily claimed")

# --------------------
# LEADERBOARD
# --------------------

st.sidebar.markdown("---")
st.sidebar.header("Leaderboard")

users=load_users()

top=sorted(
    users.items(),
    key=lambda x:x[1].get("money",0),
    reverse=True
)

for u in top[:10]:
    st.sidebar.write(u[0],"$"+str(u[1].get("money",0)))

# --------------------
# DEV PANEL
# --------------------

if users[st.session_state.username].get("dev",False):

    st.sidebar.markdown("---")
    st.sidebar.header("🛠 DEV PANEL")

    target=st.sidebar.selectbox(
        "Select Player",
        list(users.keys())
    )

    amount=st.sidebar.number_input("Give Money",0,1000000)

    if st.sidebar.button("Give Money"):
        users[target]["money"]+=amount
        save_users(users)
        st.sidebar.success("Money added")

    if st.sidebar.button("Reset Database"):
        for u in users:
            users[u]["money"]=500
            users[u]["wins"]=0
            users[u]["losses"]=0
        save_users(users)
        st.sidebar.success("Database reset")

# --------------------
# MAIN
# --------------------

st.title("🎰 Casino Games")

game=st.selectbox(
    "Game",
    ["Slots","Dice","Blackjack","Roulette"]
)

bet=st.number_input(
    "Bet",
    min_value=1,
    max_value=max(1,st.session_state.money),
    value=10
)

# --------------------
# SLOTS
# --------------------

if game=="Slots":

    symbols=["🍒","🍋","🍉","⭐","💎","7️⃣"]
    display=st.empty()

    if st.button("Spin"):

        for i in range(15):
            r=[random.choice(symbols) for _ in range(3)]
            display.write(" | ".join(r))
            time.sleep(0.1)

        r=[random.choice(symbols) for _ in range(3)]
        display.write(" | ".join(r))

        if r[0]==r[1]==r[2]:

            win=bet*6
            st.success("JACKPOT +"+str(win))
            st.session_state.money+=win
            st.session_state.wins+=1

        elif r[0]==r[1] or r[1]==r[2]:

            win=bet*2
            st.success("Win +"+str(win))
            st.session_state.money+=win
            st.session_state.wins+=1

        else:

            st.error("Lose -"+str(bet))
            st.session_state.money-=bet
            st.session_state.losses+=1

        save_progress()

# --------------------
# DICE
# --------------------

if game=="Dice":

    display=st.empty()

    if st.button("Roll"):

        for i in range(10):

            p=random.randint(1,6)
            h=random.randint(1,6)

            display.write("You:"+str(p)+" House:"+str(h))
            time.sleep(0.1)

        player=random.randint(1,6)
        house=random.randint(1,6)

        display.write("You:"+str(player)+" House:"+str(house))

        if player>house:

            st.success("Win +"+str(bet))
            st.session_state.money+=bet
            st.session_state.wins+=1

        elif player<house:

            st.error("Lose -"+str(bet))
            st.session_state.money-=bet
            st.session_state.losses+=1

        else:
            st.info("Draw")

        save_progress()

# --------------------
# BLACKJACK
# --------------------

if game=="Blackjack":

    def draw():
        return random.randint(1,11)

    display=st.empty()

    if st.button("Deal"):

        total=0

        for i in range(3):
            c=draw()
            total+=c
            display.write("Card "+str(c))
            time.sleep(0.6)

        dealer=draw()+draw()

        st.write("Player:",total)
        st.write("Dealer:",dealer)

        if total>21:

            st.error("Bust")
            st.session_state.money-=bet

        elif dealer>21 or total>dealer:

            st.success("Win")
            st.session_state.money+=bet

        elif total<dealer:

            st.error("Lose")
            st.session_state.money-=bet

        else:
            st.info("Push")

        save_progress()

# --------------------
# ROULETTE
# --------------------

if game=="Roulette":

    choice=st.selectbox("Bet on",["Red","Black","Number"])

    num=None
    if choice=="Number":
        num=st.number_input("Pick 0-36",0,36)

    display=st.empty()

    if st.button("Spin"):

        for i in range(20):
            display.write("Spinning "+str(random.randint(0,36)))
            time.sleep(0.05)

        spin=random.randint(0,36)

        if spin==0:
            color="Green"
        elif spin%2==0:
            color="Red"
        else:
            color="Black"

        display.write("Result "+str(spin)+" "+color)

        win=False

        if choice=="Red" and color=="Red":
            win=True

        if choice=="Black" and color=="Black":
            win=True

        if choice=="Number" and spin==num:

            st.success("Mega win")
            st.session_state.money+=bet*12
            win=None

        if win==True:

            st.success("Win")
            st.session_state.money+=bet

        elif win==False:

            st.error("Lose")
            st.session_state.money-=bet

        save_progress()

# --------------------
# BANKRUPT
# --------------------

if st.session_state.money<=0:

    st.error("You are broke")

    if st.button("Reset $500"):

        st.session_state.money=500
        save_progress()
