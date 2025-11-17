"""
Page de gestion des catégories et budgets
"""
import streamlit as st
import pandas as pd
from src.data_operations import (
    list_categories, add_categorie, rename_categorie, toggle_categorie,
    list_budgets, update_budget
)
from src.database import get_user_id, init_default_categories

# Vérification de l'authentification
username = st.session_state.get('username')
if not username:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()

user_id = get_user_id(username)
mois = st.session_state.get('mois', pd.Timestamp.today().strftime('%Y-%m'))

# Initialiser les catégories par défaut si nécessaire
init_default_categories(user_id)

st.title("📁 Catégories et Budgets")
st.caption(f"Mois sélectionné : {mois}")

# Section Catégories
st.subheader("Gestion des catégories")

# Ajouter une catégorie
with st.expander("➕ Ajouter une nouvelle catégorie", expanded=False):
    col1, col2 = st.columns([3, 1])
    nouvelle_cat = col1.text_input("Nom de la catégorie", key="new_cat_input")
    if col2.button("Ajouter", key="add_cat_btn"):
        if nouvelle_cat:
            try:
                add_categorie(user_id, nouvelle_cat)
                st.success(f"✅ Catégorie '{nouvelle_cat}' ajoutée.")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")
        else:
            st.warning("Veuillez saisir un nom de catégorie.")

# Liste des catégories
categories = list_categories(user_id, actives_seulement=False)

if categories.empty:
    st.info("Aucune catégorie définie. Ajoutez-en une ci-dessus.")
else:
    st.write("**Catégories existantes :**")
    
    # Séparer actives et inactives
    categories_actives = categories[categories['actif'] == 1]
    categories_inactives = categories[categories['actif'] == 0]
    
    if not categories_actives.empty:
        st.write("**Actives :**")
        for _, row in categories_actives.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                nouveau_nom = st.text_input(
                    "",
                    value=row['nom'],
                    key=f"nomcat_{row['id']}",
                    label_visibility="collapsed"
                )
            with col2:
                if st.button("✏️ Renommer", key=f"renommer_{row['id']}"):
                    if nouveau_nom and nouveau_nom != row['nom']:
                        try:
                            rename_categorie(user_id, int(row['id']), nouveau_nom)
                            st.success("✅ Catégorie renommée.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : {e}")
            with col3:
                if st.button("❌ Désactiver", key=f"toggle_{row['id']}"):
                    toggle_categorie(user_id, int(row['id']), 0)
                    st.success("✅ Catégorie désactivée.")
                    st.rerun()
    
    if not categories_inactives.empty:
        st.write("**Inactives :**")
        for _, row in categories_inactives.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text_input(
                    "",
                    value=row['nom'],
                    key=f"nomcat_inact_{row['id']}",
                    label_visibility="collapsed",
                    disabled=True
                )
            with col2:
                if st.button("✅ Activer", key=f"toggle_inact_{row['id']}"):
                    toggle_categorie(user_id, int(row['id']), 1)
                    st.success("✅ Catégorie activée.")
                    st.rerun()

st.divider()

# Section Budgets
st.subheader("Budgets du mois")
cats_actives = list_categories(user_id, actives_seulement=True)
df_budgets = list_budgets(user_id, mois)
existants = {int(r.categorie_id): float(r.budget) for r in df_budgets.itertuples(index=False)}

if cats_actives.empty:
    st.info("Aucune catégorie active. Activez ou créez des catégories ci-dessus.")
else:
    st.write("Définissez le budget pour chaque catégorie active :")
    
    # Formulaire pour tous les budgets
    with st.form("form_budgets"):
        budgets_dict = {}
        for _, row in cats_actives.iterrows():
            cat_id = int(row['id'])
            val = existants.get(cat_id, 0.0)
            budgets_dict[cat_id] = st.number_input(
                f"{row['nom']} (€)",
                min_value=0.0,
                value=float(val),
                step=10.0,
                format="%.2f",
                key=f"bud_{cat_id}"
            )
        
        submitted = st.form_submit_button("💾 Enregistrer les budgets", use_container_width=True)
        
        if submitted:
            for cat_id, budget_val in budgets_dict.items():
                if budget_val != existants.get(cat_id, 0.0):
                    update_budget(user_id, mois, cat_id, float(budget_val))
            st.success("✅ Budgets enregistrés avec succès !")
            st.rerun()

