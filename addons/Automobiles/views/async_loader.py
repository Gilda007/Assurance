# addons/Automobiles/views/async_loader.py

from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QApplication

class AsyncDataLoader(QThread):
    """Thread pour charger les données de manière asynchrone"""
    
    data_loaded = Signal(object)  # Les données chargées
    progress = Signal(int, str)    # Progression
    error = Signal(str)            # Erreur
    
    def __init__(self, load_function, *args, **kwargs):
        super().__init__()
        self.load_function = load_function
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            result = self.load_function(*self.args, **self.kwargs)
            self.data_loaded.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class AsyncPage(QWidget):
    """Classe de base pour les pages qui chargent leurs données asynchronement"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = None
        self._is_loading = False
        self._loader_thread = None
        
    def showEvent(self, event):
        """Quand la page est affichée, charger les données"""
        super().showEvent(event)
        if not self._data and not self._is_loading:
            self.load_data_async()
            
    def load_data_async(self):
        """Charge les données de manière asynchrone"""
        self._is_loading = True
        self.show_loading_screen()
        
        # Créer et démarrer le thread
        self._loader_thread = AsyncDataLoader(self._load_data)
        self._loader_thread.data_loaded.connect(self.on_data_loaded)
        self._loader_thread.progress.connect(self.on_load_progress)
        self._loader_thread.error.connect(self.on_load_error)
        self._loader_thread.start()
        
    def show_loading_screen(self):
        """Affiche un écran de chargement"""
        # À implémenter dans les classes filles
        pass
        
    def _load_data(self):
        """Méthode à surcharger - retourne les données à charger"""
        raise NotImplementedError()
        
    def on_data_loaded(self, data):
        """Appelé quand les données sont chargées"""
        self._data = data
        self._is_loading = False
        self.build_ui_with_data()
        
    def on_load_progress(self, value, message):
        """Mise à jour de la progression"""
        pass
        
    def on_load_error(self, error):
        """Erreur de chargement"""
        self._is_loading = False
        self.show_error_message(error)
        
    def build_ui_with_data(self):
        """Construit l'UI avec les données chargées"""
        pass