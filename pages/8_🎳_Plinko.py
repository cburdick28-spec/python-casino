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
st.caption("Drop the ball and watch it bounce!")
st.write(f"**Balance:** ${money:,}")

if money <= 0:
    st.error("You're out of money! Go claim your daily reward on the main page.")
    st.stop()

bet = st.number_input("Bet", min_value=1, max_value=money, value=min(10,money), step=1)

ROWS = 12
MULTIPLIERS = [10,3,1.5,1,0.5,0.3,0.2,0.1,0.2,0.3,0.5,1,1.5,3,10]
MULTIPLIER_COLORS = {10:"#FFD700",3:"#FF6B35",1.5:"#FF9F1C",1:"#2EC4B6",
                     0.5:"#3D9970",0.3:"#2ECC40",0.2:"#7FDBFF",0.1:"#AAAAAA"}

def get_color(m): return MULTIPLIER_COLORS.get(m,"#888888")

def simulate_path(rows):
    path=[]; pos=0
    for _ in range(rows):
        go_right=random.random()<0.5; path.append(go_right)
        if go_right: pos+=1
    return path,pos

for k,v in [("plinko_path",None),("plinko_slot",None),("plinko_bet",0),("plinko_dropped",False)]:
    if k not in st.session_state: st.session_state[k]=v

drop_clicked = st.button("🎳 Drop Ball!")
if drop_clicked:
    path,slot = simulate_path(ROWS)
    st.session_state.plinko_path=path; st.session_state.plinko_slot=slot
    st.session_state.plinko_bet=bet; st.session_state.plinko_dropped=True

path=st.session_state.plinko_path; slot=st.session_state.plinko_slot
do_drop="true" if drop_clicked else "false"
path_json=str(path).lower() if path else "[]"
slot_val=slot if slot is not None else -1

