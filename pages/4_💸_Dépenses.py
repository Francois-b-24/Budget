"""
Page de gestion des dépenses
"""
import streamlit as st
import pandas as pd
from datetime import date
from src.data_operations import list_depenses, add_depense, delete_depense, list_categories
from src.database import get_user_id

# Vérification de l'authentification
username = st.session_state.get('username')
if not username:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()

user_id = get_user_id(username)
mois = st.session_state.get('mois', pd.Timestamp.today().strftime('%Y-%m'))

st.title("💸 Dépenses")
st.caption(f"Mois sélectionné : {mois}")

# Formulaire d'ajout
st.subheader("Saisir une dépense")
cats_actives = list_categories(user_id, actives_seulement=True)

if cats_actives.empty:
    st.warning("⚠️ Aucune catégorie active. Ajoutez-en dans l'onglet 'Catégories et Budgets'.")
else:
    noms_cats = cats_actives['nom'].tolist()
    ids_cats = cats_actives['id'].tolist()
    
    with st.form("form_ajout_depense", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_depense = col1.date_input("Date", value=date.today())
        cat_choisie = col2.selectbox("Catégorie", options=noms_cats)
        
        description_depense = st.text_input("Description", placeholder="Ex: Courses supermarché, Essence, etc.")
        
        col3, col4 = st.columns([1, 3])
        montant = col3.number_input("Montant (€)", min_value=0.01, step=0.01, format="%.2f")
        
        submitted = st.form_submit_button("➕ Enregistrer la dépense", use_container_width=True)
        
        if submitted:
            idx = noms_cats.index(cat_choisie)
            mois_depense = date_depense.strftime('%Y-%m')
            
            # Vérifier que la dépense est dans le bon mois
            if mois_depense != mois:
                st.warning(f"⚠️ La date sélectionnée ({date_depense.strftime('%d/%m/%Y')}) correspond au mois {mois_depense}, pas au mois sélectionné ({mois}).")
                if st.button("Enregistrer quand même"):
                    add_depense(user_id, date_depense, int(ids_cats[idx]), description_depense, float(montant), mois_depense)
                    st.success("✅ Dépense enregistrée !")
                    st.rerun()
            else:
                add_depense(user_id, date_depense, int(ids_cats[idx]), description_depense, float(montant), mois)
                st.success("✅ Dépense enregistrée !")
                st.rerun()

st.divider()

# Historique des dépenses
st.subheader("Historique des dépenses")
df_depenses = list_depenses(user_id, mois)

if df_depenses.empty:
    st.info("Aucune dépense pour ce mois.")
else:
    # Métrique totale
    total_dep = df_depenses['montant'].sum()
    st.metric("Total dépensé ce mois", f"{total_dep:,.2f} €".replace(",", " "))
    
    # Tableau des dépenses
    df_display = df_depenses.copy()
    df_display = df_display.rename(columns={
        "date_depense": "Date",
        "categorie": "Catégorie",
        "description": "Description",
        "montant": "Montant (€)"
    })
    
    # Formater la date
    df_display['Date'] = pd.to_datetime(df_display['Date']).dt.strftime('%d/%m/%Y')
    df_display['Montant (€)'] = df_display['Montant (€)'].apply(lambda x: f"{x:,.2f} €".replace(",", " "))
    df_display = df_display.drop(columns=['id', 'categorie_id'])
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Suppression
    st.divider()
    st.subheader("Supprimer une dépense")
    depense_options = {
        f"{row['date_depense']} - {row['categorie']} - {row['description']} ({row['montant']:,.2f} €)": row['id']
        for _, row in df_depenses.iterrows()
    }
    
    selected = st.selectbox(
        "Sélectionner une dépense à supprimer",
        options=["-"] + list(depense_options.keys())
    )
    
    if selected != "-":
        depense_id = depense_options[selected]
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Supprimer", type="primary"):
                delete_depense(user_id, depense_id)
                st.success("✅ Dépense supprimée.")
                st.rerun()

