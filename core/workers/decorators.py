# core/workers/decorators.py
"""
Décorateurs pour simplifier l'utilisation des workers
"""

from functools import wraps
from core.workers.database_worker import async_query
from PySide6.QtWidgets import QWidget, QMessageBox


def async_load(loading_message="Chargement..."):
    """
    Décorateur pour charger des données de manière asynchrone
    
    Usage:
        @async_load("Chargement des véhicules...")
        def load_vehicles(self):
            return self.controller.get_all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Afficher le loader
            if hasattr(self, 'loading_overlay'):
                self.loading_overlay.show_loading(loading_message)
            
            def execute():
                return func(self, *args, **kwargs)
            
            # Exécuter dans un thread
            async_query.execute(
                execute,
                on_finished=lambda result: _on_finished(self, result),
                on_error=lambda error: _on_error(self, error)
            )
        
        def _on_finished(self, result):
            if hasattr(self, 'loading_overlay'):
                self.loading_overlay.hide_loading()
            
            # Appeler la méthode de callback si elle existe
            callback_name = f"_on_{func.__name__}_finished"
            if hasattr(self, callback_name):
                getattr(self, callback_name)(result)
            elif hasattr(self, 'on_data_loaded'):
                self.on_data_loaded(result)
        
        def _on_error(self, error):
            if hasattr(self, 'loading_overlay'):
                self.loading_overlay.hide_loading()
            
            callback_name = f"_on_{func.__name__}_error"
            if hasattr(self, callback_name):
                getattr(self, callback_name)(error)
            elif hasattr(self, 'on_load_error'):
                self.on_load_error(error)
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Erreur", f"Erreur de chargement: {error}")
        
        return wrapper
    return decorator


# Utilisation du décorateur
class MyView(QWidget):
    @async_load("Chargement des véhicules...")
    def load_vehicles(self):
        return self.controller.vehicles.get_all()
    
    def _on_load_vehicles_finished(self, vehicles):
        # Traiter les véhicules chargés
        self.display_vehicles(vehicles)