# 🥗 Biodélice — Plateforme de Recommandation et Planification Alimentaire Intelligente

**Biodélice** est une application web conçue avec **Django** et **PostgreSQL (Supabase)** permettant d'offrir des recommandations nutritionnelles et culinaires sur-mesure. L'application prend en compte les contraintes de santé des utilisateurs (diabète, hypertension, allergies, cœliaque), leurs régimes spécifiques (végétalien, végétarien) ainsi que les ingrédients disponibles dans leur frigo.

---

## 🚀 Fonctionnalités Principales

### 👤 Profil & Onboarding Personnalisé
* **Informations Physiques & Nutritionnelles** : Âge, poids, taille, sexe, niveau d'activité et calcul automatique du besoin calorique journalier (BMR).
* **Profil de Santé Chiffré** : Enregistrement sécurisé des allergies, régimes et maladies via des champs chiffrés (`EncryptedTextField`).
* **Niveau Culinaire** : Adaptation de la difficulté des recettes au profil de l'utilisateur (Débutant, Intermédiaire, Avancé).

### 🍲 Catalogue & Recommandations Intelligentes
* **Catalogue dynamique** : Recherche textuelle, filtres par catégorie (*Salé, Sucré, Healthy, Vegan*), niveau de difficulté et apport calorique maximum.
* **Algorithme d'Adaptation Santé** : Vérification dynamique des recettes selon les seuils tolérés (ex: taux de sucre pour diabète, taux de sel pour hypertension, mots-clés d'exclus).
* **Gestion des Favoris** : Ajout/suppression rapide en coup de cœur.

### 📅 Planning de Repas Hebdomadaire (Planner)
* **Planification dynamique** : Organisation des repas par jour (Lundi au Dimanche) et par type (Petit-déjeuner, Déjeuner, Dîner).
* **Interface fluide** : Choix des recettes depuis un volet latéral et synchronisation instantanée avec la base de données.

### 🥗 Frigo Virtuel ("Ce que j'ai au frigo")
* **Match Ingrédients ↔ Recettes** : Calcul automatique des correspondances entre les ingrédients disponibles et les recettes du catalogue.
* **Gestion en temps réel** : Ajout, normalisation et suppression d'ingrédients via une API REST interne.

### 🛠 Administration & Backoffice
* **Django Admin complet (`/admin/`)** : Gestion administrateur de tous les modèles (`User`, `FoodProduct`, `HealthConstraint`, `MealPlan`, `FridgeIngredient`, `SubstitutionRule`, `PasswordResetCode`).
* **Dashboard Custom Backoffice (`/backoffice/`)** : Statistiques globales (utilisateurs actifs, répartition des contraintes de santé, recettes populaires) mises en cache et liste paginée des produits.

---

## 🛠️ Stack Technique

* **Backend** : Django 6.0 (Python 3.10+)
* **Base de données** : PostgreSQL 17.6 hébergé sur **Supabase** (Session Pooler SSL)
* **ORM & Sécurité** : Django ORM, Chiffrement AES des données sensibles, Rate Limiting sur les endpoints sensibles
* **Frontend** : HTML5, CSS3 Moderne (Flexbox/Grid), JavaScript Vanilla (sans framework lourd)
* **APIs & Données** : Intégration de l'API Spoonacular pour l'import de recettes

---

## 📁 Architecture du Projet

```text
Software_secu/
├── accounts/               # Authentification, profils utilisateurs et produits alimentaires
│   ├── management/         # Commandes CLI pour l'import des recettes (import_sale, import_off)
│   ├── models.py           # User, HealthConstraint, FoodProduct, PasswordResetCode
│   ├── admin.py            # Configuration Django Admin avancée (CustomUserAdmin)
│   └── views.py            # Vues inscription, connexion, onboarding et mise à jour profil
├── recipes/                # Gestion des plans de repas et frigo virtuel
│   ├── models.py           # MealPlan, FridgeIngredient
│   ├── services.py         # Règles de substitution et algorithme de match frigo
│   └── views.py            # Vues catalogue, planner, favoris et API frigo
├── backoffice/             # Tableau de bord d'administration sur-mesure
│   ├── models.py           # SubstitutionRule
│   ├── views.py            # Dashboard analytique mis en cache et gestion des recettes
│   └── forms.py            # Formulaires de gestion backoffice
├── biodelice/              # Configuration globale du projet Django (settings, urls, wsgi)
├── templates/              # Templates HTML (home, regime, planner, settings, admin)
├── static/                 # Fichiers statiques (images, styles CSS)
├── .env                    # Variables d'environnement (Base de données, Clés API)
└── manage.py               # Script d'exécution Django
```

---

## ⚙️ Installation et Configuration Locale

### 1. Prérequis
* **Python 3.10+** installé sur votre machine
* Un compte **Supabase** (ou une instance PostgreSQL locale)

### 2. Cloner le dépôt
```bash
git clone https://github.com/votre-utilisateur/biodelice.git
cd biodelice
```

### 3. Créer et activer l'environnement virtuel
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Installer les dépendances
```bash
pip install django psycopg2-binary python-dotenv cryptography requests
```

### 5. Configurer les variables d'environnement (`.env`)
Créer un fichier `.env` à la racine du projet et ajouter les identifiants :

```env
SECRET_KEY=votre-cle-secrete-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuration Supabase / PostgreSQL
DB_NAME=postgres
DB_USER=postgres.votre_project_ref
DB_PASSWORD=votre_mot_de_passe_db
DB_HOST=aws-1-eu-west-3.pooler.supabase.com
DB_PORT=5432

# Optionnel : Clé API Spoonacular pour l'import de données
SPOONACULAR_API_KEY=votre_cle_api_spoonacular
```

### 6. Appliquer les migrations
```bash
python manage.py migrate
```

### 7. Créer un compte administrateur (Superuser)
```bash
python manage.py createsuperuser
```

### 8. Lancer le serveur de développement
```bash
python manage.py runserver
```

L'application sera accessible sur `http://127.0.0.1:8000/` et le Django Admin sur `http://127.0.0.1:8000/admin/`.

---

## 📥 Importation des Recettes (Spoonacular)

Le projet contient des commandes de gestion personnalisées pour remplir la base de données avec des recettes structurées :

```bash
# Importer des recettes salées
python manage.py import_sale

# Importer des recettes sucrées
python manage.py import_off
```

---

## 🔒 Sécurité et Bonnes Pratiques

* **Variables d'environnement** : Le fichier `.env` et les données sensibles sont ignorés par Git via `.gitignore`.
* **Protections intégrées** : Utilisation du middleware CSRF de Django, protection des routes d'administration (`@staff_required`), et hachage sécurisé des mots de passe.
* **Chiffrement** : Les données médicales sensibles et allergènes dans le profil utilisateur sont chiffrées au niveau du champ de base de données.

---

## 📄 Licence

Ce projet est sous licence MIT. Libre à vous de le contribuer et de l'améliorer !
