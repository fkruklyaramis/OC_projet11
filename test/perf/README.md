# Guide d'utilisation des tests de performance Locust

## Configuration
- Seuil de chargement : 5 secondes maximum
- Seuil de mise à jour : 2 secondes maximum  
- Utilisateurs par défaut : 6
- Serveur sur le port : 5001

## Commandes simples à utiliser

### 1. Démarrer le serveur Flask (dans un terminal)
```bash
python server.py
```

### 2. Lancer les tests de performance (dans un autre terminal)

#### Test rapide avec 6 utilisateurs (recommandé pour étudiant)
```bash
locust -f test/perf/locustfile.py --host=http://localhost:5001 --users=6 --spawn-rate=1 --run-time=30s --html=rapport_performance.html --headless
```

#### Test avec interface web (optionnel)
```bash
locust -f test/perf/locustfile.py --host=http://localhost:5001
```
Puis ouvrir http://localhost:8089 dans le navigateur

#### Test personnalisé avec plus d'utilisateurs
```bash
locust -f test/perf/locustfile.py --host=http://localhost:5001 --users=10 --spawn-rate=2 --run-time=60s --html=rapport_performance.html --headless
```

### 3. Consulter les résultats
- Le rapport HTML sera généré automatiquement
- Les violations des seuils sont affichées dans le terminal
- Ouvrir le fichier `rapport_performance.html` dans un navigateur

## Paramètres expliqués
- `--users=6` : Nombre d'utilisateurs simulés (défaut: 6)
- `--spawn-rate=1` : Vitesse de démarrage des utilisateurs par seconde
- `--run-time=30s` : Durée du test (30 secondes)
- `--html=rapport_performance.html` : Génère un rapport HTML
- `--headless` : Mode sans interface graphique (plus simple)

## Interprétation des résultats
✅ = Endpoint respecte les seuils
❌ = Endpoint dépasse les seuils

Seuils à vérifier :
- Pages de chargement (GET, /showSummary) : ≤ 5000ms
- Mises à jour (/purchasePlaces) : ≤ 2000ms
