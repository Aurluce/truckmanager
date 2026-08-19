# 🚛 TruckManager

> **Intelligent Fleet Management & Vehicle Tracking Platform**

TruckManager est une plateforme moderne de **gestion et de supervision de flotte automobile**, conçue pour permettre aux entreprises de transport de centraliser la gestion de leurs véhicules, conducteurs, trajets, alertes et données de géolocalisation.

Le projet combine une architecture **Web + Mobile + Backend + IoT**, avec pour objectif de fournir une solution complète de suivi et de gestion des véhicules en temps réel.

---

## 📌 Présentation

TruckManager a été conçu pour répondre aux besoins des entreprises possédant une flotte de véhicules et souhaitant améliorer :

* 📍 le suivi GPS des véhicules ;
* 🚛 la gestion de la flotte ;
* 👨‍✈️ la gestion des conducteurs ;
* 🗺️ le suivi des trajets ;
* ⚠️ la détection des situations anormales ;
* 🔔 les alertes ;
* 📊 les statistiques et rapports ;
* 🔧 la configuration des véhicules ;
* 🌐 la supervision depuis une plateforme web ;
* 📱 l'accès aux données depuis une application mobile ;
* 🔌 l'intégration avec des équipements IoT embarqués.

L'objectif à terme est de disposer d'une plateforme capable de connecter les **véhicules physiques** à une infrastructure logicielle centralisée.

---

# 🎯 Objectifs du projet

TruckManager poursuit plusieurs objectifs :

### Gestion de flotte

Centraliser toutes les informations relatives aux véhicules d'une entreprise.

### Géolocalisation

Permettre de connaître la position actuelle d'un véhicule et de consulter son historique de déplacements.

### Suivi des trajets

Enregistrer les trajets effectués et exploiter les données GPS afin de produire des statistiques.

### Système d'alertes

Détecter automatiquement certaines situations :

* dépassement de vitesse ;
* entrée dans une zone interdite ;
* sortie d'une zone autorisée ;
* arrêt prolongé ;
* comportement inhabituel ;
* problèmes liés au véhicule.

### IoT

Connecter les véhicules à la plateforme grâce à des microcontrôleurs et des modules de communication.

### Analyse des données

Transformer les données collectées en informations utiles pour les gestionnaires de flotte.

---

# 🏗️ Architecture générale

L'architecture cible de TruckManager repose sur plusieurs composants.

```text
                         ┌──────────────────────┐
                         │      VEHICULE        │
                         │                      │
                         │ ESP32 / Capteurs     │
                         │ GPS                  │
                         │ GSM                  │
                         │ Capteurs embarqués   │
                         └──────────┬───────────┘
                                    │
                              Données IoT
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     API BACKEND      │
                         │                      │
                         │ Django               │
                         │ Django REST          │
                         │ Authentication       │
                         │ Business Logic       │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
            ┌─────────────────┐           ┌─────────────────┐
            │    DATABASE     │           │   REAL-TIME     │
            │                 │           │   SERVICES      │
            │ MySQL/Postgres  │           │                 │
            │                 │           │ WebSocket       │
            └─────────────────┘           │ Notifications   │
                                          └────────┬────────┘
                                                   │
                              ┌────────────────────┴──────────────────┐
                              │                                       │
                              ▼                                       ▼
                    ┌──────────────────┐                   ┌──────────────────┐
                    │   WEB PLATFORM   │                   │  MOBILE APP      │
                    │                  │                   │                  │
                    │ Next.js / React  │                   │ Flutter          │
                    │ Dashboard        │                   │ Tracking         │
                    │ Maps              │                   │ Notifications    │
                    └──────────────────┘                   └──────────────────┘
```

---

# 🧩 Composants du système

## 1. Backend

Le backend constitue le cœur de l'application.

Il est responsable de :

