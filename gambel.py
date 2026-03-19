import streamlit as st
import random

st.set_page_config(page_title="Python Casino", page_icon="🎰")

# -----------------------
# Initialize Player Money
# -----------------------
if "money" not in st.session_state:
    st.session_state.money = 500


def normalize_money():
    st.session_state.money = int(st.session_state.money)

st.title("🎰 Python Casino")
normalize_money()
st.write("## 💰 Balance:", st.session_state.money)

if st.session_state.money <= 0:
    st.warning("You're out of money. Reset your balance to keep playing.")

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

    if st.session_state.money <= 0:
        st.info("Slots are unavailable until you reset your balance.")
    else:
        bet = st.number_input(
            "Bet Amount",
            min_value=1,
            max_value=st.session_state.money,
            value=min(10, st.session_state.money)
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
    if "blackjack_bet" not in st.session_state:
        st.session_state.blackjack_bet = 0

    def deal_card():
        return random.choice(cards)

    def hand_total(hand):
        total = sum(hand)
        aces = hand.count(11)

        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    if st.session_state.money <= 0 and not st.session_state.player:
        st.info("Blackjack is unavailable until you reset your balance.")
    elif st.session_state.money < 2 and not st.session_state.player:
        st.info("Blackjack requires at least $2 because bets must be even-dollar amounts.")
    elif not st.session_state.player:
        max_blackjack_bet = st.session_state.money if st.session_state.money % 2 == 0 else st.session_state.money - 1
        bet = st.number_input(
            "Bet",
            min_value=2,
            max_value=max_blackjack_bet,
            value=min(20, max_blackjack_bet),
            step=2
        )

        if st.button("Start Game"):
            st.session_state.player = [deal_card(), deal_card()]
            st.session_state.dealer = [deal_card(), deal_card()]
            st.session_state.blackjack_bet = bet

    if st.session_state.player:
        player_total = hand_total(st.session_state.player)

        st.write("### Your Cards:", st.session_state.player)
        st.write("Total:", player_total)

        st.write("### Dealer Card:", st.session_state.dealer[0])
        st.write("Locked Bet:", st.session_state.blackjack_bet)

        if player_total == 21 and len(st.session_state.player) == 2:
            dealer_total = hand_total(st.session_state.dealer)
            st.write("Dealer Cards:", st.session_state.dealer)
            st.write("Dealer Total:", dealer_total)

            if dealer_total == 21 and len(st.session_state.dealer) == 2:
                st.warning("Both you and the dealer have blackjack. Push!")
            else:
                blackjack_bonus = st.session_state.blackjack_bet // 2
                st.session_state.money += st.session_state.blackjack_bet + blackjack_bonus
                st.success("Blackjack! You win 3:2.")

            st.session_state.player = []
            st.session_state.dealer = []
            st.session_state.blackjack_bet = 0

        elif player_total > 21:
            st.session_state.money -= st.session_state.blackjack_bet
            st.error("Bust! You lose")
            st.session_state.player = []
            st.session_state.dealer = []
            st.session_state.blackjack_bet = 0

        elif st.button("Hit"):
            st.session_state.player.append(deal_card())
            player_total = hand_total(st.session_state.player)
            st.write("### Your Cards:", st.session_state.player)
            st.write("Total:", player_total)

            if player_total > 21:
                st.session_state.money -= st.session_state.blackjack_bet
                st.error("Bust! You lose")
                st.session_state.player = []
                st.session_state.dealer = []
                st.session_state.blackjack_bet = 0

        elif st.button("Stand"):

            while hand_total(st.session_state.dealer) < 17:
                st.session_state.dealer.append(deal_card())

            player_total = hand_total(st.session_state.player)
            dealer_total = hand_total(st.session_state.dealer)

            st.write("Dealer Cards:", st.session_state.dealer)
            st.write("Dealer Total:", dealer_total)

            if player_total > 21:
                st.session_state.money -= st.session_state.blackjack_bet
                st.error("Bust! You lose")

            elif dealer_total > 21 or player_total > dealer_total:
                st.session_state.money += st.session_state.blackjack_bet
                st.success("You win!")

            elif player_total == dealer_total:
                st.warning("Push (tie)")

            else:
                st.session_state.money -= st.session_state.blackjack_bet
                st.error("Dealer wins")

            st.session_state.player = []
            st.session_state.dealer = []
            st.session_state.blackjack_bet = 0

# ======================
# ROULETTE
# ======================
if game == "Roulette":

    st.header("🎡 Roulette")

    bet_type = st.selectbox(
        "Choose Bet Type",
        ["Number", "Red", "Black"]
    )

    if st.session_state.money <= 0:
        st.info("Roulette is unavailable until you reset your balance.")
    else:
        bet = st.number_input(
            "Bet Amount",
            min_value=1,
            max_value=st.session_state.money,
            value=min(10, st.session_state.money)
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
                    win = bet
                    st.session_state.money += win
                    st.success(f"You won ${win}")
                else:
                    st.session_state.money -= bet
                    st.error("You lost")

            elif bet_type == "Black":
                if color == "Black":
                    win = bet
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
    st.session_state.player = []
    st.session_state.dealer = []
    st.session_state.blackjack_bet = 0
    st.success("Balance Reset")
