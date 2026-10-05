# BioDelice

## Personalized Food Recommendation Platform

BioDelice est une application web développée avec Django, destinée aux personnes ayant des allergies, intolérances ou contraintes alimentaires.

L'application permet de prendre en compte le profil et les contraintes alimentaires de chaque utilisateur afin de proposer des aliments et des repas plus adaptés à ses besoins.

Les besoins pris en compte peuvent notamment concerner le diabète, la maladie cœliaque, les allergies alimentaires et différentes restrictions alimentaires.

---

## Application en ligne

**Tester BioDelice :**

https://biodelice.onrender.com/

> L'application est déployée sur Render. Avec l'offre gratuite, l'instance peut être mise en veille après une période d'inactivité. Le premier chargement après cette période peut donc être plus lent.

---

## Fonctionnalités principales

### Gestion des utilisateurs

* Création et gestion des comptes
* Authentification et déconnexion
* Gestion du profil utilisateur
* Gestion des informations personnelles et alimentaires
* Gestion des aliments à éviter
* Gestion des contraintes alimentaires

### Recommandation alimentaire

* Consultation des aliments et recettes
* Recommandations adaptées au profil utilisateur
* Prise en compte des contraintes alimentaires
* Gestion des favoris
* Substitution d'aliments

### Planification des repas

* Création et gestion de plans alimentaires
* Organisation des repas
* Gestion des ingrédients disponibles
* Prise en compte des aliments disponibles dans le réfrigérateur

### Administration

L'application dispose d'une interface d'administration permettant notamment de gérer les données de l'application et les différents éléments liés aux utilisateurs, aliments et recettes.

L'accès aux fonctionnalités d'administration est contrôlé selon les droits de l'utilisateur.

---

## Sécurité

La sécurité constitue une partie importante du projet. BioDelice intègre plusieurs mécanismes de protection au niveau de l'authentification, des données et des fonctionnalités sensibles.

### Authentification et contrôle d'accès

* Utilisation du système d'authentification natif de Django.
* Séparation entre les fonctionnalités utilisateur et administrateur.
* Contrôle des accès au back-office à l'aide des permissions Django (`is_staff` et `is_superuser`).
* Stockage sécurisé des mots de passe avec le mécanisme de hashage de Django basé sur PBKDF2 et un salt aléatoire.

### Protection des formulaires et des entrées

* Protection CSRF sur les formulaires et requêtes POST.
* Validation des données côté serveur.
* Politique de complexité des mots de passe.
* Protection contre les injections XSS grâce à l'échappement automatique des variables dans les templates Django.

### Protection des comptes

* Protection contre l'énumération des comptes lors de la récupération de mot de passe.
* Codes de récupération temporaires à usage unique.
* Limitation du nombre de tentatives sur les fonctionnalités sensibles :

  * 5 tentatives de connexion sur une période de 15 minutes.
  * 3 demandes de réinitialisation de mot de passe par heure.

### Protection des sessions

En production, les cookies de session utilisent les mécanismes `HttpOnly` et `Secure`, permettant de limiter leur exposition côté client et de garantir leur transmission via HTTPS.

### Protection des données sensibles

Les informations sensibles liées notamment aux contraintes de santé, allergies, restrictions alimentaires et aliments à éviter bénéficient de mécanismes de protection au niveau du stockage et des relations de données.

### Gestion des secrets

Les informations sensibles de configuration ne sont pas stockées dans le dépôt GitHub.

Les variables d'environnement sont utilisées pour gérer notamment :

* `SECRET_KEY`
* Identifiants de base de données
* Identifiants SMTP
* Autres paramètres sensibles de production

---

## Architecture

```text
                    Utilisateur
                        |
                        v
                Application Web
                     Django
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
    Authentification  Recettes    Planification
          |             |             |
          +-------------+-------------+
                        |
                        v
                   Django ORM
                        |
                        v
               PostgreSQL / Supabase
```

L'application Django est hébergée sur Render tandis que la base de données PostgreSQL est hébergée sur Supabase.

---

## Technologies utilisées

### Backend

* Python
* Django
* Django ORM
* Gunicorn

### Base de données

* PostgreSQL
* Supabase

### Frontend

* HTML
* CSS
* JavaScript
* Django Templates

### Déploiement

* Render
* Gunicorn
* WhiteNoise

### Bibliothèques principales

* psycopg2-binary
* Pillow
* python-dotenv
* dj-database-url
* cryptography
* requests

---

## Structure du projet

```text
Software_secu/
│
├── accounts/
├── recipes/
├── backoffice/
├── biodelice/
├── templates/
├── static/
├── media/
│
├── build.sh
├── requirements.txt
├── .env.example
├── .gitignore
├── manage.py
└── README.md
```

---

## Base de données

BioDelice utilise PostgreSQL comme système de gestion de base de données.

La base de données est hébergée sur Supabase et l'application Django communique avec celle-ci à travers le Django ORM.

Les migrations Django permettent de créer et maintenir la structure de la base de données.

---

## Déploiement

L'application est actuellement déployée sur Render.

Architecture de production :

```text
GitHub
   |
   v
Render
   |
   v
Django + Gunicorn
   |
   v
Supabase PostgreSQL
```

Le processus de déploiement prend notamment en charge :

* Installation des dépendances Python
* Collecte des fichiers statiques
* Application des migrations Django
* Démarrage de l'application avec Gunicorn

Les variables sensibles sont configurées directement dans l'environnement de production et ne sont pas publiées dans le dépôt.

---

## Installation locale

### 1. Cloner le projet

```bash
git clone https://github.com/Erennmayss/Software_secu.git
cd Software_secu
```

### 2. Créer un environnement virtuel

Sous Windows :

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à partir du fichier `.env.example` et renseigner les valeurs nécessaires à l'environnement local.

Le fichier `.env` ne doit pas être ajouté au dépôt GitHub.

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. Créer un administrateur

```bash
python manage.py createsuperuser
```

### 7. Lancer l'application

```bash
python manage.py runserver
```

L'application sera accessible à :

```text
http://127.0.0.1:8000/
```

L'interface d'administration est accessible à :

```text
http://127.0.0.1:8000/admin/
```

---

## Vérification

Les principales vérifications Django peuvent être effectuées avec :

```bash
python manage.py check
```

et :

```bash
python manage.py migrate
```

La collecte des fichiers statiques peut être vérifiée avec :

```bash
python manage.py collectstatic --no-input
```

---

## Documentation

Un rapport détaillé du projet est disponible dans le dépôt.

Le rapport présente notamment :

* L'analyse et les objectifs du projet
* Les fonctionnalités
* L'architecture
* La conception de la base de données
* L'implémentation
* Les mécanismes de sécurité
* Les tests
* Le déploiement
* Les perspectives d'amélioration

---

## Liens

**Application :**
https://biodelice.onrender.com/

**Dépôt GitHub :**
https://github.com/Erennmayss/Software_secu

---

## Projet académique

**BioDelice — Personalized Food Recommendation Platform**

Projet réalisé autour du développement sécurisé d'une application web de recommandation alimentaire personnalisée.