* l'authentification ;
* la gestion des utilisateurs ;
* la gestion des véhicules ;
* la gestion des conducteurs ;
* la gestion des trajets ;
* la réception des données GPS ;
* la gestion des alertes ;
* la gestion des zones ;
* la configuration des véhicules ;
* la génération des statistiques ;
* l'exposition des API REST.

### Technologies

* Python
* Django
* Django REST Framework
* MySQL / PostgreSQL
* REST API
* JWT Authentication

---

# 🖥️ 2. Interface Web

L'interface Web permet aux gestionnaires de flotte de superviser l'ensemble du système.

Elle est destinée notamment aux :

* administrateurs ;
* gestionnaires de flotte ;
* responsables logistiques ;
* superviseurs.

### Fonctionnalités prévues

* Dashboard ;
* gestion des véhicules ;
* gestion des conducteurs ;
* carte interactive ;
* suivi GPS ;
* historique des trajets ;
* gestion des alertes ;
* gestion des zones ;
* statistiques ;
* configuration des véhicules ;
* gestion des utilisateurs.

### Technologies

* Next.js
* React
* TypeScript
* Tailwind CSS
* REST API

---

# 📱 3. Application Mobile

Une application mobile est prévue pour permettre l'accès aux fonctionnalités principales de TruckManager depuis un smartphone.

### Fonctionnalités

* authentification ;
* tableau de bord ;
* consultation des véhicules ;
* localisation ;
* suivi des trajets ;
* affichage des alertes ;
* notifications ;
* profil utilisateur.

### Technologie

**Flutter / Dart**

---

# 🔌 4. IoT embarqué

TruckManager est conçu pour pouvoir communiquer avec des équipements installés dans les véhicules.

Le système IoT peut notamment utiliser :

* ESP32 / ESP32-S3 ;
* module GPS ;
* module GSM/4G ;
* capteurs ;
* alimentation embarquée.

Exemple d'équipements étudiés :

```text
ESP32-S3
   │
   ├── GPS
   │
   ├── GSM / 4G
   │
   ├── Capteurs
   │
   └── Alimentation véhicule
```

Les équipements embarqués collectent les données du véhicule puis les transmettent au backend.

---

# 📍 Géolocalisation

Le système de géolocalisation permet de collecter et exploiter :

* latitude ;
* longitude ;
* vitesse ;
* direction ;
* date et heure ;
* distance parcourue ;
* état du véhicule.

Les données GPS peuvent être utilisées pour :

* afficher la position actuelle ;
* reconstruire un trajet ;
* calculer des distances ;
* détecter des arrêts ;
* détecter des dépassements de vitesse ;
* analyser les déplacements.

---

# 🗺️ Cartographie

La plateforme utilise une cartographie interactive afin de représenter les véhicules et les trajets.

Les fonctionnalités cartographiques prévues comprennent :

* position actuelle ;
* marqueurs des véhicules ;
* historique GPS ;
* tracé des trajets ;
* zones géographiques ;
* zones interdites ;
* informations de localisation.

L'utilisation d'OpenStreetMap est envisagée pour la cartographie.

---

# ⚠️ Système d'alertes

TruckManager intègre une logique permettant de détecter automatiquement certaines situations.

Exemples :

| Alerte               | Description                                          |
| -------------------- | ---------------------------------------------------- |
| 🚨 Survitesse        | Le véhicule dépasse la vitesse configurée            |
| 📍 Zone interdite    | Le véhicule entre dans une zone interdite            |
| 🛑 Arrêt prolongé    | Le véhicule reste immobile pendant une durée définie |
| 📡 Perte GPS         | Absence prolongée de données GPS                     |
| 📶 Perte réseau      | Interruption de communication                        |
| 🚛 Anomalie véhicule | État anormal détecté par le système                  |

Les paramètres d'alerte peuvent être configurés par véhicule.

---

# ⚙️ Configuration des véhicules

Chaque véhicule peut disposer de paramètres spécifiques.

Exemple :

```text
GPS update interval
Data synchronization interval
Maximum speed
Stop detection threshold
Passenger weight
Load cell threshold
API endpoint
Offline mode
Alert configuration
```

