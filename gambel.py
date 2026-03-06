import streamlit as st
import random
import time

st.set_page_config(page_title="Python Casino Pro", page_icon="🎰")

# ------------------------------------------------
# LOGIN SYSTEM
# ------------------------------------------------

if "users" not in st.session_state:
    st.session_state.users = {}

if "username" not in st.session_state:
    st.session_state.username = None

if "money" not in st.session_state:
    st.session_state.money = 500

if st.session_state.username is None:

    st.title("🎰 Python Casino Login")

    name = st.text_input("Enter Username")

    if st.button("Login"):

        if name not in st.session_state.users:
            st.session_state.users[name] = 500

        st.session_state.username = name
        st.session_state.money = st.session_state.users[name]
        st.rerun()

    st.stop()

# ------------------------------------------------
# SAVE BALANCE
# ------------------------------------------------

def save_balance():
    st.session_state.users[st.session_state.username] = st.session_state.money

# ------------------------------------------------
# BLACKJACK STATE
# ------------------------------------------------

if "bj_active" not in st.session_state:
    st.session_state.bj_active = False
    st.session_state.round_over = False
    st.session_state.player = []
    st.session_state.dealer = []
    st.session_state.bet = 0

# ------------------------------------------------
# CARD SYSTEM
# ------------------------------------------------

suits = ["spades","hearts","diamonds","clubs"]
ranks = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

deck = [(r,s) for r in ranks for s in suits]

def deal_card():
    return random.choice(deck)

def card_value(card):

    r = card[0]

    if r in ["J","Q","K"]:
        return 10
    if r == "A":
        return 11

    return int(r)

def hand_value(hand):

    value = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c[0] == "A")

    while value > 21 and aces:
        value -= 10
        aces -= 1

    return value

def card_image(card):

    rank,suit = card

    rank_map = {
        "A":"ace",
        "J":"jack",
        "Q":"queen",
        "K":"king"
    }

    r = rank_map.get(rank,rank)

    return f"https://raw.githubusercontent.com/hayeah/playing-cards-assets/master/png/{r}_of_{suit}.png"

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.title("🎰 Python Casino Pro")
st.write(f"Player: **{st.session_state.username}**")
st.write(f"## 💰 Balance: ${st.session_state.money}")

# ------------------------------------------------
# GAME OVER SYSTEM
# ------------------------------------------------

if st.session_state.money <= 0:

    st.error("💀 You lost all your money!")

    st.markdown("## 🎰 Casino Bankruptcy")
    st.write("You have no chips left. Reset to continue playing.")

    if st.button("Reset Money ($500)"):

        st.session_state.money = 500
        save_balance()
        st.rerun()

    st.stop()

# ------------------------------------------------
# GAME SELECT
# ------------------------------------------------

game = st.sidebar.selectbox(
    "Choose Game",
    ["Slots","Blackjack","Roulette"]
)

# ------------------------------------------------
# SLOT MACHINE
# ------------------------------------------------

if game == "Slots":

    st.header("🎰 Slot Machine")

    symbols = ["🍒","🍋","🔔","💎","7️⃣"]

    bet = st.number_input(
        "Bet Amount",
        1,
        st.session_state.money,
        10
    )

    if st.button("Spin"):

        display = st.empty()

        for i in range(15):

            spin = [random.choice(symbols) for _ in range(3)]
            display.markdown(f"# {spin[0]} {spin[1]} {spin[2]}")
            time.sleep(0.05)

        s1,s2,s3 = spin

        if s1 == s2 == s3:

            win = bet * 5
            st.session_state.money += win
            st.success(f"🎉 JACKPOT +${win}")

        elif s1 == s2 or s2 == s3 or s1 == s3:

            win = bet * 2
            st.session_state.money += win
            st.success(f"You won +${win}")

        else:

            st.session_state.money -= bet
            st.error("You lost")

        save_balance()

# ------------------------------------------------
# BLACKJACK
# ------------------------------------------------

