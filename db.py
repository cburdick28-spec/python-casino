import requests
import base64
import streamlit as st
import json
import hashlib

GITHUB_TOKEN = st.secrets["github_token"]
REPO = "cburdick28-spec/python-casino"
FILE_PATH = "casino_db.json"
DEV_ACCOUNTS = ["Dev1", "Dev2", "Dev3"]

# ---------------- VIP TIERS ----------------
VIP_TIERS = [
    {"name": "Bronze",   "emoji": "🥉", "min": 0,      "color": "#cd7f32"},
    {"name": "Silver",   "emoji": "🥈", "min": 1000,   "color": "#c0c0c0"},
    {"name": "Gold",     "emoji": "🥇", "min": 5000,   "color": "#ffd700"},
    {"name": "Platinum", "emoji": "💎", "min": 25000,  "color": "#00d4ff"},
    {"name": "Diamond",  "emoji": "💠", "min": 100000, "color": "#b9f2ff"},
]

def get_vip_tier(money):
    tier = VIP_TIERS[0]
    for t in VIP_TIERS:
        if money >= t["min"]:
            tier = t
    return tier

def get_next_tier(money):
    for t in VIP_TIERS:
        if money < t["min"]:
            return t
    return None

# ---------------- ACHIEVEMENTS ----------------
ACHIEVEMENTS = [
    {"id": "first_win",      "name": "First Win",        "emoji": "🏆", "desc": "Win your first game"},
    {"id": "high_roller",    "name": "High Roller",      "emoji": "💰", "desc": "Bet $100 or more at once"},
    {"id": "jackpot",        "name": "Jackpot!",         "emoji": "🎰", "desc": "Win the progressive jackpot"},
    {"id": "broke",          "name": "Broke",            "emoji": "💸", "desc": "Lose all your money"},
    {"id": "millionaire",    "name": "Millionaire",      "emoji": "🤑", "desc": "Reach $1,000,000"},
    {"id": "blackjack_ace",  "name": "Blackjack!",       "emoji": "🃏", "desc": "Get a natural blackjack"},
    {"id": "royal_flush",    "name": "Royal Flush",      "emoji": "♠️", "desc": "Hit a royal flush in poker"},
    {"id": "daily_7",        "name": "Dedicated",        "emoji": "📅", "desc": "Claim daily reward 7 days in a row"},
    {"id": "silver_tier",    "name": "Going Silver",     "emoji": "🥈", "desc": "Reach Silver VIP tier"},
    {"id": "gold_tier",      "name": "Going Gold",       "emoji": "🥇", "desc": "Reach Gold VIP tier"},
    {"id": "platinum_tier",  "name": "Platinum Status",  "emoji": "💎", "desc": "Reach Platinum VIP tier"},
    {"id": "diamond_tier",   "name": "Diamond Status",   "emoji": "💠", "desc": "Reach Diamond VIP tier"},
]

def unlock_achievement(username, achievement_id):
    """Unlock an achievement for a user. Returns True if newly unlocked."""
    db = load_db()
    if username not in db["users"]:
        return False
    user = db["users"][username]
    if "achievements" not in user:
        user["achievements"] = []
    if achievement_id not in user["achievements"]:
        user["achievements"].append(achievement_id)
        db["users"][username] = user
        save_db(db)
        return True
    return False

def check_vip_achievements(username, money):
    """Check and unlock VIP tier achievements."""
    if money >= 1000:
        unlock_achievement(username, "silver_tier")
    if money >= 5000:
        unlock_achievement(username, "gold_tier")
    if money >= 25000:
        unlock_achievement(username, "platinum_tier")
    if money >= 100000:
        unlock_achievement(username, "diamond_tier")
    if money >= 1000000:
        unlock_achievement(username, "millionaire")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_db():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data["content"]).decode()
        return json.loads(content)
    return {"users": {}, "jackpot": 1000}


def save_db(db):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    data = r.json()
    sha = data["sha"]
    content = base64.b64encode(json.dumps(db, indent=4).encode()).decode()
    payload = {
        "message": "update casino database",
        "content": content,
        "sha": sha
    }
    requests.put(url, headers=headers, json=payload)


def ensure_user_fields(user_data):
    """Make sure all required fields exist on a user record."""
    defaults = {
        "timeout": 0,
        "last_daily": "",
        "achievements": [],
        "stats": {
            "games_played": 0,
            "games_won": 0,
            "games_lost": 0,
            "total_wagered": 0,
            "total_won": 0,
            "biggest_win": 0,
            "daily_streak": 0,
        }
    }
    for k, v in defaults.items():
        if k not in user_data:
            user_data[k] = v
    # ensure all stat sub-fields exist
    for k, v in defaults["stats"].items():
        if k not in user_data["stats"]:
            user_data["stats"][k] = v
    return user_data


def save_progress():
    db = load_db()
    if st.session_state.username in db["users"]:
        db["users"][st.session_state.username]["money"] = st.session_state.money
        check_vip_achievements(st.session_state.username, st.session_state.money)
    save_db(db)


def record_game(username, won, wagered, payout):
    """Update a user's stats after a game."""
    db = load_db()
    if username not in db["users"]:
        return
    user = ensure_user_fields(db["users"][username])
    stats = user["stats"]
    stats["games_played"] += 1
    stats["total_wagered"] += wagered
    if won:
        stats["games_won"] += 1
        stats["total_won"] += payout
        if payout > stats["biggest_win"]:
            stats["biggest_win"] = payout
        unlock_achievement(username, "first_win")
    else:
        stats["games_lost"] += 1
    if wagered >= 100:
        unlock_achievement(username, "high_roller")
    db["users"][username] = user
    save_db(db)
