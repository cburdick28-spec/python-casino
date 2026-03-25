import streamlit as st
import random
from collections import Counter
from itertools import combinations
from db import load_db, save_progress, record_game, unlock_achievement, DEV_ACCOUNTS, MAX_SAFE_MONEY

st.set_page_config(page_title="♠️ Texas Hold'em", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
db = load_db()
if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

for k, v in [("th_player",[]),("th_dealer",[]),("th_community",[]),
             ("th_deck",[]),("th_stage","bet"),("th_bet",0),("th_pot",0),("th_result",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

SUITS = ["♠","♥","♦","♣"]
RANKS = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
RANK_VALUES = {r: i for i, r in enumerate(RANKS, 2)}

def build_deck():
    d = [r+s for s in SUITS for r in RANKS]
    random.shuffle(d)
    return d

def card_rank(c): return c[:-1]
def card_suit(c): return c[-1]

def render_cards(hand, hide=False):
    html = ""
    for card in hand:
        if hide:
            html += """<div style="display:inline-block;width:90px;height:130px;border-radius:10px;
            border:2px solid #333;margin:6px;text-align:center;background:#1a1a2e;color:white;
            font-size:40px;padding-top:30px;">🂠</div>"""
        else:
            suit=card_suit(card); rank=card_rank(card)
            color="red" if suit in ["♥","♦"] else "black"
            html += f"""<div style="display:inline-block;width:90px;height:130px;border-radius:10px;
            border:2px solid #333;margin:6px;text-align:center;background:white;color:{color};
            font-size:22px;padding-top:8px;"><div>{rank}</div><div style="font-size:36px">{suit}</div></div>"""
    st.markdown(html, unsafe_allow_html=True)

def score_hand(hand):
    ranks = sorted([RANK_VALUES[card_rank(c)] for c in hand], reverse=True)
    suits = [card_suit(c) for c in hand]
    rank_names = [card_rank(c) for c in hand]
    counts = Counter(ranks)
    freq = sorted(counts.values(), reverse=True)
    is_flush = len(set(suits)) == 1
    is_straight = len(set(ranks)) == 5 and (max(ranks) - min(ranks) == 4)
    if set(rank_names) == {"A","2","3","4","5"}:
        is_straight = True; ranks = [5,4,3,2,1]
    if is_straight and is_flush:
        return (9,)+tuple(ranks) if max(ranks)==14 else (8,)+tuple(ranks)
    if freq[0]==4:
        quad=[r for r,c in counts.items() if c==4][0]
        return (7,quad)+tuple(sorted([r for r,c in counts.items() if c!=4],reverse=True))
    if freq[0]==3 and freq[1]==2:
        return (6,max(r for r,c in counts.items() if c==3),max(r for r,c in counts.items() if c==2))
    if is_flush: return (5,)+tuple(ranks)
    if is_straight: return (4,)+tuple(ranks)
    if freq[0]==3:
        trio=max(r for r,c in counts.items() if c==3)
        return (3,trio)+tuple(sorted([r for r,c in counts.items() if c!=3],reverse=True))
    if freq[0]==2 and freq[1]==2:
        pairs=sorted([r for r,c in counts.items() if c==2],reverse=True)
        return (2,)+tuple(pairs)+tuple(sorted([r for r,c in counts.items() if c==1],reverse=True))
    if freq[0]==2:
        pair=max(r for r,c in counts.items() if c==2)
        return (1,pair)+tuple(sorted([r for r,c in counts.items() if c!=2],reverse=True))
    return (0,)+tuple(ranks)

def evaluate_hand(cards):
    return max(score_hand(list(combo)) for combo in combinations(cards,5))

HAND_NAMES = {9:"Royal Flush",8:"Straight Flush",7:"Four of a Kind",6:"Full House",
              5:"Flush",4:"Straight",3:"Three of a Kind",2:"Two Pair",1:"Pair",0:"High Card"}

def hand_name(score): return HAND_NAMES.get(score[0],"High Card")

def action_buttons(next_stage, key_suffix):
    money = st.session_state.money
    col1, col2, col3 = st.columns(3)
    with col1:
        label = "✅ Check (Showdown)" if next_stage=="result" else "✅ Check"
        if st.button(label, key=f"check_{key_suffix}"):
            st.session_state.th_stage = next_stage; st.rerun()
    with col2:
        max_raise = max(1, min(money, MAX_SAFE_MONEY))
        raise_amt = st.number_input("Raise", min_value=1, max_value=max_raise,
                                    value=min(5,max_raise), step=1, key=f"raise_amt_{key_suffix}")
        if st.button("💰 Raise", key=f"raise_{key_suffix}"):
            st.session_state.th_pot += raise_amt
            st.session_state.th_bet += raise_amt
            st.session_state.money -= raise_amt
            save_progress()
            st.session_state.th_stage = next_stage; st.rerun()
    with col3:
        if st.button("❌ Fold", key=f"fold_{key_suffix}"):
            st.session_state.th_result = ("fold", st.session_state.th_bet, "", "")
            st.session_state.th_stage = "bet"; st.rerun()

money = st.session_state.money
st.title("♠️ Texas Hold'em Poker")
st.caption("You vs the Dealer — best 5-card hand from 2 hole cards + 5 community cards wins!")
st.write(f"**Balance:** ${money:,}")

if money <= 0:
    st.error("You're out of money! Claim your daily reward on the main page.")
    st.stop()

if st.session_state.th_result:
    outcome, net, pname, dname = st.session_state.th_result
    if outcome=="win": st.success(f"🏆 You win! **{pname}** beats dealer's **{dname}** — +${net:,}")
    elif outcome=="lose": st.error(f"Dealer wins with **{dname}** over your **{pname}** — -${net:,}")
    elif outcome=="fold": st.error(f"You folded — lost ${net:,}")
    else: st.info(f"Chop! Both have **{pname}** — bet returned")
    st.session_state.th_result = None

stage = st.session_state.th_stage

if stage == "bet":
    bet = st.number_input("Ante", min_value=1, max_value=min(money, MAX_SAFE_MONEY), value=min(10,money), step=1)
    if st.button("Deal"):
        deck = build_deck()
        st.session_state.th_deck = deck
        st.session_state.th_player = [deck.pop(), deck.pop()]
        st.session_state.th_dealer = [deck.pop(), deck.pop()]
        st.session_state.th_community = []
        st.session_state.th_bet = bet
        st.session_state.th_pot = bet * 2
        st.session_state.money -= bet
        save_progress()
        st.session_state.th_stage = "preflop"; st.rerun()

elif stage == "preflop":
    st.subheader("Your Hand"); render_cards(st.session_state.th_player)
    st.subheader("Dealer's Hand"); render_cards(st.session_state.th_dealer, hide=True)
    st.write(f"**Pot:** ${st.session_state.th_pot:,}")
    st.info("Pre-Flop — act before community cards are revealed.")
    action_buttons("flop", "preflop")

elif stage == "flop":
    deck = st.session_state.th_deck
    if len(st.session_state.th_community) == 0:
        st.session_state.th_community = [deck.pop(), deck.pop(), deck.pop()]
    st.subheader("Your Hand"); render_cards(st.session_state.th_player)
    st.subheader("Community Cards (Flop)"); render_cards(st.session_state.th_community)
    st.subheader("Dealer's Hand"); render_cards(st.session_state.th_dealer, hide=True)
    st.write(f"**Pot:** ${st.session_state.th_pot:,}")
    action_buttons("turn", "flop")

elif stage == "turn":
    community = st.session_state.th_community
    if len(community) == 3: community.append(st.session_state.th_deck.pop())
    st.subheader("Your Hand"); render_cards(st.session_state.th_player)
    st.subheader("Community Cards (Turn)"); render_cards(community)
    st.subheader("Dealer's Hand"); render_cards(st.session_state.th_dealer, hide=True)
    st.write(f"**Pot:** ${st.session_state.th_pot:,}")
    action_buttons("river", "turn")

elif stage == "river":
    community = st.session_state.th_community
    if len(community) == 4: community.append(st.session_state.th_deck.pop())
    st.subheader("Your Hand"); render_cards(st.session_state.th_player)
    st.subheader("Community Cards (River)"); render_cards(community)
    st.subheader("Dealer's Hand"); render_cards(st.session_state.th_dealer, hide=True)
    st.write(f"**Pot:** ${st.session_state.th_pot:,}")
    st.info("River — final card. Last chance to act!")
    action_buttons("result", "river")

elif stage == "result":
    community = st.session_state.th_community
    player_hand = st.session_state.th_player
    dealer_hand = st.session_state.th_dealer
    pot = st.session_state.th_pot
    st.subheader("Your Hand"); render_cards(player_hand)
    st.subheader("Community Cards"); render_cards(community)
    st.subheader("Dealer's Hand — Revealed!"); render_cards(dealer_hand)

    player_score = evaluate_hand(player_hand + community)
    dealer_score = evaluate_hand(dealer_hand + community)
    pname = hand_name(player_score)
    dname = hand_name(dealer_score)
    st.markdown(f"**Your best hand:** {pname}")
    st.markdown(f"**Dealer's best hand:** {dname}")

    if player_score > dealer_score:
        net = pot - st.session_state.th_bet
        st.session_state.money += pot
        st.session_state.th_result = ("win", net, pname, dname)
        record_game(user, True, st.session_state.th_bet, pot, "♠️ Poker")
        if pname == "Royal Flush": unlock_achievement(user, "royal_flush")
    elif player_score < dealer_score:
        st.session_state.th_result = ("lose", st.session_state.th_bet, pname, dname)
        record_game(user, False, st.session_state.th_bet, 0, "♠️ Poker")
    else:
        st.session_state.money += st.session_state.th_bet
        st.session_state.th_result = ("chop", 0, pname, dname)

    save_progress()
    st.session_state.th_stage = "bet"
    if st.button("Play Again"): st.rerun()
