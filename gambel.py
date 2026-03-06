import streamlit as st
import random

st.set_page_config(page_title="Python Casino", page_icon="🎰")

# -----------------------
# Initialize Player Money
# -----------------------
if "money" not in st.session_state:
    st.session_state.money = 500

st.title("🎰 Python Casino")
st.write("## 💰 Balance:", st.session_state.money)

game = st.sidebar.selectbox(
    "Choose Game",
    ["Slots", "Blackjack", "Roulette"]
)

# ======================
# SLOT MACHINE
# ======================
if game == "Slots":

    st.header("🎰 Slot Machine")

    symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"]

    bet = st.number_input(
        "Bet Amount",
        min_value=1,
        max_value=st.session_state.money,
        value=10
    )

    if st.button("Spin 🎰"):

        s1 = random.choice(symbols)
        s2 = random.choice(symbols)
        s3 = random.choice(symbols)

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"# {s1}")
        col2.markdown(f"# {s2}")
        col3.markdown(f"# {s3}")

        if s1 == s2 == s3:
            win = bet * 5
            st.session_state.money += win
            st.success(f"JACKPOT! You won ${win}")

        elif s1 == s2 or s2 == s3 or s1 == s3:
            win = bet * 2
            st.session_state.money += win
            st.success(f"You won ${win}")

        else:
            st.session_state.money -= bet
            st.error(f"You lost ${bet}")

# ======================
# BLACKJACK
# ======================
if game == "Blackjack":

    st.header("🃏 Blackjack")

    cards = [2,3,4,5,6,7,8,9,10,10,10,10,11]

    if "player" not in st.session_state:
        st.session_state.player = []
        st.session_state.dealer = []

    def deal_card():
        return random.choice(cards)

    if st.button("Start Game"):

        st.session_state.player = [deal_card(), deal_card()]
        st.session_state.dealer = [deal_card(), deal_card()]

    if st.session_state.player:

        st.write("### Your Cards:", st.session_state.player)
        st.write("Total:", sum(st.session_state.player))

        st.write("### Dealer Card:", st.session_state.dealer[0])

        bet = st.number_input(
            "Bet",
            min_value=1,
            max_value=st.session_state.money,
            value=20
        )

        if st.button("Hit"):
            st.session_state.player.append(deal_card())

        if st.button("Stand"):

            while sum(st.session_state.dealer) < 17:
                st.session_state.dealer.append(deal_card())

            st.write("Dealer Cards:", st.session_state.dealer)
            st.write("Dealer Total:", sum(st.session_state.dealer))

            player_total = sum(st.session_state.player)
            dealer_total = sum(st.session_state.dealer)

            if player_total > 21:
                st.session_state.money -= bet
                st.error("Bust! You lose")

            elif dealer_total > 21 or player_total > dealer_total:
                st.session_state.money += bet
                st.success("You win!")

            elif player_total == dealer_total:
                st.warning("Push (tie)")

            else:
                st.session_state.money -= bet
                st.error("Dealer wins")

# ======================
# ROULETTE
# ======================
if game == "Roulette":

    st.header("🎡 Roulette")

    bet_type = st.selectbox(
        "Choose Bet Type",
        ["Number", "Red", "Black"]
    )

    bet = st.number_input(
        "Bet Amount",
        min_value=1,
        max_value=st.session_state.money,
        value=10
    )

    if bet_type == "Number":
        chosen_number = st.number_input("Pick a number (0-36)", 0, 36)

    if st.button("Spin Wheel 🎡"):

        result = random.randint(0, 36)

        red_numbers = {
            1,3,5,7,9,12,14,16,18,19,
            21,23,25,27,30,32,34,36
        }

        if result == 0:
            color = "Green"
        elif result in red_numbers:
            color = "Red"
        else:
            color = "Black"

        st.write(f"### Result: {result} {color}")

        if bet_type == "Number":
            if result == chosen_number:
                win = bet * 35
                st.session_state.money += win
                st.success(f"You won ${win}")
            else:
                st.session_state.money -= bet
                st.error("You lost")

        elif bet_type == "Red":
            if color == "Red":
                win = bet * 2
                st.session_state.money += win
                st.success(f"You won ${win}")
            else:
                st.session_state.money -= bet
                st.error("You lost")

        elif bet_type == "Black":
            if color == "Black":
                win = bet * 2
                st.session_state.money += win
                st.success(f"You won ${win}")
            else:
                st.session_state.money -= bet
                st.error("You lost")

# ======================
# RESET
# ======================

st.sidebar.markdown("---")

if st.sidebar.button("Reset Balance"):
    st.session_state.money = 500
    st.success("Balance Reset")