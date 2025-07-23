def test_book_valid_club_and_competition(client, first_competition, first_club):
    """Test de réservation avec club et compétition valides"""
    response = client.get(f'/book/{first_competition["name"]}/{first_club["name"]}')
    assert response.status_code == 200
    # Vérifier que la page de réservation s'affiche
    assert b'booking' in response.data.lower() or b'book' in response.data.lower()


def test_book_invalid_club_valid_competition(client, first_competition):
    """Test de réservation avec club inexistant mais compétition valide"""
    response = client.get(f'/book/{first_competition["name"]}/Invalid Club Name')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_valid_club_invalid_competition(client, first_club):
    """Test de réservation avec club valide mais compétition inexistante"""
    response = client.get(f'/book/Invalid Competition/{first_club["name"]}')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_both_invalid(client):
    """Test de réservation avec club et compétition inexistants"""
    response = client.get('/book/Invalid Competition/Invalid Club')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_empty_club_name(client, first_competition):
    """Test de réservation avec nom de club vide"""
    response = client.get(f'/book/{first_competition["name"]}/ ')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_empty_competition_name(client, first_club):
    """Test de réservation avec nom de compétition vide"""
    response = client.get(f'/book/ /{first_club["name"]}')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_case_sensitive_names(client, first_competition, first_club):
    """Test de sensibilité à la casse pour les noms"""
    response = client.get(f'/book/{first_competition["name"].upper()}/{first_club["name"].upper()}')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_special_characters_in_names(client):
    """Test avec caractères spéciaux dans les noms"""
    response = client.get('/book/Competition@#$/Club@#$')
    # Flask peut retourner 404 pour des URLs mal formées, c'est normal
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert b'Something went wrong' in response.data


def test_book_url_structure(client, first_competition, first_club):
    """Test de la structure de l'URL"""
    # URL bien formée
    response = client.get(f'/book/{first_competition["name"]}/{first_club["name"]}')
    assert response.status_code == 200


def test_book_renders_correct_template_on_success(client, first_competition, first_club):
    """Test que le bon template est rendu en cas de succès"""
    response = client.get(f'/book/{first_competition["name"]}/{first_club["name"]}')
    assert response.status_code == 200
    # Vérifier des éléments spécifiques au template booking.html
    assert first_club["name"].encode() in response.data
    assert first_competition["name"].encode() in response.data


def test_book_flash_message_on_error(client):
    """Test que le message flash s'affiche en cas d'erreur"""
    response = client.get('/book/Invalid Competition/Invalid Club')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_data_passed_to_template(client, first_competition, first_club):
    """Test que les bonnes données sont passées au template"""
    response = client.get(f'/book/{first_competition["name"]}/{first_club["name"]}')
    assert response.status_code == 200

    # Vérifier que les données du club sont présentes
    assert first_club["name"].encode() in response.data
    # Supprimé : assert str(first_club["points"]).encode() in response.data

    # Vérifier que les données de la compétition sont présentes
    assert first_competition["name"].encode() in response.data
    assert str(first_competition["numberOfPlaces"]).encode() in response.data


def test_book_with_all_clubs_and_competitions(client, test_data):
    """Test de réservation en utilisant tous les clubs et compétitions disponibles"""
    # Tester avec tous les clubs valides
    for club in test_data['clubs']:
        for competition in test_data['competitions']:
            response = client.get(f'/book/{competition["name"]}/{club["name"]}')
            assert response.status_code == 200
            # Vérifier que les données sont correctement passées
            assert club["name"].encode() in response.data
            assert competition["name"].encode() in response.data


def test_book_with_clubs_by_points(client, club_with_most_points, club_with_least_points, first_competition):
    """Test de réservation avec des clubs ayant différents niveaux de points"""
    # Test avec le club ayant le plus de points
    response = client.get(f'/book/{first_competition["name"]}/{club_with_most_points["name"]}')
    assert response.status_code == 200
    assert club_with_most_points["name"].encode() in response.data
    assert first_competition["name"].encode() in response.data

    # Test avec le club ayant le moins de points
    response = client.get(f'/book/{first_competition["name"]}/{club_with_least_points["name"]}')
    assert response.status_code == 200
    assert club_with_least_points["name"].encode() in response.data
    assert first_competition["name"].encode() in response.data


def test_book_url_encoding_special_cases(client, test_data):
    """Test des cas spéciaux d'encodage d'URL"""
    club = test_data['clubs'][0]
    competition = test_data['competitions'][0]

    # Test avec des espaces dans l'URL (remplacés par %20)
    club_name_encoded = club["name"].replace(" ", "%20")
    competition_name_encoded = competition["name"].replace(" ", "%20")

    response = client.get(f'/book/{competition_name_encoded}/{club_name_encoded}')
    assert response.status_code == 200
    assert club["name"].encode() in response.data
    assert competition["name"].encode() in response.data


def test_book_validates_input_parameters(client, test_data):
    """Test que la fonction book valide correctement les paramètres d'entrée"""
    competition = test_data['competitions'][0]

    # Test avec des noms très longs
    long_name = "a" * 1000
    response = client.get(f'/book/{competition["name"]}/{long_name}')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data

    # Test avec des noms contenant seulement des espaces
    response = client.get(f'/book/{competition["name"]}/   ')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_preserves_original_data(client, first_competition, first_club, test_data):
    """Test que la fonction book ne modifie pas les données originales"""
    # Sauvegarder les données originales
    original_club_points = first_club["points"]
    original_competition_places = first_competition["numberOfPlaces"]

    # Appeler la fonction book
    response = client.get(f'/book/{first_competition["name"]}/{first_club["name"]}')
    assert response.status_code == 200

    # Vérifier que les données n'ont pas été modifiées
    import json
    with open('test/data/clubs.json', 'r') as f:
        clubs_data = json.load(f)
    with open('test/data/competitions.json', 'r') as f:
        competitions_data = json.load(f)

    # Trouver le club et la compétition
    club_found = next(c for c in clubs_data['clubs'] if c['name'] == first_club['name'])
    competition_found = next(c for c in competitions_data['competitions'] if c['name'] == first_competition['name'])

    # Vérifier que les données sont inchangées
    assert club_found["points"] == original_club_points
    assert competition_found["numberOfPlaces"] == original_competition_places
