"""
Page principale : Tableau de bord
"""
import streamlit as st
import pandas as pd
from src.data_operations import list_revenus, list_depenses, list_budgets
from src.analytics import monthly_summary, plot_category_comparison, plot_category_distribution
from src.database import get_user_id

# Vérification de l'authentification
username = st.session_state.get('username')
if not username:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()

user_id = get_user_id(username)
mois = st.session_state.get('mois', pd.Timestamp.today().strftime('%Y-%m'))
    
st.title("📊 Tableau de bord")

# Résumé mensuel
s = monthly_summary(user_id, mois)

# Métriques principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Revenus",
        f"{s['total_income']:,.2f} €".replace(",", " "),
        delta=None
    )

with col2:
    st.metric(
        "Dépensé",
        f"{s['total_spent']:,.2f} €".replace(",", " "),
        delta=None
    )

with col3:
    reste = s['overall_left']
    delta_color = "normal" if reste >= 0 else "inverse"
    st.metric(
        "Reste (global)",
        f"{reste:,.2f} €".replace(",", " "),
        delta=f"{reste:,.2f} €".replace(",", " ") if reste < 0 else None,
        delta_color=delta_color
    )

with col4:
    pourcentage = (s['total_spent'] / s['total_income'] * 100) if s['total_income'] > 0 else 0
    st.metric(
        "Taux d'utilisation",
        f"{pourcentage:.1f}%",
        delta=None
    )

st.divider()

# Graphiques
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Budget vs Dépenses")
    plot_category_comparison(user_id, mois)

with col_right:
    st.subheader("Répartition des dépenses")
    plot_category_distribution(user_id, mois)

st.divider()

# Tableau détaillé
st.subheader("Détail par catégorie")
df = s['per_category']

if df.empty:
    st.info("Aucune donnée de budget ou de dépense pour ce mois.")
else:
    # Formater le DataFrame pour l'affichage
    df_display = df.copy()
    df_display['Budget'] = df_display['Budget'].apply(lambda x: f"{x:,.2f} €".replace(",", " "))
    df_display['Dépensé'] = df_display['Dépensé'].apply(lambda x: f"{x:,.2f} €".replace(",", " "))
    df_display['Reste (catégorie)'] = df_display['Reste (catégorie)'].apply(lambda x: f"{x:,.2f} €".replace(",", " "))
    df_display['Pourcentage utilisé'] = df_display['Pourcentage utilisé'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )
    
    # Barre de progression pour chaque catégorie
    st.subheader("État des budgets par catégorie")
    for _, row in df.iterrows():
        budget = row['Budget']
        depense = row['Dépensé']
        pourcentage = row['Pourcentage utilisé']
        reste = row['Reste (catégorie)']
        
        # Déterminer la couleur de la barre
        if pourcentage > 100:
            color = "red"
        elif pourcentage > 80:
            color = "orange"
        else:
            color = "green"
        
        st.write(f"**{row['Catégorie']}**")
        st.progress(
            min(pourcentage / 100, 1.0),
            text=f"Dépensé: {depense:,.2f} € / Budget: {budget:,.2f} € ({pourcentage:.1f}%) - Reste: {reste:,.2f} €"
        )

