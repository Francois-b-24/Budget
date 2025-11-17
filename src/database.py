"""
Module de gestion de la base de données SQLite
Adapté pour Streamlit Cloud avec chemins relatifs
"""
import sqlite3
import os
import streamlit as st
from pathlib import Path


def get_db_path():
    """Retourne le chemin de la base de données, adapté pour Streamlit Cloud"""
    # Pour Streamlit Cloud, utiliser le dossier .streamlit/data
    # En développement local, utiliser data/
    # On détecte Streamlit Cloud en vérifiant si le dossier .streamlit existe
    # ou en utilisant une variable d'environnement
    if os.getenv("STREAMLIT_SHARING_MODE") or os.path.exists(".streamlit"):
        # En production Streamlit Cloud ou si .streamlit existe
        db_dir = Path(".streamlit/data")
    else:
        # En développement local
        db_dir = Path("data")
    
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "budget_app.db"


@st.cache_resource
def get_connection():
    """Créer et retourner une connexion SQLite avec vérification de thread désactivée."""
    db_path = get_db_path()
    return sqlite3.connect(str(db_path), check_same_thread=False)


@st.cache_resource
def init_database():
    """Initialiser les tables de la base de données si elles n'existent pas (idempotent)."""
    conn = get_connection()
    cur = conn.cursor()

    # Activation des clés étrangères
    cur.execute("PRAGMA foreign_keys = ON;")

    # Table des utilisateurs (pour authentification multi-utilisateurs)
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY,
               username TEXT NOT NULL UNIQUE,
               email TEXT,
               created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
           );'''
    )

    # Plusieurs revenus par mois et utilisateur
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS revenus (
               id INTEGER PRIMARY KEY,
               user_id INTEGER NOT NULL,
               mois TEXT NOT NULL,
               origine TEXT NOT NULL,
               montant REAL NOT NULL,
               FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
           );'''
    )

    # Catégories définies par l'utilisateur (suppression douce avec 'actif')
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS categories (
               id INTEGER PRIMARY KEY,
               user_id INTEGER NOT NULL,
               nom TEXT NOT NULL,
               actif INTEGER NOT NULL DEFAULT 1,
               UNIQUE(user_id, nom),
               FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
           );'''
    )

    # Budgets par catégorie et mois
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS budgets (
               id INTEGER PRIMARY KEY,
               user_id INTEGER NOT NULL,
               mois TEXT NOT NULL,
               categorie_id INTEGER NOT NULL,
               budget REAL NOT NULL,
               UNIQUE(user_id, mois, categorie_id),
               FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
               FOREIGN KEY(categorie_id) REFERENCES categories(id) ON DELETE CASCADE
           );'''
    )

    # Dépenses réelles
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS depenses (
               id INTEGER PRIMARY KEY,
               user_id INTEGER NOT NULL,
               date_depense TEXT NOT NULL,
               categorie_id INTEGER NOT NULL,
               description TEXT,
               montant REAL NOT NULL,
               mois TEXT NOT NULL,
               FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
               FOREIGN KEY(categorie_id) REFERENCES categories(id) ON DELETE SET NULL
           );'''
    )

    conn.commit()
    return conn


def get_user_id(username: str) -> int:
    """Récupère ou crée un utilisateur et retourne son ID"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Vérifier si l'utilisateur existe
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cur.fetchone()
    
    if result:
        return result[0]
    else:
        # Créer l'utilisateur
        cur.execute("INSERT INTO users(username) VALUES (?)", (username,))
        conn.commit()
        return cur.lastrowid


def init_default_categories(user_id: int):
    """Initialiser les catégories par défaut pour un utilisateur"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Vérifier si l'utilisateur a déjà des catégories
    cur.execute("SELECT COUNT(*) FROM categories WHERE user_id = ?", (user_id,))
    if cur.fetchone()[0] == 0:
        defaults = [
            ("Épargne",), ("Logement",), ("Alimentation",), ("Transport",),
            ("Électricité",), ("Internet + Mobile",), ("Loisirs",), ("Autres",)
        ]
        cur.executemany(
            "INSERT INTO categories(user_id, nom) VALUES (?, ?);",
            [(user_id, cat[0]) for cat in defaults]
        )
        conn.commit()

