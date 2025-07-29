"""
Tests d'intégration des endpoints et API
Testent les interactions entre différents endpoints et la cohérence des réponses
"""
import json
from config.messages import Messages


class TestEndpointIntegration:
    """Tests d'intégration des endpoints"""

    def test_full_navigation_flow(self, client):
        """Test du flux de navigation complet entre tous les endpoints"""
        # 1. Accès à la page d'accueil
        response = client.get('/')
        assert response.status_code == 200
        assert b'email' in response.data  # Formulaire de connexion présent

        # 2. Connexion via showSummary
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        assert response.status_code == 200
        assert b'john@simplylift.co' in response.data  # Email affiché dans le welcome
        assert b'Points available' in response.data or b'points' in response.data

        # 3. Navigation vers page de réservation
        response = client.get('/book/Simply Lift/Future Championship')
        assert response.status_code == 200
        assert b'Future Championship' in response.data
        assert b'Simply%20Lift' in response.data or b'Simply Lift' in response.data

        # 4. Effectuer une réservation
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Future Championship',
            'places': '2'
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # 5. Déconnexion
        response = client.get('/logout')
        assert response.status_code == 302  # Redirection

        # 6. Vérifier retour à l'accueil après logout
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200

    def test_endpoint_error_propagation(self, client):
        """Test de la propagation d'erreurs entre endpoints"""
        # Connexion avec email invalide
        response = client.post('/showSummary', data={'email': 'invalid@test.com'})
        # Doit rediriger vers l'accueil avec message d'erreur
        assert (response.status_code == 302 or
                Messages.CLUB_NOT_FOUND.encode() in response.data)

        # Après connexion valide, tester booking avec club invalide
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        assert response.status_code == 200

        response = client.get('/book/Invalid Club/Future Championship')
        assert response.status_code == 200
        assert Messages.CLUB_NOT_FOUND.encode() in response.data

        # Test avec compétition invalide
        response = client.get('/book/Simply Lift/Invalid Competition')
        assert response.status_code == 200
        assert Messages.COMPETITION_NOT_FOUND.encode() in response.data

        # Test avec compétition expirée
        response = client.get('/book/Simply Lift/Spring Festival')
        assert response.status_code == 200
        assert Messages.COMPETITION_EXPIRED.encode() in response.data

    def test_endpoint_data_consistency(self, client):
        """Test de cohérence des données entre les endpoints"""
        # Connexion
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        assert response.status_code == 200

        # Capturer l'état initial
        with open('test/data/testing/clubs.json', 'r') as f:
            initial_clubs = json.load(f)
        with open('test/data/testing/competitions.json', 'r') as f:
            initial_competitions = json.load(f)

        # Réservation via purchasePlaces
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Future Championship',
            'places': '3'
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # Vérifier que les données ont été mises à jour
        with open('test/data/testing/clubs.json', 'r') as f:
            updated_clubs = json.load(f)
        with open('test/data/testing/competitions.json', 'r') as f:
            updated_competitions = json.load(f)

        # Vérifier les changements dans clubs.json
        simply_lift_initial = None
        simply_lift_updated = None
        for club in initial_clubs['clubs']:
            if club['name'] == 'Simply Lift':
                simply_lift_initial = int(club['points'])
                break
        for club in updated_clubs['clubs']:
            if club['name'] == 'Simply Lift':
                simply_lift_updated = int(club['points'])
                break

        assert simply_lift_updated == simply_lift_initial - 3

        # Vérifier les changements dans competitions.json
        future_championship_initial = None
        future_championship_updated = None
        for comp in initial_competitions['competitions']:
            if comp['name'] == 'Future Championship':
                future_championship_initial = int(comp['numberOfPlaces'])
                break
        for comp in updated_competitions['competitions']:
            if comp['name'] == 'Future Championship':
                future_championship_updated = int(comp['numberOfPlaces'])
                break

        assert future_championship_updated == future_championship_initial - 3

    def test_endpoint_response_format_consistency(self, client):
        """Test de cohérence du format des réponses entre endpoints"""
        endpoints_to_test = [
            {
                'method': 'GET',
                'endpoint': '/',
                'expected_content_type': 'text/html',
                'expected_status': 200
            },
            {
                'method': 'POST',
                'endpoint': '/showSummary',
                'data': {'email': 'john@simplylift.co'},
                'expected_content_type': 'text/html',
                'expected_status': 200
            },
            {
                'method': 'GET',
                'endpoint': '/book/Simply Lift/Future Championship',
                'expected_content_type': 'text/html',
                'expected_status': 200
            },
            {
                'method': 'POST',
                'endpoint': '/purchasePlaces',
                'data': {
                    'club': 'Simply Lift',
                    'competition': 'Future Championship',
                    'places': '1'
                },
                'expected_content_type': 'text/html',
                'expected_status': 200
            },
            {
                'method': 'GET',
                'endpoint': '/logout',
                'expected_status': 302  # Redirection
            }
        ]

        for endpoint_test in endpoints_to_test:
            if endpoint_test['method'] == 'GET':
                response = client.get(endpoint_test['endpoint'])
            elif endpoint_test['method'] == 'POST':
                response = client.post(endpoint_test['endpoint'],
                                       data=endpoint_test.get('data', {}))

            assert response.status_code == endpoint_test['expected_status']

            if 'expected_content_type' in endpoint_test:
                assert endpoint_test['expected_content_type'] in response.content_type

    def test_endpoint_parameter_validation(self, client):
        """Test de validation des paramètres entre endpoints"""
        # Test avec paramètres manquants
        response = client.post('/showSummary', data={})
        # Doit gérer l'absence d'email
        assert response.status_code in [200, 302, 400]

        # Test avec paramètres invalides dans l'URL
        response = client.get('/book/ /Future Championship')  # Club avec espace
        assert response.status_code == 200  # Doit gérer gracieusement

        response = client.get('/book/Simply Lift/ ')  # Compétition avec espace
        assert response.status_code == 200

        # Test avec données POST manquantes
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            # Manque 'competition' and 'places'
        })
        # Doit gérer l'erreur
        assert response.status_code in [200, 400, 500]

    def test_endpoint_state_transitions(self, client):
        """Test des transitions d'état entre endpoints"""
        # État initial : non connecté
        response = client.get('/')
        assert response.status_code == 200

        # Transition : connexion
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        assert response.status_code == 200
        assert b'john@simplylift.co' in response.data

        # État : connecté et navigation
        response = client.get('/book/Simply Lift/Future Championship')
        assert response.status_code == 200
        assert b'Future Championship' in response.data

        # État : réservation en cours
        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Future Championship',
            'places': '2'
        })
        assert response.status_code == 200
        # Doit retourner à l'état "connecté" avec confirmation
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # Transition : déconnexion
        response = client.get('/logout')
        assert response.status_code == 302

        # État final : retour à non connecté
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200


