import streamlit as st
from db import load_db, save_db, ensure_user_fields, get_vip_tier, ACHIEVEMENTS, DEV_ACCOUNTS

st.set_page_config(page_title="🎭 Profile", layout="wide")

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Please log in from the main page first.")
    st.stop()

user = st.session_state.username
db = load_db()
users = db["users"]

if user not in users:
    st.error("User not found.")
    st.stop()

user_data = ensure_user_fields(users[user])
money = st.session_state.money
tier = get_vip_tier(money)

# ---------------- AVATAR OPTIONS ----------------
AVATARS = {
    "🎰": "Slot Machine", "🃏": "Card Shark", "🎲": "Dice Roller",
    "💎": "Diamond", "🦁": "Lion", "🐯": "Tiger", "🦊": "Fox",
    "🐺": "Wolf", "🦅": "Eagle", "🐉": "Dragon", "🤑": "Money Face",
    "😎": "Cool Guy", "🤠": "Cowboy", "🥷": "Ninja", "👑": "King",
    "🎭": "Jester", "🧙": "Wizard", "🤖": "Robot", "👾": "Alien",
    "💀": "Skull", "🔥": "Fire", "⚡": "Lightning", "🌟": "Star",
    "🍀": "Lucky Clover", "🎯": "Bullseye",
}

BANNER_COLORS = {
    "🌑 Dark":    "#0d0d1a",
    "🔵 Ocean":   "#0a3d62",
    "🟣 Purple":  "#4a0080",
    "🔴 Red":     "#7f0000",
    "🟢 Forest":  "#1a4a1a",
    "🟡 Gold":    "#7a6000",
    "🩷 Pink":    "#7a1040",
    "⬛ Midnight": "#111111",
}

TITLES = {
    "Rookie":      {"req": 0,       "emoji": "🎮"},
    "Gambler":     {"req": 1000,    "emoji": "🎲"},
    "High Roller": {"req": 10000,   "emoji": "💰"},
    "Whale":       {"req": 100000,  "emoji": "🐋"},
    "Casino King": {"req": 500000,  "emoji": "👑"},
    "Legend":      {"req": 1000000, "emoji": "🌟"},
}

def get_available_titles(money):
    return [(name, info) for name, info in TITLES.items() if money >= info["req"]]

def get_title_emoji(title):
    return TITLES.get(title, {"emoji": "🎮"})["emoji"]

def get_profile(user_data):
    if "profile" not in user_data:
        user_data["profile"] = {"avatar": "🎰", "banner": "🌑 Dark", "title": "Rookie", "bio": ""}
    return user_data["profile"]

profile = get_profile(user_data)
current_avatar = profile.get("avatar", "🎰")
current_banner = profile.get("banner", "🌑 Dark")
current_title = profile.get("title", "Rookie")
current_bio = profile.get("bio", "")
banner_color = BANNER_COLORS.get(current_banner, "#0d0d1a")
achievements = user_data.get("achievements", [])
unlocked_achievements = [a for a in ACHIEVEMENTS if a["id"] in achievements]

title_emoji = get_title_emoji(current_title)
bio_display = current_bio if current_bio else "No bio set yet."

