# 💰 Application de Gestion de Budget Personnel

Application Streamlit professionnelle pour le suivi de budget personnel, adaptée pour le déploiement sur Streamlit Cloud avec authentification multi-utilisateurs.

## 🎯 Fonctionnalités

- ✅ **Authentification sécurisée** : Système de connexion multi-utilisateurs
- ✅ **Gestion des revenus** : Enregistrement de plusieurs revenus par mois
- ✅ **Catégories personnalisées** : Création et gestion de vos propres catégories de dépenses
- ✅ **Budgets mensuels** : Définition de budgets par catégorie
- ✅ **Suivi des dépenses** : Enregistrement détaillé de toutes vos dépenses
- ✅ **Tableau de bord interactif** : Visualisations et métriques en temps réel
- ✅ **Analyses avancées** : Outils pour data scientists (export CSV/Excel, graphiques, tendances)
- ✅ **Multi-utilisateurs** : Chaque utilisateur a ses propres données isolées

## 🏗️ Architecture

L'application est organisée en modules pour une meilleure maintenabilité :

```
Budget/
├── app.py                      # Application principale
├── pages/                      # Pages Streamlit (navigation automatique)
│   ├── 1_📊_Tableau_de_bord.py
│   ├── 2_💰_Revenus.py
│   ├── 3_📁_Catégories_et_Budgets.py
│   ├── 4_💸_Dépenses.py
│   └── 5_📈_Analyses.py
├── src/                        # Modules Python
│   ├── __init__.py
│   ├── database.py            # Gestion de la base de données
│   ├── auth.py                # Authentification
│   ├── data_operations.py     # Opérations CRUD
│   └── analytics.py           # Analyses et visualisations
├── .streamlit/                 # Configuration Streamlit
│   ├── config.toml
│   └── secrets.toml.example
├── requirements.txt
└── README.md
```

## ⚙️ Installation locale

### 1️⃣ Cloner le projet

```bash
git clone <votre-repo>
cd Budget
```

### 2️⃣ Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurer l'authentification

Créez le fichier `.streamlit/secrets.toml` à partir de l'exemple :

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Générez les mots de passe hashés avec Python :

```python
import streamlit_authenticator as stauth

# Générer le hash d'un mot de passe
hashed_password = stauth.Hasher(['votre_mot_de_passe']).generate()[0]
print(hashed_password)
```

Modifiez `.streamlit/secrets.toml` avec vos utilisateurs :

```toml
[credentials]
usernames = {
    "admin" = {
        email = "admin@example.com"
        failed_login_attempts = 0
        logged_in = false
        name = "Administrateur"
        password = "$2b$12$..."  # Le hash généré
    }
}

[cookie]
expiry_days = 30
key = "changez_cette_cle_secrete"  # Changez cette clé !
name = "budget_app_cookie"
```

### 5️⃣ Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvrira dans votre navigateur à l'adresse `http://localhost:8501`.

## 🚀 Déploiement sur Streamlit Cloud

### 1️⃣ Préparer le repository

Assurez-vous que votre code est sur GitHub, GitLab ou Bitbucket.

### 2️⃣ Créer l'application sur Streamlit Cloud

1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Connectez-vous avec votre compte GitHub
3. Cliquez sur "New app"
4. Sélectionnez votre repository et la branche
5. Spécifiez le point d'entrée : `app.py`

### 3️⃣ Configurer les secrets

Dans les paramètres de l'application sur Streamlit Cloud :

1. Allez dans "Settings" → "Secrets"
2. Ajoutez la configuration au format TOML :

```toml
[credentials]
usernames = {
    "admin" = {
        email = "admin@example.com"
        failed_login_attempts = 0
        logged_in = false
        name = "Administrateur"
        password = "$2b$12$..."  # Hash généré
    }
}

[cookie]
expiry_days = 30
key = "votre_cle_secrete_aleatoire_longue"  # Générez une clé aléatoire !
name = "budget_app_cookie"
```

**⚠️ Important** : 
- Générez une clé aléatoire forte pour `cookie.key`
- Ne partagez jamais vos secrets publiquement
- Utilisez des mots de passe forts

### 4️⃣ Déployer

Cliquez sur "Deploy" et attendez que l'application se déploie.

## 📊 Utilisation

### Navigation

L'application utilise la navigation par pages de Streamlit. Les pages sont accessibles via les onglets en haut de l'écran :

1. **📊 Tableau de bord** : Vue d'ensemble avec métriques et graphiques
2. **💰 Revenus** : Gestion des revenus mensuels
3. **📁 Catégories et Budgets** : Création de catégories et définition des budgets
4. **💸 Dépenses** : Enregistrement des dépenses
5. **📈 Analyses** : Outils d'analyse avancés et export de données

### Sélection du mois

Utilisez le sélecteur dans la barre latérale pour changer de mois.

### Export de données

Dans la page "Analyses", vous pouvez exporter vos données :
- **CSV** : Fichiers séparés pour revenus, dépenses et budgets
- **Excel** : Fichier unique avec plusieurs feuilles

## 🔒 Sécurité

- Les mots de passe sont hashés avec bcrypt
- Chaque utilisateur a ses propres données isolées
- Les sessions sont gérées via des cookies sécurisés
- Les secrets ne sont jamais stockés dans le code

## 💾 Stockage des données

Les données sont stockées dans une base SQLite :
- **Local** : `data/budget_app.db`
- **Streamlit Cloud** : `.streamlit/data/budget_app.db`

Chaque utilisateur a ses propres données grâce à un système de `user_id`.

## 🛠️ Technologies utilisées

- **Streamlit** : Framework d'application web
- **SQLite** : Base de données
- **Pandas** : Manipulation de données
- **Plotly** : Visualisations interactives
- **streamlit-authenticator** : Authentification
- **openpyxl** : Export Excel

## 📝 Notes pour les développeurs

### Structure de la base de données

- `users` : Table des utilisateurs
- `revenus` : Revenus mensuels par utilisateur
- `categories` : Catégories de dépenses par utilisateur
- `budgets` : Budgets mensuels par catégorie et utilisateur
- `depenses` : Dépenses réelles par utilisateur

### Ajouter de nouvelles fonctionnalités

1. Ajoutez les fonctions de données dans `src/data_operations.py`
2. Créez les visualisations dans `src/analytics.py`
3. Créez une nouvelle page dans `pages/` si nécessaire

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

Ce projet est sous licence MIT.

## ✨ Points forts

- ✅ Architecture modulaire et maintenable
- ✅ Authentification sécurisée multi-utilisateurs
- ✅ Interface utilisateur moderne et intuitive
- ✅ Adapté pour Streamlit Cloud
- ✅ Outils d'analyse pour data scientists
- ✅ Export de données (CSV/Excel)
- ✅ Graphiques interactifs avec Plotly
- ✅ Responsive et user-friendly
