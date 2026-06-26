# Gestion de projet - Serveur (API)

API backend de l'application de gestion de projet. Ce dépôt contient uniquement
le serveur : une API REST développée avec FastAPI, exposant les fonctionnalités
d'authentification, de gestion des projets, des tâches et des participants.

Le client (application web séparée) consomme cette API.

## Présentation

L'API permet à un utilisateur authentifié de :

- créer un compte et se connecter (authentification par JWT) ;
- créer, consulter, modifier et supprimer des projets ;
- ajouter, consulter, modifier et supprimer des tâches au sein d'un projet ;
- suivre l'avancement des tâches via un statut (`todo`, `in_progress`, `done`) ;
- ajouter et retirer des participants à un projet ;
- assigner une tâche au propriétaire ou à un participant du projet.

### Stack technique

- **Python 3** + **FastAPI** pour l'API
- **SQLAlchemy** + **SQLite** pour la persistance des données
- **JWT** (via `python-jose`) pour l'authentification
- **passlib (bcrypt)** pour le hashage des mots de passe

## Prérequis

- Python 3.10 ou supérieur
- pip

## Installation (Windows / PowerShell)

Depuis la racine du dépôt :

```powershell
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le serveur
uvicorn app.main:app --reload
```

> Si l'activation du venv est bloquée par la politique d'exécution PowerShell,
> exécutez une fois (dans un PowerShell en mode administrateur ou pour
> l'utilisateur courant) :
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

Pour désactiver l'environnement virtuel une fois terminé :

```powershell
deactivate
```

## Installation (macOS / Linux)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Utilisation

Au premier démarrage, les tables sont créées automatiquement dans le fichier
`app.db` (SQLite) et un compte de démonstration est inséré s'il n'existe pas
déjà :

- email : `demo@demo.com`
- mot de passe : `demo1234`

Le serveur démarre par défaut sur `http://127.0.0.1:8000`.

### Documentation interactive

Une fois le serveur lancé, la documentation interactive (Swagger UI) est
disponible à l'adresse :

```
http://127.0.0.1:8000/docs
```

Une documentation alternative (ReDoc) est également disponible :

```
http://127.0.0.1:8000/redoc
```

## Structure du projet

```
gestion-projet-serveur/
├── app/
│   ├── __init__.py
│   ├── main.py              point d'entrée de l'API, config, CORS, démarrage
│   ├── database.py          connexion SQLite + session SQLAlchemy
│   ├── models.py            les tables (User, Project, Task, participants)
│   ├── schemas.py           les schémas Pydantic (entrées/sorties de l'API)
│   ├── auth.py               hashage des mots de passe + JWT + utilisateur courant
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          /auth/register, /auth/login
│       ├── projects.py      CRUD des projets
│       ├── tasks.py         CRUD des tâches + filtre par statut
│       └── participants.py  ajout / liste / retrait des participants
├── requirements.txt         les dépendances Python
├── .gitignore                venv, __pycache__, *.db
├── README.md
└── app.db                    base SQLite, créée au 1er lancement (ignorée par git)
```

## Endpoints principaux

### Authentification

| Méthode | Route            | Description                  |
|---------|------------------|-------------------------------|
| POST    | `/auth/register` | Crée un compte               |
| POST    | `/auth/login`    | Renvoie un token JWT         |

### Projets (authentification obligatoire)

| Méthode | Route             | Description                                   |
|---------|-------------------|------------------------------------------------|
| POST    | `/projects`       | Crée un projet (utilisateur courant = owner)  |
| GET     | `/projects`       | Liste les projets (owner ou participant)      |
| GET     | `/projects/{id}`  | Détail d'un projet                            |
| PUT     | `/projects/{id}`  | Modifie un projet (owner uniquement)          |
| DELETE  | `/projects/{id}`  | Supprime un projet (owner uniquement)         |

### Tâches

| Méthode | Route                          | Description                                      |
|---------|--------------------------------|----------------------------------------------------|
| POST    | `/projects/{id}/tasks`        | Crée une tâche dans un projet                      |
| GET     | `/projects/{id}/tasks`        | Liste les tâches (filtre `?status_filter=...`)     |
| GET     | `/tasks/{id}`                 | Détail d'une tâche                                 |
| PUT     | `/tasks/{id}`                 | Modifie une tâche                                  |
| DELETE  | `/tasks/{id}`                 | Supprime une tâche                                 |

### Participants

| Méthode | Route                                         | Description                          |
|---------|------------------------------------------------|----------------------------------------|
| POST    | `/projects/{id}/participants`                 | Ajoute un participant par email (owner)|
| GET     | `/projects/{id}/participants`                 | Liste les participants                 |
| DELETE  | `/projects/{id}/participants/{user_id}`       | Retire un participant (owner)          |

## Authentification

L'API utilise un JWT transmis dans l'en-tête HTTP :

```
Authorization: Bearer <token>
```

Le token est obtenu via `/auth/login` et doit être inclus dans toutes les
requêtes vers les routes protégées (`/projects`, `/tasks`, `/participants`).

## Gestion des erreurs

Les erreurs sont renvoyées au format JSON avec un code HTTP cohérent :

```json
{ "detail": "message d'erreur clair" }
```

Codes utilisés : `400` (donnée invalide ou conflit), `401` (authentification
manquante ou invalide), `403` (accès refusé), `404` (ressource introuvable).

## CORS

Le serveur autorise les requêtes provenant de `http://localhost:5173`
(origine par défaut d'un client Vite/React en développement).