plinko_html = f"""<!DOCTYPE html><html><head>
<style>body{{margin:0;background:transparent;display:flex;justify-content:center;flex-direction:column;align-items:center;font-family:Arial,sans-serif;}}
canvas{{border-radius:12px;}}#resultBox{{font-size:22px;font-weight:bold;color:white;margin-top:14px;min-height:36px;text-align:center;}}</style></head><body>
<canvas id="c" width="520" height="560"></canvas><div id="resultBox">🎳 Drop the ball!</div>
<script>
const canvas=document.getElementById('c'),ctx=canvas.getContext('2d');
const W=520,H=560,ROWS={ROWS},MULTS={MULTIPLIERS},path={path_json},doDROP={do_drop},finalSlot={slot_val};
const PAD=30,boardW=W-PAD*2,boardH=H-100,rowH=boardH/(ROWS+1);
function pegX(row,col){{const spacing=boardW/(row+2);return PAD+spacing*(col+1);}}
function pegY(row){{return 40+rowH*(row+1);}}
function getMultColor(m){{const colors={{"10":"#FFD700","3":"#FF6B35","1.5":"#FF9F1C","1":"#2EC4B6","0.5":"#3D9970","0.3":"#2ECC40","0.2":"#7FDBFF","0.1":"#AAAAAA"}};return colors[String(m)]||"#888";}}
function drawBoard(ballX,ballY,showBall){{
  ctx.clearRect(0,0,W,H);ctx.fillStyle='#0d0d1a';ctx.roundRect(0,0,W,H,16);ctx.fill();
  ctx.fillStyle='#FFD700';ctx.font='bold 20px Arial';ctx.textAlign='center';ctx.fillText('🎳 PLINKO',W/2,28);
  for(let r=0;r<ROWS;r++)for(let c=0;c<=r;c++){{ctx.beginPath();ctx.arc(pegX(r,c),pegY(r),5,0,2*Math.PI);ctx.fillStyle='#ffffff88';ctx.fill();}}
  const slotW=boardW/MULTS.length,slotY=H-60;
  for(let i=0;i<MULTS.length;i++){{
    const sx=PAD+i*slotW,color=getMultColor(MULTS[i]),isWinner=(i===finalSlot&&!doDROP);
    ctx.fillStyle=isWinner?color:color+'88';ctx.beginPath();ctx.roundRect(sx+2,slotY,slotW-4,50,6);ctx.fill();
    ctx.fillStyle=isWinner?'#000':'#fff';ctx.font=`bold ${{MULTS[i]>=3?14:11}}px Arial`;ctx.textAlign='center';ctx.fillText(MULTS[i]+'x',sx+slotW/2,slotY+30);
  }}
  if(showBall){{ctx.beginPath();ctx.arc(ballX,ballY,10,0,2*Math.PI);const grad=ctx.createRadialGradient(ballX-3,ballY-3,1,ballX,ballY,10);grad.addColorStop(0,'#ff6b6b');grad.addColorStop(1,'#cc0000');ctx.fillStyle=grad;ctx.fill();}}
}}
function computeWaypoints(){{
  const pts=[{{x:W/2,y:20}}];let col=0;
  for(let r=0;r<ROWS;r++){{pts.push({{x:pegX(r,col),y:pegY(r)}});if(path[r])col+=1;}}
  pts.push({{x:PAD+finalSlot*(boardW/MULTS.length)+(boardW/MULTS.length)/2,y:H-35}});return pts;
}}
drawBoard(W/2,20,false);
if(doDROP){{
  const waypoints=computeWaypoints(),totalDuration=3000,segDuration=totalDuration/(waypoints.length-1),startTime=performance.now();
  document.getElementById('resultBox').textContent='🎳 Dropping...';
  function animate(now){{
    const elapsed=now-startTime,segIndex=Math.min(Math.floor(elapsed/segDuration),waypoints.length-2);
    const segProgress=Math.min((elapsed-segIndex*segDuration)/segDuration,1);
    const from=waypoints[segIndex],to=waypoints[segIndex+1];
    const t=segProgress<0.5?2*segProgress*segProgress:-1+(4-2*segProgress)*segProgress;
    drawBoard(from.x+(to.x-from.x)*t,from.y+(to.y-from.y)*t,true);
    if(elapsed<totalDuration)requestAnimationFrame(animate);
    else{{
      drawBoard(waypoints[waypoints.length-1].x,waypoints[waypoints.length-1].y,true);
      const mult=MULTS[finalSlot],color=getMultColor(mult);
      document.getElementById('resultBox').innerHTML=`<span style="color:${{color}}">🎳 Landed on <b>${{mult}}x</b>!</span>`;
    }}
  }}
  requestAnimationFrame(animate);
}}else if(finalSlot>=0){{
  const slotW=boardW/MULTS.length,fx=PAD+finalSlot*slotW+slotW/2;
  drawBoard(fx,H-35,true);const mult=MULTS[finalSlot],color=getMultColor(mult);
  document.getElementById('resultBox').innerHTML=`<span style="color:${{color}}">🎳 Last: <b>${{mult}}x</b></span>`;
}}
</script></body></html>"""

st.components.v1.html(plinko_html, height=620)

if drop_clicked and st.session_state.plinko_dropped:
    time.sleep(3.5)
    locked_bet=st.session_state.plinko_bet; landed_slot=st.session_state.plinko_slot
    multiplier=MULTIPLIERS[landed_slot]; payout=int(locked_bet*multiplier)
    if payout > locked_bet:
        net=payout-locked_bet; st.success(f"🎉 {multiplier}x! +${net:,}")
        st.session_state.money+=net; record_game(user,True,locked_bet,payout,"🎳 Plinko")
    elif payout==locked_bet:
        st.info(f"1x — bet returned."); record_game(user,True,locked_bet,locked_bet,"🎳 Plinko")
    else:
        net_loss=locked_bet-payout; st.error(f"❌ {multiplier}x — lost ${net_loss:,}")
        st.session_state.money-=net_loss; record_game(user,False,locked_bet,payout,"🎳 Plinko")
    save_progress()
    st.write(f"**New Balance:** ${st.session_state.money:,}")
    st.session_state.plinko_dropped=False

st.markdown("---")
st.subheader("💡 Multiplier Guide")
cols=st.columns(len(set(MULTIPLIERS))); shown=set(); col_idx=0
for m in MULTIPLIERS:
    if m not in shown:
        with cols[col_idx%len(cols)]:
            c=get_color(m)
            st.markdown(f'<div style="background:{c};border-radius:8px;padding:8px;text-align:center;color:{"#000" if m>=1 else "#fff"};font-weight:bold;">{m}x</div>',unsafe_allow_html=True)
        shown.add(m); col_idx+=1
