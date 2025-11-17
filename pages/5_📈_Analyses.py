"""
Page d'analyses avancées pour data scientists
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.data_operations import get_all_data
from src.analytics import plot_trends, export_data
from src.database import get_user_id

# Vérification de l'authentification
username = st.session_state.get('username')
if not username:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()

user_id = get_user_id(username)

st.title("📈 Analyses Avancées")
st.caption("Outils d'analyse pour data scientists")

# Sélection de la période
st.subheader("Période d'analyse")
col1, col2 = st.columns(2)

with col1:
    date_debut = st.date_input(
        "Date de début",
        value=pd.Timestamp.today() - pd.DateOffset(months=6),
        max_value=pd.Timestamp.today()
    )

with col2:
    date_fin = st.date_input(
        "Date de fin",
        value=pd.Timestamp.today(),
        max_value=pd.Timestamp.today()
    )

if date_debut > date_fin:
    st.error("La date de début doit être antérieure à la date de fin.")
    st.stop()

# Générer la liste des mois
months = pd.date_range(start=date_debut, end=date_fin, freq='MS')
months_str = [m.strftime('%Y-%m') for m in months]

if not months_str:
        st.info("Aucune période sélectionnée.")
        st.stop()

st.divider()

# Graphique des tendances
st.subheader("Évolution des revenus et dépenses")
if len(months_str) > 1:
        plot_trends(user_id, months_str)
else:
        st.info("Sélectionnez une période d'au moins 2 mois pour voir les tendances.")

st.divider()

# Statistiques globales
st.subheader("Statistiques globales")
data = get_all_data(user_id)

# Filtrer par période
if not data['revenus'].empty:
        data['revenus']['mois'] = pd.to_datetime(data['revenus']['mois'], format='%Y-%m', errors='coerce')
        revenus_periode = data['revenus'][
            (data['revenus']['mois'] >= pd.Timestamp(date_debut)) &
            (data['revenus']['mois'] <= pd.Timestamp(date_fin))
        ]
else:
        revenus_periode = pd.DataFrame()

if not data['depenses'].empty:
        data['depenses']['date_depense'] = pd.to_datetime(data['depenses']['date_depense'], errors='coerce')
        depenses_periode = data['depenses'][
            (data['depenses']['date_depense'] >= pd.Timestamp(date_debut)) &
            (data['depenses']['date_depense'] <= pd.Timestamp(date_fin))
        ]
else:
        depenses_periode = pd.DataFrame()

col1, col2, col3, col4 = st.columns(4)

with col1:
        total_rev = revenus_periode['montant'].sum() if not revenus_periode.empty else 0
        st.metric("Total revenus", f"{total_rev:,.2f} €".replace(",", " "))

with col2:
        total_dep = depenses_periode['montant'].sum() if not depenses_periode.empty else 0
        st.metric("Total dépenses", f"{total_dep:,.2f} €".replace(",", " "))

with col3:
        solde = total_rev - total_dep
        st.metric("Solde", f"{solde:,.2f} €".replace(",", " "))

with col4:
        nb_mois = len(months_str)
        moyenne_mensuelle = solde / nb_mois if nb_mois > 0 else 0
        st.metric("Moyenne mensuelle", f"{moyenne_mensuelle:,.2f} €".replace(",", " "))

st.divider()

# Analyse par catégorie
if not depenses_periode.empty:
        st.subheader("Analyse par catégorie")
        depenses_par_cat = depenses_periode.groupby('categorie')['montant'].agg(['sum', 'count', 'mean']).reset_index()
        depenses_par_cat.columns = ['Catégorie', 'Total (€)', 'Nombre', 'Moyenne (€)']
        depenses_par_cat = depenses_par_cat.sort_values('Total (€)', ascending=False)
        
        st.dataframe(
            depenses_par_cat.style.format({
                'Total (€)': '{:,.2f}',
                'Moyenne (€)': '{:,.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )

st.divider()

# Export de données
st.subheader("Export des données")
st.write("Téléchargez vos données pour analyses externes :")

col1, col2 = st.columns(2)

with col1:
        if st.button("📥 Exporter en CSV", use_container_width=True):
            csv_data = export_data(user_id, format='csv')
            col_csv1, col_csv2, col_csv3 = st.columns(3)
            with col_csv1:
                st.download_button(
                    label="📄 Revenus (CSV)",
                    data=csv_data['revenus'],
                    file_name=f"revenus_{username}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            with col_csv2:
                st.download_button(
                    label="📄 Dépenses (CSV)",
                    data=csv_data['depenses'],
                    file_name=f"depenses_{username}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            with col_csv3:
                st.download_button(
                    label="📄 Budgets (CSV)",
                    data=csv_data['budgets'],
                    file_name=f"budgets_{username}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

with col2:
        if st.button("📊 Exporter en Excel", use_container_width=True):
            excel_data = export_data(user_id, format='excel')
            st.download_button(
                label="📊 Télécharger Excel",
                data=excel_data,
                file_name=f"budget_complet_{username}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

