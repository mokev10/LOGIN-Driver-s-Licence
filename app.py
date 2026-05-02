# app.py
import streamlit as st
import re
import sqlite3
from hashlib import sha256

st.set_page_config(page_title="TYNORAH - Sign Up", page_icon="🌀", layout="centered")

# ---------------- CSS with transitions and micro-interactions ----------------
st.markdown(
    """
    <style>
    :root{
      --bg-1: #f6f8ff;
      --card: #ffffff;
      --muted: #7b7f8a;
      --accent-a: #7b61ff;
      --accent-b: #5ec8ff;
      --accent-c: #ff5c9e;
      --glass: rgba(255,255,255,0.6);
    }

    /* Page background */
    .stApp {
      background: linear-gradient(180deg, var(--bg-1) 0%, #ffffff 100%);
      font-family: Inter, Roboto, "Segoe UI", Arial, sans-serif;
      -webkit-font-smoothing:antialiased;
    }

    /* Card */
    .card {
      max-width: 560px;
      margin: 36px auto;
      background: linear-gradient(180deg, rgba(255,255,255,0.9), var(--card));
      border-radius: 18px;
      padding: 28px;
      box-shadow: 0 14px 40px rgba(30,35,90,0.06);
      transition: transform 0.45s cubic-bezier(.2,.9,.2,1), box-shadow 0.35s ease;
      will-change: transform;
      border: 1px solid rgba(124,124,160,0.06);
    }
    .card:hover {
      transform: translateY(-6px);
      box-shadow: 0 26px 60px rgba(30,35,90,0.09);
    }

    /* Header */
    .brand {
      font-weight: 800;
      font-size: 28px;
      color: #11121a;
      letter-spacing: 0.4px;
    }
    .subtitle {
      color: var(--muted);
      margin-top: 6px;
      margin-bottom: 18px;
      font-size: 14px;
    }

    /* Inputs */
    .stTextInput>div>div>input, .stTextInput>div>div>textarea {
      border-radius: 12px;
      padding: 12px 14px;
      border: 1px solid #eef0fb;
      background: linear-gradient(180deg, #ffffff, #fbfbff);
      transition: box-shadow 0.22s ease, transform 0.18s ease, border-color 0.18s ease;
      outline: none;
      box-shadow: none;
    }
    .stTextInput>div>div>input:focus {
      border-color: rgba(123,97,255,0.9);
      box-shadow: 0 6px 20px rgba(123,97,255,0.08);
      transform: translateY(-2px);
    }
    label {
      font-weight: 600;
      color: #222233;
      display:block;
      margin-bottom:6px;
      font-size:14px;
    }

    /* Checkbox label */
    .terms {
      color: var(--muted);
      font-size: 13px;
      margin-top: 8px;
    }

    /* Animated gradient button */
    .gradient-btn {
      display:inline-block;
      width:100%;
      padding:12px 16px;
      border-radius: 12px;
      color: #fff !important;
      font-weight: 800;
      font-size: 15px;
      border: none;
      cursor: pointer;
      background: linear-gradient(90deg, var(--accent-a) 0%, var(--accent-b) 50%, var(--accent-c) 100%);
      background-size: 200% 100%;
      transition: background-position 0.6s ease, transform 0.18s ease, box-shadow 0.18s ease;
      box-shadow: 0 10px 30px rgba(92,88,255,0.12);
    }
    .gradient-btn:hover {
      background-position: 100% 0;
      transform: translateY(-3px);
      box-shadow: 0 18px 40px rgba(92,88,255,0.16);
    }
    .gradient-btn:active {
      transform: translateY(-1px) scale(0.997);
    }

    /* Password meter */
    .pw-meter {
      height:10px;
      border-radius:8px;
      background: linear-gradient(90deg, #f2f6ff, #f8fbff);
      overflow:hidden;
      margin-top:8px;
      transition: opacity 0.2s ease;
    }
    .pw-meter > div {
      height:100%;
      border-radius:8px;
      transition: width 0.35s cubic-bezier(.2,.9,.2,1), background 0.35s ease;
    }

    /* Small note and sign in */
    .small-note {
      text-align:center;
      color:var(--muted);
      font-size:13px;
      margin-top:14px;
    }
    .signin {
      text-align:center;
      margin-top:10px;
      font-size:14px;
    }
    .signin a {
      color: var(--accent-c);
      font-weight:700;
      text-decoration:none;
    }

    /* Micro-interaction for error/success messages */
    .stAlert {
      transition: transform 0.28s ease, opacity 0.28s ease;
    }

    /* Responsive */
    @media (max-width:600px) {
      .card { margin:18px; padding:20px; }
      .brand { font-size:22px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Helper functions ----------------
def is_valid_email(addr: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (addr or "").strip()))

def password_strength(pw: str) -> tuple:
    score = 0
    if len(pw) >= 8: score += 1
    if re.search(r"[A-Z]", pw) and re.search(r"[a-z]", pw): score += 1
    if re.search(r"\d", pw): score += 1
    if re.search(r"[^\w\s]", pw): score += 1
    labels = ["Très faible", "Faible", "Moyen", "Fort", "Très fort"]
    colors = ["#ff6b6b", "#ff9f6b", "#ffd36b", "#7be36b", "#2ee6a7"]
    widths = ["6%", "28%", "56%", "80%", "100%"]
    return score, labels[score], colors[score], widths[score]

# ---------------- Simple local DB ----------------
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
    except Exception:
        return False, "Erreur interne."

init_db()

# ---------------- UI ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown('<div class="brand">TYNORAH</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Inscris-toi rapidement — transitions fluides et micro-interactions</div>', unsafe_allow_html=True)

with st.form("signup_form"):
    st.markdown("**Email address**")
    email = st.text_input("", placeholder="you@example.com", key="email")

    st.markdown("**Password**")
    password = st.text_input("", type="password", placeholder="8 caractères minimum", key="password")

    st.markdown("**Confirm password**")
    confirm = st.text_input("", type="password", placeholder="Re-saisir le mot de passe", key="confirm")

    # Password strength visual
    score, label, color, width = password_strength(password or "")
    st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center;"><div style="font-size:13px; color:#6b6b7a">Force du mot de passe</div><div style="font-weight:700; color:{color}">{label}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pw-meter"><div style="width:{width}; background:{color}"></div></div>', unsafe_allow_html=True)

    agree = st.checkbox("J'accepte les conditions d'utilisation", key="agree")
    submitted = st.form_submit_button("S'INSCRIRE")

    # Styled HTML button for consistent look (still triggers form submit)
    st.markdown(
        """
        <div style="margin-top:10px;">
            <button class="gradient-btn" onclick="document.querySelector('form').dispatchEvent(new Event('submit', {cancelable: true}))">
                S'INSCRIRE
            </button>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------- Validation ----------------
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
        ok, msg = save_user(email_val, password)
        if ok:
            st.success(msg)
            st.info("Un email de confirmation a été simulé vers " + email_val)
            st.balloons()
            # clear fields
            st.session_state["email"] = ""
            st.session_state["password"] = ""
            st.session_state["confirm"] = ""
        else:
            st.error(msg)

# ---------------- Footer ----------------
st.markdown(
    """
    <div class="small-note">
      En cliquant sur <strong>S'INSCRIRE</strong>, tu acceptes nos Conditions et la Politique de confidentialité.
    </div>
    <div class="signin">
      Déjà un compte ? <a href="#" style="color: #ff5c9e; font-weight:700;">Se connecter</a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('</div>', unsafe_allow_html=True)
