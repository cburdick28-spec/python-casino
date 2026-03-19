import requests
import base64
import streamlit as st
import random
import json
import os
import hashlib
import datetime
import time

# -------- PASSWORD HASH --------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

GITHUB_TOKEN = st.secrets["github_token"]
REPO = "cburdick28-spec/python-casino"
FILE_PATH = "casino_db.json"

DB_FILE = "casino_db.json"
DEV_ACCOUNTS = ["Dev1", "Dev2", "Dev3"]


# -------- LOAD DATABASE FROM GITHUB --------
def load_db():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data["content"]).decode()
        return json.loads(content)
    return {"users": {}, "jackpot": 1000}


# -------- SAVE DATABASE TO GITHUB --------
def save_db(db):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    data = r.json()
    sha = data["sha"]
    content = base64.b64encode(json.dumps(db, indent=4).encode()).decode()
    payload = {
        "message": "update casino database",
        "content": content,
        "sha": sha
    }
    requests.put(url, headers=headers, json=payload)


# ---------------- DATABASE ----------------
db = load_db()

# Make sure required fields exist
if "users" not in db:
    db["users"] = {}
if "jackpot" not in db:
    db["jackpot"] = 1000

# Ensure all users have required fields
for u in db["users"]:
    if "timeout" not in db["users"][u]:
        db["users"][u]["timeout"] = 0
    if "last_daily" not in db["users"][u]:
        db["users"][u]["last_daily"] = ""

save_db(db)
users = db["users"]

