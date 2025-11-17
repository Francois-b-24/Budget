"""
Module d'analyses et de visualisations pour data scientists
"""
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from .data_operations import get_all_data


def monthly_summary(user_id: int, mois: str) -> dict:
    """Calcule le résumé mensuel"""
    from .data_operations import list_revenus, list_depenses, list_budgets
    
    revenus = list_revenus(user_id, mois)
    depenses = list_depenses(user_id, mois)
    budgets = list_budgets(user_id, mois)

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
            'Reste (catégorie)': b - s,
            'Pourcentage utilisé': (s / b * 100) if b > 0 else 0
        })
    
    df = pd.DataFrame(lignes).sort_values('Catégorie') if lignes else pd.DataFrame(
        columns=['Catégorie', 'Budget', 'Dépensé', 'Reste (catégorie)', 'Pourcentage utilisé']
    )

    return {
        'total_income': total_revenus,
        'total_spent': total_depenses,
        'overall_left': total_revenus - total_depenses,
        'per_category': df
    }


def plot_category_comparison(user_id: int, mois: str):
    """Graphique comparant budget vs dépenses par catégorie"""
    from .data_operations import list_budgets, list_depenses
    
    budgets = list_budgets(user_id, mois)
    depenses = list_depenses(user_id, mois)
    
    if budgets.empty and depenses.empty:
        st.info("Aucune donnée disponible pour ce mois.")
        return
    
    # Préparer les données
    depenses_par_cat = depenses.groupby('categorie')['montant'].sum() if not depenses.empty else pd.Series()
    
    df_viz = pd.DataFrame({
        'Catégorie': budgets['categorie'].tolist() if not budgets.empty else depenses_par_cat.index.tolist(),
        'Budget': budgets['budget'].tolist() if not budgets.empty else [0] * len(depenses_par_cat),
        'Dépensé': [depenses_par_cat.get(cat, 0) for cat in (budgets['categorie'].tolist() if not budgets.empty else depenses_par_cat.index.tolist())]
    })
    
    if df_viz.empty:
        st.info("Aucune donnée disponible pour ce mois.")
        return
    
    # Graphique en barres groupées
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Budget',
        x=df_viz['Catégorie'],
        y=df_viz['Budget'],
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name='Dépensé',
        x=df_viz['Catégorie'],
        y=df_viz['Dépensé'],
        marker_color='coral'
    ))
    
    fig.update_layout(
        title='Budget vs Dépenses par Catégorie',
        xaxis_title='Catégorie',
        yaxis_title='Montant (€)',
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_trends(user_id: int, months: list):
    """Graphique des tendances sur plusieurs mois"""
    from .data_operations import list_revenus, list_depenses
    
    revenus_totaux = []
    depenses_totales = []
    
    for mois in months:
        rev = list_revenus(user_id, mois)
        dep = list_depenses(user_id, mois)
        revenus_totaux.append(rev['montant'].sum() if not rev.empty else 0)
        depenses_totales.append(dep['montant'].sum() if not dep.empty else 0)
    
    df_trends = pd.DataFrame({
        'Mois': months,
        'Revenus': revenus_totaux,
        'Dépenses': depenses_totales
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_trends['Mois'],
        y=df_trends['Revenus'],
        mode='lines+markers',
        name='Revenus',
        line=dict(color='green', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_trends['Mois'],
        y=df_trends['Dépenses'],
        mode='lines+markers',
        name='Dépenses',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title='Évolution des Revenus et Dépenses',
        xaxis_title='Mois',
        yaxis_title='Montant (€)',
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_category_distribution(user_id: int, mois: str):
    """Graphique en camembert de la répartition des dépenses"""
    from .data_operations import list_depenses
    
    depenses = list_depenses(user_id, mois)
    
    if depenses.empty:
        st.info("Aucune dépense pour ce mois.")
        return
    
    depenses_par_cat = depenses.groupby('categorie')['montant'].sum().reset_index()
    depenses_par_cat.columns = ['Catégorie', 'Montant']
    
    fig = px.pie(
        depenses_par_cat,
        values='Montant',
        names='Catégorie',
        title='Répartition des Dépenses par Catégorie'
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)


def export_data(user_id: int, format: str = 'csv'):
    """Exporte toutes les données de l'utilisateur"""
    data = get_all_data(user_id)
    
    if format == 'csv':
        # Exporter chaque table en CSV
        return {
            'revenus': data['revenus'].to_csv(index=False).encode('utf-8'),
            'depenses': data['depenses'].to_csv(index=False).encode('utf-8'),
            'budgets': data['budgets'].to_csv(index=False).encode('utf-8')
        }
    elif format == 'excel':
        # Exporter en Excel avec plusieurs feuilles
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data['revenus'].to_excel(writer, sheet_name='Revenus', index=False)
            data['depenses'].to_excel(writer, sheet_name='Dépenses', index=False)
            data['budgets'].to_excel(writer, sheet_name='Budgets', index=False)
        return output.getvalue()
    
    return None

