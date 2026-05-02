# app.py
import streamlit as st
import re
import sqlite3
from hashlib import sha256

TARGET_URL = "https://driver-license.streamlit.app/"

st.set_page_config(page_title="TYNORAH - Auth", page_icon="🌀", layout="centered")

# Minimal CSS (kept concise)
st.markdown(
    """
    <style>
    :root{--accent-a:#7b61ff;--accent-b:#5ec8ff;--muted:#7b7f8a;}
    .stApp{font-family:Inter,Roboto,Arial;}
    .card{max-width:560px;margin:36px auto;padding:24px;border-radius:14px;background:#fff;box-shadow:0 12px 30px rgba(30,35,90,0.06);}
    .brand{font-weight:800;font-size:26px;color:#111;}
    .subtitle{color:var(--muted);margin-bottom:14px;}
    .gradient-btn{background:linear-gradient(90deg,var(--accent-a),var(--accent-b));color:#fff;padding:10px;border-radius:10px;border:none;width:100%;font-weight:700;cursor:pointer;}
    .pw-meter{height:10px;border-radius:8px;background:#f2f6ff;overflow:hidden;margin-top:8px;}
    .pw-meter>div{height:100%;border-radius:8px;transition:width .35s;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Helpers
def is_valid_email(addr: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (addr or "").strip()))

def password_strength(pw: str):
    score = 0
    if len(pw) >= 8: score += 1
    if re.search(r"[A-Z]", pw) and re.search(r"[a-z]", pw): score += 1
    if re.search(r"\d", pw): score += 1
    if re.search(r"[^\w\s]", pw): score += 1
    labels = ["Très faible","Faible","Moyen","Fort","Très fort"]
    colors = ["#ff6b6b","#ff9f6b","#ffd36b","#7be36b","#2ee6a7"]
    widths = ["6%","28%","56%","80%","100%"]
    return score, labels[score], colors[score], widths[score]

# Simple SQLite for demo
DB_PATH = "users.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT)")
    conn.commit()
    conn.close()

def save_user(email: str, password: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        pw_hash = sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, pw_hash))
        conn.commit()
        conn.close()
        return True, "Compte créé."
    except sqlite3.IntegrityError:
        return False, "Email déjà utilisé."
    except Exception:
        return False, "Erreur interne."

def check_credentials(email: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    return sha256(password.encode()).hexdigest() == row[0]

init_db()

# UI
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="brand">TYNORAH</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Inscription / Connexion</div>', unsafe_allow_html=True)

tab = st.tabs(["Sign Up", "Login"])

# --- Sign Up tab ---
with tab[0]:
    with st.form("signup_form"):
        st.markdown("**Email**")
        email = st.text_input("", placeholder="you@example.com", key="su_email")
        st.markdown("**Password**")
        password = st.text_input("", type="password", placeholder="8 caractères minimum", key="su_pw")
        st.markdown("**Confirm password**")
        confirm = st.text_input("", type="password", placeholder="Re-saisir", key="su_confirm")
        agree = st.checkbox("J'accepte les conditions", key="su_agree")
        submitted = st.form_submit_button("S'INSCRIRE")

        # visual meter
        score, label, color, width = password_strength(password or "")
        st.markdown(f'<div style="display:flex;justify-content:space-between;"><div style="color:#6b6b7a">Force</div><div style="font-weight:700;color:{color}">{label}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="pw-meter"><div style="width:{width};background:{color}"></div></div>', unsafe_allow_html=True)

    if submitted:
        errors = []
        if not is_valid_email(email):
            errors.append("Email invalide.")
        if not password or len(password) < 8:
            errors.append("Mot de passe trop court.")
        if password != confirm:
            errors.append("Les mots de passe ne correspondent pas.")
        if not agree:
            errors.append("Accepte les conditions.")
        if errors:
            for e in errors:
                st.error(e)
        else:
            ok, msg = save_user(email.strip(), password)
            if ok:
                st.success(msg)
                st.info("Redirection en cours...")
                # JS redirect to external URL
                st.markdown(f"<script>window.location.href = '{TARGET_URL}';</script>", unsafe_allow_html=True)
            else:
                st.error(msg)

# --- Login tab ---
with tab[1]:
    with st.form("login_form"):
        st.markdown("**Email**")
        le = st.text_input("", placeholder="you@example.com", key="li_email")
        st.markdown("**Password**")
        lpw = st.text_input("", type="password", placeholder="Ton mot de passe", key="li_pw")
        lsub = st.form_submit_button("SE CONNECTER")

    if lsub:
        if not is_valid_email(le):
            st.error("Email invalide.")
        elif not lpw:
            st.error("Mot de passe requis.")
        else:
            if check_credentials(le.strip(), lpw):
                st.success("Connexion réussie. Redirection...")
                st.markdown(f"<script>window.location.href = '{TARGET_URL}';</script>", unsafe_allow_html=True)
            else:
                st.error("Identifiants incorrects.")

st.markdown('</div>', unsafe_allow_html=True)
