# app.py
import streamlit as st
import streamlit.components.v1 as components
import re
import sqlite3
from hashlib import sha256

# ---------------- Configuration ----------------
st.set_page_config(page_title="TYNORAH - Auth", page_icon="🌀", layout="centered")
TARGET_URL = "https://driver-license.streamlit.app/"

# ---------------- Helpers ----------------
def is_valid_email(addr: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (addr or "").strip()))

def password_strength(pw: str):
    score = 0
    if len(pw) >= 8: score += 1
    if re.search(r"[A-Z]", pw) and re.search(r"[a-z]", pw): score += 1
    if re.search(r"\d", pw): score += 1
    if re.search(r"[^\w\s]", pw): score += 1
    labels = ["Très faible", "Faible", "Moyen", "Fort", "Très fort"]
    colors = ["#ff6b6b", "#ff9f6b", "#ffd36b", "#7be36b", "#2ee6a7"]
    widths = ["6%", "28%", "56%", "80%", "100%"]
    return score, labels[score], colors[score], widths[score]

# ---------------- Simple SQLite DB (demo) ----------------
DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password_hash TEXT)"
    )
    conn.commit()
    conn.close()

def save_user(email: str, password: str):
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
        return False, f"Erreur interne: {e}"

def check_credentials(email: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    return sha256(password.encode("utf-8")).hexdigest() == row[0]

init_db()

# ---------------- Redirection same-tab robuste ----------------
def redirect_same_tab(url: str, delay_seconds: int = 0):
    """
    Tentative de redirection dans le même onglet :
    1) Exécute un script JS qui tente window.top.location.href (pour iframe) puis window.location.href.
    2) Ajoute un meta refresh en fallback.
    3) Affiche un lien cliquable en dernier recours.
    """
    js = f"""
    <script>
    (function() {{
      try {{
        // Si l'app est dans un iframe, tenter la navigation top-level
        if (window.top && window.top !== window) {{
          try {{
            window.top.location.href = "{url}";
            return;
          }} catch (e) {{
            // Si cross-origin bloque window.top, on continue vers window.location
            console.warn("window.top navigation blocked, fallback to window.location");
          }}
        }}
        // Navigation dans le même onglet
        window.location.href = "{url}";
      }} catch (err) {{
        console.error("Redirect JS failed:", err);
      }}
    }})();
    </script>
    """
    # Exécute le JS côté client
    components.html(js, height=0)

    # Meta refresh fallback (certaines politiques CSP autorisent les meta tags)
    meta = f'<meta http-equiv="refresh" content="{delay_seconds};url={url}">'
    components.html(meta, height=0)

    # Lien cliquable visible pour l'utilisateur si tout échoue
    st.markdown(f"[Si la redirection automatique échoue, clique ici pour continuer]({url})")

# ---------------- CSS (soigné, transitions) ----------------
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
    }
    .stApp { background: linear-gradient(180deg, var(--bg-1) 0%, #ffffff 100%); font-family: Inter, Roboto, Arial, sans-serif; }
    .card { max-width: 640px; margin: 36px auto; background: var(--card); border-radius: 16px; padding: 26px; box-shadow: 0 14px 40px rgba(30,35,90,0.06); border: 1px solid rgba(124,124,160,0.06); transition: transform .35s ease; }
    .brand { font-weight:800; font-size:28px; color:#111; }
    .subtitle { color:var(--muted); margin-top:6px; margin-bottom:18px; font-size:14px; }
    .stTextInput>div>div>input { border-radius:10px; padding:10px 12px; border:1px solid #eef0fb; background:linear-gradient(180deg,#fff,#fbfbff); transition: box-shadow .18s ease, transform .12s ease; }
    .stTextInput>div>div>input:focus { border-color: rgba(123,97,255,0.9); box-shadow: 0 8px 24px rgba(123,97,255,0.08); transform: translateY(-2px); }
    .gradient-btn { background: linear-gradient(90deg, var(--accent-a) 0%, var(--accent-b) 50%, var(--accent-c) 100%); color:#fff; padding:12px 14px; border-radius:12px; width:100%; border:none; font-weight:800; cursor:pointer; box-shadow: 0 10px 30px rgba(92,88,255,0.12); transition: transform .18s ease, background-position .6s ease; background-size:200% 100%; }
    .gradient-btn:hover { transform: translateY(-3px); background-position:100% 0; box-shadow: 0 18px 40px rgba(92,88,255,0.16); }
    .pw-meter { height:10px; border-radius:8px; background: linear-gradient(90deg,#f2f6ff,#f8fbff); overflow:hidden; margin-top:8px; }
    .pw-meter > div { height:100%; border-radius:8px; transition: width .35s cubic-bezier(.2,.9,.2,1), background .35s ease; }
    .small-note { text-align:center; color:var(--muted); font-size:13px; margin-top:14px; }
    .signin { text-align:center; margin-top:10px; font-size:14px; }
    .signin a { color: var(--accent-c); font-weight:700; text-decoration:none; }
    @media (max-width:600px) { .card { margin:18px; padding:18px; } .brand { font-size:22px; } }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- UI ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="brand">TYNORAH</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Inscription / Connexion — redirection dans le même onglet</div>', unsafe_allow_html=True)

tabs = st.tabs(["Sign Up", "Login"])

# --- Sign Up tab ---
with tabs[0]:
    with st.form("signup_form"):
        st.markdown("**Email**")
        email = st.text_input("", placeholder="you@example.com", key="su_email")
        st.markdown("**Password**")
        password = st.text_input("", type="password", placeholder="8 caractères minimum", key="su_pw")
        st.markdown("**Confirm password**")
        confirm = st.text_input("", type="password", placeholder="Re-saisir le mot de passe", key="su_confirm")
        agree = st.checkbox("J'accepte les conditions d'utilisation", key="su_agree")
        submitted = st.form_submit_button("S'INSCRIRE")

        # Password strength visual
        score, label, color, width = password_strength(password or "")
        st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;"><div style="font-size:13px;color:#6b6b7a">Force du mot de passe</div><div style="font-weight:700;color:{color}">{label}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="pw-meter"><div style="width:{width};background:{color}"></div></div>', unsafe_allow_html=True)

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
                st.info("Redirection en cours dans le même onglet...")
                # Rediriger dans le même onglet (robuste)
                redirect_same_tab(TARGET_URL, delay_seconds=1)
            else:
                st.error(msg)

# --- Login tab ---
with tabs[1]:
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
                st.success("Connexion réussie. Redirection dans le même onglet...")
                redirect_same_tab(TARGET_URL, delay_seconds=1)
            else:
                st.error("Identifiants incorrects.")

# ---------------- Footer ----------------
st.markdown(
    """
    <div class="small-note">
      En cliquant sur <strong>S'INSCRIRE</strong> ou <strong>SE CONNECTER</strong>, tu acceptes nos Conditions et la Politique de confidentialité.
    </div>
    <div class="signin">
      Déjà un compte ? <a href="#" style="color:#ff5c9e;font-weight:700;">Se connecter</a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('</div>', unsafe_allow_html=True)