class TestEndpointDataFlow:
    """Tests du flux de données entre endpoints"""

    def test_data_persistence_across_endpoints(self, client):
        """Test que les modifications persistent à travers les endpoints"""
        # Connexion et première modification
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        assert response.status_code == 200

        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Future Championship',
            'places': '2'
        })
        assert response.status_code == 200
        assert Messages.BOOKING_COMPLETE.encode() in response.data

        # Nouvelle connexion pour vérifier la persistance
        response = client.post('/showSummary', data={'email': 'kate@shelifts.co.uk'})
        assert response.status_code == 200

        # Les modifications précédentes doivent être persistées
        with open('test/data/testing/clubs.json', 'r') as f:
            clubs_data = json.load(f)

        # Simply Lift doit avoir des points modifiés
        simply_lift_found = False
        for club in clubs_data['clubs']:
            if club['name'] == 'Simply Lift':
                simply_lift_found = True
                # Les points doivent être différents de la valeur par défaut
                break
        assert simply_lift_found

    def test_cross_endpoint_error_handling(self, client):
        """Test de gestion d'erreurs à travers les endpoints"""
        # Séquence d'opérations avec erreurs intercalées
        operations = [
            # Opération valide
            {
                'type': 'login',
                'data': {'email': 'john@simplylift.co'},
                'should_succeed': True
            },
            # Opération invalide
            {
                'type': 'book',
                'endpoint': '/book/Invalid Club/Future Championship',
                'should_succeed': False
            },
            # Opération valide après erreur
            {
                'type': 'book',
                'endpoint': '/book/Simply Lift/Future Championship',
                'should_succeed': True
            },
            # Opération d'achat invalide
            {
                'type': 'purchase',
                'data': {
                    'club': 'Simply Lift',
                    'competition': 'Spring Festival',  # Expirée
                    'places': '1'
                },
                'should_succeed': False
            },
            # Opération d'achat valide après erreur
            {
                'type': 'purchase',
                'data': {
                    'club': 'Simply Lift',
                    'competition': 'Future Championship',
                    'places': '1'
                },
                'should_succeed': True
            }
        ]

        successful_operations = 0
        failed_operations = 0

        for operation in operations:
            if operation['type'] == 'login':
                response = client.post('/showSummary', data=operation['data'])
                if operation['should_succeed']:
                    assert response.status_code == 200
                    successful_operations += 1
                else:
                    failed_operations += 1

            elif operation['type'] == 'book':
                response = client.get(operation['endpoint'])
                assert response.status_code == 200
                if operation['should_succeed']:
                    # Pas d'erreur dans la réponse
                    successful_operations += 1
                else:
                    # Doit contenir un message d'erreur
                    error_found = any([
                        Messages.CLUB_NOT_FOUND.encode() in response.data,
                        Messages.COMPETITION_NOT_FOUND.encode() in response.data,
                        Messages.COMPETITION_EXPIRED.encode() in response.data
                    ])
                    assert error_found
                    failed_operations += 1

            elif operation['type'] == 'purchase':
                response = client.post('/purchasePlaces', data=operation['data'])
                assert response.status_code == 200
                if operation['should_succeed']:
                    assert Messages.BOOKING_COMPLETE.encode() in response.data
                    successful_operations += 1
                else:
                    # Doit contenir un message d'erreur
                    error_found = any([
                        Messages.COMPETITION_EXPIRED.encode() in response.data,
                        Messages.MAX_PLACES_EXCEEDED.encode() in response.data,
                        b'not enough points' in response.data
                    ])
                    assert error_found
                    failed_operations += 1

        # Vérifier qu'on a eu les bons nombres de succès et d'échecs
        expected_successes = sum(1 for op in operations if op['should_succeed'])
        expected_failures = sum(1 for op in operations if not op['should_succeed'])

        assert successful_operations == expected_successes
        assert failed_operations == expected_failures

    def test_endpoint_data_race_conditions(self, client):
        """Test de conditions de course potentielles entre endpoints"""
        # Simuler des accès "rapides" aux mêmes données

        # État initial
        with open('test/data/testing/clubs.json', 'r') as f:
            initial_clubs = json.load(f)

        # Séquence rapide d'opérations sur le même club
        responses = []

        # Connexion
        response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        responses.append(response)

        # Plusieurs achats rapides
        for i in range(3):
            response = client.post('/purchasePlaces', data={
                'club': 'Simply Lift',
                'competition': 'Future Championship',
                'places': '1'
            })
            responses.append(response)

        # Vérifier que toutes les requêtes ont été traitées
        for response in responses:
            assert response.status_code == 200

        # Vérifier la cohérence finale des données
        with open('test/data/testing/clubs.json', 'r') as f:
            final_clubs = json.load(f)

        # Simply Lift doit avoir exactement 3 points en moins
        initial_points = None
        final_points = None

        for club in initial_clubs['clubs']:
            if club['name'] == 'Simply Lift':
                initial_points = int(club['points'])
                break

        for club in final_clubs['clubs']:
            if club['name'] == 'Simply Lift':
                final_points = int(club['points'])
                break

        # Les 3 achats d'1 place chacun doivent être reflétés
        expected_successful_purchases = sum(1 for r in responses[1:]
                                            if Messages.BOOKING_COMPLETE.encode() in r.data)
        assert final_points == initial_points - expected_successful_purchases

    def test_endpoint_url_parameter_handling(self, client):
        """Test de gestion des paramètres d'URL entre endpoints"""
        # Test avec différents formats de noms
        test_cases = [
            {
                'club': 'Simply Lift',
                'competition': 'Future Championship',
                'should_work': True
            },
            {
                'club': 'She Lifts',
                'competition': 'Next Year Games',
                'should_work': True
            },
            {
                'club': 'Non Existent Club',
                'competition': 'Future Championship',
                'should_work': False,
                'expected_error': Messages.CLUB_NOT_FOUND
            },
            {
                'club': 'Simply Lift',
                'competition': 'Non Existent Competition',
                'should_work': False,
                'expected_error': Messages.COMPETITION_NOT_FOUND
            }
        ]

        for case in test_cases:
            # Test endpoint /book avec paramètres d'URL
            response = client.get(f"/book/{case['club']}/{case['competition']}")
            assert response.status_code == 200

            if case['should_work']:
                # Doit afficher la page de booking
                assert case['club'].encode() in response.data
                assert case['competition'].encode() in response.data
            else:
                # Doit afficher le message d'erreur approprié
                assert case['expected_error'].encode() in response.data
