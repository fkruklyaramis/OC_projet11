"""
Configuration centralisée des messages de l'application
"""


class Messages:
    # Messages d'erreur
    CLUB_NOT_FOUND = "Club not found. Please try again."
    COMPETITION_NOT_FOUND = "Competition not found. Please try again."
    SOMETHING_WENT_WRONG = "Something went wrong-please try again"
    NOT_ENOUGH_POINTS = "Not enough points! You need {places} points but have {current_points}"
    MAX_PLACES_EXCEEDED = "You cannot book more than 12 places per competition!"

    # Messages de succès
    BOOKING_COMPLETE = "Great-booking complete!"

    # Messages informationnels
    TRANSPARENCY_INFO = "For transparency, here are the current points for each club:"
    CLUB_POINTS_OVERVIEW = "Club Points Overview"
    ENTER_YOUR_EMAIL = "Enter your email"
    PLACES_AVAILABLE = "Places available"

    # Mots-clés pour les pages
    WELCOME_KEYWORDS = ["welcome", "summary"]
    BOOKING_KEYWORDS = ["booking", "book", "places"]

    # Limites de l'application
    MAX_PLACES_PER_BOOKING = 12

    @staticmethod
    def format_not_enough_points(places_required, current_points):
        """Format le message de points insuffisants"""
        return Messages.NOT_ENOUGH_POINTS.format(
            places=places_required,
            current_points=current_points
        )

    @staticmethod
    def check_welcome_page(response_data):
        """Vérifie si c'est une page de bienvenue"""
        response_lower = response_data.lower()
        return any(keyword.encode() in response_lower for keyword in Messages.WELCOME_KEYWORDS)

    @staticmethod
    def check_booking_page(response_data):
        """Vérifie si c'est une page de réservation"""
        response_lower = response_data.lower()
        return any(keyword.encode() in response_lower for keyword in Messages.BOOKING_KEYWORDS)

    @staticmethod
    def check_index_page(response_data):
        """Vérifie si c'est la page d'accueil"""
        return (Messages.CLUB_POINTS_OVERVIEW.encode() in response_data or
                Messages.ENTER_YOUR_EMAIL.encode() in response_data)