if game == "Blackjack":

    st.header("🃏 Blackjack")

    if not st.session_state.bj_active and not st.session_state.round_over:

        bet = st.number_input(
            "Bet Amount",
            1,
            st.session_state.money,
            25
        )

        if st.button("Start Game"):

            st.session_state.bet = bet
            st.session_state.player = [deal_card(),deal_card()]
            st.session_state.dealer = [deal_card(),deal_card()]
            st.session_state.bj_active = True
            st.rerun()

    if st.session_state.bj_active:

        st.subheader("Your Hand")

        cols = st.columns(len(st.session_state.player))

        for i,c in enumerate(st.session_state.player):
            cols[i].image(card_image(c),width=100)

        player_total = hand_value(st.session_state.player)
        st.write("Total:",player_total)

        st.subheader("Dealer Shows")
        st.image(card_image(st.session_state.dealer[0]),width=100)

        if player_total > 21:

            st.error("💥 Bust!")

            st.session_state.money -= st.session_state.bet
            save_balance()

            st.session_state.bj_active = False
            st.session_state.round_over = True
            st.rerun()

        col1,col2 = st.columns(2)

        if col1.button("Hit"):

            st.session_state.player.append(deal_card())
            st.rerun()

        if col2.button("Stand"):

            while hand_value(st.session_state.dealer) < 17:
                st.session_state.dealer.append(deal_card())

            dealer_total = hand_value(st.session_state.dealer)

            st.subheader("Dealer Hand")

            cols = st.columns(len(st.session_state.dealer))

            for i,c in enumerate(st.session_state.dealer):
                cols[i].image(card_image(c),width=100)

            st.write("Dealer:",dealer_total)

            if dealer_total > 21 or player_total > dealer_total:

                st.success("🎉 You Win!")
                st.session_state.money += st.session_state.bet

            elif dealer_total == player_total:

                st.warning("Push")

            else:

                st.error("Dealer Wins")
                st.session_state.money -= st.session_state.bet

            save_balance()

            st.session_state.bj_active = False
            st.session_state.round_over = True

    if st.session_state.round_over:

        if st.button("Play Again"):

            st.session_state.player=[]
            st.session_state.dealer=[]
            st.session_state.round_over=False
            st.rerun()

# ------------------------------------------------
# ROULETTE
# ------------------------------------------------

if game == "Roulette":

    st.header("🎡 Roulette")

    bet_type = st.selectbox(
        "Bet Type",
        ["Number","Red","Black"]
    )

    bet = st.number_input(
        "Bet Amount",
        1,
        st.session_state.money,
        10
    )

    if bet_type == "Number":
        chosen = st.number_input("Pick number",0,36)

    if st.button("Spin"):

        wheel = st.empty()

        for i in range(25):

            wheel.markdown(f"# 🎡 {random.randint(0,36)}")
            time.sleep(0.04)

        result = random.randint(0,36)

        red_numbers = {
            1,3,5,7,9,12,14,16,18,19,
            21,23,25,27,30,32,34,36
        }

        if result == 0:
            color="Green"
        elif result in red_numbers:
            color="Red"
        else:
            color="Black"

        wheel.markdown(f"# 🎡 {result} {color}")

        if bet_type == "Number":

            if result == chosen:

                win = bet * 35
                st.session_state.money += win
                st.success(f"+${win}")

            else:

                st.session_state.money -= bet
                st.error("Lost")

        elif bet_type == "Red":

            if color == "Red":
                st.session_state.money += bet
                st.success("Win")

            else:
                st.session_state.money -= bet
                st.error("Lost")

        elif bet_type == "Black":

            if color == "Black":
                st.session_state.money += bet
                st.success("Win")

            else:
                st.session_state.money -= bet
                st.error("Lost")

        save_balance()

# ------------------------------------------------
# LEADERBOARD
# ------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.header("🏆 Leaderboard")

sorted_players = sorted(
    st.session_state.users.items(),
    key=lambda x: x[1],
    reverse=True
)

for name,balance in sorted_players[:5]:
    st.sidebar.write(f"{name} — ${balance}")
