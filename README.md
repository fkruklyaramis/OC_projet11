# 🏋️ GUDLFT Registration - Système de Réservation de Compétitions

## 📋 Description du Projet

GUDLFT est une application web Flask permettant aux clubs de musculation de réserver des places pour des compétitions. Le système gère les points des clubs, la validation des dates et les réservations.

## 🚀 Fonctionnalités Principales

### ✅ Fonctionnalités Implémentées
- **Connexion par email** : Les secrétaires de club se connectent avec leur email
- **Affichage des compétitions** : Liste des compétitions disponibles avec dates et places
- **Réservation de places** : Système de réservation avec déduction de points
- **Validation des dates** : Impossible de réserver pour des compétitions passées
- **Limitation des places** : Maximum 12 places par réservation
- **Vérification des points** : Contrôle que le club a suffisamment de points
- **Points publics** : Affichage transparent des points de tous les clubs
- **Persistance des données** : Sauvegarde automatique dans les fichiers JSON

### 🔧 Corrections de Bugs Appliquées
1. **Bug #1** : Gestion des emails inconnus lors de la connexion
2. **Bug #2** : Mise à jour des fichiers JSON après réservation  
3. **Bug #3** : Gestion des clubs/compétitions inexistants
4. **Bug #4** : Validation des données lors de l'achat de places

## 🗂️ Structure du Projet

```
OC_projet11/
├── server.py                      # Application Flask principale
├── config/
│   └── messages.py                # Configuration des messages et seuils
├── templates/
│   ├── index.html                 # Page d'accueil
│   ├── welcome.html               # Page d'accueil connecté
│   └── booking.html               # Page de réservation
├── clubs.json                     # Données des clubs (production)
├── competitions.json              # Données des compétitions (production)
├── test/
│   ├── data/
│   │   ├── source/               # Données de référence
│   │   └── testing/              # Données de test isolées
│   ├── unit/                     # Tests unitaires (50 tests)
│   ├── integration/              # Tests d'intégration (17 tests)
│   └── perf/                     # Tests de performance Locust
└── requirements.txt              # Dépendances Python
```

## 🛣️ Routes de l'Application

### Routes Principales
- `GET /` - Page d'accueil avec formulaire de connexion
- `POST /showSummary` - Connexion et affichage du tableau de bord
- `GET /book/<club>/<competition>` - Page de réservation
- `POST /purchasePlaces` - Traitement de l'achat de places
- `GET /logout` - Déconnexion
- `GET /publicPoints` - Affichage public des points des clubs

### Validation des Routes
- **Validation des paramètres** : Vérification club/compétition existants
- **Validation des dates** : Blocage des réservations pour compétitions passées
- **Validation des données** : Contrôle des données POST
- **Gestion d'erreurs** : Messages d'erreur appropriés pour chaque cas

## 🏗️ Architecture Technique

### Technologies Utilisées
- **Backend** : Flask 3.1.1 (Python)
- **Templates** : Jinja2
- **Données** : Fichiers JSON
- **Tests** : pytest 8.4.1
- **Performance** : Locust 2.37.14
- **Coverage** : coverage.py

### Gestion des Données
- **Environnement de test** : Isolation des données dans `test/data/testing/`
- **Environnement de production** : Données dans les fichiers racine
- **Sauvegarde automatique** : Mise à jour des JSON après chaque transaction

### Configuration Centralisée (`config/messages.py`)
```python
class Messages:
    # Messages d'erreur, succès, informations
    # Méthodes utilitaires pour validation
    # Constantes de l'application

class PerformanceThresholds:
    MAX_LOADING_TIME = 5.0  # 5 secondes maximum
    MAX_UPDATE_TIME = 2.0   # 2 secondes maximum  
    DEFAULT_USERS = 6       # 6 utilisateurs par défaut
```

## 🧪 Tests et Qualité

### Tests Unitaires (50 tests)
```bash
# Lancer tous les tests unitaires
python -m pytest test/unit -v

# Tests spécifiques
python -m pytest test/unit/test_login.py -v      # Tests de connexion
python -m pytest test/unit/test_book.py -v       # Tests de réservation
python -m pytest test/unit/test_purchase.py -v   # Tests d'achat
python -m pytest test/unit/test_public_points.py -v # Tests points publics
```

### Tests d'Intégration (17 tests)
```bash
# Lancer tous les tests d'intégration
python -m pytest test/integration -v

# Tests spécifiques
python -m pytest test/integration/test_workflows.py -v  # Workflows complets
python -m pytest test/integration/test_endpoints.py -v  # Cohérence des endpoints
```

### Tests Complets
```bash
# Tous les tests (unitaires + intégration)
python -m pytest test/ -v

# Tests rapides (arrêt au premier échec)
python -m pytest test/ -x
```

