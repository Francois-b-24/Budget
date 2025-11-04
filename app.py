import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

# -----------------------
# Config de l'application
# -----------------------
st.set_page_config(
    page_title="Suivi Budgétaire",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------
# Utilitaires BDD
# -----------------------
@st.cache_resource
def obtenir_connexion():
    """Créer et retourner une connexion SQLite avec vérification de thread désactivée."""
    return sqlite3.connect('/Users/f.b/Desktop/Data_Science/Data_Science/Projets/Budget/budget_app.db', check_same_thread=False)

@st.cache_resource
def initialiser_bdd():
    """Initialiser les tables de la base de données si elles n'existent pas (idempotent)."""
    conn = obtenir_connexion()
    cur = conn.cursor()

    # Activation des clés étrangères
    cur.execute("PRAGMA foreign_keys = ON;")

    # Plusieurs revenus par mois
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS revenus (
               id INTEGER PRIMARY KEY,
               mois TEXT NOT NULL,
               origine TEXT NOT NULL,
               montant REAL NOT NULL
           );'''
    )

    # Catégories définies par l'utilisateur (suppression douce avec 'actif')
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS categories (
               id INTEGER PRIMARY KEY,
               nom TEXT NOT NULL UNIQUE,
               actif INTEGER NOT NULL DEFAULT 1
           );'''
    )

    # Budgets par catégorie et mois
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS budgets (
               id INTEGER PRIMARY KEY,
               mois TEXT NOT NULL,
               categorie_id INTEGER NOT NULL,
               budget REAL NOT NULL,
               UNIQUE(mois, categorie_id),
               FOREIGN KEY(categorie_id) REFERENCES categories(id) ON DELETE CASCADE
           );'''
    )

    # Dépenses réelles
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS depenses (
               id INTEGER PRIMARY KEY,
               date_depense TEXT NOT NULL,
               categorie_id INTEGER NOT NULL,
               description TEXT,
               montant REAL NOT NULL,
               mois TEXT NOT NULL,
               FOREIGN KEY(categorie_id) REFERENCES categories(id) ON DELETE SET NULL
           );'''
    )

    conn.commit()

    # Initialiser un ensemble simple de catégories par défaut si vide
    cur.execute("SELECT COUNT(*) FROM categories;")
    if cur.fetchone()[0] == 0:
        defaults = [
            ("Épargne",), ("Logement",), ("Alimentation" ,), ("Transport",),
            ("Électricité",), ("Internet + Mobile",), ("Loisirs",), ("Autres",)
        ]
        cur.executemany("INSERT INTO categories(nom) VALUES (?);", defaults)
        conn.commit()

initialiser_bdd()

# -----------------------
# Lecteurs mis en cache
# -----------------------
@st.cache_data
def lister_categories(actives_seulement: bool = True) -> pd.DataFrame:
    conn = obtenir_connexion()
    q = "SELECT id, nom, actif FROM categories" + (" WHERE actif=1" if actives_seulement else "") + " ORDER BY nom;"
    return pd.read_sql_query(q, conn)

@st.cache_data
def lister_revenus(mois: str) -> pd.DataFrame:
    conn = obtenir_connexion()
    return pd.read_sql_query("SELECT id, origine, montant FROM revenus WHERE mois=? ORDER BY id DESC;", conn, params=(mois,))

@st.cache_data
def lister_budgets(mois: str) -> pd.DataFrame:
    conn = obtenir_connexion()
    q = (
        """
        SELECT b.id, b.categorie_id, c.nom AS categorie, b.budget
        FROM budgets b
        JOIN categories c ON c.id=b.categorie_id
        WHERE b.mois=? AND c.actif=1
        ORDER BY c.nom
        """
    )
    return pd.read_sql_query(q, conn, params=(mois,))

@st.cache_data
def lister_depenses(mois: str) -> pd.DataFrame:
    conn = obtenir_connexion()
    q = (
        """
        SELECT d.id, d.date_depense, c.nom AS categorie, d.description, d.montant, d.categorie_id
        FROM depenses d
        JOIN categories c ON c.id=d.categorie_id
        WHERE d.mois=?
        ORDER BY datetime(d.date_depense) DESC, d.id DESC
        """
    )
    return pd.read_sql_query(q, conn, params=(mois,))

# -----------------------
# Écrivains (vider les caches après écriture)
# -----------------------
def _vider_caches_lecture():
    lister_categories.clear()
    lister_revenus.clear()
    lister_budgets.clear()
    lister_depenses.clear()

# Catégories
def ajouter_categorie(nom: str):
    conn = obtenir_connexion()
    with conn:
        conn.execute("INSERT OR IGNORE INTO categories(nom, actif) VALUES (?, 1);", (nom,))
    _vider_caches_lecture()

def renommer_categorie(cat_id: int, nouveau_nom: str):
    conn = obtenir_connexion()
    with conn:
        conn.execute("UPDATE categories SET nom=? WHERE id=?;", (nouveau_nom, cat_id))
    _vider_caches_lecture()

