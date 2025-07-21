import pytest
import shutil
import os
from server import app
import server


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Copie les JSON de production vers test/data/ et configure l'environnement"""
    # Créer le dossier test/data s'il n'existe pas
    os.makedirs('test/data', exist_ok=True)

    # Copier les fichiers de production vers test/data
    shutil.copy('clubs.json', 'test/data/clubs.json')
    shutil.copy('competitions.json', 'test/data/competitions.json')


@pytest.fixture(autouse=True)
def reset_test_data():
    """Restaure les données de test avant chaque test"""
    # Restaurer les copies originales depuis la racine
    shutil.copy('clubs.json', 'test/data/clubs.json')
    shutil.copy('competitions.json', 'test/data/competitions.json')

    # Forcer le rechargement des données avec les chemins de test
    os.environ['TESTING'] = '1'  # Activer le mode test
    server.clubs = server.loadClubs()
    server.competitions = server.loadCompetitions()

    # Nettoyer après le test
    if 'TESTING' in os.environ:
        del os.environ['TESTING']


@pytest.fixture
def client():
    app.config['TESTING'] = True
    os.environ['TESTING'] = '1'  # S'assurer que le mode test est activé

    with app.test_client() as client:
        with app.app_context():
            yield client
