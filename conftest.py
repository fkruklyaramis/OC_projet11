import pytest
import shutil
import os
import json
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

    yield


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

    yield

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


@pytest.fixture
def test_data():
    """Fixture qui retourne les données de test depuis les fichiers JSON"""
    with open('test/data/clubs.json', 'r') as f:
        clubs_data = json.load(f)

    with open('test/data/competitions.json', 'r') as f:
        competitions_data = json.load(f)

    return {
        'clubs': clubs_data['clubs'],
        'competitions': competitions_data['competitions']
    }


@pytest.fixture
def first_club(test_data):
    """Retourne le premier club des données de test"""
    return test_data['clubs'][0]


@pytest.fixture
def second_club(test_data):
    """Retourne le deuxième club des données de test"""
    return test_data['clubs'][1] if len(test_data['clubs']) > 1 else test_data['clubs'][0]


@pytest.fixture
def third_club(test_data):
    """Retourne le troisième club des données de test"""
    return test_data['clubs'][2] if len(test_data['clubs']) > 2 else test_data['clubs'][0]


@pytest.fixture
def club_with_least_points(test_data):
    """Retourne le club avec le moins de points"""
    return min(test_data['clubs'], key=lambda c: int(c['points']))


@pytest.fixture
def club_with_most_points(test_data):
    """Retourne le club avec le plus de points"""
    return max(test_data['clubs'], key=lambda c: int(c['points']))


@pytest.fixture
def first_competition(test_data):
    """Retourne la première compétition des données de test"""
    return test_data['competitions'][0]


@pytest.fixture
def second_competition(test_data):
    """Retourne la deuxième compétition des données de test"""
    return test_data['competitions'][1] if len(test_data['competitions']) > 1 else test_data['competitions'][0]


@pytest.fixture
def valid_email(first_club):
    """Retourne un email valide"""
    return first_club['email']


@pytest.fixture
def invalid_email():
    """Retourne un email invalide"""
    return 'invalid@email.com'
