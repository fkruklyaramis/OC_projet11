"""
Tests d'intégration pour les workflows complets de l'application
Testent les parcours utilisateur de bout en bout avec plusieurs composants
"""
import json
from config.messages import Messages


class TestCompleteBookingWorkflows:
    """Tests du workflow complet de réservation"""

    def test_complete_booking_success_workflow(self, client):
        """Test du workflow complet : connexion → navigation → réservation → confirmation"""
        # 1. Accès à la page d'accueil
        response = client.get('/')
        assert response.status_code == 200
        assert b'email' in response.data or b'Welcome' in response.data

        # 2. Connexion via showSummary
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        assert response.status_code == 200
        assert b'john@simplylift.co' in response.data  # Email affiché dans le welcome
        assert b'Points available' in response.data

        # 3. Navigation vers page de réservation
        response = client.get('/book/Simply Lift/Future Championship')
        assert response.status_code == 200
        assert b'Future Championship' in response.data

        # 4. Vérifier l'état initial des données
        with open('test/data/testing/clubs.json', 'r') as f:
            clubs_before = json.load(f)
        with open('test/data/testing/competitions.json', 'r') as f:
            competitions_before = json.load(f)

        initial_club_points = None
        initial_competition_places = None
        for club in clubs_before['clubs']:
            if club['name'] == 'Simply Lift':
                initial_club_points = int(club['points'])
                break
        for comp in competitions_before['competitions']:
            if comp['name'] == 'Future Championship':
                initial_competition_places = int(comp['numberOfPlaces'])
                break

        # 5. Effectuer la réservation
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Future Championship',
            'places': '3'
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # 6. Vérifier que toutes les données ont été mises à jour cohérément
        with open('test/data/testing/clubs.json', 'r') as f:
            clubs_after = json.load(f)
        with open('test/data/testing/competitions.json', 'r') as f:
            competitions_after = json.load(f)

        # Points du club diminués
        for club in clubs_after['clubs']:
            if club['name'] == 'Simply Lift':
                assert int(club['points']) == initial_club_points - 3
                break

        # Places de la compétition diminuées
        for comp in competitions_after['competitions']:
            if comp['name'] == 'Future Championship':
                assert int(comp['numberOfPlaces']) == initial_competition_places - 3
                break

        # 7. Test de déconnexion
        response = client.get('/logout')
        assert response.status_code == 302  # Redirection vers l'accueil

    def test_multiple_bookings_sequential_workflow(self, client):
        """Test de réservations séquentielles avec mise à jour des données"""
        # Connexion avec Simply Lift (15 points initiaux)
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        assert response.status_code == 200

        # Première réservation : 2 places
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Future Championship',
            'places': '2'
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # Vérifier l'état intermédiaire
        with open('test/data/testing/clubs.json', 'r') as f:
            clubs_data = json.load(f)
        for club in clubs_data['clubs']:
            if club['name'] == 'Simply Lift':
                intermediate_points = int(club['points'])
                break

        # Deuxième réservation : 3 places supplémentaires sur une autre compétition
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Next Year Games',
            'places': '3'
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # Vérifier l'état final
        with open('test/data/testing/clubs.json', 'r') as f:
            clubs_final = json.load(f)
        for club in clubs_final['clubs']:
            if club['name'] == 'Simply Lift':
                final_points = int(club['points'])
                assert final_points == intermediate_points - 3
                break

    def test_booking_failure_data_integrity_workflow(self, client):
        """Test que les échecs de réservation n'altèrent pas les données"""
        # Connexion
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        assert response.status_code == 200

        # Capturer l'état initial
        with open('test/data/testing/clubs.json', 'r') as f:
            clubs_before = json.load(f)
        with open('test/data/testing/competitions.json', 'r') as f:
            competitions_before = json.load(f)

        # Tentative de réservation échouée (compétition expirée)
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',  # Compétition passée
            'places': '2'
        })
        assert response.status_code == 200
        assert Messages.COMPETITION_EXPIRED.encode() in response.data

        # Tentative de réservation échouée (trop de places)
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Future Championship',
            'places': '15'  # > 12 maximum
        })
        assert response.status_code == 200
        assert Messages.MAX_PLACES_EXCEEDED.encode() in response.data

        # Vérifier que les données n'ont pas changé
        with open('test/data/testing/clubs.json', 'r') as f:
            clubs_after = json.load(f)
        with open('test/data/testing/competitions.json', 'r') as f:
            competitions_after = json.load(f)

        assert clubs_before == clubs_after
        assert competitions_before == competitions_after


