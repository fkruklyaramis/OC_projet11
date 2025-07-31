import json
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for
from config.messages import Messages


def get_data_path(filename):
    """Retourne le chemin du fichier de données selon l'environnement"""
    if os.environ.get('TESTING') or hasattr(app, 'config') and app.config.get('TESTING'):
        return f'test/data/testing/{filename}'
    return filename


def loadClubs():
    with open(get_data_path('clubs.json')) as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def saveClubs():
    """Sauvegarde la liste des clubs dans le fichier JSON"""
    data = {'clubs': clubs}
    with open(get_data_path('clubs.json'), 'w') as file:
        json.dump(data, file, indent=4)


def loadCompetitions():
    with open(get_data_path('competitions.json')) as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


def saveCompetitions():
    """Sauvegarde la liste des compétitions dans le fichier JSON"""
    data = {'competitions': competitions}
    with open(get_data_path('competitions.json'), 'w') as file:
        json.dump(data, file, indent=4)


app = Flask(__name__)
# Load the secret key from environment variable
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template('index.html', clubs=clubs)


@app.route('/showSummary', methods=['POST'])
def showSummary():
    club_list = [club for club in clubs if club['email'] == request.form['email']]
    # bug fix #1 : unknown email on login
    if not club_list:
        flash(Messages.CLUB_NOT_FOUND)  # ← Utilise la config
        return redirect(url_for('index'))
    club = club_list[0]
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<club>/<competition>')
def book(club, competition):
    # bug fix 3 : unknown club or competition on booking
    foundClub_list = [c for c in clubs if c['name'] == club]
    foundCompetition_list = [c for c in competitions if c['name'] == competition]

    if not foundClub_list:
        flash(Messages.CLUB_NOT_FOUND)  # ← Utilise la config
        return render_template('welcome.html', club={"name": club}, competitions=competitions)
    elif not foundCompetition_list:
        flash(Messages.COMPETITION_NOT_FOUND)  # ← Utilise la config
        return render_template('welcome.html', club={"name": club}, competitions=competitions)
    else:
        foundClub = foundClub_list[0]
        foundCompetition = foundCompetition_list[0]

        # Vérifier si la compétition est dans le passé
        competition_date = datetime.strptime(foundCompetition['date'], '%Y-%m-%d %H:%M:%S')
        current_date = datetime.now()

        if competition_date < current_date:
            flash(Messages.COMPETITION_EXPIRED)
            return render_template('welcome.html', club=foundClub, competitions=competitions)

        return render_template('booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    # bug fix 4 : unknown club or competition on purchase
    competition_list = [c for c in competitions if c['name'] == request.form['competition']]
    club_list = [c for c in clubs if c['name'] == request.form['club']]

    if not competition_list or not club_list:
        flash(Messages.SOMETHING_WENT_WRONG)  # ← Utilise la config
        return render_template('welcome.html', club={"name": request.form['club']}, competitions=competitions)

    competition = competition_list[0]
    club = club_list[0]
    placesRequired = int(request.form['places'])

    # Vérifier si la compétition est dans le passé
    competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    current_date = datetime.now()

    if competition_date < current_date:
        flash(Messages.COMPETITION_EXPIRED)
        return render_template('welcome.html', club=club, competitions=competitions)

    # Limiter à 12 places maximum
    if placesRequired > Messages.MAX_PLACES_PER_BOOKING:  # ← Utilise la config
        flash(Messages.MAX_PLACES_EXCEEDED)  # ← Utilise la config
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérifier si le club a assez de points
    if int(club['points']) < placesRequired:
        flash(Messages.format_not_enough_points(placesRequired, club['points']))  # ← Utilise la config
        return render_template('welcome.html', club=club, competitions=competitions)

    # Décrémenter les places de la compétition
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired

    # Décrémenter les points du club
    club['points'] = int(club['points']) - placesRequired

    # bug fix #2 : update jsons compétitions et clubs
    saveCompetitions()
    saveClubs()

    flash(Messages.BOOKING_COMPLETE)  # ← Utilise la config
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

