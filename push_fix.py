import requests
import base64
import toml
import os

# -------- LOAD TOKEN FROM SECRETS --------
secrets_paths = [
    "/workspaces/python-casino/.streamlit/secrets.toml",
    "/home/vscode/.streamlit/secrets.toml"
]

GITHUB_TOKEN = None
for path in secrets_paths:
    if os.path.exists(path):
        secrets = toml.load(path)
        GITHUB_TOKEN = secrets.get("github_token")
        break

if not GITHUB_TOKEN:
    print("❌ Could not find github_token in secrets.toml")
    exit(1)

REPO = "cburdick28-spec/python-casino"
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

def push_file(local_path, remote_path):
    if not os.path.exists(local_path):
        print(f"⚠️  Skipping {local_path} (not found locally)")
        return

    with open(local_path, "r") as f:
        content = f.read()

    url = f"https://api.github.com/repos/{REPO}/contents/{remote_path}"

    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {
        "message": f"update {remote_path}",
        "content": base64.b64encode(content.encode()).decode()
    }
    if sha:
        payload["sha"] = sha

    r2 = requests.put(url, headers=headers, json=payload)
    if r2.status_code in (200, 201):
        print(f"✅ Pushed {remote_path}")
    else:
        print(f"❌ Failed to push {remote_path}: {r2.status_code} {r2.text}")

# -------- PUSH ALL FILES --------
push_file("gambel.py", "gambel.py")
push_file("db.py", "db.py")
push_file("pages/1_🎰_Slots.py", "pages/1_🎰_Slots.py")
push_file("pages/2_🃏_Blackjack.py", "pages/2_🃏_Blackjack.py")
push_file("pages/3_🎡_Roulette.py", "pages/3_🎡_Roulette.py")
push_file("pages/4_Poker.py", "pages/4_Poker.py")

print("\n🎰 Done! Run with: streamlit run gambel.py")