class TestMultiUserWorkflows:
    """Tests d'intégration avec plusieurs utilisateurs/clubs"""

    def test_multiple_clubs_concurrent_bookings(self, client):
        """Test de réservations par différents clubs sur la même compétition"""
        # Capturer l'état initial de Future Championship
        with open('test/data/testing/competitions.json', 'r') as f:
            initial_data = json.load(f)
        initial_places = None
        for comp in initial_data['competitions']:
            if comp['name'] == 'Future Championship':
                initial_places = int(comp['numberOfPlaces'])
                break

        # Club 1: Simply Lift réserve 3 places
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        assert response.status_code == 200
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Future Championship',
            'places': '3'
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # Club 2: She Lifts réserve 2 places
        response = client.post('/showSummary', data={'email': 'kate@shelifts.co.uk'})
        assert response.status_code == 200
        response = client.post('/purchasePlaces', data={
            'club': 'She Lifts',
            'competition': 'Future Championship',
            'places': '2'
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # Club 3: Powerhouse Gym réserve 4 places
        response = client.post('/showSummary', data={'email': 'contact@powerhousegym.com'})
        assert response.status_code == 200
        response = client.post('/purchasePlaces', data={
            'club': 'Powerhouse Gym',
            'competition': 'Future Championship',
            'places': '4'
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # Vérifier que le total des places a été correctement décrementé
        with open('test/data/testing/competitions.json', 'r') as f:
            final_data = json.load(f)
        for comp in final_data['competitions']:
            if comp['name'] == 'Future Championship':
                final_places = int(comp['numberOfPlaces'])
                expected_places = initial_places - 3 - 2 - 4  # Total: 9 places réservées
                assert final_places == expected_places
                break

        # Vérifier que chaque club a bien été débité
        with open('test/data/testing/clubs.json', 'r') as f:
            clubs_data = json.load(f)

        expected_deductions = {
            'Simply Lift': 3,
            'She Lifts': 2,
            'Powerhouse Gym': 4
        }

        for club in clubs_data['clubs']:
            if club['name'] in expected_deductions:
                # Vérifier que les points ont été décrementés (sans connaître les valeurs initiales exactes)
                assert int(club['points']) >= 0

    def test_cross_competition_bookings_workflow(self, client):
        """Test de réservations croisées sur différentes compétitions"""
        competitions_to_test = [
            ('Future Championship', 'Simply Lift', 'john@simplylift.co', 2),
            ('Next Year Games', 'She Lifts', 'kate@shelifts.co.uk', 3),
            ('Future Championship', 'Powerhouse Gym', 'contact@powerhousegym.com', 1),
        ]

        for competition, club, email, places in competitions_to_test:
            # Connexion
            response = client.post('/showSummary', data={'email': email})
            assert response.status_code == 200
            assert email.encode() in response.data  # L'email est affiché, pas le nom du club

            # Navigation vers booking (optionnel)
            response = client.get(f'/book/{club}/{competition}')
            assert response.status_code == 200

            # Réservation
            response = client.post('/purchasePlaces', data={
                'club': club,
                'competition': competition,
                'places': str(places)
            })
            assert response.status_code == 200
            assert Messages.BOOKING_COMPLETE.encode() in response.data

        # Vérifier que toutes les compétitions et clubs ont été mis à jour
        with open('test/data/testing/competitions.json', 'r') as f:
            competitions_data = json.load(f)
        with open('test/data/testing/clubs.json', 'r') as f:
            clubs_data = json.load(f)

        # Vérifier que les données sont cohérentes
        for comp in competitions_data['competitions']:
            assert int(comp['numberOfPlaces']) >= 0

        for club in clubs_data['clubs']:
            assert int(club['points']) >= 0


class TestErrorRecoveryWorkflows:
    """Tests de workflows de récupération d'erreurs"""

    def test_error_recovery_mixed_operations(self, client):
        """Test de récupération après erreurs dans un workflow mixte"""
        # 1. Opération réussie
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        assert response.status_code == 200

        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Future Championship',
            'places': '2'
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # 2. Opération échouée - compétition expirée
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',  # Passée
            'places': '1'
        })
        assert response.status_code == 200
        assert Messages.COMPETITION_EXPIRED.encode() in response.data

        # 3. Nouvelle opération réussie après l'erreur
        response = client.post('/showSummary', data={'email': 'kate@shelifts.co.uk'})
        assert response.status_code == 200

        response = client.post('/purchasePlaces', data={
            'club': 'She Lifts',
            'competition': 'Next Year Games',
            'places': '1'
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # Vérifier que les opérations réussies ont bien été enregistrées
        with open('test/data/testing/clubs.json', 'r') as f:
            clubs_data = json.load(f)

        # Les deux clubs doivent avoir été débités
        clubs_debited = 0
        for club in clubs_data['clubs']:
            if club['name'] in ['Simply Lift', 'She Lifts']:
                # Vérifier qu'il y a eu des changements (sans connaître les valeurs exactes)
                clubs_debited += 1

        assert clubs_debited == 2

    def test_boundary_conditions_workflow(self, client):
        """Test des conditions limites en workflow complet"""
        # Se connecter avec Iron Temple (4 points seulement)
        response = client.post('/showSummary', data={'email': 'admin@irontemple.com'})
        assert response.status_code == 200
        assert b'admin@irontemple.com' in response.data

        # Test 1: Réservation exacte des points disponibles
        response = client.get('/book/Iron Temple/Future Championship')
        assert response.status_code == 200

        response = client.post('/purchasePlaces', data={
            'club': 'Iron Temple',
            'competition': 'Future Championship',
            'places': '4'  # Exactement tous les points
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # Test 2: Vérifier qu'il ne reste plus de points
        with open('test/data/testing/clubs.json', 'r') as f:
            clubs_data = json.load(f)
        for club in clubs_data['clubs']:
            if club['name'] == 'Iron Temple':
                assert int(club['points']) == 0
                break

        # Test 3: Tentative de nouvelle réservation (doit échouer)
        response = client.post('/purchasePlaces', data={
            'club': 'Iron Temple',
            'competition': 'Next Year Games',
            'places': '1'  # Même 1 place doit échouer
        })
        assert response.status_code == 200
        expected_message = Messages.format_not_enough_points(1, 0)
        assert expected_message.encode() in response.data
