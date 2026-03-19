import requests
import base64
import streamlit as st
import json
import hashlib

GITHUB_TOKEN = st.secrets["github_token"]
REPO = "cburdick28-spec/python-casino"
FILE_PATH = "casino_db.json"
DEV_ACCOUNTS = ["Dev1", "Dev2", "Dev3"]


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


def save_progress():
    db = load_db()
    if st.session_state.username in db["users"]:
        db["users"][st.session_state.username]["money"] = st.session_state.money
    save_db(db)
