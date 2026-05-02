# app.py
import streamlit as st
import streamlit.components.v1 as components
import re
import sqlite3
from hashlib import sha256

"""
TYNORAH - Auth complet et robuste pour redirection SAME-TAB

But:
- Fournir une application Streamlit complète (signup + login).
- Après succès (signup ou login), tenter une redirection DANS LE MÊME ONGLET
  de façon robuste en multipliant les méthodes JS et un fallback meta-refresh.
- Toujours afficher un lien cliquable et des messages de debug pour l'utilisateur.
- Code prêt à copier-coller dans GitHub et déployer sur Streamlit Cloud.

Usage:
- Déposer ce fichier app.py dans ton repo GitHub.
- Déployer sur Streamlit Cloud (pas besoin d'exécuter localement).
"""

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

# ---------------- Redirection SAME-TAB robuste ----------------
def redirect_same_tab(url: str, delay_seconds: int = 0):
    """
    Tentative robuste de redirection DANS LE MÊME ONGLET.
    Méthodes essayées côté client (JS), dans l'ordre :
      1) window.top.location.replace(url)  (meilleur pour iframe -> top-level)
      2) window.top.location.href = url
      3) window.location.replace(url)
      4) window.location.href = url
      5) location.assign(url)
      6) document.location = url
    Chaque tentative est entourée de try/catch et on enchaîne avec des timeouts
    pour maximiser les chances selon les politiques CSP/sandbox.
    Fallback : meta refresh + lien cliquable.
    """
    # JS multi-stratégies avec logs console pour debug
    js = f"""
    <script>
    (function() {{
      const target = "{url}";
      function tryReplaceTop() {{
        try {{
          if (window.top && window.top !== window) {{
            // Essayer replace sur top (ne crée pas d'historique)
            window.top.location.replace(target);
            console.log("redirect: window.top.location.replace -> attempted");
            return true;
          }}
        }} catch (e) {{
          console.warn("redirect: window.top.replace blocked:", e);
        }}
        return false;
      }}

      function tryHrefTop() {{
        try {{
          if (window.top && window.top !== window) {{
            window.top.location.href = target;
            console.log("redirect: window.top.location.href -> attempted");
            return true;
          }}
        }} catch (e) {{
          console.warn("redirect: window.top.href blocked:", e);
        }}
        return false;
      }}

      function tryReplaceSelf() {{
        try {{
          window.location.replace(target);
          console.log("redirect: window.location.replace -> attempted");
          return true;
        }} catch (e) {{
          console.warn("redirect: window.location.replace blocked:", e);
        }}
        return false;
      }}

      function tryHrefSelf() {{
        try {{
          window.location.href = target;
          console.log("redirect: window.location.href -> attempted");
          return true;
        }} catch (e) {{
          console.warn("redirect: window.location.href blocked:", e);
        }}
        return false;
      }}

      function tryAssign() {{
        try {{
          window.location.assign(target);
          console.log("redirect: window.location.assign -> attempted");
          return true;
        }} catch (e) {{
          console.warn("redirect: window.location.assign blocked:", e);
        }}
        return false;
      }}

      function tryDocumentLocation() {{
        try {{
          document.location = target;
          console.log("redirect: document.location -> attempted");
          return true;
        }} catch (e) {{
          console.warn("redirect: document.location blocked:", e);
        }}
        return false;
      }}

      // Sequence with small delays to allow each attempt to take effect if permitted
      try {{
        if (tryReplaceTop()) return;
      }} catch(e){{console.warn("err1", e)}}
      setTimeout(function() {{
        try {{
          if (tryHrefTop()) return;
        }} catch(e){{console.warn("err2", e)}}
      }}, 50);

      setTimeout(function() {{
        try {{
          if (tryReplaceSelf()) return;
        }} catch(e){{console.warn("err3", e)}}
      }}, 150);

      setTimeout(function() {{
        try {{
          if (tryHrefSelf()) return;
        }} catch(e){{console.warn("err4", e)}}
      }}, 300);

      setTimeout(function() {{
        try {{
          if (tryAssign()) return;
        }} catch(e){{console.warn("err5", e)}}
      }}, 500);

      setTimeout(function() {{
        try {{
          if (tryDocumentLocation()) return;
        }} catch(e){{console.warn("err6", e)}}
      }}, 800);

      // Si tout échoue, on loggue et on laisse le meta-refresh et le lien cliquable faire le job.
      setTimeout(function() {{
        console.warn("redirect: toutes les tentatives JS ont été effectuées; si la navigation est bloquée, vérifier la console et la politique CSP/sandbox.");
      }}, 1200);
    }})();
    </script>
    """
    # Exécuter le JS côté client via components.html (meilleur contexte d'exécution)
    try:
        components.html(js, height=0)
    except Exception as e:
        # Si components.html échoue côté serveur, on affiche un message et on continue avec fallback
        st.warning("Impossible d'exécuter le script de redirection côté client: " + str(e))

    # Meta refresh fallback (certaines politiques autorisent les meta tags)
    meta = f'<meta http-equiv="refresh" content="{delay_seconds};url={url}">'
    try:
        components.html(meta, height=0)
    except Exception:
        # Si components.html échoue, on ignore (on a déjà le lien cliquable)
        pass

    # Lien cliquable visible pour l'utilisateur si tout échoue
    st.markdown(
        f"""
        **Si la redirection automatique échoue :**
        - Clique sur ce lien pour continuer : [{url}]({url})
        - Vérifie la console du navigateur (F12 → Console) pour voir les erreurs JS ou les règles CSP/sandbox.
        """
    )

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
    .card { max-width: 720px; margin: 36px auto; background: var(--card); border-radius: 16px; padding: 26px; box-shadow: 0 14px 40px rgba(30,35,90,0.06); border: 1px solid rgba(124,124,160,0.06); transition: transform .35s ease; }
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
    .debug { margin-top:12px; padding:10px; background:#f8f9ff; border-radius:8px; color:#333; font-size:13px; }
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
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;"><div style="font-size:13px;color:#6b6b7a">Force du mot de passe</div><div style="font-weight:700;color:{color}">{label}</div></div>',
            unsafe_allow_html=True,
        )
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
                # Tentative de redirection SAME-TAB
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

# ---------------- Debug / Aide utilisateur ----------------
st.markdown(
    """
    <div class="debug">
      <strong>Si la redirection ne fonctionne toujours pas :</strong>
      <ul>
        <li>Ouvre la console du navigateur (F12 → Console) et copie-colle ici l'erreur JS affichée.</li>
        <li>Vérifie si l'app est affichée dans un <em>iframe</em> ou intégrée dans une autre page. Si oui, la page parente peut bloquer la navigation top-level (sandbox / allow-top-navigation).</li>
        <li>Les bloqueurs de pop-ups ou certaines politiques CSP peuvent empêcher la redirection. Essaie d'ouvrir l'app directement (URL Streamlit) dans un nouvel onglet pour tester.</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

# Bouton manuel pour retenter la redirection (utile pour debug)
if st.button("Retenter la redirection maintenant (même onglet)"):
    st.info("Nouvelle tentative de redirection...")
    redirect_same_tab(TARGET_URL, delay_seconds=1)

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