def activer_desactiver_categorie(cat_id: int, actif: int):
    conn = obtenir_connexion()
    with conn:
        conn.execute("UPDATE categories SET actif=? WHERE id=?;", (actif, cat_id))
    _vider_caches_lecture()

# Revenus
def ajouter_revenu(mois: str, origine: str, montant: float):
    conn = obtenir_connexion()
    with conn:
        conn.execute("INSERT INTO revenus(mois, origine, montant) VALUES(?,?,?);", (mois, origine, montant))
    _vider_caches_lecture()

def supprimer_revenu(id_rev: int):
    conn = obtenir_connexion()
    with conn:
        conn.execute("DELETE FROM revenus WHERE id=?;", (id_rev,))
    _vider_caches_lecture()

# Budgets
def mettre_a_jour_budget(mois: str, categorie_id: int, budget: float):
    conn = obtenir_connexion()
    with conn:
        conn.execute(
            """
            INSERT INTO budgets(mois, categorie_id, budget) VALUES(?,?,?)
            ON CONFLICT(mois, categorie_id) DO UPDATE SET budget=excluded.budget;
            """,
            (mois, categorie_id, budget)
        )
    _vider_caches_lecture()

# Dépenses
def ajouter_depense(date_depense: date, categorie_id: int, description_depense: str, montant: float, mois: str):
    conn = obtenir_connexion()
    with conn:
        conn.execute(
            "INSERT INTO depenses(date_depense, categorie_id, description, montant, mois) VALUES(?,?,?,?,?);",
            (date_depense.isoformat() if isinstance(date_depense, date) else str(date_depense), categorie_id, description_depense, montant, mois)
        )
    _vider_caches_lecture()

def supprimer_depense(id_dep: int):
    conn = obtenir_connexion()
    with conn:
        conn.execute("DELETE FROM depenses WHERE id=?;", (id_dep,))
    _vider_caches_lecture()

# -----------------------
# Aides : résumés
# -----------------------
@st.cache_data
def resume_mensuel(mois: str) -> dict:
    revenus = lister_revenus(mois)
    depenses = lister_depenses(mois)
    budgets = lister_budgets(mois)

    total_revenus = float(revenus['montant'].sum()) if not revenus.empty else 0.0
    total_depenses = float(depenses['montant'].sum()) if not depenses.empty else 0.0

    # Dépenses par catégorie
    par_categorie = depenses.groupby('categorie')['montant'].sum() if not depenses.empty else pd.Series(dtype=float)
    budget_map = dict(zip(budgets['categorie'], budgets['budget']))

    lignes = []
    categories = sorted(set(budget_map.keys()) | set(par_categorie.index))
    for c in categories:
        b = float(budget_map.get(c, 0.0))
        s = float(par_categorie.get(c, 0.0))
        lignes.append({
            'Catégorie': c,
            'Budget': b,
            'Dépensé': s,
            'Reste (catégorie)': b - s
        })
    df = pd.DataFrame(lignes).sort_values('Catégorie') if lignes else pd.DataFrame(columns=['Catégorie','Budget','Dépensé','Reste (catégorie)'])

    return {
        'total_income': total_revenus,
        'total_spent': total_depenses,
        'overall_left': total_revenus - total_depenses,
        'per_category': df
    }

# -----------------------
# État UI
# -----------------------
if 'mois' not in st.session_state:
    st.session_state.mois = pd.Timestamp.today().strftime('%Y-%m')

st.title("Assistant Budget Pas à Pas")

# Sélecteur de mois
plage_mois = pd.date_range(start="2024-01-01", end="2027-01-01", freq='MS')
options = [m.strftime('%Y-%m') for m in plage_mois]
st.session_state.mois = st.selectbox("Mois", options=options, index=options.index(st.session_state.mois) if st.session_state.mois in options else 0)

# Onglets : revenus, catégories & budgets, dépenses, tableau de bord
ong_revenus, ong_cats, ong_depenses, ong_tableau = st.tabs(["Revenus", "Catégories & Budgets", "Dépenses", "Tableau de bord"])

# -----------------------
# Onglet 1 : Revenus
# -----------------------
with ong_revenus:
    st.subheader("Revenus du mois sélectionné")
    df_revenus = lister_revenus(st.session_state.mois)
    if df_revenus.empty:
        st.info("Aucun revenu saisi pour ce mois.")
    else:
        total_rev = df_revenus['montant'].sum()
        st.metric("Total revenus", f"{total_rev:,.2f} €".replace(",", " "))
        st.dataframe(df_revenus.rename(columns={'origine': 'Origine', 'montant': 'Montant (€)'}), use_container_width=True)

    with st.form("form_ajout_revenu"):
        col1, col2, col3 = st.columns([2,1,1])
        origine = col1.text_input("Origine (ex: Salaire, APL, etc.)")
        montant = col2.number_input("Montant (€)", min_value=0.0, step=50.0)
        soumis = st.form_submit_button("Ajouter le revenu")
        if soumis and origine and montant > 0:
            ajouter_revenu(st.session_state.mois, origine, float(montant))
            st.success("Revenu ajouté.")

    # Contrôles simples de suppression
    if not df_revenus.empty:
        id_suppr = st.selectbox("Supprimer un revenu", options=["-"] + df_revenus['id'].astype(str).tolist())
        if id_suppr != "-":
            if st.button("Confirmer la suppression"):
                supprimer_revenu(int(id_suppr))
                st.success("Revenu supprimé.")

