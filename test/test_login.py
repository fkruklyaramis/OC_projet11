
def test_index_page_loads(client):
    """Test que la page d'accueil se charge correctement"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the GUDLFT Registration Portal!' in response.data


def test_valid_email_login(client):
    """Test de connexion avec un email valide"""
    # Utiliser un email qui existe dans clubs.json
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200
    assert b'Welcome' in response.data


def test_invalid_email_login(client):
    """Test de connexion avec un email invalide - BUG CORRIGÉ"""
    response = client.post('/showSummary', data={'email': 'invalid@email.com'})
    # Doit rediriger vers la page d'accueil
    assert response.status_code == 302
    assert response.location.endswith('/')


def test_invalid_email_shows_flash_message(client):
    """Test que le message flash s'affiche pour un email invalide"""
    response = client.post('/showSummary', data={'email': 'invalid@email.com'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Club not found. Please try again.' in response.data


def test_empty_email_login(client):
    """Test de connexion avec un email vide"""
    response = client.post('/showSummary', data={'email': ''})
    assert response.status_code == 302
    assert response.location.endswith('/')


def test_logout_redirects_to_index(client):
    """Test que la route logout redirige vers la page d'accueil"""
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location.endswith('/')


def test_logout_accessible_after_login(client):
    """Test que logout fonctionne après une connexion"""
    # Se connecter d'abord
    login_response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert login_response.status_code == 200

    # Puis se déconnecter
    logout_response = client.get('/logout')
    assert logout_response.status_code == 302
    assert logout_response.location.endswith('/')


def test_logout_with_follow_redirects(client):
    """Test que logout redirige bien vers la page d'accueil avec follow_redirects"""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome to the GUDLFT Registration Portal!' in response.data
    assert b'Please enter your secretary email to continue:' in response.data