Cette approche permet d'adapter le comportement du système aux caractéristiques de chaque véhicule.

---

# 🔐 Sécurité

La plateforme prend en compte plusieurs aspects de sécurité :

* authentification des utilisateurs ;
* gestion des rôles ;
* contrôle d'accès ;
* protection des API ;
* validation des données ;
* variables d'environnement ;
* séparation des environnements de développement et de production.

Les secrets et informations sensibles ne doivent jamais être stockés directement dans le dépôt Git.

---

# 📊 Gestion des données

Les principales données manipulées par TruckManager comprennent :

```text
Users
   │
   ├── Vehicles
   │       │
   │       ├── GPS positions
   │       ├── Trips
   │       ├── Alerts
   │       ├── Configurations
   │       └── Restricted zones
   │
   ├── Drivers
   │
   └── Permissions
```

---

# 🛠️ Stack technique

## Backend

| Technologie           | Utilisation           |
| --------------------- | --------------------- |
| Python                | Langage principal     |
| Django                | Framework backend     |
| Django REST Framework | API REST              |
| MySQL                 | Base de données       |
| PostgreSQL            | Base de données cible |
| JWT                   | Authentification API  |

## Frontend

| Technologie  | Utilisation           |
| ------------ | --------------------- |
| Next.js      | Application Web       |
| React        | Interface utilisateur |
| TypeScript   | Typage                |
| Tailwind CSS | Interface             |

## Mobile

| Technologie   | Utilisation        |
| ------------- | ------------------ |
| Flutter       | Application mobile |
| Dart          | Langage            |
| OpenStreetMap | Cartographie       |

## IoT

| Technologie      | Utilisation             |
| ---------------- | ----------------------- |
| ESP32 / ESP32-S3 | Contrôleur              |
| GPS              | Géolocalisation         |
| GSM / 4G         | Communication           |
| Capteurs         | Acquisition des données |

## DevOps / outils

* Git
* GitHub
* Docker
* Linux
* Postman
* VS Code

---

# 📁 Architecture du Backend

L'architecture Django est organisée autour de plusieurs applications métier.

```text
backend/
│
├── apps/
│   ├── authentication/
│   ├── vehicles/
│   ├── trips/
│   ├── events/
│   ├── alerts/
│   ├── stats/
│   └── fleet_management/
│
├── config/
├── manage.py
├── requirements.txt
└── .env
```

Chaque application possède une responsabilité fonctionnelle distincte afin de faciliter la maintenance et l'évolution du système.

---

# 🚀 Installation

## Prérequis

Avant de commencer, installer :

* Python 3.11+
* pip
* MySQL ou PostgreSQL
* Git
* Node.js
* Flutter SDK
* Docker *(optionnel)*

---

## 1. Cloner le projet

```bash
git clone https://github.com/Aurluce/TruckManager.git
cd TruckManager
```

> Adapte le nom du dépôt si le repository utilise actuellement un autre nom.

---

# 🐍 Backend Django

Créer un environnement virtuel :

```bash
python3 -m venv venv
```

Activer l'environnement :

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

# ⚙️ Configuration

Créer un fichier `.env` :

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=truckmanager
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

ALLOWED_HOSTS=localhost,127.0.0.1
```

Ne jamais publier le fichier `.env`.

---

# 🗄️ Base de données

Créer la base de données :

```sql
CREATE DATABASE truckmanager;
```

Puis appliquer les migrations :

```bash
python manage.py makemigrations
python manage.py migrate
```

Créer un administrateur :

```bash
python manage.py createsuperuser
```

Lancer le serveur :

```bash
python manage.py runserver
```

API disponible par défaut sur :

```text
http://127.0.0.1:8000/
```

---

# 🖥️ Frontend

Installer les dépendances :

```bash
npm install
```

Lancer le serveur de développement :

```bash
npm run dev
```

---

# 📱 Flutter

Installer les dépendances :

```bash
flutter pub get
```

Vérifier l'environnement :

```bash
flutter doctor
```

Lancer l'application :

```bash
flutter run
```

---

# 🔗 API

L'API REST constitue l'interface de communication principale entre les différentes parties du système.

Exemples d'API :

```text
/api/auth/
/api/vehicles/
/api/trips/
/api/events/
/api/alerts/
/api/stats/
```

Les endpoints évoluent avec le développement du projet.

---

# 🔄 Flux de données GPS

Le fonctionnement général est le suivant :

```text
GPS
 │
 ▼
