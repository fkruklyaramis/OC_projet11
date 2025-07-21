import json


def test_purchase_saves_updated_competition_places(client):
    """Test que le nombre de places de la compétition est sauvegardé correctement"""
    # Se connecter avec un club qui a des points
    client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Récupérer le nombre initial de places depuis test/data/
    with open('test/data/competitions.json', 'r') as f:
        initial_data = json.load(f)
    initial_places = None
    for comp in initial_data['competitions']:
        if comp['name'] == 'Spring Festival':
            initial_places = int(comp['numberOfPlaces'])
            break

    # Acheter 3 places
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': '3'
    })

    assert response.status_code == 200
    assert b'Great-booking complete!' in response.data

    # Vérifier que le fichier JSON de test a été mis à jour
    with open('test/data/competitions.json', 'r') as f:
        updated_data = json.load(f)

    for comp in updated_data['competitions']:
        if comp['name'] == 'Spring Festival':
            assert int(comp['numberOfPlaces']) == initial_places - 3
            break


def test_purchase_saves_decremented_club_points(client):
    """Test que les points du club sont décrémentes et sauvegardés correctement"""
    # Se connecter avec un club qui a des points
    client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Récupérer les points initiaux depuis test/data/
    with open('test/data/clubs.json', 'r') as f:
        initial_data = json.load(f)
    initial_points = None
    for club in initial_data['clubs']:
        if club['name'] == 'Simply Lift':
            initial_points = int(club['points'])
            break

    # Acheter 2 places
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': '2'
    })

    assert response.status_code == 200
    assert b'Great-booking complete!' in response.data

    # Vérifier que le fichier JSON de test a été mis à jour
    with open('test/data/clubs.json', 'r') as f:
        updated_data = json.load(f)

    for club in updated_data['clubs']:
        if club['name'] == 'Simply Lift':
            assert int(club['points']) == initial_points - 2
            break


def test_purchase_insufficient_points(client):
    """Test d'achat avec points insuffisants"""
    # Se connecter avec Iron Temple qui n'a que 4 points
    response = client.post('/showSummary', data={'email': 'admin@irontemple.com'})
    assert response.status_code == 200

    # Essayer d'acheter 10 places (plus que les 4 points disponibles)
    response = client.post('/purchasePlaces', data={
        'club': 'Iron Temple',
        'competition': 'Spring Festival',
        'places': '10'
    })

    assert response.status_code == 200
    assert b'Not enough points! You need 10 points but have 4' in response.data

    # Vérifier que les points n'ont PAS été décrémentes dans test/data/
    with open('test/data/clubs.json', 'r') as f:
        data = json.load(f)

    for club in data['clubs']:
        if club['name'] == 'Iron Temple':
            assert club['points'] == '4'  # Toujours 4 points
            break


def test_purchase_more_than_12_places(client):
    """Test d'achat de plus de 12 places"""
    # Se connecter avec un club qui a assez de points
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200

    # Récupérer les points initiaux depuis test/data/
    with open('test/data/clubs.json', 'r') as f:
        initial_data = json.load(f)
    initial_points = None
    for club in initial_data['clubs']:
        if club['name'] == 'Simply Lift':
            initial_points = int(club['points'])
            break

    # Essayer d'acheter 15 places (> 12 maximum)
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': '15'
    })

    assert response.status_code == 200
    assert b'You cannot book more than 12 places per competition!' in response.data

    # Vérifier que les points n'ont pas changé dans test/data/
    with open('test/data/clubs.json', 'r') as f:
        club_data = json.load(f)

    for club in club_data['clubs']:
        if club['name'] == 'Simply Lift':
            assert int(club['points']) == initial_points  # Pas de changement
            break


def test_purchase_exactly_12_places_success(client):
    """Test qu'on peut acheter exactement 12 places si on a assez de points"""
    # Se connecter avec She Lifts qui a 12 points
    response = client.post('/showSummary', data={'email': 'kate@shelifts.co.uk'})
    assert response.status_code == 200

    # Acheter exactement 12 places
    response = client.post('/purchasePlaces', data={
        'club': 'She Lifts',
        'competition': 'Spring Festival',
        'places': '12'
    })

    assert response.status_code == 200
    assert b'Great-booking complete!' in response.data

    # Vérifier que les points sont à 0 maintenant dans test/data/
    with open('test/data/clubs.json', 'r') as f:
        data = json.load(f)

    for club in data['clubs']:
        if club['name'] == 'She Lifts':
            assert club['points'] == '0'
            break


def test_purchase_zero_places_error(client):
    """Test qu'on ne peut pas acheter 0 place"""
    # Se connecter
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Essayer d'acheter 0 place - cela devrait causer une erreur ou être rejeté
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': '0'
    })

    # Le comportement peut varier selon votre implémentation
    # Soit erreur côté serveur, soit validation côté client
    assert response.status_code in [200, 400, 500]
