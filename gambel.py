import streamlit as st
import random
import json
import os
import hashlib
import datetime
import time

DB_FILE = "casino_users.json"

# ------------------------
# DATABASE
# ------------------------

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

# ------------------------
# LOAD USERS
# ------------------------

users = load_users()

for u in users:
    users[u].setdefault("password","")
    users[u].setdefault("money",500)
    users[u].setdefault("wins",0)
    users[u].setdefault("losses",0)
    users[u].setdefault("last_daily","")
    users[u].setdefault("dev",False)

# ------------------------
# DEV ACCOUNTS
# ------------------------

devpass = hash_password("Dev")

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

# ------------------------
# SESSION STATE
# ------------------------

if "username" not in st.session_state:
    st.session_state.username=None

if "money" not in st.session_state:
    st.session_state.money=500

if "wins" not in st.session_state:
    st.session_state.wins=0

if "losses" not in st.session_state:
    st.session_state.losses=0

# Blackjack session data
if "bj_player" not in st.session_state:
    st.session_state.bj_player=[]

if "bj_dealer" not in st.session_state:
    st.session_state.bj_dealer=[]

if "bj_active" not in st.session_state:
    st.session_state.bj_active=False

# ------------------------
# SAVE PROGRESS
# ------------------------

def save_progress():

    users=load_users()

    if st.session_state.username in users:

        if users[st.session_state.username].get("dev",False):
            st.session_state.money=999999999

        users[st.session_state.username]["money"]=st.session_state.money
        users[st.session_state.username]["wins"]=st.session_state.wins
        users[st.session_state.username]["losses"]=st.session_state.losses

    save_users(users)

# ------------------------
# LOGIN
# ------------------------

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

# ------------------------
# SIDEBAR
# ------------------------

st.sidebar.title("🎰 Casino")

st.sidebar.write("User:",st.session_state.username)
st.sidebar.write("Money:",st.session_state.money)
st.sidebar.write("Wins:",st.session_state.wins)
st.sidebar.write("Losses:",st.session_state.losses)

if st.sidebar.button("Logout"):
    st.session_state.username=None
    st.rerun()

# ------------------------
# DAILY REWARD
# ------------------------

users=load_users()
today=str(datetime.date.today())

if users[st.session_state.username]["last_daily"]!=today:

    if st.sidebar.button("Claim $100 Daily"):

        st.session_state.money+=100
        users[st.session_state.username]["last_daily"]=today

        save_users(users)
        save_progress()

        st.sidebar.success("Daily claimed")

# ------------------------
# LEADERBOARD
# ------------------------

st.sidebar.markdown("---")
st.sidebar.header("Leaderboard")

users=load_users()

top=sorted(users.items(),key=lambda x:x[1].get("money",0),reverse=True)

for u in top[:10]:
    st.sidebar.write(u[0],"$"+str(u[1].get("money",0)))

# ------------------------
# DEV PANEL
# ------------------------

if users[st.session_state.username].get("dev",False):

    st.sidebar.markdown("---")
    st.sidebar.header("🛠 DEV PANEL")

    target=st.sidebar.selectbox("Select Player",list(users.keys()))
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

# ------------------------
# GAME SELECT
# ------------------------

st.title("🎰 Casino Games")

game=st.selectbox("Game",["Slots","Dice","Blackjack","Roulette"])

bet=st.number_input("Bet",1,max(1,st.session_state.money),10)

# ------------------------
# SLOTS
# ------------------------

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

        elif r[0]==r[1] or r[1]==r[2]:

            win=bet*2
            st.success("Win +"+str(win))
            st.session_state.money+=win

        else:

            st.error("Lose -"+str(bet))
            st.session_state.money-=bet

        save_progress()

# ------------------------
# DICE
# ------------------------

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

        elif player<house:

            st.error("Lose -"+str(bet))
            st.session_state.money-=bet

        else:
            st.info("Draw")

        save_progress()

# ------------------------
# CARD DISPLAY FUNCTION
# ------------------------

