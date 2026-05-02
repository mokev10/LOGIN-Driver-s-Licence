# app.py
import streamlit as st
import re

st.set_page_config(page_title="TYNORAH - Sign Up", page_icon="https://img.icons8.com/external-inipagistudio-mixed-inipagistudio/24/external-ai-web-programmer-inipagistudio-mixed-inipagistudio.png", layout="centered")

# --- Styles CSS pour la carte et le bouton gradient ---
st.markdown(
    """
    <style>
    /* Fond de la page */
    .stApp {
        background: linear-gradient(180deg, #f7f8fc 0%, #ffffff 100%);
        font-family: 'Segoe UI', Roboto, Arial, sans-serif;
    }

    /* Carte blanche centrée */
    .card {
        background: #ffffff;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 10px 30px rgba(20, 20, 50, 0.08);
        max-width: 420px;
        margin: 40px auto;
    }

    /* Titre */
    .brand {
        font-weight: 700;
        font-size: 28px;
        letter-spacing: 1px;
        color: #2b2b3a;
        text-align: center;
        margin-bottom: 18px;
    }

    /* Labels et champs */
    .stTextInput>div>div>input, .stTextInput>div>div>textarea {
        border-radius: 10px;
        padding: 12px 14px;
        border: 1px solid #e6e6ef;
        background: #fbfbff;
    }

    /* Checkbox spacing */
    .terms {
        margin-top: 8px;
        margin-bottom: 12px;
        color: #6b6b7a;
        font-size: 14px;
    }

    /* Bouton gradient large */
    .gradient-btn {
        background: linear-gradient(90deg, #7b61ff 0%, #5ec8ff 100%);
        color: white !important;
        border: none;
        padding: 12px 18px;
        width: 100%;
        border-radius: 12px;
        font-weight: 700;
        font-size: 15px;
        cursor: pointer;
        box-shadow: 0 6px 18px rgba(92, 88, 255, 0.18);
    }

    .small-note {
        text-align: center;
        color: #8b8b9a;
        font-size: 13px;
        margin-top: 12px;
    }

    .signin {
        text-align: center;
        margin-top: 10px;
        font-size: 14px;
    }

    .signin a {
        color: #ff5c9e;
        font-weight: 600;
        text-decoration: none;
    }

    /* Responsive */
    @media (max-width: 480px) {
        .card { margin: 20px; padding: 20px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Card container ---
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown('<div class="brand">TYNORAH</div>', unsafe_allow_html=True)

# Use a form to group inputs and handle submission
with st.form(key="signup_form"):
    email = st.text_input("**Email address**", placeholder="you@example.com")
    password = st.text_input("**Password**", type="password", placeholder="Enter a strong password")
    confirm = st.text_input("**Confirm password**", type="password", placeholder="Re-enter your password")
    agree = st.checkbox("I agree to the terms")
    submitted = st.form_submit_button(label="SIGN UP")

    # Custom styled submit button (works visually but still triggers form submit)
    # We add a small HTML button purely for style; the real submit is the form_submit_button above.
    st.markdown(
        """
        <div style="margin-top:10px;">
            <button class="gradient-btn" onclick="document.querySelector('form').dispatchEvent(new Event('submit', {cancelable: true}))">
                SIGN UP
            </button>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Validation and feedback
def is_valid_email(addr: str) -> bool:
    # Simple regex for email validation
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", addr or ""))

if submitted:
    errors = []
    if not email or not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if password != confirm:
        errors.append("Passwords do not match.")
    if not agree:
        errors.append("You must agree to the terms to continue.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        # Simulate account creation success
        st.success("Account created successfully. Welcome to TYNORAH!")
        st.info("A confirmation email has been sent to " + email)

# Terms note and sign in link
st.markdown(
    """
    <div class="small-note">
        By clicking <strong>SIGN UP</strong>, you agree to our Terms of Service and Privacy Policy.
    </div>
    <div class="signin">
        Already have an account? <a href="#">Sign in</a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('</div>', unsafe_allow_html=True)
