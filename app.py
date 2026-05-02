# app.py
import streamlit as st
import re
import sqlite3
from hashlib import sha256

# ---------------- Page config ----------------
st.set_page_config(page_title="TYNORAH - Inscription", page_icon="🌀", layout="centered")

# ---------------- CSS styling ----------------
st.markdown(
    """
    <style>
    :root{
      --bg:#f3f6fb;
      --card:#ffffff;
      --muted:#7b7f8a;
      --accent1:#7b61ff;
      --accent2:#5ec8ff;
      --pink:#ff5c9e;
    }
    .stApp { background: linear-gradient(180deg, var(--bg) 0%, #ffffff 100%); font-family: Inter, Roboto, Arial, sans-serif; }
    .card {
      background: var(--card);
      border-radius: 18px;
      padding: 28px;
      box-shadow: 0 12px 30px rgba(30,35,90,0.06);
      max-width: 520px;
      margin: 36px auto;
    }
    .brand {
      font-weight: 800;
      font-size: 30px;
      color: #222233;
      text-align: left;
      letter-spacing: 0.6px;
    }
    .subtitle { color: var(--muted); margin-top:6px; margin-bottom:18px; font-size:14px; }
    .stTextInput>div>div>input, .stTextInput>div>div>textarea {
      border-radius: 12px;
      padding: 12px 14px;
      border: 1px solid #e9e9f2;
      background: #fbfbff;
    }
    .row { display:flex; gap:12px; align-items:center; }
    .terms { color: var(--muted); font-size:13px; }
    .small-note { text-align:center; color:var(--muted); font-size:13px; margin-top:12px; }
    .signin { text-align:center; margin-top:10px; font-size:14px; }
    .signin a { color: var(--pink); font-weight:600; text-decoration:none; }
    .gradient-btn {
      background: linear-gradient(90deg, var(--accent1) 0%, var(--accent2) 100%);
      color: white !important;
      border: none;
      padding: 12px 16px;
      width: 100%;
      border-radius: 12px;
      font-weight: 700;
      font-size: 15px;
      cursor: pointer;
      box-shadow: 0 8px 24px rgba(92,88,255,0.14);
    }
    .pw-meter { height:10px; border-radius:8px; background:#eef2ff; overflow:hidden; }
    .pw-meter > div { height:100%; border-radius:8px; transition: width 0.25s ease; }
    .muted-link { color:var(--muted); text-decoration:none; }
    @media (max-width:600px){
      .card { margin:18px; padding:20px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Helper functions ----------------
def is_valid_email(addr: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (addr or "").strip()))

def password_strength(pw: str) -> tuple:
    """Return (score 0-4, label, color, width%)"""
    score = 0
    if len(pw) >= 8: score += 1
    if re.search(r"[A-Z]", pw) and re.search(r"[a-z]", pw): score += 1
    if re.search(r"\d", pw): score += 1
    if re.search(r"[^\w\s]", pw): score += 1
    labels = ["Très faible", "Faible", "Moyen", "Fort", "Très fort"]
    colors = ["#ff6b6b", "#ff9f6b", "#ffd36b", "#7be36b", "#2ee6a7"]
    widths = ["8%", "28%", "56%", "80%", "100%"]
    return score, labels[score], colors[score], widths[score]

# ---------------- Optional local DB (simulation) ----------------
DB_PATH = "users.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password_hash TEXT)"
    )
    conn.commit()
    conn.close()

def save_user(email: str, password: str) -> tuple:
    """Save user hashed password. Returns (success, message)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        pw_hash = sha256(password.encode("utf-8")).hexdigest()
        c.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, pw_hash))
        conn.commit()
        conn.close()
        return True, "Compte créé avec succès."
    except sqlite3.IntegrityError:
        return False, "Cette adresse email est déjà utilisée."
    except Exception as e:
        return False, "Erreur interne, réessaye plus tard."

init_db()

# ---------------- UI layout ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)

# Header
col1, col2 = st.columns([3,1])
with col1:
    st.markdown('<div class="brand">TYNORAH</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Crée ton compte en quelques secondes</div>', unsafe_allow_html=True)
with col2:
    # small decorative circle or icon
    st.markdown('<div style="text-align:right; font-size:20px; color:#7b61ff;">✨</div>', unsafe_allow_html=True)

# Form
with st.form("signup", clear_on_submit=False):
    st.markdown("**Email address**")
    email = st.text_input("", placeholder="you@example.com", key="email_input")

    # Password row with show/hide
    st.markdown("**Password**")
    pw_col1, pw_col2 = st.columns([4,1])
    with pw_col1:
        password = st.text_input("", type="password" if not st.session_state.get("show_pw") else "default",
                                 placeholder="8 caractères minimum", key="pw_input")
    with pw_col2:
        # toggle show/hide
        show = st.checkbox("Afficher", key="show_pw")
        st.session_state["show_pw"] = show

    st.markdown("**Confirm password**")
    confirm = st.text_input("", type="password" if not st.session_state.get("show_pw_confirm") else "default",
                            placeholder="Re-saisis le mot de passe", key="pw_confirm_input")
    # separate checkbox for confirm show/hide
    st.checkbox("Afficher", key="show_pw_confirm", on_change=lambda: st.session_state.update({"show_pw_confirm": not st.session_state.get("show_pw_confirm", False)}))

    # Password strength meter
    score, label, color, width = password_strength(password or "")
    st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center;"><div style="font-size:13px; color:#6b6b7a">Force du mot de passe</div><div style="font-weight:700; color:{color}">{label}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pw-meter"><div style="width:{width}; background:{color}"></div></div>', unsafe_allow_html=True)

    agree = st.checkbox("J'accepte les conditions d'utilisation", key="agree_terms")

    # Submit button (styled)
    submitted = st.form_submit_button("S'INSCRIRE")

    # Also render a styled HTML button for visual consistency (does not replace form submit)
    st.markdown(
        """
        <div style="margin-top:8px;">
            <button class="gradient-btn" onclick="document.querySelector('form').dispatchEvent(new Event('submit', {cancelable: true}))">
                S'INSCRIRE
            </button>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------- Validation and processing ----------------
if submitted:
    errors = []
    email_val = (email or "").strip()
    if not email_val or not is_valid_email(email_val):
        errors.append("Adresse email invalide.")
    if not password or len(password) < 8:
        errors.append("Le mot de passe doit contenir au moins 8 caractères.")
    if password != confirm:
        errors.append("Les mots de passe ne correspondent pas.")
    if not agree:
        errors.append("Tu dois accepter les conditions pour continuer.")
    if password and " " in password:
        errors.append("Le mot de passe ne doit pas contenir d'espaces.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        # Save user (simulation) and show success
        ok, msg = save_user(email_val, password)
        if ok:
            st.success(msg)
            st.info("Un email de confirmation a été simulé vers " + email_val)
            st.balloons()
            # Optionally clear inputs
            st.session_state["email_input"] = ""
            st.session_state["pw_input"] = ""
            st.session_state["pw_confirm_input"] = ""
        else:
            st.error(msg)

# ---------------- Footer notes ----------------
st.markdown(
    """
    <div class="small-note">
        En cliquant sur <strong>S'INSCRIRE</strong>, tu acceptes nos Conditions et la Politique de confidentialité.
    </div>
    <div class="signin">
        Déjà un compte ? <a class="muted-link" href="#">Se connecter</a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('</div>', unsafe_allow_html=True)
