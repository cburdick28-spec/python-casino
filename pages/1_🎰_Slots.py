import streamlit as st
import random
import time
from db import load_db, save_db, save_progress, record_game, unlock_achievement, DEV_ACCOUNTS

st.set_page_config(page_title="🎰 Slots", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
db = load_db()

if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

money = st.session_state.money

st.title("🎰 Slots")
st.header(f"💰 Progressive Jackpot: ${db['jackpot']:,}")
st.write(f"**Balance:** ${money:,}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

bet = st.number_input("Bet", min_value=1, max_value=money, value=min(10, money), step=1)

SYMBOLS = ["🍒", "🍋", "🍉", "⭐", "💎", "7️⃣"]

# Pre-pick the result before animating so they always match
if "slots_result" not in st.session_state:
    st.session_state.slots_result = None
if "slots_spun" not in st.session_state:
    st.session_state.slots_spun = False
if "slots_bet" not in st.session_state:
    st.session_state.slots_bet = 0

spin_clicked = st.button("🎰 Spin!")

if spin_clicked:
    st.session_state.slots_result = [random.choice(SYMBOLS) for _ in range(3)]
    st.session_state.slots_spun = True
    st.session_state.slots_bet = bet

result = st.session_state.slots_result if st.session_state.slots_result else ["🎰", "🎰", "🎰"]
do_spin = "true" if spin_clicked else "false"
r0, r1, r2 = result[0], result[1], result[2]

# Build animated slots HTML
slots_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{
    margin: 0;
    background: transparent;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    font-family: Arial, sans-serif;
  }}
  #machine {{
    background: linear-gradient(145deg, #1a1a2e, #16213e);
    border: 4px solid #FFD700;
    border-radius: 20px;
    padding: 30px 40px;
    box-shadow: 0 0 30px #FFD70066;
    text-align: center;
  }}
  #title {{
    color: #FFD700;
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 20px;
    letter-spacing: 3px;
  }}
  #reels {{
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-bottom: 20px;
  }}
  .reel-window {{
    width: 100px;
    height: 120px;
    overflow: hidden;
    border: 3px solid #FFD700;
    border-radius: 12px;
    background: #0d0d1a;
    position: relative;
  }}
  .reel {{
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
  }}
  .symbol {{
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 56px;
    flex-shrink: 0;
  }}
  #result-line {{
    position: absolute;
    top: 50%;
    left: -4px;
    right: -4px;
    height: 4px;
    background: #FFD700;
    transform: translateY(-50%);
    opacity: 0.6;
    pointer-events: none;
  }}
  #resultBox {{
    font-size: 22px;
    font-weight: bold;
    color: white;
    min-height: 36px;
    margin-top: 10px;
  }}
</style>
</head>
<body>
<div id="machine">
  <div id="title">🎰 SLOTS 🎰</div>
  <div id="reels">
    <div class="reel-window" id="w0">
      <div class="reel" id="r0"></div>
      <div id="result-line"></div>
    </div>
    <div class="reel-window" id="w1">
      <div class="reel" id="r1"></div>
      <div id="result-line"></div>
    </div>
    <div class="reel-window" id="w2">
      <div class="reel" id="r2"></div>
      <div id="result-line"></div>
    </div>
  </div>
  <div id="resultBox">🎰 Press Spin!</div>
</div>

<script>
const symbols = ["🍒","🍋","🍉","⭐","💎","7️⃣"];
const finalSymbols = ["{r0}", "{r1}", "{r2}"];
const doSpin = {do_spin};

// Build each reel with many symbols ending with the correct one
function buildReel(reelEl, finalSymbol, extraRows) {{
  reelEl.innerHTML = '';
  // Add random symbols on top for spinning effect
  for (let i = 0; i < extraRows; i++) {{
    const div = document.createElement('div');
    div.className = 'symbol';
    div.textContent = symbols[Math.floor(Math.random() * symbols.length)];
    reelEl.appendChild(div);
  }}
  // Final symbol at the bottom
  const div = document.createElement('div');
  div.className = 'symbol';
  div.textContent = finalSymbol;
  reelEl.appendChild(div);
}}

const extraRows = 20;

// Build all reels
for (let i = 0; i < 3; i++) {{
  const reel = document.getElementById('r' + i);
  buildReel(reel, finalSymbols[i], extraRows);
  // Start showing first symbol
  reel.style.top = '0px';
}}

if (doSpin) {{
  // Each reel starts at top=0 and needs to scroll down to show final symbol
  // Total height = (extraRows) * 120px (so final symbol is at extraRows * 120)
  const totalScroll = extraRows * 120;
  const durations = [2500, 3000, 3500]; // staggered stop times

  document.getElementById('resultBox').textContent = '🎰 Spinning...';

  for (let i = 0; i < 3; i++) {{
    const reel = document.getElementById('r' + i);
    const duration = durations[i];
    const startTime = performance.now();

    (function animateReel(reelEl, dur) {{
      function easeOut(t) {{ return 1 - Math.pow(1 - t, 3); }}

      function frame(now) {{
        const t = Math.min((now - startTime) / dur, 1);
        const pos = -totalScroll * easeOut(t);
        reelEl.style.top = pos + 'px';
        if (t < 1) {{
          requestAnimationFrame(frame);
        }}
      }}
      requestAnimationFrame(frame);
    }})(reel, duration);
  }}

  // After all reels stop, show result
  setTimeout(function() {{
    const s0 = finalSymbols[0], s1 = finalSymbols[1], s2 = finalSymbols[2];
    if (s0 === s1 && s1 === s2) {{
      document.getElementById('resultBox').innerHTML = '🎉 <b>JACKPOT! ' + s0 + s1 + s2 + '</b>';
    }} else if (s0 === s1 || s1 === s2) {{
      document.getElementById('resultBox').innerHTML = '✅ <b>Winner! ' + s0 + ' ' + s1 + ' ' + s2 + '</b>';
    }} else {{
      document.getElementById('resultBox').innerHTML = '❌ <b>No match. ' + s0 + ' ' + s1 + ' ' + s2 + '</b>';
    }}
  }}, 3600);
}}
</script>
</body>
</html>"""

st.components.v1.html(slots_html, height=320)

# Handle result after animation
if spin_clicked and st.session_state.slots_spun:
    time.sleep(4)  # wait for all reels to finish

    r = st.session_state.slots_result
    locked_bet = st.session_state.slots_bet

    db = load_db()
    jackpot = db["jackpot"]
    won = False
    payout = 0

    if r[0] == r[1] == r[2]:
        win = locked_bet * st.session_state.get("jackpot_odds", 6)
        st.success(f"🎰 JACKPOT! +${win:,}")
        st.success(f"💰 Progressive Jackpot Won: ${jackpot:,}")
        st.session_state.money += win + jackpot
        payout = win + jackpot
        db["jackpot"] = 1000
        won = True
        unlock_achievement(user, "jackpot")

    elif r[0] == r[1] or r[1] == r[2]:
        win = locked_bet * 2
        st.success(f"✅ Winner! +${win:,}")
        st.session_state.money += win
        payout = win
        won = True

    else:
        st.error(f"❌ No match. -${locked_bet:,}")
        st.session_state.money -= locked_bet
        db["jackpot"] += int(locked_bet * 0.25)

    save_db(db)
    record_game(user, won, locked_bet, payout)
    save_progress()
    st.write(f"**New Balance:** ${st.session_state.money:,}")
    st.session_state.slots_spun = False
