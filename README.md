# 💰 Application de Gestion de Budget Mensuel

Cette application Streamlit permet de gérer simplement ses revenus et ses dépenses chaque mois.
Elle est conçue pour être intuitive, légère et accessible à tous.

# 🎯 Objectif
- Enregistrer plusieurs revenus mensuels (salaire, primes, aides, etc.)
- Créer ses catégories de dépenses personnalisées
- Saisir les dépenses réelles pour chaque poste
- Visualiser un bilan clair : budget prévu, dépenses, et reste disponible
- Obtenir une vue d’ensemble mensuelle de sa situation financière

# 🧭 Fonctionnement

L’application se compose de 4 onglets :

## 1️⃣ Revenus

Ajoutez un ou plusieurs revenus pour le mois sélectionné.
Exemples : Salaire, APL, Remboursement, Freelance…

## 2️⃣ Catégories & Budgets

Créez vos propres postes de dépenses (loyer, transport, loisirs…).
Attribuez un budget mensuel à chaque catégorie.

## 3️⃣ Dépenses

Enregistrez vos dépenses réelles en précisant :
- La date
- La catégorie
- Une description (facultative)
- Le montant

## 4️⃣ Tableau de bord

Consultez :
- Le total des revenus
- Le total des dépenses
- Le reste global du mois
- Le détail par catégorie : budget, dépensé, reste

Un graphique affiche la répartition des dépenses par catégorie.

# ⚙️ Installation rapide

## 1️⃣ Cloner le projet :
```bash
git clone https://github.com/ton-utilisateur/budget-app.git
cd budget-app
```

## 2️⃣ Installer les dépendances :
```bash
poetry install 
```

## 3️⃣ Lancer l’application :
```bash
streamlit run app.py
```

Une page s'ouvrira dans votre navigateur par défaut. 

💾 Données enregistrées

Les données sont stockées localement dans un fichier SQLite :

```bash
data/budget_app.db
```

Aucune donnée n’est envoyée en ligne.
Vous pouvez sauvegarder ou transférer ce fichier pour garder votre historique.

💡 Conseils
- Ajustez vos budgets chaque mois selon vos priorités.
- Les catégories peuvent être renommées ou désactivées à tout moment.
- L’application fonctionne sur ordinateur, tablette ou mobile.
- Vous pouvez changer le dossier de stockage via la variable DB_PATH.

⸻

✨ Points forts

- Simple et intuitif ✅
- Totalement personnalisable ✅
- Données conservées en local ✅
- Tableau de bord clair et graphique intégré ✅
- Aucun compte ou configuration complexe requis ✅
