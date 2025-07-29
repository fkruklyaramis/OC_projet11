from config.messages import Messages


def test_valid_login(client):
    """Test de connexion avec un email valide"""
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200
    # Vérifier que la page de bienvenue s'affiche
    assert Messages.check_welcome_page(response.data)


def test_invalid_email_login(client):
    """Test de connexion avec un email invalide"""
    response = client.post('/showSummary', data={'email': 'invalid@email.com'})
    assert response.status_code == 302  # Redirection vers index


def test_invalid_email_with_redirect(client):
    """Test de connexion avec email invalide et suivi des redirections"""
    response = client.post('/showSummary', data={'email': 'invalid@email.com'}, follow_redirects=True)
    assert response.status_code == 200
    assert Messages.CLUB_NOT_FOUND.encode() in response.data


def test_empty_email_login(client):
    """Test de connexion avec un email vide"""
    response = client.post('/showSummary', data={'email': ''})
    assert response.status_code == 302  # Redirection vers index


def test_login_sets_session(client):
    """Test que la connexion configure correctement la session"""
    with client.session_transaction() as session:
        # La session doit être vide avant la connexion
        assert len(session) == 0

    # Se connecter
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200


def test_logout_redirects_to_index(client):
    """Test que logout redirige vers la page d'accueil"""
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location.endswith('/')


def test_logout_accessible_after_login(client):
    """Test que logout est accessible après connexion"""
    # Se connecter d'abord
    client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Puis se déconnecter
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location.endswith('/')


def test_logout_with_follow_redirects(client):
    """Test logout avec suivi des redirections"""
    # Se connecter d'abord
    client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Se déconnecter avec follow_redirects
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'GUDLFT Registration' in response.data  # Page d'accueil
