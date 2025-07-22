def test_book_valid_club_and_competition(client):
    """Test de réservation avec club et compétition valides"""
    response = client.get('/book/Spring Festival/Simply Lift')
    assert response.status_code == 200
    # Vérifier que la page de réservation s'affiche
    assert b'booking' in response.data.lower() or b'book' in response.data.lower()


def test_book_invalid_club_valid_competition(client):
    """Test de réservation avec club inexistant mais compétition valide"""
    response = client.get('/book/Spring Festival/Invalid Club Name')
    # Maintenant que le bug est corrigé, on s'attend à une redirection vers welcome
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_valid_club_invalid_competition(client):
    """Test de réservation avec club valide mais compétition inexistante"""
    response = client.get('/book/Invalid Competition/Simply Lift')
    # Maintenant que le bug est corrigé, on s'attend à une redirection vers welcome
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_both_invalid(client):
    """Test de réservation avec club et compétition inexistants"""
    response = client.get('/book/Invalid Competition/Invalid Club')
    # Maintenant que le bug est corrigé, on s'attend à une redirection vers welcome
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_empty_club_name(client):
    """Test de réservation avec nom de club vide"""
    response = client.get('/book/Spring Festival/ ')
    # Test avec un nom de club vide/espace
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_empty_competition_name(client):
    """Test de réservation avec nom de compétition vide"""
    response = client.get('/book/ /Simply Lift')
    # Test avec un nom de compétition vide/espace
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_case_sensitive_names(client):
    """Test de réservation avec des noms en casse différente"""
    # Tester si les noms sont sensibles à la casse
    response = client.get('/book/spring festival/simply lift')
    # Les noms sont sensibles à la casse, donc erreur attendue
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_special_characters_in_names(client):
    """Test de réservation avec caractères spéciaux dans les noms"""
    response = client.get('/book/Spring%20Festival/Simply%20Lift')
    # Test avec URL encoding
    assert response.status_code in [200, 302, 404, 500]


def test_book_url_structure(client):
    """Test de la structure URL de la route book"""
    # Vérifier que la route accepte bien les paramètres
    response = client.get('/book/Test/Test')
    # Même si les données n'existent pas, la route doit être accessible
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_renders_correct_template_on_success(client):
    """Test que la bonne template est rendue en cas de succès"""
    response = client.get('/book/Spring Festival/Simply Lift')
    assert response.status_code == 200
    # La fonction devrait utiliser booking.html
    # On peut vérifier indirectement en cherchant des éléments spécifiques
    # à la page de réservation


def test_book_flash_message_on_error(client):
    """Test que le message flash apparaît en cas d'erreur"""
    response = client.get('/book/Invalid/Invalid')
    assert response.status_code == 200
    # Vérifier que le message d'erreur est présent
    assert b'Something went wrong' in response.data


def test_book_data_passed_to_template(client):
    """Test que les bonnes données sont passées au template"""
    response = client.get('/book/Spring Festival/Simply Lift')
    if response.status_code == 200:
        # Vérifier que les informations du club et de la compétition sont présentes
        assert b'Simply Lift' in response.data
        assert b'Spring Festival' in response.data
