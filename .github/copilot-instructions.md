# Copilot Instructions for python-casino

## Repository Overview

This is a **multi-page Python casino web application** built with [Streamlit](https://streamlit.io/). Players can register/login and play several casino games, each on its own page. User data (balances, achievements, bet history, stats) is persisted by committing a JSON file directly to this GitHub repository via the GitHub API.

**Language/Runtime:** Python 3.11  
**Framework:** Streamlit  
**Data persistence:** GitHub API — reads/writes `casino_db.json` in the repo root using a GitHub token stored in Streamlit secrets.

---

## Project Layout

```
python-casino/
├── gambel.py                  # Entry point: main page (login, register, lobby, leaderboard)
├── db.py                      # All database I/O, constants, helpers (load_db, save_db, etc.)
├── casino_db.json             # Persisted player data (committed to repo via GitHub API)
├── push_fix.py                # Dev utility: manually push source files to GitHub
├── .devcontainer/
│   └── devcontainer.json      # Codespaces / VS Code Dev Container configuration
└── pages/                     # Streamlit multi-page app pages (loaded automatically by Streamlit)
    ├── 1_🎰_Slots.py
    ├── 2_🃏_Blackjack.py
    ├── 3_🎡_Roulette.py
    ├── 4_Poker.py
    ├── 5_Chat.py
    ├── 6_📊_Stats.py
    ├── 7_🎲_Craps.py
    ├── 8_🎳_Plinko.py
    ├── 9_🎭_Profile.py
    ├── 10_🏇_Horse_Racing.py
    └── 11_📈_History.py
```

---

## Architecture

- **`gambel.py`** is the Streamlit entry point. It handles login/registration, session state initialization, the sidebar (leaderboard, daily reward, dev panel), and links to all game pages.
- **`db.py`** is the single source of truth for all data access. It exposes:
  - `load_db()` / `save_db(db)` — fetch/commit `casino_db.json` via the GitHub API.
  - `save_progress()` — write the current user's balance from `st.session_state` back to the DB.
  - `record_game(username, won, wagered, payout, game_name)` — update stats and bet history.
  - `unlock_achievement(username, achievement_id)` / `check_vip_achievements(username, money)` — achievement helpers.
  - `ensure_user_fields(user_data)` — backfill default fields for older user records.
  - `hash_password(password)` — SHA-256 digest.
  - Constants: `DEV_ACCOUNTS`, `VIP_TIERS`, `ACHIEVEMENTS`, `MAX_SAFE_MONEY`.
- **`MAX_SAFE_MONEY = (1 << 53) - 1`** — always use this constant as the `max_value` for `st.number_input` bet fields to prevent JavaScript integer overflow.
- **Each page in `pages/`** is an independent Streamlit script. Pages must guard against unauthenticated access at the top:
  ```python
  if "username" not in st.session_state or st.session_state.username is None:
      st.warning("Please log in from the main page first.")
      st.stop()
  ```
- **Dev accounts** (`DEV_ACCOUNTS = ["Dev1", "Dev2", "Dev3"]`) get unlimited money and access to an admin panel.
- **Session state key `money`** holds the current user's balance in-memory; `save_progress()` flushes it to the DB.

---

## Environment & Secrets

The app requires a Streamlit secrets file at `.streamlit/secrets.toml` (or the Codespaces equivalent) containing:

```toml
github_token = "ghp_..."
```

This token is used by `db.py` and `push_fix.py` to read/write `casino_db.json` via the GitHub API. Without it the app will not start.

---

## Running the App

```bash
# Install dependencies (no requirements.txt; install manually)
pip install streamlit requests toml

# Run the app
streamlit run gambel.py
```

The app listens on port **8501** by default. The Dev Container starts it automatically via `postAttachCommand`.

There are **no linting, build, or test scripts** configured in this repository. There is no CI/CD pipeline.

---

## Key Conventions

- Always import helpers from `db.py`; do not duplicate database logic in page files.
- Always cap `st.number_input` bet values with `max_value=min(money, MAX_SAFE_MONEY)` to avoid JS Number bounds errors.
- Call `record_game()` after every game outcome so stats and bet history stay up to date.
- Call `save_progress()` whenever the user's balance changes and needs to be persisted.
- Do not store secrets in source code; use `st.secrets["github_token"]`.
- Page filenames follow the pattern `<number>_<emoji>_<Name>.py` to control sidebar order in Streamlit.
- `casino_db.json` is a live data file committed by the running app; do not hand-edit it unless restoring a backup.
