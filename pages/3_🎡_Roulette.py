import streamlit as st
import random
import time
from db import load_db, save_db, save_progress, record_game, DEV_ACCOUNTS

st.set_page_config(page_title="🎡 Roulette", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
db = load_db()
if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

money = st.session_state.money

st.title("🎡 Roulette")
st.write(f"**Balance:** ${money:,}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

bet = st.number_input("Bet", 1, money, min(10, money))
choice = st.selectbox("Bet on", ["Red", "Black", "Number"])
num = None
if choice == "Number":
    num = int(st.number_input("Pick 0-36", 0, 36))

if "roulette_spun" not in st.session_state:
    st.session_state.roulette_spun = False
if "roulette_number" not in st.session_state:
    st.session_state.roulette_number = 0

RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

def get_color(n):
    if n == 0: return "Green"
    return "Red" if n in RED_NUMBERS else "Black"

spin_clicked = st.button("🎡 Spin the Wheel!")

if spin_clicked:
    st.session_state.roulette_number = random.randint(0, 36)
    st.session_state.roulette_spun = True

spin_result = st.session_state.roulette_number

# Build the animated wheel HTML
wheel_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin: 0; background: transparent; display: flex; justify-content: center; align-items: center; flex-direction: column; }}
  #wheelWrap {{ position: relative; width: 320px; height: 320px; margin: 0 auto; }}
  #wheelCanvas {{ border-radius: 50%; }}
  #pointer {{
    position: absolute;
    top: 50%;
    right: -18px;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-top: 12px solid transparent;
    border-bottom: 12px solid transparent;
    border-right: 28px solid #FFD700;
    filter: drop-shadow(0 0 4px #FFD700);
  }}
  #resultBox {{
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    color: white;
    margin-top: 14px;
    min-height: 36px;
    font-family: Arial, sans-serif;
  }}
</style>
</head>
<body>
<div id="wheelWrap">
  <canvas id="wheelCanvas" width="320" height="320"></canvas>
  <div id="pointer"></div>
</div>
<div id="resultBox">🎡 Spin the wheel!</div>

<script>
const canvas = document.getElementById('wheelCanvas');
const ctx = canvas.getContext('2d');
const cx = 160, cy = 160, r = 150;

const numbers = [0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,
                 24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26];
const redNums = new Set([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]);

function sliceColor(n) {{
  if (n === 0) return '#00aa00';
  return redNums.has(n) ? '#cc2200' : '#111111';
}}

function drawWheel(angle) {{
  ctx.clearRect(0, 0, 320, 320);
  const slice = (2 * Math.PI) / numbers.length;

  for (let i = 0; i < numbers.length; i++) {{
    const start = angle + i * slice;
    const end = start + slice;

    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, r, start, end);
    ctx.closePath();
    ctx.fillStyle = sliceColor(numbers[i]);
    ctx.fill();
    ctx.strokeStyle = '#888';
    ctx.lineWidth = 0.5;
    ctx.stroke();

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(start + slice / 2);
    ctx.translate(r - 20, 0);
    ctx.rotate(Math.PI / 2);
    ctx.fillStyle = 'white';
    ctx.font = 'bold 9px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(numbers[i], 0, 0);
    ctx.restore();
  }}

  // outer ring
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, 2 * Math.PI);
  ctx.strokeStyle = '#FFD700';
  ctx.lineWidth = 4;
  ctx.stroke();

  // center hub
  ctx.beginPath();
  ctx.arc(cx, cy, 16, 0, 2 * Math.PI);
  ctx.fillStyle = '#FFD700';
  ctx.fill();
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();
}}

let currentAngle = 0;
drawWheel(currentAngle);

const targetNumber = {spin_result};
const shouldSpin = {'true' if spin_clicked else 'false'};

if (shouldSpin) {{
  const idx = numbers.indexOf(targetNumber);
  const slice = (2 * Math.PI) / numbers.length;
  // We want the target slice to end up at the right (pointer position = angle 0)
  const targetAngle = -(idx * slice + slice / 2);
  const fullSpins = (6 + Math.random() * 4) * 2 * Math.PI;
  const finalAngle = targetAngle - fullSpins;
  const duration = 5000;
  const startTime = performance.now();
  const startAngle = currentAngle;

  function easeOut(t) {{
    return 1 - Math.pow(1 - t, 4);
  }}

  const resultBox = document.getElementById('resultBox');
  resultBox.textContent = '🎡 Spinning...';

  function animate(now) {{
    const elapsed = now - startTime;
    const t = Math.min(elapsed / duration, 1);
    currentAngle = startAngle + (finalAngle - startAngle) * easeOut(t);
    drawWheel(currentAngle);

    if (t < 1) {{
      requestAnimationFrame(animate);
    }} else {{
      const color = targetNumber === 0 ? 'Green' : (Array.from(new Set([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36])).includes(targetNumber) ? 'Red' : 'Black');
      const colorEmoji = color === 'Red' ? '🔴' : color === 'Green' ? '🟢' : '⚫';
      resultBox.innerHTML = colorEmoji + ' <b>' + targetNumber + ' ' + color + '</b>';
    }}
  }}

  requestAnimationFrame(animate);
}}
</script>
</body>
</html>
"""

st.components.v1.html(wheel_html, height=400)

# Show result and calculate winnings after spin
if st.session_state.roulette_spun and spin_clicked:
    color = get_color(spin_result)

    # wait for animation
    time.sleep(5.5)

    st.markdown(f"### Result: **{spin_result} — {color}**")

    won = False
    payout = 0

    if choice == "Number" and spin_result == num:
        payout = bet * 35
        st.success(f"🎉 Big Win! +${payout:,}")
        st.session_state.money += payout
        won = True
    elif choice == color:
        payout = bet
        st.success(f"✅ Winner! +${bet:,}")
        st.session_state.money += bet
        won = True
    else:
        st.error(f"❌ No win. -${bet:,}")
        st.session_state.money -= bet

    record_game(user, won, bet, payout)
    save_progress()
    st.write(f"**New Balance:** ${st.session_state.money:,}")
    st.session_state.roulette_spun = False