### Rapport de Couverture
```bash
# Générer le rapport HTML de couverture (uniquement server.py)
python -m pytest test/ --cov=server --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur
```

## ⚡ Tests de Performance avec Locust

### Configuration des Seuils
- **Chargement maximum** : 5 secondes
- **Mises à jour maximum** : 2 secondes
- **Utilisateurs par défaut** : 6

### Commandes Locust

#### 1. Démarrer le serveur Flask
```bash
python -m flask run
```

#### 2. Tests de performance automatisés
```bash
# Mode Web UI (par défaut - ouvre http://localhost:8089)
locust -f test/perf/locustfile.py --host=http://localhost:5050

# Mode CLI direct avec 6 utilisateurs, durée 60s
locust -f test/perf/locustfile.py --host=http://localhost:5050 --users 6 --spawn-rate 2 --run-time 60s --headless

# Avec rapport HTML
locust -f test/perf/locustfile.py --host=http://localhost:5050 --users 6 --spawn-rate 2 --run-time 60s --headless --html rapport_locust.html
```

### Interprétation des Résultats
- ✅ **Conformité** : Tous les endpoints respectent les seuils
- ❌ **Violation** : Temps de réponse dépassant les seuils
- **Rapport HTML** : Graphiques et statistiques détaillées
- **Terminal** : Résumé en temps réel avec violations

### Types de Tests de Performance
- **WebsiteUser** : Tests de chargement (pages GET, connexion)
- **BookingUser** : Tests de mise à jour (achats POST)
- **Mesures** : Temps de réponse, throughput, erreurs

## 🚀 Installation et Lancement

### Prérequis
- Python 3.8+
- pip

### Installation
```bash
# Cloner le projet
git clone <url-du-repo>
cd OC_projet11

# Installer les dépendances
pip install -r requirements.txt

# Installer Locust pour les tests de performance
pip install locust
```

### Lancement de l'Application
```bash
# Démarrer le serveur de développement
python server.py

# L'application sera disponible sur http://localhost:5000
```

### Variables d'Environnement
```bash
# Optionnel : définir une clé secrète
export SECRET_KEY="votre-cle-secrete"

# Mode test (utilise les données de test/data/testing/)
export TESTING=1
```

## 📊 Données de Test

### Clubs de Test
- **Simply Lift** : john@simplylift.co (13 points)
- **Iron Temple** : admin@irontemple.com (4 points)  
- **She Lifts** : kate@shelifts.co.uk (12 points)

### Compétitions de Test
- **Spring Festival** : 2020-03-27 10:00:00 (passée)
- **Fall Classic** : 2020-10-22 13:30:00 (passée)
- **Future Championship** : 2026-06-15 14:00:00 (future)
- **Next Year Games** : 2026-08-20 09:00:00 (future)

## 🔍 Debugging et Développement

### Logs et Erreurs
- **Mode debug** : `app.run(debug=True)` activé
- **Messages Flash** : Retours utilisateur pour toutes les actions
- **Gestion d'erreurs** : Validation complète des entrées

### Tests Locaux
```bash
# Test rapide de l'API
curl http://localhost:5000/
curl http://localhost:5000/publicPoints

# Vérification des données
cat clubs.json
cat competitions.json
```

## 📈 Métriques de Qualité

### Couverture de Code
- **Tests unitaires** : 50 tests couvrant toutes les fonctions
- **Tests d'intégration** : 17 tests pour les workflows complets
- **Couverture** : >90% du code couvert

### Performance
- **Temps de réponse** : <15ms en moyenne
- **Conformité aux seuils** : 100% des endpoints respectent les limites
- **Charge supportée** : Testé jusqu'à 10 utilisateurs simultanés

### Standards de Code
- **PEP 8** : Respect des conventions Python
- **Documentation** : Commentaires et docstrings
- **Configuration centralisée** : Tous les messages dans `config/`

## 🎯 Points d'Amélioration Future

### Fonctionnalités Potentielles
- [ ] Base de données (SQLite/PostgreSQL)
- [ ] Authentification avec mot de passe
- [ ] API REST
- [ ] Interface d'administration
- [ ] Notifications email
- [ ] Historique des réservations

### Optimisations Techniques
- [ ] Cache Redis
- [ ] Rate limiting
- [ ] Logs structurés
- [ ] Déploiement Docker
- [ ] CI/CD Pipeline

---

## 📞 Support

Pour toute question ou problème :
1. Vérifier que tous les tests passent : `python -m pytest test/ -v`
2. Vérifier les performances : `locust -f test/perf/locustfile.py --host=http://localhost:5000 --headless`
3. Consulter les logs du serveur Flask
4. Vérifier la configuration dans `config/messages.py`
