# class BaseModule:
#     """Tous les modules doivent hériter de cette classe."""
#     def __init__(self, main_window):
#         self.main_window = main_window

#     def setup(self):
#         """Méthode appelée au démarrage pour enregistrer les fonctionnalités."""
#         pass


# core/base_module.py
from PySide6.QtWidgets import QWidget

class BaseModule(QWidget):
    """Classe de base pour tous les modules - hérite de QWidget"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.module_id = None
        self.module_name = None
    
    def setup(self):
        """Méthode appelée après l'initialisation du module"""
        pass
    
    def get_widget(self):
        """Retourne le widget principal du module"""
        return self