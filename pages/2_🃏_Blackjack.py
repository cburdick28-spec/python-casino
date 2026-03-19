import streamlit as st
import random
from db import load_db, save_db, save_progress, record_game, unlock_achievement, DEV_ACCOUNTS

st.set_page_config(page_title="🃏 Blackjack", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
db = load_db()

if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

for k, v in [("bj_player", []), ("bj_dealer", []), ("bj_active", False), ("bj_result", None), ("bj_bet", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

suits = ["♠", "♥", "♦", "♣"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def draw_card():
    return random.choice(ranks) + random.choice(suits)

def card_value(card):
    r = card[:-1]
    if r in ["J", "Q", "K"]: return 10
    if r == "A": return 11
    return int(r)

def hand_value(hand):
    total = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c[:-1] == "A")
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
        html += f"""<div style="display:inline-block;width:100px;height:140px;
        border-radius:10px;border:2px solid #333;margin:6px;text-align:center;
        background:white;color:{color};font-size:24px;padding-top:10px;">
        <div>{rank}</div><div style="font-size:40px">{suit}</div></div>"""
    st.markdown(html, unsafe_allow_html=True)

money = st.session_state.money
st.title("🃏 Blackjack")
st.write(f"**Balance:** ${money:,}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

bet = st.number_input("Bet", min_value=1, max_value=money, value=min(10, money), step=1)

if st.session_state.bj_result:
    r, amt, msg = st.session_state.bj_result
    if r == "win":
        st.success(f"{msg}  +${amt:,}")
    elif r == "lose":
        st.error(f"{msg}  -${amt:,}")
    else:
        st.info("Push — bet returned")
    st.session_state.bj_result = None

if not st.session_state.bj_active:
    if st.button("Deal"):
        st.session_state.bj_bet = bet
        st.session_state.bj_player = [draw_card(), draw_card()]
        st.session_state.bj_dealer = [draw_card(), draw_card()]
        st.session_state.bj_active = True
        # Check for natural blackjack
        if hand_value(st.session_state.bj_player) == 21:
            unlock_achievement(user, "blackjack_ace")
        st.rerun()

if st.session_state.bj_active:
    player = st.session_state.bj_player
    dealer = st.session_state.bj_dealer

    st.subheader("Your Hand")
    render_cards(player)
    st.write(f"Total: {hand_value(player)}")

    st.subheader("Dealer Shows")
    render_cards([dealer[0]])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Hit"):
            new_card = draw_card()
            player.append(new_card)
            if hand_value(player) > 21:
                st.session_state.money -= st.session_state.bj_bet
                st.session_state.bj_result = ("lose", st.session_state.bj_bet, f"Bust! Drew {new_card}")
                st.session_state.bj_active = False
                record_game(user, False, st.session_state.bj_bet, 0)
                save_progress()
            st.rerun()

    with col2:
        if st.button("Stand"):
            while hand_value(dealer) < 17:
                dealer.append(draw_card())

            pt = hand_value(player)
            dt = hand_value(dealer)

            if dt > 21 or pt > dt:
                st.session_state.money += st.session_state.bj_bet
                st.session_state.bj_result = ("win", st.session_state.bj_bet, "You win!")
                record_game(user, True, st.session_state.bj_bet, st.session_state.bj_bet)
            elif pt < dt:
                st.session_state.money -= st.session_state.bj_bet
                st.session_state.bj_result = ("lose", st.session_state.bj_bet, "Dealer wins")
                record_game(user, False, st.session_state.bj_bet, 0)
            else:
                st.session_state.bj_result = ("push", 0, "Push")

            st.session_state.bj_active = False
            save_progress()
            st.rerun()
