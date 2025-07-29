from config.messages import Messages


def test_book_valid_club_and_competition(client):
    """Test de réservation avec club et compétition valides"""
    response = client.get('/book/Simply Lift/Future Championship')
    assert response.status_code == 200
    assert b'Booking' in response.data
    assert b'Simply Lift' in response.data
    assert b'Future Championship' in response.data


def test_book_invalid_club_valid_competition(client):
    """Test avec club invalide et compétition valide"""
    response = client.get('/book/Unknown Club/Spring Festival')
    assert response.status_code == 200
    assert Messages.CLUB_NOT_FOUND.encode() in response.data


def test_book_valid_club_invalid_competition(client):
    """Test avec club valide et compétition invalide"""
    response = client.get('/book/Simply Lift/Unknown Competition')
    assert response.status_code == 200
    assert Messages.COMPETITION_NOT_FOUND.encode() in response.data


def test_book_both_invalid(client):
    """Test avec club et compétition invalides"""
    response = client.get('/book/Unknown Club/Unknown Competition')
    assert response.status_code == 200
    assert Messages.CLUB_NOT_FOUND.encode() in response.data


def test_book_empty_club_name(client):
    """Test avec nom de club vide"""
    response = client.get('/book/ /Spring Festival')
    assert response.status_code == 200
    assert Messages.CLUB_NOT_FOUND.encode() in response.data


def test_book_empty_competition_name(client):
    """Test avec nom de compétition vide"""
    response = client.get('/book/Simply Lift/ ')
    assert response.status_code == 200
    assert Messages.COMPETITION_NOT_FOUND.encode() in response.data


def test_book_case_sensitive_names(client):
    """Test que les noms sont sensibles à la casse"""
    response = client.get('/book/simply lift/spring festival')
    assert response.status_code == 200
    assert Messages.CLUB_NOT_FOUND.encode() in response.data


def test_book_special_characters_in_names(client):
    """Test avec caractères spéciaux dans les noms"""
    response = client.get('/book/Club@Special/Competition#123')
    assert response.status_code == 200
    assert Messages.CLUB_NOT_FOUND.encode() in response.data


def test_book_url_structure(client):
    """Test que l'URL suit la structure attendue /book/<club>/<competition>"""
    response = client.get('/book/Simply Lift/Future Championship')
    assert response.status_code == 200


def test_book_renders_correct_template_on_success(client):
    """Test que le bon template est rendu en cas de succès"""
    response = client.get('/book/Simply Lift/Future Championship')
    assert response.status_code == 200
    assert b'<form' in response.data  # Le template booking.html contient un formulaire


def test_book_flash_message_on_error(client):
    """Test que les messages flash apparaissent en cas d'erreur"""
    response = client.get('/book/Unknown Club/Spring Festival')
    assert response.status_code == 200
    assert Messages.CLUB_NOT_FOUND.encode() in response.data


def test_book_data_passed_to_template(client):
    """Test que les bonnes données sont passées au template"""
    response = client.get('/book/Simply Lift/Future Championship')
    assert response.status_code == 200

    # Vérifier que les données du club et de la compétition sont dans la réponse
    assert b'Simply Lift' in response.data
    assert b'Future Championship' in response.data


def test_book_with_all_clubs_and_competitions(client):
    """Test de réservation avec tous les clubs et compétitions disponibles"""
    test_cases = [
        ('Simply Lift', 'Future Championship'),
        ('Iron Temple', 'Next Year Games'),
        ('She Lifts', 'Future Championship'),
        ('Powerhouse Gym', 'Next Year Games'),
        ('Fit Nation', 'Future Championship'),
        ('Strength Society', 'Next Year Games')
    ]

    for club_name, competition_name in test_cases:
        response = client.get(f'/book/{club_name}/{competition_name}')
        assert response.status_code == 200
        assert club_name.encode() in response.data
        assert competition_name.encode() in response.data


def test_book_with_clubs_by_points(client):
    """Test de réservation en vérifiant les points des clubs"""
    # Simply Lift a 15 points
    response = client.get('/book/Simply Lift/Future Championship')
    assert response.status_code == 200
    assert b'Simply Lift' in response.data

    # Iron Temple a 4 points (moins de points)
    response = client.get('/book/Iron Temple/Next Year Games')
    assert response.status_code == 200
    assert b'Iron Temple' in response.data


def test_book_url_encoding_special_cases(client):
    """Test avec des caractères qui pourraient poser problème dans l'URL"""
    # Test avec des espaces (déjà gérés par Flask)
    response = client.get('/book/Simply Lift/Future Championship')
    assert response.status_code == 200


def test_book_validates_input_parameters(client):
    """Test que la route valide correctement les paramètres d'entrée"""
    # Test avec paramètres valides
    response = client.get('/book/Simply Lift/Future Championship')
    assert response.status_code == 200

    # Test avec paramètres qui n'existent pas
    response = client.get('/book/NonExistentClub/NonExistentCompetition')
    assert response.status_code == 200
    assert Messages.CLUB_NOT_FOUND.encode() in response.data


def test_book_preserves_original_data(client):
    """Test que la consultation ne modifie pas les données originales"""
    # Faire plusieurs requêtes et vérifier que les données restent cohérentes
    for _ in range(3):
        response = client.get('/book/Simply Lift/Future Championship')
        assert response.status_code == 200
        assert b'Simply Lift' in response.data
        assert b'Future Championship' in response.data


def test_book_past_competition_blocked(client):
    """Test qu'on ne peut pas réserver des places pour une compétition passée"""
    response = client.get('/book/Simply Lift/Spring Festival')
    assert response.status_code == 200
    assert Messages.COMPETITION_EXPIRED.encode() in response.data


def test_book_future_competition_allowed(client):
    """Test qu'on peut réserver des places pour une compétition future"""
    response = client.get('/book/Simply Lift/Future Championship')
    assert response.status_code == 200
    assert b'<form' in response.data  # Le template booking.html contient un formulaire
    assert b'Simply Lift' in response.data
    assert b'Future Championship' in response.data


def test_book_multiple_past_competitions_blocked(client):
    """Test que toutes les compétitions passées sont bloquées"""
    past_competitions = [
        'Spring Festival',
        'Fall Classic',
        'Winter Challenge',
        'Summer Showdown',
        'Autumn Championship'
    ]

    for competition in past_competitions:
        response = client.get(f'/book/Simply Lift/{competition}')
        assert response.status_code == 200
        assert Messages.COMPETITION_EXPIRED.encode() in response.data


def test_book_multiple_future_competitions_allowed(client):
    """Test que toutes les compétitions futures sont autorisées"""
    future_competitions = [
        'Future Championship',
        'Next Year Games'
    ]

    for competition in future_competitions:
        response = client.get(f'/book/Simply Lift/{competition}')
        assert response.status_code == 200
        assert b'<form' in response.data  # Le template booking.html contient un formulaire
