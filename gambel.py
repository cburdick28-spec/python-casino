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
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

users = load_users()

for u in users:
    users[u].setdefault("password", "")
    users[u].setdefault("money", 500)
    users[u].setdefault("wins", 0)
    users[u].setdefault("losses", 0)
    users[u].setdefault("last_daily", "")
    users[u].setdefault("dev", False)

devpass = hash_password("Dev")

for dev in ["Dev1", "Dev2", "Dev3"]:
    if dev not in users:
        users[dev] = {
            "password": devpass,
            "money": 999999999,
            "wins": 0,
            "losses": 0,
            "last_daily": "",
            "dev": True
        }

save_users(users)

# ------------------------
# SESSION STATE
# ------------------------
defaults = {
    "username": None,
    "money": 500,
    "wins": 0,
    "losses": 0,
    "bj_player": [],
    "bj_dealer": [],
    "bj_active": False,
    "bj_result": None
}

for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

params = st.query_params

if st.session_state.username is None and "user" in params:
    auto_user = params["user"]
    users = load_users()

    if auto_user in users and users[auto_user].get("dev", False):
        st.session_state.username = auto_user
        st.session_state.money = users[auto_user]["money"]
        st.session_state.wins = users[auto_user]["wins"]
        st.session_state.losses = users[auto_user]["losses"]

def save_progress():
    users = load_users()

    if st.session_state.username in users:

        if users[st.session_state.username].get("dev", False):
            st.session_state.money = 999999999

        users[st.session_state.username]["money"] = st.session_state.money
        users[st.session_state.username]["wins"] = st.session_state.wins
        users[st.session_state.username]["losses"] = st.session_state.losses

    save_users(users)

# ------------------------
# LOGIN
# ------------------------
if st.session_state.username is None:

    st.title("🎰 Ultimate Casino")

    tab1, tab2 = st.tabs(["Login", "Register"])
    users = load_users()

    with tab1:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Login"):

            if user in users and users[user]["password"] == hash_password(pw):

                st.session_state.username = user
                st.session_state.money = users[user]["money"]
                st.session_state.wins = users[user]["wins"]
                st.session_state.losses = users[user]["losses"]

                if users[user].get("dev", False):
                    st.query_params.update({"user": user})

                st.rerun()

            else:
                st.error("Invalid login")

    with tab2:

        newu = st.text_input("New Username")
        newp = st.text_input("New Password", type="password")

        if st.button("Register"):

            if newu == "" or newp == "":
                st.error("Fill all fields")

            elif newu in users:
                st.error("User exists")

            else:
                users[newu] = {
                    "password": hash_password(newp),
                    "money": 500,
                    "wins": 0,
                    "losses": 0,
                    "last_daily": "",
                    "dev": False
                }

                save_users(users)
                st.success("Account created")

    st.stop()

# ------------------------
# SIDEBAR
# ------------------------
st.sidebar.title("🎰 Casino")

st.sidebar.write("User:", st.session_state.username)
st.sidebar.write("Money:", st.session_state.money)
st.sidebar.write("Wins:", st.session_state.wins)
st.sidebar.write("Losses:", st.session_state.losses)

if st.sidebar.button("Logout"):
    st.session_state.username = None
    st.query_params.clear()
    st.rerun()

users = load_users()
today = str(datetime.date.today())

if users[st.session_state.username]["last_daily"] != today:

    if st.sidebar.button("Claim $100 Daily"):
        st.session_state.money += 100
        users[st.session_state.username]["last_daily"] = today

        save_users(users)
        save_progress()

        st.sidebar.success("Daily claimed")

# ------------------------
# LEADERBOARD
# ------------------------
st.sidebar.markdown("---")
st.sidebar.header("Leaderboard")

users = load_users()

top = sorted(users.items(), key=lambda x: x[1].get("money",0), reverse=True)

for u in top[:10]:
    st.sidebar.write(u[0], "$"+str(u[1].get("money",0)))

# ------------------------
# GAME SELECT
# ------------------------
st.title("🎰 Casino Games")

game = st.selectbox("Game", ["Slots","Dice","Blackjack","Roulette"])

max_bet = max(1, st.session_state.money)
bet = st.number_input("Bet",1,max_bet,10)

# ------------------------
# BLACKJACK
# ------------------------
suits = ["♠","♥","♦","♣"]
ranks = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

def draw_card():
    return random.choice(ranks)+random.choice(suits)

def card_value(card):
    r = card[:-1]
    if r in ["J","Q","K"]:
        return 10
    if r == "A":
        return 11
    return int(r)

def hand_value(hand):
    total = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c.startswith("A"))

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total

if game == "Blackjack":

    st.header("🃏 Blackjack")

    if st.session_state.bj_result:
        r,amt = st.session_state.bj_result

        if r=="win":
            st.success(f"You won +{amt}")
        elif r=="lose":
            st.error(f"You lost -{amt}")
        else:
            st.info("Push")

        st.session_state.bj_result=None

    if not st.session_state.bj_active:

        if st.button("Deal"):
            st.session_state.bj_player=[draw_card(),draw_card()]
            st.session_state.bj_dealer=[draw_card(),draw_card()]
            st.session_state.bj_active=True
            st.rerun()

    if st.session_state.bj_active:

        player=st.session_state.bj_player
        dealer=st.session_state.bj_dealer

        st.write("Your Hand:",player,"Total:",hand_value(player))
        st.write("Dealer Shows:",dealer[0])

        col1,col2=st.columns(2)

        with col1:
            if st.button("Hit"):

                player.append(draw_card())

                if hand_value(player)>21:
                    st.session_state.money-=bet
                    st.session_state.bj_result=("lose",bet)
                    st.session_state.bj_active=False
                    save_progress()

                st.rerun()

        with col2:
            if st.button("Stand"):

                while hand_value(dealer)<17:
                    dealer.append(draw_card())

                pt=hand_value(player)
                dt=hand_value(dealer)

                if dt>21 or pt>dt:
                    st.session_state.money+=bet
                    st.session_state.bj_result=("win",bet)

                elif pt<dt:
                    st.session_state.money-=bet
                    st.session_state.bj_result=("lose",bet)

                else:
                    st.session_state.bj_result=("push",0)

                st.session_state.bj_active=False
                save_progress()
                st.rerun()
