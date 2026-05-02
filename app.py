# app.py
import streamlit as st
import re

st.set_page_config(page_title="TYNORAH", layout="centered", initial_sidebar_state="collapsed")

# Minimal CSS
st.markdown(
    """
    <style>
    :root {
      --bg: #ffffff;
      --muted: #8a8f98;
      --accent: #6b63ff;
    }
    .stApp { background: var(--bg); font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; }
    .container {
      max-width: 420px;
      margin: 48px auto;
      padding: 28px;
      border-radius: 12px;
      background: transparent;
    }
    .brand { font-weight:700; font-size:22px; color:#111; margin-bottom:6px; }
    .hint { color:var(--muted); font-size:13px; margin-bottom:18px; }
    .stTextInput>div>div>input { border-radius:10px; padding:10px 12px; border:1px solid #ececf2; }
    .submit { background: var(--accent); color:#fff; border-radius:10px; padding:10px 12px; width:100%; font-weight:700; border:none; }
    .note { color:var(--muted); font-size:13px; text-align:center; margin-top:12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="container">', unsafe_allow_html=True)
st.markdown('<div class="brand">TYNORAH</div>', unsafe_allow_html=True)
st.markdown('<div class="hint">Créer un compte — interface la plus simple possible</div>', unsafe_allow_html=True)

# Form
with st.form("minimal_signup"):
    email = st.text_input("**Email**", placeholder="you@example.com")
    password = st.text_input("**Mot de passe**", type="password", placeholder="8 caractères minimum")
    confirm = st.text_input("**Confirmer mot de passe**", type="password", placeholder="Re-saisir le mot de passe")
    agree = st.checkbox("J'accepte les conditions")
    submitted = st.form_submit_button("S'INSCRIRE")

# Validation
def valid_email(e: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (e or "").strip()))

if submitted:
    errors = []
    if not valid_email(email):
        errors.append("Email invalide.")
    if not password or len(password) < 8:
        errors.append("Le mot de passe doit contenir au moins 8 caractères.")
    if password != confirm:
        errors.append("Les mots de passe ne correspondent pas.")
    if not agree:
        errors.append("Tu dois accepter les conditions.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        st.success("Compte créé. Bienvenue.")
        st.info(f"Confirmation envoyée à {email}")

# Footer minimal
st.markdown('<div class="note">En cliquant sur S\'INSCRIRE tu acceptes nos Conditions</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
