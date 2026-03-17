class BaseModule:
    """Tous les modules doivent hériter de cette classe."""
    def __init__(self, main_window):
        self.main_window = main_window

    def setup(self):
        """Méthode appelée au démarrage pour enregistrer les fonctionnalités."""
        pass