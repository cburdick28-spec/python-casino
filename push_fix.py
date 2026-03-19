import requests
import base64
import json
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
    print("Make sure /workspaces/python-casino/.streamlit/secrets.toml exists and contains:")
    print('  github_token = "your_token_here"')
    exit(1)

REPO = "cburdick28-spec/python-casino"
FILE_PATH = "gambel.py"

# -------- READ THE FIXED FILE --------
with open("gambel.py", "r") as f:
    new_content = f.read()

# -------- GET CURRENT SHA FROM GITHUB --------
url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

r = requests.get(url, headers=headers)
if r.status_code != 200:
    print(f"❌ Failed to fetch file from GitHub: {r.status_code} {r.text}")
    exit(1)

sha = r.json()["sha"]

# -------- PUSH UPDATED FILE --------
content_encoded = base64.b64encode(new_content.encode()).decode()

payload = {
    "message": "fix: auto-push all bug fixes from Claude",
    "content": content_encoded,
    "sha": sha
}

r2 = requests.put(url, headers=headers, json=payload)

if r2.status_code in (200, 201):
    print("✅ gambel.py successfully pushed to GitHub!")
else:
    print(f"❌ Failed to push: {r2.status_code} {r2.text}")