ESP32
 │
 ▼
GSM / 4G
 │
 ▼
Django REST API
 │
 ▼
Database
 │
 ├───────────────┐
 ▼               ▼
Web Dashboard   Mobile App
```

Le véhicule transmet régulièrement ses informations au serveur.

Le backend valide les données, les enregistre puis les rend disponibles aux interfaces de supervision.

---

# 📈 Roadmap

## 🚛 Fleet Management

* [x] Structure initiale du backend
* [x] Gestion des véhicules
* [ ] Gestion avancée des conducteurs
* [ ] Gestion des documents
* [ ] Gestion de la maintenance

## 📍 GPS Tracking

* [ ] Réception des coordonnées GPS
* [ ] Position temps réel
* [ ] Historique des positions
* [ ] Tracé des trajets
* [ ] Optimisation de la fréquence GPS

## ⚠️ Alertes

* [ ] Détection de survitesse
* [ ] Zones interdites
* [ ] Détection d'arrêt
* [ ] Notifications mobiles
* [ ] Notifications temps réel

## 🔌 IoT

* [ ] Firmware ESP32
* [ ] Communication GPS
* [ ] Communication GSM/4G
* [ ] Protocole de communication sécurisé
* [ ] Mode hors ligne
* [ ] Synchronisation différée

## 📊 Analytics

* [ ] Statistiques des trajets
* [ ] Distance parcourue
* [ ] Temps de conduite
* [ ] Temps d'arrêt
* [ ] Analyse de consommation
* [ ] Rapports exportables

## ☁️ Production

* [ ] Dockerisation
* [ ] CI/CD
* [ ] Déploiement cloud
* [ ] Monitoring
* [ ] Logging centralisé
* [ ] Backup automatique

---

# 🧪 Tests

Le projet est progressivement accompagné de tests automatisés.

Backend :

```bash
python manage.py test
```

Pour les tests supplémentaires :

```bash
pytest
```

---



# 🌍 Vision du projet

TruckManager n'est pas uniquement conçu comme un simple CRUD de gestion de véhicules.

L'objectif est de construire progressivement une véritable plateforme **Fleet Management + IoT**, capable de faire communiquer :

**véhicules → équipements IoT → réseau mobile → API → base de données → applications Web/Mobile**

Cette architecture permettra à terme d'intégrer des fonctionnalités avancées telles que :

* analyse prédictive ;
* maintenance prédictive ;
* optimisation des trajets ;
* analyse comportementale ;
* détection automatique d'anomalies ;
* intelligence artificielle appliquée à la flotte.

---

# 🔮 Évolutions futures

Les évolutions envisagées comprennent notamment :

### 🤖 Intelligence artificielle

* prédiction des pannes ;
* détection d'anomalies ;
* prédiction de consommation ;
* scoring des conducteurs ;
* optimisation des trajets.

### ☁️ Cloud

* déploiement scalable ;
* stockage distribué ;
* monitoring ;
* haute disponibilité.

### 📡 IoT

* communication temps réel ;
* MQTT ;
* OTA firmware updates ;
* gestion centralisée des équipements.

---


# 👨‍💻 Auteur

**Aurluce Feudjio**

Full-Stack Software Developer

🇨🇲 Cameroon

🌐 Portfolio : https://aurluce.vercel.app

💼 LinkedIn : https://www.linkedin.com/in/aurluce-feudjio-b41575274/

🐙 GitHub : https://github.com/Aurluce


