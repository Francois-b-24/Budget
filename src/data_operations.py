"""
Module pour les opérations de lecture/écriture sur la base de données
"""
import pandas as pd
import streamlit as st
from datetime import date
from .database import get_connection, get_user_id


# -----------------------
# Lecteurs mis en cache
# -----------------------
@st.cache_data
def list_categories(user_id: int, actives_seulement: bool = True) -> pd.DataFrame:
    """Liste les catégories d'un utilisateur"""
    conn = get_connection()
    q = "SELECT id, nom, actif FROM categories WHERE user_id = ?"
    if actives_seulement:
        q += " AND actif=1"
    q += " ORDER BY nom;"
    return pd.read_sql_query(q, conn, params=(user_id,))


@st.cache_data
def list_revenus(user_id: int, mois: str) -> pd.DataFrame:
    """Liste les revenus d'un utilisateur pour un mois donné"""
    conn = get_connection()
    return pd.read_sql_query(
        "SELECT id, origine, montant FROM revenus WHERE user_id=? AND mois=? ORDER BY id DESC;",
        conn, params=(user_id, mois)
    )


@st.cache_data
def list_budgets(user_id: int, mois: str) -> pd.DataFrame:
    """Liste les budgets d'un utilisateur pour un mois donné"""
    conn = get_connection()
    q = """
        SELECT b.id, b.categorie_id, c.nom AS categorie, b.budget
        FROM budgets b
        JOIN categories c ON c.id=b.categorie_id
        WHERE b.user_id=? AND b.mois=? AND c.actif=1
        ORDER BY c.nom
    """
    return pd.read_sql_query(q, conn, params=(user_id, mois))


@st.cache_data
def list_depenses(user_id: int, mois: str) -> pd.DataFrame:
    """Liste les dépenses d'un utilisateur pour un mois donné"""
    conn = get_connection()
    q = """
        SELECT d.id, d.date_depense, c.nom AS categorie, d.description, d.montant, d.categorie_id
        FROM depenses d
        JOIN categories c ON c.id=d.categorie_id
        WHERE d.user_id=? AND d.mois=?
        ORDER BY datetime(d.date_depense) DESC, d.id DESC
    """
    return pd.read_sql_query(q, conn, params=(user_id, mois))


@st.cache_data
def get_all_data(user_id: int) -> dict:
    """Récupère toutes les données d'un utilisateur pour analyses"""
    conn = get_connection()
    
    revenus = pd.read_sql_query(
        "SELECT * FROM revenus WHERE user_id=? ORDER BY mois, id",
        conn, params=(user_id,)
    )
    
    depenses = pd.read_sql_query(
        "SELECT d.*, c.nom AS categorie FROM depenses d LEFT JOIN categories c ON d.categorie_id=c.id WHERE d.user_id=? ORDER BY d.date_depense",
        conn, params=(user_id,)
    )
    
    budgets = pd.read_sql_query(
        "SELECT b.*, c.nom AS categorie FROM budgets b LEFT JOIN categories c ON b.categorie_id=c.id WHERE b.user_id=? ORDER BY b.mois, c.nom",
        conn, params=(user_id,)
    )
    
    return {
        'revenus': revenus,
        'depenses': depenses,
        'budgets': budgets
    }


def clear_cache():
    """Vide les caches de lecture"""
    list_categories.clear()
    list_revenus.clear()
    list_budgets.clear()
    list_depenses.clear()
    get_all_data.clear()


# -----------------------
# Écrivains (vider les caches après écriture)
# -----------------------

# Catégories
def add_categorie(user_id: int, nom: str):
    """Ajoute une catégorie pour un utilisateur"""
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO categories(user_id, nom, actif) VALUES (?, ?, 1);",
            (user_id, nom)
        )
    clear_cache()


def rename_categorie(user_id: int, cat_id: int, nouveau_nom: str):
    """Renomme une catégorie"""
    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE categories SET nom=? WHERE id=? AND user_id=?;",
            (nouveau_nom, cat_id, user_id)
        )
    clear_cache()


def toggle_categorie(user_id: int, cat_id: int, actif: int):
    """Active ou désactive une catégorie"""
    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE categories SET actif=? WHERE id=? AND user_id=?;",
            (actif, cat_id, user_id)
        )
    clear_cache()


# Revenus
def add_revenu(user_id: int, mois: str, origine: str, montant: float):
    """Ajoute un revenu"""
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO revenus(user_id, mois, origine, montant) VALUES(?,?,?,?);",
            (user_id, mois, origine, montant)
        )
    clear_cache()


def delete_revenu(user_id: int, id_rev: int):
    """Supprime un revenu"""
    conn = get_connection()
    with conn:
        conn.execute(
            "DELETE FROM revenus WHERE id=? AND user_id=?;",
            (id_rev, user_id)
        )
    clear_cache()


# Budgets
def update_budget(user_id: int, mois: str, categorie_id: int, budget: float):
    """Met à jour ou crée un budget"""
    conn = get_connection()
    with conn:
        conn.execute(
            """
            INSERT INTO budgets(user_id, mois, categorie_id, budget) VALUES(?,?,?,?)
            ON CONFLICT(user_id, mois, categorie_id) DO UPDATE SET budget=excluded.budget;
            """,
            (user_id, mois, categorie_id, budget)
        )
    clear_cache()


# Dépenses
def add_depense(user_id: int, date_depense: date, categorie_id: int, description_depense: str, montant: float, mois: str):
    """Ajoute une dépense"""
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO depenses(user_id, date_depense, categorie_id, description, montant, mois) VALUES(?,?,?,?,?,?);",
            (
                user_id,
                date_depense.isoformat() if isinstance(date_depense, date) else str(date_depense),
                categorie_id,
                description_depense,
                montant,
                mois
            )
        )
    clear_cache()


def delete_depense(user_id: int, id_dep: int):
    """Supprime une dépense"""
    conn = get_connection()
    with conn:
        conn.execute(
            "DELETE FROM depenses WHERE id=? AND user_id=?;",
            (id_dep, user_id)
        )
    clear_cache()

