import pytest
import os
import shutil
import server


def get_test_data_path(filename):
    """Retourne le chemin vers le fichier de données de test"""
    return os.path.join('test', 'data', 'testing', filename)


@pytest.fixture
def app():
    """Fixture pour l'application Flask requise par pytest-flask"""
    return server.app


@pytest.fixture(autouse=True)
def setup_test_data():
    """Copie automatiquement les fichiers source vers testing avant chaque test"""
    source_dir = os.path.join('test', 'data', 'source')
    testing_dir = os.path.join('test', 'data', 'testing')

    # Créer le répertoire testing s'il n'existe pas
    os.makedirs(testing_dir, exist_ok=True)

    # Copier clubs.json et competitions.json
    shutil.copy2(os.path.join(source_dir, 'clubs.json'),
                 os.path.join(testing_dir, 'clubs.json'))
    shutil.copy2(os.path.join(source_dir, 'competitions.json'),
                 os.path.join(testing_dir, 'competitions.json'))

    # Configurer l'environnement de test
    os.environ['TESTING'] = '1'

    # Recharger les données du serveur avec les nouvelles données
    server.clubs = server.loadClubs()
    server.competitions = server.loadCompetitions()

    yield

    # Nettoyer après le test
    if 'TESTING' in os.environ:
        del os.environ['TESTING']


@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    server.app.config['SECRET_KEY'] = 'test-secret-key-for-testing'
    os.environ['TESTING'] = '1'  # S'assurer que le mode test est activé

    with server.app.test_client() as client:
        with server.app.app_context():
            yield client
