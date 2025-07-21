import json
import os
from flask import Flask, render_template, request, redirect, flash, url_for


def get_data_path(filename):
    """Retourne le chemin du fichier de données selon l'environnement"""
    if os.environ.get('TESTING') or hasattr(app, 'config') and app.config.get('TESTING'):
        return f'test/data/{filename}'
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
        flash("Club not found. Please try again.")
        return redirect(url_for('index'))
    club = club_list[0]
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    # Limiter à 12 places maximum
    if placesRequired > 12:
        flash("You cannot book more than 12 places per competition!")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérifier si le club a assez de points
    if int(club['points']) < placesRequired:
        flash(f"Not enough points! You need {placesRequired} points but have {club['points']}")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Décrémenter les places de la compétition
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired

    # Décrémenter les points du club
    club['points'] = str(int(club['points']) - placesRequired)

    # bug fix #2 : update jsons compétitions et clubs
    saveCompetitions()
    saveClubs()

    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