# -----------------------
# Onglet 2 : Catégories & Budgets
# -----------------------
with ong_cats:
    st.subheader("Catégories")
    categories = lister_categories(actives_seulement=False)

    # Ajouter une catégorie
    c1, c2 = st.columns([3,1])
    nouvelle_cat = c1.text_input("Nouvelle catégorie")
    if c2.button("Ajouter"):
        if nouvelle_cat:
            ajouter_categorie(nouvelle_cat)
            st.success(f"Catégorie '{nouvelle_cat}' ajoutée.")

    # Gestion des catégories
    if not categories.empty:
        for _, row in categories.iterrows():
            coln, colr, colt = st.columns([3,1,1])
            nouveau_nom = coln.text_input("", value=row['nom'], key=f"nomcat_{row['id']}")
            if colr.button("Renommer", key=f"renommer_{row['id']}"):
                renommer_categorie(int(row['id']), nouveau_nom)
                st.success("Renommée.")
            label_toggle = "Désactiver" if row['actif'] == 1 else "Activer"
            if colt.button(label_toggle, key=f"toggle_{row['id']}"):
                activer_desactiver_categorie(int(row['id']), 0 if row['actif'] == 1 else 1)
                st.success("Mise à jour de l'état.")

    st.divider()
    st.subheader("Budgets du mois")
    cats_actives = lister_categories(actives_seulement=True)
    df_budgets = lister_budgets(st.session_state.mois)
    existants = {int(r.categorie_id): float(r.budget) for r in df_budgets.itertuples(index=False)}

    for _, row in cats_actives.iterrows():
        cat_id = int(row['id'])
        val = existants.get(cat_id, 0.0)
        nouvelle_val = st.number_input(f"{row['nom']} (€)", min_value=0.0, value=float(val), step=10.0, key=f"bud_{cat_id}")
        if nouvelle_val != val:
            mettre_a_jour_budget(st.session_state.mois, cat_id, float(nouvelle_val))

# -----------------------
# Onglet 3 : Dépenses
# -----------------------
with ong_depenses:
    st.subheader("Saisir une dépense")
    cats_actives = lister_categories(actives_seulement=True)
    if cats_actives.empty:
        st.info("Aucune catégorie active. Ajoutez-en dans l'onglet précédent.")
    else:
        noms_cats = cats_actives['nom'].tolist()
        ids_cats = cats_actives['id'].tolist()
        with st.form("form_ajout_depense"):
            date_depense = st.date_input("Date", value=date.today())
            cat_choisie = st.selectbox("Catégorie", options=noms_cats)
            description_depense = st.text_input("Description")
            montant = st.number_input("Montant (€)", min_value=0.01, format="%.2f")
            if st.form_submit_button("Enregistrer la dépense"):
                idx = noms_cats.index(cat_choisie)
                ajouter_depense(date_depense, int(ids_cats[idx]), description_depense, float(montant), st.session_state.mois)
                st.success("Dépense enregistrée !")

    st.subheader("Historique des dépenses")
    df_depenses = lister_depenses(st.session_state.mois)
    if df_depenses.empty:
        st.info("Aucune dépense pour ce mois.")
    else:
        st.dataframe(df_depenses.rename(columns={"date_depense":"Date","categorie":"Catégorie","description":"Description","montant":"Montant (€)"}), use_container_width=True)
        id_suppr_dep = st.selectbox("Supprimer une dépense", options=["-"] + df_depenses['id'].astype(str).tolist())
        if id_suppr_dep != "-" and st.button("Confirmer la suppression de la dépense"):
            supprimer_depense(int(id_suppr_dep))
            st.success("Dépense supprimée.")

# -----------------------
# Onglet 4 : Tableau de bord
# -----------------------
with ong_tableau:
    st.subheader("Vue d'ensemble")
    s = resume_mensuel(st.session_state.mois)

    m1, m2, m3 = st.columns(3)
    m1.metric("Revenus", f"{s['total_income']:,.2f} €".replace(",", " "))
    m2.metric("Dépensé", f"{s['total_spent']:,.2f} €".replace(",", " "))
    m3.metric("Reste (global)", f"{s['overall_left']:,.2f} €".replace(",", " "))

    st.subheader("Dépenses par catégorie vs budget")
    df = s['per_category']
    if df.empty:
        st.info("Aucune donnée de budget ou de dépense pour ce mois.")
    else:
        st.dataframe(df, use_container_width=True)
        # Graphique en barres simple des dépenses par catégorie
        chart_data = df.set_index('Catégorie')[['Dépensé']]
        st.bar_chart(chart_data, use_container_width=True)