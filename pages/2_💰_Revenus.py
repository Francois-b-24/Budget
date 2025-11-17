"""
Page de gestion des revenus
"""
import streamlit as st
import pandas as pd
from src.data_operations import list_revenus, add_revenu, delete_revenu
from src.database import get_user_id

# Vérification de l'authentification
username = st.session_state.get('username')
if not username:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()

user_id = get_user_id(username)
mois = st.session_state.get('mois', pd.Timestamp.today().strftime('%Y-%m'))

st.title("💰 Revenus")
st.caption(f"Mois sélectionné : {mois}")

# Liste des revenus
st.subheader("Revenus du mois")
df_revenus = list_revenus(user_id, mois)

if df_revenus.empty:
    st.info("Aucun revenu saisi pour ce mois.")
    total_rev = 0
else:
    total_rev = df_revenus['montant'].sum()
    st.metric("Total revenus", f"{total_rev:,.2f} €".replace(",", " "))
    
    # Afficher le tableau
    df_display = df_revenus.copy()
    df_display = df_display.rename(columns={
        'origine': 'Origine',
        'montant': 'Montant (€)'
    })
    df_display['Montant (€)'] = df_display['Montant (€)'].apply(lambda x: f"{x:,.2f} €".replace(",", " "))
    df_display = df_display.drop(columns=['id'])
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)

st.divider()

# Formulaire d'ajout
st.subheader("Ajouter un revenu")
with st.form("form_ajout_revenu", clear_on_submit=True):
    col1, col2 = st.columns([2, 1])
    origine = col1.text_input("Origine", placeholder="Ex: Salaire, APL, Prime, etc.")
    montant = col2.number_input("Montant (€)", min_value=0.0, step=10.0, format="%.2f")
    
    submitted = st.form_submit_button("➕ Ajouter le revenu", use_container_width=True)
    
    if submitted:
        if not origine:
            st.error("Veuillez saisir une origine.")
        elif montant <= 0:
            st.error("Le montant doit être supérieur à 0.")
        else:
            add_revenu(user_id, mois, origine, float(montant))
            st.success("✅ Revenu ajouté avec succès !")
            st.rerun()

# Suppression
if not df_revenus.empty:
    st.divider()
    st.subheader("Supprimer un revenu")
    revenu_options = {
        f"{row['origine']} - {row['montant']:,.2f} €": row['id']
        for _, row in df_revenus.iterrows()
    }
    
    selected = st.selectbox(
        "Sélectionner un revenu à supprimer",
        options=["-"] + list(revenu_options.keys())
    )
    
    if selected != "-":
        revenu_id = revenu_options[selected]
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Supprimer", type="primary"):
                delete_revenu(user_id, revenu_id)
                st.success("✅ Revenu supprimé.")
                st.rerun()

