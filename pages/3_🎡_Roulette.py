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

RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

def get_color(n):
    if n == 0: return "Green"
    return "Red" if n in RED_NUMBERS else "Black"

# Session state
if "rou_result" not in st.session_state:
    st.session_state.rou_result = None
if "rou_pending" not in st.session_state:
    st.session_state.rou_pending = False
if "rou_bet" not in st.session_state:
    st.session_state.rou_bet = 0
if "rou_choice" not in st.session_state:
    st.session_state.rou_choice = None
if "rou_num" not in st.session_state:
    st.session_state.rou_num = None

# Roulette wheel order (standard European)
WHEEL_ORDER = [0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,
               24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26]

def build_wheel_html(target_number, should_spin):
    spin_js = "false"
    if should_spin:
        spin_js = "true"

    return f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin:0; background:transparent; display:flex; justify-content:center;
         align-items:center; flex-direction:column; font-family:Arial,sans-serif; }}
  #wrap {{ position:relative; width:320px; height:320px; margin:0 auto; }}
  #pointer {{
    position:absolute; top:50%; right:-22px;
    transform:translateY(-50%);
    width:0; height:0;
    border-top:13px solid transparent;
    border-bottom:13px solid transparent;
    border-right:30px solid #FFD700;
    filter: drop-shadow(0 0 6px #FFD700);
  }}
  #resultBox {{
    text-align:center; font-size:24px; font-weight:bold;
    color:white; margin-top:16px; min-height:40px;
  }}
</style>
</head>
<body>
<div id="wrap">
  <canvas id="c" width="320" height="320"></canvas>
  <div id="pointer"></div>
</div>
<div id="resultBox" id="resultBox">🎡 Place your bet and spin!</div>

<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
const cx = 160, cy = 160, R = 148;

const numbers = {WHEEL_ORDER};
const redSet = new Set([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]);
const target = {target_number};
const doSpin = {spin_js};

function sliceColor(n) {{
  if (n === 0) return '#009900';
  return redSet.has(n) ? '#cc1100' : '#111111';
}}

function drawWheel(angle) {{
  ctx.clearRect(0, 0, 320, 320);
  const slice = (2 * Math.PI) / numbers.length;

  for (let i = 0; i < numbers.length; i++) {{
    const a0 = angle + i * slice;
    const a1 = a0 + slice;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, R, a0, a1);
    ctx.closePath();
    ctx.fillStyle = sliceColor(numbers[i]);
    ctx.fill();
    ctx.strokeStyle = '#555';
    ctx.lineWidth = 0.8;
    ctx.stroke();

    // label
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(a0 + slice / 2);
    ctx.translate(R - 18, 0);
    ctx.rotate(Math.PI / 2);
    ctx.fillStyle = 'white';
    ctx.font = 'bold 9px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(numbers[i], 0, 3);
    ctx.restore();
  }}

  // gold ring
  ctx.beginPath();
  ctx.arc(cx, cy, R, 0, 2*Math.PI);
  ctx.strokeStyle = '#FFD700';
  ctx.lineWidth = 5;
  ctx.stroke();

  // center hub
  ctx.beginPath();
  ctx.arc(cx, cy, 18, 0, 2*Math.PI);
  ctx.fillStyle = '#FFD700';
  ctx.fill();
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();
}}

let currentAngle = 0;
drawWheel(currentAngle);

if (doSpin) {{
  // Find where the target number sits on the wheel
  const idx = numbers.indexOf(target);
  const slice = (2 * Math.PI) / numbers.length;

  // The pointer is on the RIGHT side (angle = 0).
  // We need the target slice center to land at angle 0.
  // Slice i starts at: currentAngle + i*slice
  // We want: currentAngle + idx*slice + slice/2 = 0 (mod 2pi)
  // So finalAngle = -(idx*slice + slice/2)
  const targetFinalAngle = -(idx * slice + slice / 2);

  // Add several full rotations for effect
  const spins = 6 + Math.random() * 3;
  const finalAngle = targetFinalAngle - spins * 2 * Math.PI;

  const duration = 5000;
  const startAngle = currentAngle;
  const startTime = performance.now();

  document.getElementById('resultBox').textContent = '🎡 Spinning...';

  function easeOut(t) {{
    return 1 - Math.pow(1 - t, 4);
  }}

  function animate(now) {{
    const t = Math.min((now - startTime) / duration, 1);
    currentAngle = startAngle + (finalAngle - startAngle) * easeOut(t);
    drawWheel(currentAngle);

    if (t < 1) {{
      requestAnimationFrame(animate);
    }} else {{
      // Snap exactly
      currentAngle = finalAngle;
      drawWheel(currentAngle);
      const color = target === 0 ? 'Green' : (redSet.has(target) ? 'Red' : 'Black');
      const emoji = color === 'Red' ? '🔴' : color === 'Green' ? '🟢' : '⚫';
      document.getElementById('resultBox').innerHTML = emoji + ' <b>' + target + ' — ' + color + '</b>';
    }}
  }}

  requestAnimationFrame(animate);
}}
</script>
</body>
</html>
""".replace("{WHEEL_ORDER}", str(WHEEL_ORDER))

# Show the wheel (pre-spin state or after spin)
current_target = st.session_state.rou_result if st.session_state.rou_result is not None else 0
wheel_placeholder = st.empty()
wheel_placeholder.components.v1.html(
    build_wheel_html(current_target, False), height=420
)

if st.button("🎡 Spin the Wheel!"):
    # Lock in the bet and choice NOW before spinning
    spin_num = random.randint(0, 36)
    st.session_state.rou_result = spin_num
    st.session_state.rou_bet = bet
    st.session_state.rou_choice = choice
    st.session_state.rou_num = num

    # Show animated wheel with the correct target
    wheel_placeholder.empty()
    st.components.v1.html(build_wheel_html(spin_num, True), height=420)

    # Wait for animation to finish
    time.sleep(5.8)

    # Show result
    color = get_color(spin_num)
    st.markdown(f"### 🎯 Result: **{spin_num} — {color}**")

    won = False
    payout = 0

    if choice == "Number" and spin_num == num:
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
