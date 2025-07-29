from config.messages import Messages


def test_purchase_past_competition_blocked(client):
    """Test qu'on ne peut pas acheter des places pour une compétition passée"""
    # Se connecter avec Simply Lift
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Essayer d'acheter des places pour une compétition passée
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Spring Festival',  # Compétition passée (2020)
        'places': '2'
    })

    assert response.status_code == 200
    assert Messages.COMPETITION_EXPIRED.encode() in response.data


def test_purchase_future_competition_allowed(client):
    """Test qu'on peut acheter des places pour une compétition future"""
    # Se connecter avec Simply Lift
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Acheter des places pour une compétition future
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Future Championship',  # Compétition future (2026)
        'places': '2'
    })

    assert response.status_code == 200
    assert Messages.BOOKING_COMPLETE.encode() in response.data


def test_purchase_multiple_past_competitions_blocked(client):
    """Test que toutes les compétitions passées bloquent l'achat"""
    past_competitions = [
        'Spring Festival',
        'Fall Classic',
        'Winter Challenge',
        'Summer Showdown',
        'Autumn Championship'
    ]

    for competition in past_competitions:
        # Se connecter avec Simply Lift
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

        # Essayer d'acheter des places
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': competition,
            'places': '1'
        })

        assert response.status_code == 200
        assert Messages.COMPETITION_EXPIRED.encode() in response.data


def test_purchase_multiple_future_competitions_allowed(client):
    """Test que toutes les compétitions futures permettent l'achat"""
    future_competitions = [
        ('Future Championship', 'Powerhouse Gym'),  # 8 points
        ('Next Year Games', 'She Lifts')  # 12 points
    ]

    for competition, club_name in future_competitions:
        # Se connecter avec le club approprié
        if club_name == 'Powerhouse Gym':
            email = 'contact@powerhousegym.com'
        else:  # She Lifts
            email = 'kate@shelifts.co.uk'

        response = client.post('/showSummary', data={'email': email})

        # Acheter des places
        response = client.post('/purchasePlaces', data={
            'club': club_name,
            'competition': competition,
            'places': '1'
        })

        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data


def test_book_expired_vs_valid_competitions_mixed(client):
    """Test mixte avec compétitions expirées et valides"""
    # Compétition expirée
    response = client.get('/book/Simply Lift/Fall Classic')
    assert response.status_code == 200
    assert Messages.COMPETITION_EXPIRED.encode() in response.data

    # Compétition valide
    response = client.get('/book/Simply Lift/Next Year Games')
    assert response.status_code == 200
    assert b'<form' in response.data  # Le template booking.html contient un formulaire
    assert b'Next Year Games' in response.data


def test_purchase_expired_vs_valid_competitions_mixed(client):
    """Test mixte d'achat avec compétitions expirées et valides"""
    # Se connecter avec Simply Lift
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Compétition expirée - doit échouer
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Winter Challenge',  # Expirée
        'places': '1'
    })
    assert response.status_code == 200
    assert Messages.COMPETITION_EXPIRED.encode() in response.data

    # Compétition valide - doit réussir
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Future Championship',  # Future
        'places': '1'
    })
    assert response.status_code == 200
    assert Messages.BOOKING_COMPLETE.encode() in response.data
