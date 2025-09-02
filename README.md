# suprss_aro
4PROJ SUPINFO M1 Sci. Eng. 2024-2025

# Documentation Technique – Projet de Lecture et Partage de Flux RSS

---

## 1. Introduction

### 1.1 Contexte du projet
Ce projet a pour objectif de développer une plateforme complète permettant aux utilisateurs de s’abonner à des flux RSS, de gérer leurs collections, de commenter, de partager et d’interagir avec d’autres utilisateurs.  
L’application repose sur une architecture **Fullstack** avec un **backend FastAPI** et un **frontend React (Vite)**, orchestrés via **Docker**.

### 1.2 Public visé
- Développeurs qui souhaitent déployer, maintenir ou contribuer au projet.  

- Utilisateurs finaux intéressés par un lecteur RSS collaboratif.  

- Administrateurs système chargés de l’installation et du monitoring.  

### 1.3 Technologies utilisées
- **Backend** : FastAPI, SQLAlchemy, Alembic, Celery, Redis.  
- **Frontend** : React, Vite, Nginx.  
- **Base de données** : PostgreSQL.  
- **Conteneurisation** : Docker & Docker Compose.  
- **Sécurité** : OAuth2, JWT, bcrypt, passlib.  

---

## 2. Objectifs

### 2.1 Problématique résolue
Les flux RSS sont souvent sous-exploités car les lecteurs classiques manquent de fonctionnalités collaboratives.  
Ce projet vise à centraliser :
- La lecture des flux RSS.  

- Le partage de collections entre utilisateurs. 

- La gestion de commentaires et de notifications.  

### 2.2 Valeur ajoutée du produit
- Interface intuitive pour la lecture et le suivi des flux.  

- Gestion collaborative des collections.  

- Notifications et interactions sociales (followers, commentaires).  

- Tâches automatisées pour l’actualisation des flux.  

### 2.3 Cas d’utilisation principaux
- Un utilisateur suit et lit ses flux RSS.  

- Une équipe partage une collection thématique de flux. 

- Un administrateur configure des permissions pour les membres d’une collection.  

---

## 3. Informations sur le produit

### 3.1 Vue d’ensemble
- Application web (frontend React).  

- API REST exposée par FastAPI.  

- Système d’authentification OAuth2 / JWT.  

- Tâches planifiées via Celery + Redis.  

### 3.2 Fonctionnalités principales
- Gestion des utilisateurs et authentification. 

- Abonnement à des flux RSS.  

- Création et partage de collections.  

- Commentaires et chat collaboratif.  

- Notifications et suivi des utilisateurs.  

### 3.3 Prérequis système
- **Système** : Linux, MacOS ou Windows avec WSL2.  
- **Dépendances** : Docker + Docker Compose.  
- **Ressources minimales** :  
  - CPU : 2 cœurs  
  - RAM : 2 Go  
  - Stockage : 2 Go  

---

## 4. Guide d’installation

### 4.1 Pré-requis
- Docker 24+  

- Docker Compose 2+  

- Accès à internet pour télécharger les dépendances  

### 4.2 Étapes d’installation
```bash
# Cloner le dépôt
git clone https://github.com/mon-org/lecteur-rss.git
cd lecteur-rss

# Lancer les services Docker
docker-compose up --build -d

# Appliquer les migrations
docker-compose exec backend alembic upgrade head
```
Ensuite :
- Créer un compte administrateur via l’API ou un script d’initialisation.

## 5. Guide utilisateur
### 5.1 Premiers pas

- Accéder à l’application via http://localhost:3000.
- Créer un compte ou se connecter via OAuth2 (Google, GitHub, Microsoft).

### 5.2 Navigation

- Profil → Paramètres utilisateur.
- Accueil → Vue générale des flux suivis.
- Collections → Gestion et partage des collections.
- Liste Articles → Articles lus ou favoris.
- Notifications → Suivi des interactions.

### 5.3 Exemples d’utilisation

- Gestion du profil utilisateur.
- Ajouter un flux RSS via son URL.
- Créer une collection et inviter d’autres utilisateurs.
- Lire et commenter un article dans une collection.
- Recherche d'articles et de collection associés.

## 6. Détails techniques
### 6.1 Architecture générale

- Frontend : React + Vite, servi par Nginx.

- Backend : FastAPI, expose une API REST.

- Base de données : PostgreSQL via SQLAlchemy.
- Worker Celery : tâches asynchrones (mise à jour des flux).
- Redis : broker et cache.

### 6.2 Modèle de données

- Utilisateur : comptes et authentification.
- Flux RSS : abonnement et gestion.
- Collection : regroupement collaboratif.
- Commentaires & Chat : interactions.
- Permissions : gestion des rôles dans une collection.

### 6.3 Référence API (exemples)

- POST /auth/login → Connexion utilisateur.
- GET /feeds/ → Liste des flux suivis.
- POST /collections/ → Créer une nouvelle collection.
- POST /collections/{id}/invite → Inviter un utilisateur.

## 7. Dépannage (Troubleshooting)

- Problème : backend ne démarre pas
→ Vérifier DATABASE_URL et la disponibilité de PostgreSQL.
- Problème : Celery worker inactif
→ Vérifier la connexion à Redis (REDIS_URL).
- Erreur 401 (Unauthorized)
→ Vérifier la configuration OAuth2 et les tokens JWT.

## 8. Maintenance et support

- Mises à jour : appliquer les migrations Alembic avant chaque nouvelle version.
- Monitoring : configurer Sentry pour suivre les erreurs.
- Logs : suivre les logs Docker :
```bash
docker-compose logs -f backend
```
- Contribution : via issues et pull requests GitHub.

## 9. Annexes

- Dépendances Python : voir requirements.txt.
- Dépendances frontend : voir package.json.
- Fichiers Docker : docker-compose.yml, Dockerfile.backend, Dockerfile.frontend.

## 10. Historique des révisions

- v1.0 – Août 2025 : Première version avec backend, frontend, tâches Celery et migrations Alembic.
- v1.1 – Prévu : Ajout de tests automatisés et monitoring avancé.
    - v1.1.1– Prévu : Implémentation de photo de profil