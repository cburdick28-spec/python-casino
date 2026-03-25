import streamlit as st
import random
import time
from db import load_db, save_progress, record_game, DEV_ACCOUNTS

st.set_page_config(page_title="🎳 Plinko", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
db = load_db()
if user in DEV_ACCOUNTS:
    st.session_state.money = 999999999

money = st.session_state.money
st.title("🎳 Plinko")
st.caption("Drop the ball and watch it bounce through the pegs!")
st.write(f"**Balance:** ${money:,}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

bet = st.number_input("Bet", min_value=1, max_value=money, value=min(10, money), step=1)

ROWS = 12
MULTIPLIERS = [10, 3, 1.5, 1, 0.5, 0.3, 0.2, 0.1, 0.2, 0.3, 0.5, 1, 1.5, 3, 10]
MULTIPLIER_COLORS = {10:"#FFD700",3:"#FF6B35",1.5:"#FF9F1C",1:"#2EC4B6",
                     0.5:"#3D9970",0.3:"#2ECC40",0.2:"#7FDBFF",0.1:"#AAAAAA"}

def get_color(m): return MULTIPLIER_COLORS.get(m, "#888888")

def simulate_path(rows):
    path = []; pos = 0
    for _ in range(rows):
        go_right = random.random() < 0.5
        path.append(go_right)
        if go_right: pos += 1
    return path, pos

for k, v in [("plinko_path", None), ("plinko_slot", None),
             ("plinko_bet", 0), ("plinko_dropped", False)]:
    if k not in st.session_state:
        st.session_state[k] = v

drop_clicked = st.button("🎳 Drop Ball!")
if drop_clicked:
    path, slot = simulate_path(ROWS)
    st.session_state.plinko_path = path
    st.session_state.plinko_slot = slot
    st.session_state.plinko_bet = bet
    st.session_state.plinko_dropped = True

path = st.session_state.plinko_path
slot = st.session_state.plinko_slot
do_drop = "true" if drop_clicked else "false"
path_json = str(path).lower() if path else "[]"
slot_val = slot if slot is not None else -1

# Key trick: use a unique key per drop so the canvas always re-renders fresh
canvas_key = f"plinko_{slot_val}_{drop_clicked}"

plinko_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin:0; background:transparent; display:flex; justify-content:center;
         flex-direction:column; align-items:center; font-family:Arial,sans-serif; }}
  canvas {{ border-radius:12px; }}
  #resultBox {{ font-size:22px; font-weight:bold; color:white;
                margin-top:14px; min-height:36px; text-align:center; }}
</style>
</head>
<body>
<canvas id="c" width="520" height="580"></canvas>
<div id="resultBox">🎳 Drop the ball!</div>
<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
const W = 520, H = 580;
const ROWS = {ROWS};
const MULTS = {MULTIPLIERS};
const path = {path_json};
const doDROP = {do_drop};
const finalSlot = {slot_val};

const PAD = 40;
const boardW = W - PAD * 2;
const boardH = H - 110;
const rowH = boardH / (ROWS + 1);

// Decorative pegs — visual only, evenly spaced
function decoPegX(row, col) {{
  const count = row + 2;
  const spacing = boardW / (count + 1);
  return PAD + spacing * (col + 1);
}}
function decoPegY(row) {{
  return 50 + rowH * (row + 1);
}}

// Invisible physics pegs — triangle grid used for ball path only
function physPegX(row, col) {{
  const count = row + 1;
  const spacing = boardW / (count + 1);
  return PAD + spacing * (col + 1);
}}
function physPegY(row) {{
  return 50 + rowH * (row + 1);
}}

function getMultColor(m) {{
  const colors = {{"10":"#FFD700","3":"#FF6B35","1.5":"#FF9F1C","1":"#2EC4B6",
                   "0.5":"#3D9970","0.3":"#2ECC40","0.2":"#7FDBFF","0.1":"#AAAAAA"}};
  return colors[String(m)] || "#888";
}}