# ---------------- SESSION ----------------
defaults = {
    "username": None,
    "money": 500,
    "wins": 0,
    "losses": 0,
    "bj_player": [],
    "bj_dealer": [],
    "bj_active": False,
    "bj_result": None,
    "bj_bet": 0,
    "jackpot_odds": 6
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------- SAVE ----------------
def save_progress():
    db = load_db()
    if st.session_state.username in db["users"]:
        db["users"][st.session_state.username]["money"] = st.session_state.money
    save_db(db)


# ---------------- LOGIN ----------------
if st.session_state.username is None:

    st.title("🎰 Ultimate Casino")

    tab1, tab2 = st.tabs(["Login", "Register"])

    db = load_db()
    users = db["users"]

    with tab1:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Login"):
            if user in users and users[user]["password"] == hash_password(pw):
                st.session_state.username = user
                st.session_state.money = users[user]["money"]
                st.rerun()
            else:
                st.error("Invalid login")

    with tab2:
        newu = st.text_input("New Username")
        newp = st.text_input("New Password", type="password")

        if st.button("Register"):
            if newu in users:
                st.error("User exists")
            elif not newu.strip():
                st.error("Username cannot be empty")
            elif not newp.strip():
                st.error("Password cannot be empty")
            else:
                users[newu] = {
                    "password": hash_password(newp),
                    "money": 500,
                    "last_daily": "",
                    "timeout": 0  # FIX: missing timeout field on registration
                }
                db["users"] = users
                save_db(db)
                st.success("Account created! Please log in.")

    st.stop()


# ---------------- SIDEBAR ----------------
st.sidebar.title("🎰 Casino")

user = st.session_state.username
db = load_db()
users = db["users"]

# Ensure all users have required fields
for u in users:
    if "timeout" not in users[u]:
        users[u]["timeout"] = 0
    if "last_daily" not in users[u]:
        users[u]["last_daily"] = ""

# ---------------- TIMEOUT CHECK ----------------
now = time.time()

if users[user]["timeout"] > now:
    remaining = int(users[user]["timeout"] - now)
    minutes = remaining // 60
    seconds = remaining % 60
    st.error(f"⏳ You are timed out for {minutes}m {seconds}s")
    st.stop()

# Dev infinite money
if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

st.sidebar.write("User:", user)

# Show role
if user in DEV_ACCOUNTS:
    st.sidebar.write("Role: 👑 Developer")
else:
    st.sidebar.write("Role: 🎮 Player")

st.sidebar.write("Money:", st.session_state.money)

if st.sidebar.button("Logout"):
    st.session_state.username = None
    st.rerun()

# ---------------- DEV PANEL ----------------
if user in DEV_ACCOUNTS:
    st.sidebar.markdown("---")
    st.sidebar.header("👑 Dev Panel")

    target = st.sidebar.selectbox("Select User", list(users.keys()))
    give = st.sidebar.number_input("Give Money", 0, 1000000)

    if st.sidebar.button("Give Money"):
        users[target]["money"] += give
        db["users"] = users
        save_db(db)
        st.sidebar.success("Money given")

    if st.sidebar.button("Reset All Money"):
        for u in users:
            users[u]["money"] = 500
        db["users"] = users
        save_db(db)
        st.sidebar.success("All balances reset")

    new_odds = st.sidebar.slider("Slot Jackpot Multiplier", 2, 20, st.session_state.jackpot_odds)
    st.session_state.jackpot_odds = new_odds

    # -------- TIMEOUT SYSTEM (DEV ONLY) --------
    st.sidebar.subheader("⏳ Timeout Player")

    timeout_user = st.sidebar.selectbox(
        "Player to timeout",
        list(users.keys()),
        key="timeout_select"
    )

    timeout_minutes = st.sidebar.number_input("Timeout minutes", 1, 10000, 5)

    if st.sidebar.button("Timeout Player"):
        users[timeout_user]["timeout"] = time.time() + timeout_minutes * 60
        db["users"] = users
        save_db(db)
        st.sidebar.success(f"{timeout_user} timed out for {timeout_minutes} minutes")

    # -------- REMOVE TIMEOUT (DEV ONLY) --------
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔓 Remove Timeout")

    untimeout_user = st.sidebar.selectbox(
        "Player to remove timeout",
        list(users.keys()),
        key="remove_timeout_select"
    )

    if st.sidebar.button("Remove Timeout"):
        users[untimeout_user]["timeout"] = 0
        db["users"] = users
        save_db(db)
        st.sidebar.success(f"{untimeout_user} timeout removed")


# ---------------- DAILY ----------------
today = str(datetime.date.today())

if users[user]["last_daily"] != today:
    if st.sidebar.button("Claim $100 Daily"):
        st.session_state.money += 100
        users[user]["last_daily"] = today
        db["users"] = users
        save_db(db)
        save_progress()
        st.rerun()  # FIX: added rerun so sidebar updates immediately


# ---------------- LEADERBOARD ----------------
st.sidebar.markdown("---")
st.sidebar.header("Leaderboard")

# FIX: exclude Dev accounts from leaderboard so they don't dominate
top = sorted(
    [(u, v) for u, v in users.items() if u not in DEV_ACCOUNTS],
    key=lambda x: x[1]["money"],
    reverse=True
)

for u in top[:10]:
    st.sidebar.write(u[0], "$" + str(u[1]["money"]))


# ---------------- JACKPOT DISPLAY ----------------
st.title("🎰 Casino Games")
st.header(f"💰 Progressive Jackpot: ${db['jackpot']}")

game = st.selectbox("Game", ["Slots", "Blackjack", "Roulette"])

money = st.session_state.money


# ---------------- BANKRUPTCY ----------------
if money <= 0:
    if users[user]["last_daily"] == today:
        if st.button("Play Again ($250)"):
            st.session_state.money = 250
            save_progress()
            st.rerun()
    else:
        st.warning("Claim daily reward in sidebar")
    st.stop()

bet = st.number_input("Bet", 1, money, min(10, money))


# ---------------- SLOTS ----------------
if game == "Slots":

    symbols = ["🍒", "🍋", "🍉", "⭐", "💎", "7️⃣"]
    display = st.empty()

    if st.button("Spin"):

        for i in range(15):
            r = [random.choice(symbols) for _ in range(3)]
            display.write(" | ".join(r))
            time.sleep(0.05)

        r = [random.choice(symbols) for _ in range(3)]
        display.write(" | ".join(r))

        # FIX: reload db fresh before modifying jackpot to avoid stale state
        db = load_db()
        jackpot = db["jackpot"]

        if r[0] == r[1] == r[2]:
            win = bet * st.session_state.jackpot_odds
            st.success(f"🎰 JACKPOT +{win}")
            st.session_state.money += win
            st.success(f"💰 Progressive Jackpot Won: ${jackpot}")
            st.session_state.money += jackpot
            db["jackpot"] = 1000

        elif r[0] == r[1] or r[1] == r[2]:
            win = bet * 2
            st.success(f"Win +{win}")
            st.session_state.money += win

        else:
            st.error(f"Lose -{bet}")
            st.session_state.money -= bet
            db["jackpot"] += int(bet * 0.25)

        save_db(db)
        save_progress()


# ---------------- BLACKJACK ----------------
suits = ["♠", "♥", "♦", "♣"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def draw_card():
    return random.choice(ranks) + random.choice(suits)


def card_value(card):
    r = card[:-1]  # strips the suit character
    if r in ["J", "Q", "K"]:
        return 10
    if r == "A":
        return 11
    return int(r)


def hand_value(hand):
    total = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c[:-1] == "A")  # FIX: use [:-1] to match card_value logic
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def render_cards(hand):
    html = ""
    for card in hand:
        suit = card[-1]
        rank = card[:-1]
        color = "red" if suit in ["♥", "♦"] else "black"
        html += f"""
        <div style="
        display:inline-block;
        width:100px;
        height:140px;
        border-radius:10px;
        border:2px solid #333;
        margin:6px;
        text-align:center;
        background:white;
        color:{color};
        font-size:24px;
        padding-top:10px;
        ">
        <div>{rank}</div>
        <div style="font-size:40px">{suit}</div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)


if game == "Blackjack":

    st.header("🃏 Blackjack")

    # Show previous result
    if st.session_state.bj_result:
        r, amt, msg = st.session_state.bj_result
        if r == "win":
            st.success(f"{msg}  +{amt}")
        elif r == "lose":
            st.error(f"{msg}  -{amt}")
        else:
            st.info("Push")
        st.session_state.bj_result = None

    # Deal
    if not st.session_state.bj_active:
        if st.button("Deal"):
            st.session_state.bj_bet = bet
            st.session_state.bj_player = [draw_card(), draw_card()]
            st.session_state.bj_dealer = [draw_card(), draw_card()]
            st.session_state.bj_active = True
            st.rerun()

    # Active round
    if st.session_state.bj_active:

        player = st.session_state.bj_player
        dealer = st.session_state.bj_dealer

        st.subheader("Your Hand")
        render_cards(player)
        st.write("Total:", hand_value(player))

        st.subheader("Dealer Shows")
        render_cards([dealer[0]])

        col1, col2 = st.columns(2)

        # HIT
        with col1:
            if st.button("Hit"):
                new_card = draw_card()
                player.append(new_card)
                if hand_value(player) > 21:
                    st.session_state.money -= st.session_state.bj_bet
                    st.session_state.bj_result = (
                        "lose",
                        st.session_state.bj_bet,  # FIX: was using `bet` (new input) instead of locked bj_bet
                        f"You busted with {new_card}"
                    )
                    st.session_state.bj_active = False
                    save_progress()
                st.rerun()

        # STAND
        with col2:
            if st.button("Stand"):
                while hand_value(dealer) < 17:
                    dealer.append(draw_card())

                pt = hand_value(player)
                dt = hand_value(dealer)

                if dt > 21 or pt > dt:
                    st.session_state.money += st.session_state.bj_bet
                    st.session_state.bj_result = (
                        "win",
                        st.session_state.bj_bet,  # FIX: was using `bet` instead of locked bj_bet
                        "You win!"
                    )
                elif pt < dt:
                    st.session_state.money -= st.session_state.bj_bet
                    st.session_state.bj_result = (
                        "lose",
                        st.session_state.bj_bet,  # FIX: was using `bet` instead of locked bj_bet
                        "Dealer wins"
                    )
                else:
                    st.session_state.bj_result = ("push", 0, "Push")

                st.session_state.bj_active = False
                save_progress()
                st.rerun()


# ---------------- ROULETTE ----------------
if game == "Roulette":

    choice = st.selectbox("Bet on", ["Red", "Black", "Number"])
    num = None

    if choice == "Number":
        num = int(st.number_input("Pick 0-36", 0, 36))

    if st.button("Spin"):
        spin = random.randint(0, 36)

        # FIX: original logic (even=Red, odd=Black) was wrong.
        # Real roulette uses a specific set of red numbers.
        red_numbers = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

        if spin == 0:
            color = "Green"
        elif spin in red_numbers:
            color = "Red"
        else:
            color = "Black"

        st.write("Result:", spin, color)

        if choice == "Number" and spin == num:
            win = bet * 35  # FIX: standard roulette pays 35:1, not 12:1
            st.success(f"Big Win! +{win}")
            st.session_state.money += win

        elif choice == color:
            st.success(f"Win +{bet}")
            st.session_state.money += bet

        else:
            st.error(f"Lose -{bet}")
            st.session_state.money -= bet

        save_progress()
