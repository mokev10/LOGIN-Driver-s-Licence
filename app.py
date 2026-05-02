# app.py
import streamlit as st
import re
import sqlite3
from hashlib import sha256
import streamlit.components.v1 as components

TARGET_URL = "https://driver-license.streamlit.app/"

st.set_page_config(page_title="TYNORAH - Auth", layout="centered")

# --- Minimal UI ---
st.markdown("<div style='max-width:640px;margin:28px auto;padding:20px;border-radius:12px;background:#fff;box-shadow:0 8px 30px rgba(0,0,0,0.04)'><h2>TYNORAH</h2><p style='color:#666'>Sign up / Login demo</p></div>", unsafe_allow_html=True)

# --- Simple DB ---
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

# --- Helpers ---
def is_valid_email(addr: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (addr or "").strip()))

def do_redirect_js(url: str, new_tab: bool = False) -> None:
    """Try redirect using components.html (works better than st.markdown for JS)."""
    if new_tab:
        js = f"<script>window.open('{url}', '_blank');</script>"
    else:
        js = f"<script>window.location.href = '{url}';</script>"
    # components.html executes the JS in the browser context
    components.html(js, height=0)

def do_meta_refresh(url: str, delay: int = 1) -> None:
    """Fallback: meta refresh (some CSPs still allow it)."""
    html = f"""<meta http-equiv="refresh" content="{delay};url={url}">"""
    components.html(html, height=0)

# --- Auth UI (signup + login) ---
tabs = st.tabs(["Sign Up", "Login"])

with tabs[0]:
    with st.form("signup"):
        email = st.text_input("Email", key="su_email")
        pw = st.text_input("Password", type="password", key="su_pw")
        pwc = st.text_input("Confirm", type="password", key="su_confirm")
        agree = st.checkbox("J'accepte les conditions", key="su_agree")
        submitted = st.form_submit_button("S'INSCRIRE")
    if submitted:
        errs = []
        if not is_valid_email(email): errs.append("Email invalide.")
        if not pw or len(pw) < 8: errs.append("Mot de passe trop court.")
        if pw != pwc: errs.append("Les mots de passe ne correspondent pas.")
        if not agree: errs.append("Accepte les conditions.")
        if errs:
            for e in errs: st.error(e)
        else:
            ok, msg = save_user(email.strip(), pw)
            if ok:
                st.success(msg)
                st.info("Tentative de redirection vers la page externe...")
                # 1) Try components JS redirect (same tab)
                try:
                    do_redirect_js(TARGET_URL, new_tab=False)
                    st.write("Redirection JS envoyée (même onglet). Si rien ne se passe, voir les alternatives ci‑dessous.")
                except Exception as e:
                    st.warning("Impossible d'exécuter JS via components: " + str(e))
                    # 2) Fallback meta refresh
                    do_meta_refresh(TARGET_URL, delay=1)
                    st.write("Fallback meta refresh inséré.")
                # 3) Always show clickable link as last resort
                st.markdown(f"[Si la redirection ne fonctionne pas, clique ici pour ouvrir la page]({TARGET_URL})")
            else:
                st.error(msg)

with tabs[1]:
    with st.form("login"):
        le = st.text_input("Email", key="li_email")
        lpw = st.text_input("Password", type="password", key="li_pw")
        lsub = st.form_submit_button("SE CONNECTER")
    if lsub:
        if not is_valid_email(le):
            st.error("Email invalide.")
        elif not lpw:
            st.error("Mot de passe requis.")
        else:
            if check_credentials(le.strip(), lpw):
                st.success("Connexion réussie. Tentative de redirection...")
                # Try JS redirect in new tab first (less likely blocked)
                try:
                    do_redirect_js(TARGET_URL, new_tab=True)
                    st.write("Tentative d'ouverture dans un nouvel onglet envoyée.")
                except Exception:
                    do_meta_refresh(TARGET_URL, delay=1)
                    st.write("Fallback meta refresh inséré.")
                st.markdown(f"[Si la redirection ne fonctionne pas, clique ici]({TARGET_URL})")
            else:
                st.error("Identifiants incorrects.")

# --- Debugging hints visible à l'utilisateur ---
st.markdown("---")
st.markdown("**Si la redirection bloque encore, vérifie :**")
st.markdown("- Console du navigateur (F12) pour voir les erreurs JS ou les règles CSP.")
st.markdown("- Si l'app est affichée dans un iframe, la navigation top-level peut être bloquée.")
st.markdown("- Les bloqueurs de pop-ups peuvent empêcher l'ouverture dans un nouvel onglet.")
st.markdown("- Essaie d'ouvrir l'app dans un navigateur différent ou en mode incognito.")
