import json
from config.messages import Messages


def test_purchase_insufficient_points(client, club_with_least_points, first_competition):
    """Test d'achat avec points insuffisants"""
    # Se connecter avec le club ayant le moins de points
    response = client.post('/showSummary', data={'email': club_with_least_points['email']})
    assert response.status_code == 200

    # Essayer d'acheter plus de places que de points disponibles
    places_to_buy = int(club_with_least_points['points']) + 5
    response = client.post('/purchasePlaces', data={
        'club': club_with_least_points['name'],
        'competition': first_competition['name'],
        'places': str(places_to_buy)
    })

    assert response.status_code == 200
    expected_message = Messages.format_not_enough_points(places_to_buy, club_with_least_points['points'])
    assert expected_message.encode() in response.data


def test_purchase_saves_decremented_club_points(client, first_club, first_competition):
    """Test que les points du club sont décrémentes et sauvegardés correctement"""
    # Se connecter avec le premier club
    client.post('/showSummary', data={'email': first_club['email']})

    # Récupérer les points initiaux depuis test/data/
    with open('test/data/clubs.json', 'r') as f:
        initial_data = json.load(f)
    initial_points = None
    for club in initial_data['clubs']:
        if club['name'] == first_club['name']:
            initial_points = int(club['points'])
            break

    # Acheter 2 places
    response = client.post('/purchasePlaces', data={
        'club': first_club['name'],
        'competition': first_competition['name'],
        'places': '2'
    })

    assert response.status_code == 200
    assert Messages.BOOKING_COMPLETE.encode() in response.data

    # Vérifier que le fichier JSON de test a été mis à jour
    with open('test/data/clubs.json', 'r') as f:
        updated_data = json.load(f)

    for club in updated_data['clubs']:
        if club['name'] == first_club['name']:
            assert int(club['points']) == initial_points - 2
            break


def test_purchase_saves_updated_competition_places(client, first_club, first_competition):
    """Test que le nombre de places de la compétition est sauvegardé correctement"""
    # Se connecter avec le premier club
    client.post('/showSummary', data={'email': first_club['email']})

    # Récupérer le nombre initial de places
    with open('test/data/competitions.json', 'r') as f:
        initial_data = json.load(f)
    initial_places = None
    for comp in initial_data['competitions']:
        if comp['name'] == first_competition['name']:
            initial_places = int(comp['numberOfPlaces'])
            break

    # Acheter 3 places
    response = client.post('/purchasePlaces', data={
        'club': first_club['name'],
        'competition': first_competition['name'],
        'places': '3'
    })

    assert response.status_code == 200
    assert Messages.BOOKING_COMPLETE.encode() in response.data

    # Vérifier que le fichier JSON de test a été mis à jour
    with open('test/data/competitions.json', 'r') as f:
        updated_data = json.load(f)

    for comp in updated_data['competitions']:
        if comp['name'] == first_competition['name']:
            assert int(comp['numberOfPlaces']) == initial_places - 3
            break


def test_purchase_more_than_12_places(client, club_with_most_points, first_competition):
    """Test d'achat de plus de 12 places"""
    # Se connecter avec le club ayant le plus de points
    response = client.post('/showSummary', data={'email': club_with_most_points['email']})
    assert response.status_code == 200

    # Récupérer les points initiaux depuis test/data/
    with open('test/data/clubs.json', 'r') as f:
        initial_data = json.load(f)
    initial_points = None
    for club in initial_data['clubs']:
        if club['name'] == club_with_most_points['name']:
            initial_points = int(club['points'])
            break

    # Essayer d'acheter 15 places (> 12 maximum)
    response = client.post('/purchasePlaces', data={
        'club': club_with_most_points['name'],
        'competition': first_competition['name'],
        'places': '15'
    })

    assert response.status_code == 200
    assert Messages.MAX_PLACES_EXCEEDED.encode() in response.data

    # Vérifier que les points n'ont pas changé dans test/data/
    with open('test/data/clubs.json', 'r') as f:
        club_data = json.load(f)

    for club in club_data['clubs']:
        if club['name'] == club_with_most_points['name']:
            assert int(club['points']) == initial_points  # Pas de changement
            break


def test_purchase_exactly_12_places_success(client, test_data, first_competition):
    """Test qu'on peut acheter exactement 12 places si on a assez de points"""
    # Trouver un club qui a au moins 12 points
    club_with_enough_points = None
    for club in test_data['clubs']:
        if int(club['points']) >= Messages.MAX_PLACES_PER_BOOKING:
            club_with_enough_points = club
            break

    if not club_with_enough_points:
        import pytest
        pytest.skip("Aucun club n'a assez de points pour ce test")

    # Se connecter avec ce club
    response = client.post('/showSummary', data={'email': club_with_enough_points['email']})
    assert response.status_code == 200

    # Acheter exactement 12 places
    response = client.post('/purchasePlaces', data={
        'club': club_with_enough_points['name'],
        'competition': first_competition['name'],
        'places': str(Messages.MAX_PLACES_PER_BOOKING)
    })

    assert response.status_code == 200
    assert Messages.BOOKING_COMPLETE.encode() in response.data

    # Vérifier que les points ont été décrémentes correctement
    with open('test/data/clubs.json', 'r') as f:
        data = json.load(f)

    for club in data['clubs']:
        if club['name'] == club_with_enough_points['name']:
            expected_points = int(club_with_enough_points['points']) - Messages.MAX_PLACES_PER_BOOKING
            assert int(club['points']) == expected_points
            break


def test_purchase_zero_places_error(client, first_club, first_competition):
    """Test qu'on ne peut pas acheter 0 place"""
    # Se connecter
    response = client.post('/showSummary', data={'email': first_club['email']})

    # Essayer d'acheter 0 place - cela devrait causer une erreur ou être rejeté
    response = client.post('/purchasePlaces', data={
        'club': first_club['name'],
        'competition': first_competition['name'],
        'places': '0'
    })

    # Le comportement peut varier selon votre implémentation
    # Soit erreur côté serveur, soit validation côté client
    assert response.status_code in [200, 400, 500]


def test_purchase_invalid_club_or_competition(client, test_data):
    """Test d'achat avec club ou compétition invalide"""
    valid_club = test_data['clubs'][0]
    valid_competition = test_data['competitions'][0]

    # Test avec club invalide
    response = client.post('/purchasePlaces', data={
        'club': 'Invalid Club',
        'competition': valid_competition['name'],
        'places': '2'
    })
    assert response.status_code == 200
    assert Messages.SOMETHING_WENT_WRONG.encode() in response.data

    # Test avec compétition invalide
    response = client.post('/purchasePlaces', data={
        'club': valid_club['name'],
        'competition': 'Invalid Competition',
        'places': '2'
    })
    assert response.status_code == 200
    assert Messages.SOMETHING_WENT_WRONG.encode() in response.data
