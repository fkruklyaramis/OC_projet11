def test_index_page_shows_club_points_table(client):
    """Test que la page d'accueil affiche le tableau des points des clubs"""
    response = client.get('/')
    assert response.status_code == 200

    # Vérifier que le tableau est présent
    assert b'Club Points Overview' in response.data
    assert b'<table' in response.data
    assert b'Club Name' in response.data
    assert b'Available Points' in response.data

    # Vérifier que les clubs apparaissent dans le tableau
    assert b'Simply Lift' in response.data
    assert b'Iron Temple' in response.data
    assert b'She Lifts' in response.data

    # Vérifier que les points sont affichés
    assert b'15' in response.data  # Points de Simply Lift
    assert b'4' in response.data   # Points de Iron Temple
    assert b'12' in response.data  # Points de She Lifts


def test_public_table_readonly_no_login_required(client):
    """Test que le tableau est accessible sans connexion"""
    response = client.get('/')
    assert response.status_code == 200

    # Le tableau doit être visible sans se connecter
    assert b'Club Points Overview' in response.data
    assert b'For transparency' in response.data

    # Pas de champs de modification dans le tableau
    assert b'<input' not in response.data.split(b'<table')[1].split(b'</table>')[0]
    assert b'<form' not in response.data.split(b'<table')[1].split(b'</table>')[0]


def test_points_table_displays_current_data(client):
    """Test que le tableau affiche les données actuelles des points"""
    # Récupérer les données depuis le fichier de test
    import json
    with open('test/data/clubs.json', 'r') as f:
        clubs_data = json.load(f)

    response = client.get('/')
    assert response.status_code == 200

    # Vérifier que chaque club et ses points sont dans la réponse
    for club in clubs_data['clubs']:
        club_name = club['name'].encode()
        club_points = club['points'].encode()

        assert club_name in response.data
        assert club_points in response.data


def test_table_styling_and_structure(client):
    """Test que le tableau a une structure et un style appropriés"""
    response = client.get('/')
    assert response.status_code == 200

    # Vérifier la structure HTML du tableau
    assert b'<thead>' in response.data
    assert b'<tbody>' in response.data
    assert b'<th' in response.data
    assert b'<td' in response.data

    # Vérifier que le style est appliqué
    assert b'border="1"' in response.data
    assert b'border-collapse: collapse' in response.data