def render_cards(hand):

    html = ""

    for c in hand:

        if c in ["♥","♦"]:
            color = "red"
        else:
            color = "black"

        html += f"""
        <div style="
            display:inline-block;
            width:90px;
            height:130px;
            border-radius:10px;
            border:2px solid #333;
            margin:6px;
            font-size:60px;
            text-align:center;
            line-height:120px;
            background:white;
            color:{color};
            box-shadow:3px 3px 8px rgba(0,0,0,0.3);
        ">
        {c}
        </div>
        """

    st.markdown(html, unsafe_allow_html=True)
# ------------------------
# BLACKJACK CARD SYSTEM
# ------------------------

import random

suits = ["♠","♥","♦","♣"]
ranks = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

def draw_card():
    return random.choice(ranks) + random.choice(suits)

def card_value(card):

    rank = card[:-1]

    if rank in ["J","Q","K"]:
        return 10
    if rank == "A":
        return 11

    return int(rank)

def hand_value(hand):

    total = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c.startswith("A"))

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total


# ------------------------
# CARD DISPLAY
# ------------------------

def render_cards(hand):

    html=""

    for card in hand:

        suit = card[-1]
        rank = card[:-1]

        color = "red" if suit in ["♥","♦"] else "black"

        html += f"""
        <div style="
        display:inline-block;
        width:100px;
        height:140px;
        border-radius:10px;
        border:2px solid #333;
        margin:6px;
        font-size:40px;
        text-align:center;
        line-height:60px;
        background:white;
        color:{color};
        box-shadow:3px 3px 8px rgba(0,0,0,0.3);
        ">
        <div style="font-size:22px">{rank}</div>
        <div style="font-size:40px">{suit}</div>
        </div>
        """

    st.markdown(html, unsafe_allow_html=True)
# ------------------------
# BLACKJACK DISPLAY
# ------------------------

if game == "Blackjack":

    st.header("🃏 Blackjack")

    if st.button("Deal") and not st.session_state.bj_active:

        st.session_state.bj_player=[draw_card(),draw_card()]
        st.session_state.bj_dealer=[draw_card(),draw_card()]
        st.session_state.bj_active=True


    if st.session_state.bj_active:

        player = st.session_state.bj_player
        dealer = st.session_state.bj_dealer

        st.subheader("Your Hand")
        render_cards(player)
        st.write("Total:",hand_value(player))

        st.subheader("Dealer Shows")
        render_cards([dealer[0]])

        col1,col2 = st.columns(2)

        with col1:
            if st.button("Hit"):

                player.append(draw_card())

                if hand_value(player) > 21:

                    render_cards(player)
                    st.error("Bust! Lose -"+str(bet))
                    st.session_state.money -= bet

                    st.session_state.bj_active=False
                    save_progress()
                    st.rerun()

        with col2:
            if st.button("Stand"):

                while hand_value(dealer) < 17:
                    dealer.append(draw_card())

                st.subheader("Dealer Hand")
                render_cards(dealer)
                st.write("Dealer Total:",hand_value(dealer))

                if hand_value(dealer) > 21 or hand_value(player) > hand_value(dealer):

                    st.success("Win +"+str(bet))
                    st.session_state.money += bet

                elif hand_value(player) < hand_value(dealer):

                    st.error("Lose -"+str(bet))
                    st.session_state.money -= bet

                else:
                    st.info("Push")

                st.session_state.bj_active=False
                save_progress()
                st.rerun()
# ------------------------
# ROULETTE
# ------------------------

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
            st.success("Mega Win!")
            st.session_state.money+=bet*12
            win=None

        if win==True:
            st.success("Win +"+str(bet))
            st.session_state.money+=bet

        elif win==False:
            st.error("Lose -"+str(bet))
            st.session_state.money-=bet

        save_progress()

# ------------------------
# BANKRUPT
# ------------------------

if st.session_state.money<=0:

    st.error("You are broke!")

    if st.button("Reset $500"):
        st.session_state.money=500
        save_progress()
