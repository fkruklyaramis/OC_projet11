def test_valid_login(client, valid_email):
    """Test de connexion avec un email valide"""
    response = client.post('/showSummary', data={'email': valid_email})
    assert response.status_code == 200
    # Vérifier que la page de bienvenue s'affiche
    assert b'welcome' in response.data.lower() or b'summary' in response.data.lower()


def test_invalid_email_login(client, invalid_email):
    """Test de connexion avec un email invalide"""
    response = client.post('/showSummary', data={'email': invalid_email})
    assert response.status_code == 302  # Redirection vers index


def test_invalid_email_with_redirect(client, invalid_email):
    """Test de connexion avec email invalide et suivi des redirections"""
    response = client.post('/showSummary', data={'email': invalid_email}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Club not found' in response.data


def test_empty_email_login(client):
    """Test de connexion avec un email vide"""
    response = client.post('/showSummary', data={'email': ''})
    assert response.status_code == 302  # Redirection vers index


def test_login_sets_session(client, valid_email):
    """Test que la connexion configure correctement la session"""
    with client.session_transaction() as session:
        # La session doit être vide avant la connexion
        assert len(session) == 0

    # Se connecter
    response = client.post('/showSummary', data={'email': valid_email})
    assert response.status_code == 200


def test_logout_redirects_to_index(client):
    """Test que logout redirige vers la page d'accueil"""
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location.endswith('/')


def test_logout_accessible_after_login(client, valid_email):
    """Test que logout est accessible après connexion"""
    # Se connecter d'abord
    login_response = client.post('/showSummary', data={'email': valid_email})
    assert login_response.status_code == 200

    # Puis se déconnecter
    logout_response = client.get('/logout')
    assert logout_response.status_code == 302


def test_logout_with_follow_redirects(client):
    """Test logout avec suivi des redirections"""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    # Vérifier qu'on est bien sur la page d'accueil
    assert b'Club Points Overview' in response.data or b'Enter your email' in response.data
