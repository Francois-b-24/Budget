"""
Application principale de suivi budgétaire
Adaptée pour Streamlit Cloud avec authentification
"""
import streamlit as st
import pandas as pd
from src.auth import check_authentication, require_auth
from src.database import init_database, get_user_id, init_default_categories


# Configuration de la page
st.set_page_config(
    page_title="Suivi Budgétaire",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialiser la base de données
init_database()

# Vérifier l'authentification
auth_status, username = check_authentication()

if not auth_status:
    st.stop()

# L'utilisateur est authentifié
user_id = get_user_id(username)
init_default_categories(user_id)

# Initialiser le mois sélectionné dans session_state
if 'mois' not in st.session_state:
    st.session_state.mois = pd.Timestamp.today().strftime('%Y-%m')

# Sidebar avec sélecteur de mois et informations utilisateur
with st.sidebar:
    st.title("💰 Suivi Budgétaire")
    st.divider()
    
    # Informations utilisateur
    st.write(f"👤 **{st.session_state.get('name', username)}**")
    st.caption(f"Connecté en tant que : {username}")
    
    st.divider()
    
    # Sélecteur de mois
    st.subheader("📅 Sélection du mois")
    plage_mois = pd.date_range(
        start=pd.Timestamp.today() - pd.DateOffset(years=2),
        end=pd.Timestamp.today() + pd.DateOffset(years=1),
        freq='MS'
    )
    options = [m.strftime('%Y-%m') for m in plage_mois]
    
    current_index = options.index(st.session_state.mois) if st.session_state.mois in options else len(options) - 1
    
    mois_selectionne = st.selectbox(
        "Mois",
        options=options,
        index=current_index,
        format_func=lambda x: pd.Timestamp(x).strftime('%B %Y')
    )
    
    st.session_state.mois = mois_selectionne
    
    st.divider()

    # Navigation rapide
    st.subheader("🧭 Navigation")
    st.info("Utilisez les onglets en haut de la page pour naviguer.")

    st.divider()

    # Informations
    st.caption("💡 **Astuce** : Les données sont stockées par utilisateur et par mois.")

# Le reste de l'application est géré par les pages dans le dossier pages/
# Streamlit les charge automatiquement grâce à la structure de dossiers
