import re


def test_index_page_shows_club_points_table(client, test_data):
    """Test que la page d'accueil affiche le tableau des points des clubs"""
    response = client.get('/')
    assert response.status_code == 200

    # Vérifier que le tableau est présent
    assert b'Club Points Overview' in response.data
    assert b'<table' in response.data
    assert b'Club Name' in response.data
    assert b'Available Points' in response.data

    response_text = response.data.decode()

    # Vérifier que chaque club du JSON est présent dans la table
    for club in test_data['clubs']:
        club_name = club['name']
        club_points = club['points']

        # Vérifier que le nom du club est dans la réponse
        assert club_name in response_text, f"Club '{club_name}' not found in table"

        # Vérifier que les points du club sont dans la réponse
        assert club_points in response_text, f"Points '{club_points}' for club '{club_name}' not found in table"

    # Compter les lignes de données avec regex (plus fiable)
    tr_pattern = r'<tr[^>]*>.*?</tr>'
    all_trs = re.findall(tr_pattern, response_text, re.DOTALL | re.IGNORECASE)

    # Filtrer pour ne garder que les lignes de données (pas l'en-tête)
    data_rows = [tr for tr in all_trs if not re.search(r'Club\s+Name|Available\s+Points', tr, re.IGNORECASE)]

    expected_club_count = len(test_data['clubs'])
    actual_club_count = len(data_rows)

    print(f"Clubs attendus: {expected_club_count}")
    print(f"Lignes de données trouvées: {actual_club_count}")

    assert actual_club_count == expected_club_count, (
        f"Expected {expected_club_count} clubs, but found {actual_club_count}"
    )


def test_public_table_readonly_no_login_required(client):
    """Test que le tableau est accessible sans connexion"""
    response = client.get('/')
    assert response.status_code == 200

    # Le tableau doit être visible sans se connecter
    assert b'Club Points Overview' in response.data
    assert b'For transparency' in response.data

    # Pas de champs de modification dans le tableau
    table_section = response.data.split(b'<table')[1].split(b'</table>')[0]
    assert b'<input' not in table_section
    assert b'<form' not in table_section


def test_points_table_displays_current_data(client, test_data):
    """Test que le tableau affiche les données actuelles des points"""
    response = client.get('/')
    assert response.status_code == 200

    # Vérifier que chaque club et ses points sont dans la réponse
    for club in test_data['clubs']:
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
