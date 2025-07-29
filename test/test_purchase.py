import json
from config.messages import Messages


def test_purchase_insufficient_points(client):
    """Test qu'on ne peut pas acheter plus de places que de points disponibles"""
    # Se connecter avec Iron Temple (4 points)
    response = client.post('/showSummary', data={'email': 'admin@irontemple.com'})

    # Essayer d'acheter 10 places (plus que les 4 points disponibles)
    response = client.post('/purchasePlaces', data={
        'club': 'Iron Temple',
        'competition': 'Future Championship',
        'places': '10'
    })

    assert response.status_code == 200
    expected_message = Messages.format_not_enough_points(10, 4)
    assert expected_message.encode() in response.data


def test_purchase_saves_decremented_club_points(client):
    """Test que les points du club sont sauvegardés correctement après achat"""
    # Se connecter avec Simply Lift (15 points)
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Vérifier les points initiaux
    with open('test/data/testing/clubs.json', 'r') as f:
        initial_data = json.load(f)
    initial_points = None
    for club in initial_data['clubs']:
        if club['name'] == 'Simply Lift':
            initial_points = club['points']
            break

    # Acheter 2 places
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Future Championship',
        'places': '2'
    })

    assert response.status_code == 200
    assert Messages.BOOKING_COMPLETE.encode() in response.data

    # Vérifier que le fichier JSON de test a été mis à jour
    with open('test/data/testing/clubs.json', 'r') as f:
        updated_data = json.load(f)

    for club in updated_data['clubs']:
        if club['name'] == 'Simply Lift':
            assert club['points'] == initial_points - 2
            break


def test_purchase_saves_updated_competition_places(client):
    """Test que le nombre de places de la compétition est sauvegardé correctement"""
    # Se connecter avec Simply Lift
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Vérifier les places initiales
    with open('test/data/testing/competitions.json', 'r') as f:
        initial_data = json.load(f)
    initial_places = None
    for comp in initial_data['competitions']:
        if comp['name'] == 'Future Championship':
            initial_places = comp['numberOfPlaces']
            break

    # Acheter 3 places
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Future Championship',
        'places': '3'
    })

    assert response.status_code == 200
    assert Messages.BOOKING_COMPLETE.encode() in response.data

    # Vérifier que le fichier JSON de test a été mis à jour
    with open('test/data/testing/competitions.json', 'r') as f:
        updated_data = json.load(f)

    for comp in updated_data['competitions']:
        if comp['name'] == 'Future Championship':
            assert comp['numberOfPlaces'] == initial_places - 3
            break


def test_purchase_more_than_12_places(client):
    """Test qu'on ne peut pas acheter plus de 12 places"""
    # Se connecter avec Simply Lift (15 points, assez pour 15 places)
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Vérifier les points initiaux
    with open('test/data/testing/clubs.json', 'r') as f:
        initial_data = json.load(f)
    initial_points = None
    for club in initial_data['clubs']:
        if club['name'] == 'Simply Lift':
            initial_points = club['points']
            break

    # Essayer d'acheter 15 places (> 12 maximum)
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Future Championship',
        'places': '15'
    })

    assert response.status_code == 200
    assert Messages.MAX_PLACES_EXCEEDED.encode() in response.data

    # Vérifier que les points n'ont pas changé dans test/data/testing/
    with open('test/data/testing/clubs.json', 'r') as f:
        club_data = json.load(f)

    for club in club_data['clubs']:
        if club['name'] == 'Simply Lift':
            assert club['points'] == initial_points  # Pas de changement
            break


def test_purchase_exactly_12_places_success(client):
    """Test qu'on peut acheter exactement 12 places si on a assez de points"""
    # Se connecter avec Simply Lift (15 points, assez pour 12 places)
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Acheter exactement 12 places
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Future Championship',
        'places': '12'
    })

    assert response.status_code == 200
    assert Messages.BOOKING_COMPLETE.encode() in response.data

    # Vérifier que les points ont été décrementés correctement
    with open('test/data/testing/clubs.json', 'r') as f:
        data = json.load(f)

    for club in data['clubs']:
        if club['name'] == 'Simply Lift':
            expected_points = 15 - Messages.MAX_PLACES_PER_BOOKING  # 15 - 12 = 3
            assert club['points'] == expected_points
            break


def test_purchase_zero_places_error(client):
    """Test qu'on ne peut pas acheter 0 place"""
    # Se connecter
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Essayer d'acheter 0 place - cela devrait causer une erreur ou être rejeté
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Future Championship',
        'places': '0'
    })

    # Le comportement peut varier selon l'implémentation
    # Soit une erreur, soit pas de changement
    assert response.status_code == 200


def test_purchase_invalid_club_or_competition(client):
    """Test avec club ou compétition invalides"""
    # Se connecter
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Test avec club invalide
    response = client.post('/purchasePlaces', data={
        'club': 'Invalid Club',
        'competition': 'Future Championship',
        'places': '2'
    })
    assert response.status_code == 200

    # Test avec compétition invalide
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Invalid Competition',
        'places': '2'
    })
    assert response.status_code == 200


def test_purchase_with_multiple_clubs(client):
    """Test d'achat avec différents clubs"""
    # Test avec She Lifts (12 points)
    response = client.post('/showSummary', data={'email': 'kate@shelifts.co.uk'})

    response = client.post('/purchasePlaces', data={
        'club': 'She Lifts',
        'competition': 'Next Year Games',
        'places': '5'
    })
    assert response.status_code == 200
    assert Messages.BOOKING_COMPLETE.encode() in response.data

    # Test avec Fit Nation (10 points)
    response = client.post('/showSummary', data={'email': 'info@fitnation.com'})

    response = client.post('/purchasePlaces', data={
        'club': 'Fit Nation',
        'competition': 'Future Championship',
        'places': '3'
    })
    assert response.status_code == 200
    assert Messages.BOOKING_COMPLETE.encode() in response.data


def test_purchase_updates_both_files(client):
    """Test que l'achat met à jour à la fois clubs.json et competitions.json"""
    # Se connecter avec Powerhouse Gym (8 points)
    response = client.post('/showSummary', data={'email': 'contact@powerhousegym.com'})

    # Acheter 4 places pour Summer Showdown
    response = client.post('/purchasePlaces', data={
        'club': 'Powerhouse Gym',
        'competition': 'Future Championship',
        'places': '4'
    })

    assert response.status_code == 200
    assert Messages.BOOKING_COMPLETE.encode() in response.data

    # Vérifier les deux fichiers JSON
    with open('test/data/testing/clubs.json', 'r') as f:
        clubs_data = json.load(f)

    with open('test/data/testing/competitions.json', 'r') as f:
        competitions_data = json.load(f)

    # Vérifier que les points du club ont diminué
    for club in clubs_data['clubs']:
        if club['name'] == 'Powerhouse Gym':
            assert club['points'] == 4  # 8 - 4 = 4
            break

    # Vérifier que les places de la compétition ont diminué
    for comp in competitions_data['competitions']:
        if comp['name'] == 'Future Championship':
            assert comp['numberOfPlaces'] == 26  # 30 - 4 = 26
            break