function drawBoard(ballX, ballY, showBall, litSlot) {{
  ctx.clearRect(0, 0, W, H);

  // Background
  ctx.fillStyle = '#0d0d1a';
  ctx.roundRect(0, 0, W, H, 16);
  ctx.fill();

  // Title
  ctx.fillStyle = '#FFD700';
  ctx.font = 'bold 20px Arial';
  ctx.textAlign = 'center';
  ctx.fillText('🎳 PLINKO', W/2, 28);

  // Decorative pegs
  for (let r = 0; r < ROWS; r++) {{
    const count = r + 2;
    for (let c = 0; c < count; c++) {{
      const x = decoPegX(r, c);
      const y = decoPegY(r);
      const grd = ctx.createRadialGradient(x, y, 0, x, y, 8);
      grd.addColorStop(0, '#ffffffcc');
      grd.addColorStop(0.4, '#aaaaaa88');
      grd.addColorStop(1, '#44444400');
      ctx.beginPath(); ctx.arc(x, y, 8, 0, 2*Math.PI);
      ctx.fillStyle = grd; ctx.fill();
      ctx.beginPath(); ctx.arc(x, y, 4, 0, 2*Math.PI);
      ctx.fillStyle = '#cccccc'; ctx.fill();
      ctx.strokeStyle = '#888'; ctx.lineWidth = 1; ctx.stroke();
    }}
  }}

  // Multiplier slots
  const slotCount = MULTS.length;
  const slotW = boardW / slotCount;
  const slotY = H - 65;
  for (let i = 0; i < slotCount; i++) {{
    const sx = PAD + i * slotW;
    const color = getMultColor(MULTS[i]);
    const isLit = (i === litSlot);
    ctx.fillStyle = isLit ? color : color + '55';
    ctx.beginPath(); ctx.roundRect(sx + 2, slotY, slotW - 4, 52, 6); ctx.fill();
    if (isLit) {{
      ctx.shadowColor = color; ctx.shadowBlur = 12;
      ctx.beginPath(); ctx.roundRect(sx + 2, slotY, slotW - 4, 52, 6);
      ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke();
      ctx.shadowBlur = 0;
    }}
    ctx.fillStyle = isLit ? '#000' : '#fff';
    ctx.font = `bold ${{MULTS[i] >= 3 ? 13 : 10}}px Arial`;
    ctx.textAlign = 'center';
    ctx.fillText(MULTS[i] + 'x', sx + slotW/2, slotY + 30);
  }}

  // Ball — always draw if showBall is true
  if (showBall) {{
    ctx.beginPath();
    ctx.arc(ballX + 2, ballY + 2, 10, 0, 2*Math.PI);
    ctx.fillStyle = '#00000044'; ctx.fill();
    const grad = ctx.createRadialGradient(ballX-3, ballY-3, 1, ballX, ballY, 10);
    grad.addColorStop(0, '#ff9999');
    grad.addColorStop(0.5, '#ff3333');
    grad.addColorStop(1, '#aa0000');
    ctx.beginPath(); ctx.arc(ballX, ballY, 10, 0, 2*Math.PI);
    ctx.fillStyle = grad; ctx.fill();
    ctx.beginPath(); ctx.arc(ballX-3, ballY-3, 3, 0, 2*Math.PI);
    ctx.fillStyle = '#ffffff88'; ctx.fill();
  }}
}}

// Compute waypoints using invisible physics grid
function computeWaypoints() {{
  const pts = [];
  pts.push({{x: W/2, y: 30}});
  let col = 0;
  for (let r = 0; r < ROWS; r++) {{
    const px = physPegX(r, col);
    const py = physPegY(r);
    pts.push({{x: px, y: py - 8}});
    pts.push({{x: px + (path[r] ? 8 : -8), y: py + 4}});
    if (path[r]) col += 1;
  }}
  const slotW = boardW / MULTS.length;
  pts.push({{x: PAD + finalSlot * slotW + slotW/2, y: H - 40}});
  return pts;
}}

