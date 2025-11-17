"""
Module d'authentification utilisateur
Utilise streamlit-authenticator pour la gestion des sessions
"""
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
from pathlib import Path


def load_config():
    """Charge la configuration d'authentification depuis secrets.toml ou config.yaml"""
    # Essayer d'abord avec secrets.toml (Streamlit Cloud)
    if "credentials" in st.secrets:
        # Construire un dict Python mutable à partir de st.secrets
        usernames = {}
        for username, data in st.secrets["credentials"]["usernames"].items():
            usernames[username] = {
                "email": data["email"],
                "name": data["name"],
                "password": data["password"],
                "failed_login_attempts": int(data.get("failed_login_attempts", 0)),
                "logged_in": bool(data.get("logged_in", False)),
            }

        return {
            "credentials": {
                "usernames": usernames
            },
            "cookie": {
                "expiry_days": st.secrets["cookie"]["expiry_days"],
                "key": st.secrets["cookie"]["key"],
                "name": st.secrets["cookie"]["name"],
            },
            "preauthorized": {
                "emails": st.secrets["preauthorized"]["emails"]
            }
        }

    # Sinon, chercher un fichier config.yaml local
    config_path = Path(".streamlit/config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as file:
            return yaml.load(file, Loader=SafeLoader)
    
    # Configuration par défaut pour le développement
    # ⚠️ Mot de passe : "Francoisking" déjà hashé avec streamlit-authenticator
    return {
        "credentials": {
            "usernames": {
                "admin": {
                    "email": "f.boussengui@gmail.com",
                    "failed_login_attempts": 0,
                    "logged_in": False,
                    "name": "Francoisb",
                    # Hash généré une fois pour toutes (ex. via un script séparé)
                    "password": "$2b$12$s1PpvW.rqip9ABV01/iIn.K1yyIVjy21v4Y9xGs4Q54GERWlCnlyC"
                }
            }
        },
        "cookie": {
            "expiry_days": 30,
            "key": "budget_app_key_change_in_production",
            "name": "budget_app_cookie"
        },
        "preauthorized": {
            "emails": []
        }
    }


def init_authenticator():
    """Initialise et retourne l'authentificateur Streamlit"""
    config = load_config()

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    return authenticator


def check_authentication():
    """Vérifie l'authentification et retourne le statut de connexion"""
    authenticator = init_authenticator()

    # Gérer la connexion/déconnexion
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = None
        st.session_state.username = None
        st.session_state.name = None

    # Tentative de connexion : la nouvelle API renseigne st.session_state
    if st.session_state.get('authentication_status') is None:
        authenticator.login(
            location='main',
            fields={
                'Form name': 'Connexion',
                'Username': "Nom d'utilisateur",
                'Password': 'Mot de passe',
                'Login': 'Connexion'
            }
        )

    auth_status = st.session_state.get('authentication_status')
    username = st.session_state.get('username')
    name = st.session_state.get('name')

    # Messages d'information
    if auth_status is False:
        st.error('Username/password incorrect')
    elif auth_status is None:
        st.warning('Veuillez entrer vos identifiants')

    # Gérer la déconnexion : le composant remet authentication_status à None
    if auth_status:
        authenticator.logout('Déconnexion', 'sidebar')

    return auth_status, username

    # Gérer la déconnexion
    if st.session_state.authentication_status:
        authenticator.logout('Déconnexion', 'sidebar')
        if not st.session_state.get('logged_in', True):
            st.session_state.authentication_status = None
            st.session_state.username = None
            st.session_state.name = None
            st.rerun()

    return st.session_state.get('authentication_status', False), st.session_state.get('username')


def require_auth():
    """Décorateur pour protéger les pages nécessitant une authentification"""
    auth_status, username = check_authentication()
    if not auth_status:
        st.stop()
    return username
