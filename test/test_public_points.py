from config.messages import Messages


def test_index_page_shows_club_points_table(client):
    """Test que la page d'accueil affiche le tableau des points des clubs"""
    response = client.get('/')
    assert response.status_code == 200

    # Vérifier que le tableau est présent
    assert Messages.CLUB_POINTS_OVERVIEW.encode() in response.data
    assert b'<table' in response.data
    assert b'Club Name' in response.data
    assert b'Available Points' in response.data

    response_text = response.data.decode()

    # Vérifier que les clubs spécifiques sont présents dans la table
    assert 'Simply Lift' in response_text
    assert 'Iron Temple' in response_text
    assert 'She Lifts' in response_text
    assert 'Powerhouse Gym' in response_text
    assert 'Fit Nation' in response_text
    assert 'Strength Society' in response_text

    # Vérifier que les points sont affichés (maintenant en tant qu'entiers)
    assert '15' in response_text  # Simply Lift points
    assert '4' in response_text   # Iron Temple points
    assert '12' in response_text  # She Lifts points


def test_public_table_readonly_no_login_required(client):
    """Test que le tableau public est accessible sans connexion"""
    response = client.get('/')
    assert response.status_code == 200

    # Pas besoin de se connecter pour voir les points
    assert Messages.CLUB_POINTS_OVERVIEW.encode() in response.data
    assert b'<table' in response.data


def test_points_table_displays_current_data(client):
    """Test que le tableau affiche les données actuelles des points"""
    response = client.get('/')
    assert response.status_code == 200

    response_text = response.data.decode()

    # Vérifier que chaque club et ses points sont dans la réponse
    clubs_data = [
        ('Simply Lift', '15'),
        ('Iron Temple', '4'),
        ('She Lifts', '12'),
        ('Powerhouse Gym', '8'),
        ('Fit Nation', '10'),
        ('Strength Society', '6')
    ]

    for club_name, club_points in clubs_data:
        assert club_name in response_text
        assert club_points in response_text


def test_table_styling_and_structure(client):
    """Test que le tableau a la structure HTML appropriée"""
    response = client.get('/')
    assert response.status_code == 200

    # Vérifier la structure HTML du tableau
    assert b'<table' in response.data
    assert b'<thead>' in response.data or b'<th>' in response.data
    assert b'<tbody>' in response.data or b'<tr>' in response.data
    # Chercher <td avec ou sans attributs
    assert b'<td' in response.data

    # Vérifier les en-têtes de colonne
    assert b'Club Name' in response.data
    assert b'Available Points' in response.data


def test_points_table_shows_all_registered_clubs(client):
    """Test que le tableau affiche tous les clubs enregistrés"""
    response = client.get('/')
    assert response.status_code == 200

    response_text = response.data.decode()

    # Compter le nombre de clubs affichés
    expected_clubs = ['Simply Lift', 'Iron Temple', 'She Lifts', 'Powerhouse Gym', 'Fit Nation', 'Strength Society']

    for club in expected_clubs:
        assert club in response_text, f"Club '{club}' not found in points table"


def test_points_displayed_as_numbers_not_strings(client):
    """Test que les points sont affichés comme des nombres"""
    response = client.get('/')
    assert response.status_code == 200

    response_text = response.data.decode()

    # Les points ne devraient plus être entre guillemets (pas de "15" mais 15)
    assert '"15"' not in response_text  # Plus de string
    assert '"4"' not in response_text   # Plus de string
    assert '15' in response_text        # Nombre direct
    assert '4' in response_text         # Nombre direct