// Always start by drawing the board in idle state
drawBoard(W/2, 30, false, -1);

if (doDROP && finalSlot >= 0) {{
  // Drop animation
  const waypoints = computeWaypoints();
  const totalDuration = 3200;
  const segDuration = totalDuration / (waypoints.length - 1);
  const startTime = performance.now();
  document.getElementById('resultBox').textContent = '🎳 Dropping...';

  function easeInOut(t) {{
    return t < 0.5 ? 2*t*t : -1+(4-2*t)*t;
  }}

  function animate(now) {{
    const elapsed = now - startTime;
    const segIndex = Math.min(Math.floor(elapsed / segDuration), waypoints.length - 2);
    const segProgress = Math.min((elapsed - segIndex * segDuration) / segDuration, 1);
    const from = waypoints[segIndex];
    const to = waypoints[segIndex + 1];
    const t = easeInOut(segProgress);
    const bx = from.x + (to.x - from.x) * t;
    const by = from.y + (to.y - from.y) * t;
    const litSlot = elapsed >= totalDuration * 0.9 ? finalSlot : -1;
    drawBoard(bx, by, true, litSlot);

    if (elapsed < totalDuration) {{
      requestAnimationFrame(animate);
    }} else {{
      // Final resting position
      const slotW = boardW / MULTS.length;
      const fx = PAD + finalSlot * slotW + slotW/2;
      drawBoard(fx, H - 40, true, finalSlot);
      const mult = MULTS[finalSlot];
      const color = getMultColor(mult);
      document.getElementById('resultBox').innerHTML =
        `<span style="color:${{color}}">🎳 Landed on <b>${{mult}}x</b>!</span>`;
    }}
  }}
  requestAnimationFrame(animate);

}} else if (!doDROP && finalSlot >= 0) {{
  // Show previous result with ball resting in slot
  const slotW = boardW / MULTS.length;
  const fx = PAD + finalSlot * slotW + slotW/2;
  drawBoard(fx, H - 40, true, finalSlot);
  const mult = MULTS[finalSlot];
  const color = getMultColor(mult);
  document.getElementById('resultBox').innerHTML =
    `<span style="color:${{color}}">🎳 Last result: <b>${{mult}}x</b></span>`;
}}
</script>
</body>
</html>"""

st.components.v1.html(plinko_html, height=640, key=canvas_key)

if drop_clicked and st.session_state.plinko_dropped:
    time.sleep(3.8)
    locked_bet = st.session_state.plinko_bet
    landed_slot = st.session_state.plinko_slot
    multiplier = MULTIPLIERS[landed_slot]
    payout = int(locked_bet * multiplier)

    if payout > locked_bet:
        net = payout - locked_bet
        st.success(f"🎉 {multiplier}x multiplier! +${net:,}")
        st.session_state.money += net
        record_game(user, True, locked_bet, payout, "🎳 Plinko")
    elif payout == locked_bet:
        st.info(f"1x — bet returned.")
        record_game(user, True, locked_bet, locked_bet, "🎳 Plinko")
    else:
        net_loss = locked_bet - payout
        st.error(f"❌ {multiplier}x — lost ${net_loss:,}")
        st.session_state.money -= net_loss
        record_game(user, False, locked_bet, payout, "🎳 Plinko")

    save_progress()
    st.write(f"**New Balance:** ${st.session_state.money:,}")
    st.session_state.plinko_dropped = False

# Multiplier legend
st.markdown("---")
st.subheader("💡 Multiplier Guide")
cols = st.columns(len(set(MULTIPLIERS)))
shown = set(); col_idx = 0
for m in MULTIPLIERS:
    if m not in shown:
        with cols[col_idx % len(cols)]:
            c = get_color(m)
            st.markdown(
                f'<div style="background:{c};border-radius:8px;padding:8px;text-align:center;'
                f'color:{"#000" if m >= 1 else "#fff"};font-weight:bold;">{m}x</div>',
                unsafe_allow_html=True
            )
        shown.add(m); col_idx += 1







