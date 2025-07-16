import pytest
from server import app


@pytest.fixture
def client():
    # Créer un fichier temporaire pour la base de données de test
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def sample_clubs():
    return [
        {"name": "Test Club", "email": "test@club.com", "points": "10"},
        {"name": "Another Club", "email": "another@club.com", "points": "15"}
    ]


@pytest.fixture
def sample_competitions():
    return [
        {"name": "Test Competition", "date": "2025-08-01 10:00:00", "numberOfPlaces": "25"},
        {"name": "Another Competition", "date": "2025-09-01 10:00:00", "numberOfPlaces": "15"}
    ]
