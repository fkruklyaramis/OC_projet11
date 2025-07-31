"""
Tests de performance avec Locust - Version Simple
Tests selon les spécifications :
- Temps de chargement ≤ 5 secondes
- Mises à jour ≤ 2 secondes
- 6 utilisateurs par défaut

Usage:
    locust -f test/perf/locustfile.py --host=http://localhost:5050
"""
import time
import sys
import os
from locust import HttpUser, task, between, events

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.messages import PerformanceThresholds  # noqa: E402


class WebsiteUser(HttpUser):
    """Utilisateur simulé testant les pages de chargement"""
    wait_time = between(1, 3)

    def on_start(self):
        """Initialisation - visite de la page d'accueil"""
        self.client.get("/")

    @task(3)
    def test_homepage_loading(self):
        """Test du temps de chargement de la page d'accueil (seuil: 5s)"""
        start_time = time.time()
        with self.client.get("/", catch_response=True) as response:
            response_time = time.time() - start_time

            if response.status_code == 200:
                if response_time <= PerformanceThresholds.MAX_LOADING_TIME:
                    response.success()
                else:
                    response.failure(
                        f"Page d'accueil trop lente: {response_time:.2f}s > "
                        f"{PerformanceThresholds.MAX_LOADING_TIME}s"
                    )
            else:
                response.failure(f"Erreur HTTP: {response.status_code}")

    @task(2)
    def test_login_loading(self):
        """Test du temps de chargement de la connexion (seuil: 5s)"""
        start_time = time.time()
        with self.client.post("/showSummary",
                              data={'email': 'john@simplylift.co'},
                              catch_response=True) as response:
            response_time = time.time() - start_time

            if response.status_code == 200:
                if response_time <= PerformanceThresholds.MAX_LOADING_TIME:
                    response.success()
                else:
                    response.failure(
                        f"Connexion trop lente: {response_time:.2f}s > "
                        f"{PerformanceThresholds.MAX_LOADING_TIME}s"
                    )
            else:
                response.failure(f"Erreur de connexion: {response.status_code}")

    @task(2)
    def test_booking_page_loading(self):
        """Test du temps de chargement de la page de réservation (seuil: 5s)"""
        start_time = time.time()
        with self.client.get("/book/Simply Lift/Future Championship",
                             catch_response=True) as response:
            response_time = time.time() - start_time

            if response.status_code == 200:
                if response_time <= PerformanceThresholds.MAX_LOADING_TIME:
                    response.success()
                else:
                    response.failure(
                        f"Page de réservation trop lente: {response_time:.2f}s > "
                        f"{PerformanceThresholds.MAX_LOADING_TIME}s"
                    )
            else:
                response.failure(f"Erreur page de réservation: {response.status_code}")


class BookingUser(HttpUser):
    """Utilisateur simulé testant les mises à jour (achats de places)"""
    wait_time = between(2, 5)

    def on_start(self):
        """Connexion au démarrage"""
        self.client.post("/showSummary", data={'email': 'john@simplylift.co'})

    @task(1)
    def test_purchase_update_time(self):
        """Test du temps de mise à jour lors d'un achat (seuil: 2s)"""
        start_time = time.time()
        with self.client.post("/purchasePlaces",
                              data={
                                  'club': 'Simply Lift',
                                  'competition': 'Future Championship',
                                  'places': '1'
                              },
                              catch_response=True) as response:
            response_time = time.time() - start_time

            if response.status_code == 200:
                if response_time <= PerformanceThresholds.MAX_UPDATE_TIME:
                    response.success()
                else:
                    response.failure(
                        f"Mise à jour trop lente: {response_time:.2f}s > "
                        f"{PerformanceThresholds.MAX_UPDATE_TIME}s"
                    )
            else:
                response.failure(f"Erreur lors de l'achat: {response.status_code}")


# Événements pour afficher les résultats
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Affichage des seuils au début du test"""
    print("\n" + "="*60)
    print("TESTS DE PERFORMANCE LOCUST")
    print("="*60)
    print("Seuils configurés:")
    print(f"   • Chargement maximum: {PerformanceThresholds.MAX_LOADING_TIME}s")
    print(f"   • Mise à jour maximum: {PerformanceThresholds.MAX_UPDATE_TIME}s")
    print(f"   • Utilisateurs par défaut: {PerformanceThresholds.DEFAULT_USERS}")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Affichage du résumé à la fin du test"""
    print("\n" + "="*60)
    print("RÉSULTATS DES TESTS DE PERFORMANCE")
    print("="*60)

    stats = environment.stats

    print("Statistiques globales:")
    print(f"   • Requêtes totales: {stats.total.num_requests}")
    print(f"   • Échecs: {stats.total.num_failures}")
    print(f"   • Temps de réponse médian: {stats.total.median_response_time}ms")
    print(f"   • Temps de réponse moyen: {stats.total.avg_response_time:.1f}ms")
    print(f"   • Temps de réponse max: {stats.total.max_response_time}ms")

    # Vérification des seuils
    violations_chargement = 0
    violations_mise_a_jour = 0

    max_loading_ms = PerformanceThresholds.MAX_LOADING_TIME * 1000
    max_update_ms = PerformanceThresholds.MAX_UPDATE_TIME * 1000

    print("Détail par endpoint:")
    for entry in stats.entries.values():
        is_loading = (entry.method == "GET" or
                      (entry.method == "POST" and "/showSummary" in entry.name))
        is_update = (entry.method == "POST" and "/purchasePlaces" in entry.name)

        status = "OK"
        if is_loading and entry.max_response_time > max_loading_ms:
            violations_chargement += 1
            status = "KO"
        elif is_update and entry.max_response_time > max_update_ms:
            violations_mise_a_jour += 1
            status = "KO"

        print(f"   {status} {entry.method} {entry.name}: "
              f"max={entry.max_response_time}ms, "
              f"avg={entry.avg_response_time:.1f}ms")

    print("Conformité aux seuils:")
    print(f"   • Violations chargement (>{PerformanceThresholds.MAX_LOADING_TIME}s): "
          f"{violations_chargement}")
    print(f"   • Violations mise à jour (>{PerformanceThresholds.MAX_UPDATE_TIME}s): "
          f"{violations_mise_a_jour}")

    if violations_chargement == 0 and violations_mise_a_jour == 0:
        print("OK - Tous les seuils sont respectés !")
    else:
        print("KO - es seuils ont été dépassés.")

    print("="*60 + "\n")