# ---------------- PROFILE CARD ----------------
st.markdown(f"""
<div style="background:linear-gradient(135deg,{banner_color},{banner_color}cc);
border:2px solid {tier['color']};border-radius:16px;padding:30px;margin-bottom:24px;">
  <div style="display:flex;align-items:center;gap:24px;">
    <div style="font-size:80px;line-height:1;">{current_avatar}</div>
    <div>
      <div style="font-size:28px;font-weight:bold;color:white;">{user}</div>
      <div style="font-size:16px;color:{tier['color']};margin:4px 0;">
        {tier['emoji']} {tier['name']} VIP &nbsp;|&nbsp; {title_emoji} {current_title}
      </div>
      <div style="font-size:14px;color:#aaa;margin-top:6px;">
        💰 ${money:,} &nbsp;|&nbsp; 🏆 {len(unlocked_achievements)} achievements
      </div>
      <div style="font-size:14px;color:#ccc;margin-top:8px;font-style:italic;">
        "{bio_display}"
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------- EDIT PROFILE ----------------
st.header("✏️ Edit Profile")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎭 Choose Avatar")
    selected_avatar = current_avatar
    avatar_cols = st.columns(5)
    for i, (emoji, name) in enumerate(AVATARS.items()):
        with avatar_cols[i % 5]:
            if st.button(emoji, key=f"av_{emoji}", help=name):
                selected_avatar = emoji

    st.markdown("---")
    st.subheader("🎨 Banner Color")
    banner_keys = list(BANNER_COLORS.keys())
    current_banner_idx = banner_keys.index(current_banner) if current_banner in banner_keys else 0
    selected_banner = st.selectbox("Banner", banner_keys, index=current_banner_idx)

with col2:
    st.subheader("🏅 Title")
    available_titles = get_available_titles(money)
    title_options = [f"{info['emoji']} {name}" for name, info in available_titles]
    title_names = [name for name, _ in available_titles]
    current_idx = title_names.index(current_title) if current_title in title_names else 0
    selected_title_display = st.selectbox("Choose Title", title_options, index=current_idx)
    selected_title = title_names[title_options.index(selected_title_display)]

    st.markdown("---")
    st.subheader("📝 Bio")
    selected_bio = st.text_area("Bio", value=current_bio, max_chars=120,
                                placeholder="Tell other players about yourself...")
    st.caption(f"{len(selected_bio)}/120 characters")

    st.markdown("**🔒 Locked Titles:**")
    for name, info in TITLES.items():
        if money < info["req"]:
            st.markdown(
                f"<span style='color:#555'>{info['emoji']} {name} — requires ${info['req']:,}</span>",
                unsafe_allow_html=True
            )

if st.button("💾 Save Profile", type="primary"):
    db = load_db()
    if user in db["users"]:
        if "profile" not in db["users"][user]:
            db["users"][user]["profile"] = {}
        db["users"][user]["profile"]["avatar"] = selected_avatar
        db["users"][user]["profile"]["banner"] = selected_banner
        db["users"][user]["profile"]["title"] = selected_title
        db["users"][user]["profile"]["bio"] = selected_bio
        save_db(db)
        st.success("✅ Profile saved!")
        st.rerun()

st.markdown("---")

# ---------------- ACHIEVEMENTS SHOWCASE ----------------
st.header("🏆 Achievements")

if not unlocked_achievements:
    st.info("No achievements yet — start playing to unlock them!")
else:
    ach_cols = st.columns(4)
    for i, ach in enumerate(unlocked_achievements):
        with ach_cols[i % 4]:
            st.markdown(f"""
            <div style="background:#2a2a2a;border:1px solid #FFD700;
            border-radius:10px;padding:12px;text-align:center;margin-bottom:10px;">
            <div style="font-size:28px">{ach['emoji']}</div>
            <div style="font-weight:bold;font-size:13px;color:#FFD700">{ach['name']}</div>
            <div style="font-size:11px;color:#aaa">{ach['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# ---------------- OTHER PLAYERS ----------------
st.header("👥 Other Players")

other_users = {u: v for u, v in db["users"].items() if u != user and u not in DEV_ACCOUNTS}

if not other_users:
    st.info("No other players yet!")
else:
    p_cols = st.columns(min(3, len(other_users)))
    for i, (uname, udata) in enumerate(other_users.items()):
        udata = ensure_user_fields(udata)
        uprofile = get_profile(udata)
        utier = get_vip_tier(udata.get("money", 0))
        ubanner_color = BANNER_COLORS.get(uprofile.get("banner", "🌑 Dark"), "#0d0d1a")
        uavatar = uprofile.get("avatar", "🎰")
        utitle = uprofile.get("title", "Rookie")
        utitle_emoji = get_title_emoji(utitle)
        ubio = uprofile.get("bio", "") or "No bio set."
        uach = len(udata.get("achievements", []))
        umoney = udata.get("money", 0)

        with p_cols[i % 3]:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{ubanner_color},{ubanner_color}cc);
            border:2px solid {utier['color']};border-radius:12px;padding:16px;margin-bottom:12px;">
            <div style="font-size:48px;text-align:center">{uavatar}</div>
            <div style="font-size:16px;font-weight:bold;color:white;text-align:center">{uname}</div>
            <div style="font-size:12px;color:{utier['color']};text-align:center">
              {utier['emoji']} {utier['name']} &nbsp;|&nbsp; {utitle_emoji} {utitle}
            </div>
            <div style="font-size:12px;color:#aaa;text-align:center;margin-top:4px;">
              💰 ${umoney:,} &nbsp;|&nbsp; 🏆 {uach}
            </div>
            <div style="font-size:12px;color:#ccc;text-align:center;font-style:italic;margin-top:6px;">
              "{ubio}"
            </div>
            </div>
            """, unsafe_allow_html=True)
