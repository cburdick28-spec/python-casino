import random
import streamlit as st
from db import load_db, save_progress, record_game, unlock_achievement, DEV_ACCOUNTS, MAX_SAFE_MONEY

st.set_page_config(page_title="🃏 Blackjack", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
_ = load_db()

if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

for k, v in [
    ("bj_hands", []),
    ("bj_dealer", []),
    ("bj_active", False),
    ("bj_result", []),
    ("bj_current_hand", 0),
]:
    if k not in st.session_state:
        st.session_state[k] = v

suits = ["♠", "♥", "♦", "♣"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def draw_card():
    return random.choice(ranks) + random.choice(suits)


def card_value(card):
    rank = card[:-1]
    if rank in ["J", "Q", "K"]:
        return 10
    if rank == "A":
        return 11
    return int(rank)


def hand_value(hand):
    total = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c[:-1] == "A")
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21


def can_split(hand):
    return len(hand) == 2 and hand[0][:-1] == hand[1][:-1]


def can_cover(extra):
    total_exposure = sum(h["bet"] for h in st.session_state.bj_hands)
    return total_exposure + extra <= st.session_state.money


def render_cards(hand):
    html = ""
    for card in hand:
        suit = card[-1]
        rank = card[:-1]
        color = "red" if suit in ["♥", "♦"] else "black"
        html += f"""<div style="display:inline-block;width:92px;height:130px;border-radius:10px;
        border:2px solid #333;margin:6px;text-align:center;background:white;color:{color};
        font-size:22px;padding-top:10px;"><div>{rank}</div><div style="font-size:34px">{suit}</div></div>"""
    st.markdown(html, unsafe_allow_html=True)


def settle_round():
    hands = st.session_state.bj_hands
    dealer = st.session_state.bj_dealer

    if not all(hand_value(h["cards"]) > 21 for h in hands):
        while hand_value(dealer) < 17:
            dealer.append(draw_card())

    dealer_total = hand_value(dealer)
    round_messages = []

    for idx, hand in enumerate(hands, start=1):
        cards = hand["cards"]
        bet = hand["bet"]
        total = hand_value(cards)
        label = f"Hand {idx}"

        if hand.get("natural_blackjack"):
            if is_blackjack(dealer):
                round_messages.append(("push", f"{label}: Push (both blackjack)."))
            else:
                win = int(bet * 1.5)
                st.session_state.money += win
                round_messages.append(("win", f"{label}: Blackjack! +${win:,}"))
                record_game(user, True, bet, win, "🃏 Blackjack")
            continue

        if total > 21:
            st.session_state.money -= bet
            round_messages.append(("lose", f"{label}: Bust. -${bet:,}"))
            record_game(user, False, bet, 0, "🃏 Blackjack")
        elif dealer_total > 21 or total > dealer_total:
            st.session_state.money += bet
            round_messages.append(("win", f"{label}: Win! +${bet:,}"))
            record_game(user, True, bet, bet, "🃏 Blackjack")
        elif total < dealer_total:
            st.session_state.money -= bet
            round_messages.append(("lose", f"{label}: Dealer wins. -${bet:,}"))
            record_game(user, False, bet, 0, "🃏 Blackjack")
        else:
            round_messages.append(("push", f"{label}: Push — bet returned."))

    st.session_state.bj_result = round_messages
    st.session_state.bj_active = False
    st.session_state.bj_current_hand = 0
    save_progress()


def finish_or_advance_hand():
    next_idx = st.session_state.bj_current_hand + 1
    while next_idx < len(st.session_state.bj_hands) and st.session_state.bj_hands[next_idx]["finished"]:
        next_idx += 1

    if next_idx >= len(st.session_state.bj_hands):
        settle_round()
    else:
        st.session_state.bj_current_hand = next_idx


money = st.session_state.money
st.title("🃏 Blackjack")
st.write(f"**Balance:** ${money:,}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

if "bj_bet_input" not in st.session_state:
    st.session_state.bj_bet_input = min(10, money)
else:
    st.session_state.bj_bet_input = min(st.session_state.bj_bet_input, min(money, MAX_SAFE_MONEY))

bet = st.number_input(
    "Bet",
    min_value=1,
    max_value=min(money, MAX_SAFE_MONEY),
    value=st.session_state.bj_bet_input,
    step=1,
    key="bj_bet_input",
)

if st.session_state.bj_result:
    for result_type, message in st.session_state.bj_result:
        if result_type == "win":
            st.success(message)
        elif result_type == "lose":
            st.error(message)
        else:
            st.info(message)
    st.session_state.bj_result = []

if not st.session_state.bj_active:
    if st.button("Deal"):
        locked_bet = int(bet)
        player_cards = [draw_card(), draw_card()]
        dealer_cards = [draw_card(), draw_card()]

        st.session_state.bj_hands = [{
            "cards": player_cards,
            "bet": locked_bet,
            "finished": False,
            "doubled": False,
            "natural_blackjack": False,
        }]
        st.session_state.bj_dealer = dealer_cards
        st.session_state.bj_current_hand = 0
        st.session_state.bj_active = True

        if is_blackjack(player_cards):
            st.session_state.bj_hands[0]["natural_blackjack"] = True
            unlock_achievement(user, "blackjack_ace")

        if is_blackjack(player_cards) or is_blackjack(dealer_cards):
            st.session_state.bj_hands[0]["finished"] = True
            settle_round()

        st.rerun()

if st.session_state.bj_active:
    dealer = st.session_state.bj_dealer
    hands = st.session_state.bj_hands
    current = st.session_state.bj_current_hand
    active_hand = hands[current]

    st.subheader("Dealer Shows")
    render_cards([dealer[0]])

    st.markdown("---")
    for idx, hand in enumerate(hands, start=1):
        marker = " 👉" if (idx - 1) == current and not hand["finished"] else ""
        st.subheader(f"Your Hand {idx}{marker}")
        render_cards(hand["cards"])
        st.write(f"Total: {hand_value(hand['cards'])} | Bet: ${hand['bet']:,}")

    can_act = not active_hand["finished"]
    can_double = can_act and len(active_hand["cards"]) == 2 and not active_hand["doubled"] and can_cover(active_hand["bet"])
    can_split_now = can_act and can_split(active_hand["cards"]) and can_cover(active_hand["bet"]) and len(hands) < 4

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("Hit", disabled=not can_act):
            active_hand["cards"].append(draw_card())
            if hand_value(active_hand["cards"]) > 21:
                active_hand["finished"] = True
                finish_or_advance_hand()
            st.rerun()

    with c2:
        if st.button("Stand", disabled=not can_act):
            active_hand["finished"] = True
            finish_or_advance_hand()
            st.rerun()

    with c3:
        if st.button("Double", disabled=not can_double):
            active_hand["bet"] *= 2
            active_hand["doubled"] = True
            active_hand["cards"].append(draw_card())
            active_hand["finished"] = True
            finish_or_advance_hand()
            st.rerun()

    with c4:
        if st.button("Split", disabled=not can_split_now):
            first, second = active_hand["cards"]
            original_bet = active_hand["bet"]
            hand_one = {
                "cards": [first, draw_card()],
                "bet": original_bet,
                "finished": False,
                "doubled": False,
                "natural_blackjack": False,
            }
            hand_two = {
                "cards": [second, draw_card()],
                "bet": original_bet,
                "finished": False,
                "doubled": False,
                "natural_blackjack": False,
            }
            hands[current:current + 1] = [hand_one, hand_two]
            st.session_state.bj_hands = hands
            st.session_state.bj_current_hand = current
            st.rerun()

    if can_act:
        if can_split_now:
            st.caption("Split is available for matching ranks.")
        if can_double:
            st.caption("Double is available on your first action for this hand.")
