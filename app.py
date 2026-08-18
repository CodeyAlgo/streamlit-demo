import streamlit as st
import json
import os
import re
import random
import hashlib
from datetime import datetime

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
st.set_page_config(page_title="Vault Login", page_icon="🔐", layout="centered")

USERS_FILE = "users.json"


# ----------------------------------------------------------------------
# STORAGE HELPERS (simple JSON file acting as a mini "database")
# ----------------------------------------------------------------------
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def hash_password(password: str) -> str:
    # Never store plaintext passwords
    return hashlib.sha256(password.encode()).hexdigest()


# ----------------------------------------------------------------------
# VALIDATION
# ----------------------------------------------------------------------
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


def validate_registration(username, email, password, confirm_password, users):
    errors = []

    if not username or len(username.strip()) < 3:
        errors.append("Username must be at least 3 characters long.")

    if username in users:
        errors.append("That username is already taken.")

    if not email or not re.match(EMAIL_REGEX, email):
        errors.append("Please enter a valid email address.")

    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters long.")

    if password != confirm_password:
        errors.append("Passwords do not match.")

    return errors


def validate_login(username, password, users):
    errors = []

    if username not in users:
        errors.append("No account found with that username.")
    elif users[username]["password"] != hash_password(password):
        errors.append("Incorrect password.")

    return errors


# ----------------------------------------------------------------------
# SESSION STATE INIT
# ----------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "auth"          # auth -> dashboard
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "clicks" not in st.session_state:
    st.session_state.clicks = 0


# ----------------------------------------------------------------------
# FUN "DO SOMETHING" BUTTON LOGIC (dashboard action)
# ----------------------------------------------------------------------
FORTUNES = [
    "Your next bug will fix itself... eventually.",
    "A great commit message is coming your way.",
    "Beware of off-by-one errors today.",
    "You will find the semicolon you've been missing.",
    "Your code will compile on the first try. (Just kidding.)",
    "Someone will finally review your pull request.",
    "Today is a good day to refactor.",
    "Your coffee will stay hot for once.",
]


def draw_fortune():
    st.session_state.clicks += 1
    return random.choice(FORTUNES)


# ----------------------------------------------------------------------
# AUTH PAGE
# ----------------------------------------------------------------------
def auth_page():
    st.title("🔐 Welcome")
    st.caption("Log in to an existing account, or register a new one.")

    users = load_users()

    tab_login, tab_register = st.tabs(["Log In", "Register"])

    # ---------------- LOGIN TAB ----------------
    with tab_login:
        with st.form("login_form"):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_submitted = st.form_submit_button("Log In")

        if login_submitted:
            errors = validate_login(login_username, login_password, users)
            if errors:
                for e in errors:
                    st.error(e)
            else:
                st.success("Registration successful.")  # per spec: confirmation on success
                st.session_state.current_user = login_username
                st.session_state.page = "dashboard"
                st.rerun()

    # ---------------- REGISTER TAB ----------------
    with tab_register:
        with st.form("register_form"):
            reg_username = st.text_input("Choose a username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Choose a password", type="password", key="reg_password")
            reg_confirm = st.text_input("Confirm password", type="password", key="reg_confirm")
            register_submitted = st.form_submit_button("Register")

        if register_submitted:
            errors = validate_registration(reg_username, reg_email, reg_password, reg_confirm, users)
            if errors:
                for e in errors:
                    st.error(e)
            else:
                users[reg_username] = {
                    "email": reg_email,
                    "password": hash_password(reg_password),
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                }
                save_users(users)
                st.success("Registration successful.")
                st.session_state.current_user = reg_username
                st.session_state.page = "dashboard"
                st.rerun()


# ----------------------------------------------------------------------
# DASHBOARD PAGE
# ----------------------------------------------------------------------
def dashboard_page():
    st.title("📊 Dashboard")
    st.write(f"Welcome, **{st.session_state.current_user}**!")
    st.divider()

    st.subheader("Daily Dev Fortune")
    st.write("Click the button to draw a random fortune for your coding session.")

    if st.button("🔮 Draw My Fortune"):
        fortune = draw_fortune()
        st.info(fortune)

    st.caption(f"You've drawn a fortune {st.session_state.clicks} time(s) this session.")

    st.divider()
    if st.button("Log Out"):
        st.session_state.current_user = None
        st.session_state.page = "auth"
        st.session_state.clicks = 0
        st.rerun()


# ----------------------------------------------------------------------
# ROUTER
# ----------------------------------------------------------------------
if st.session_state.page == "auth":
    auth_page()
else:
    dashboard_page()
