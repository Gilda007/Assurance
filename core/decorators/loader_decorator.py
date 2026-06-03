# core/decorators/loader_decorator.py
"""
Décorateur pour afficher automatiquement le loader pendant l'exécution
"""

from functools import wraps
from PySide6.QtCore import QTimer, QMetaObject, Qt
from core.widgets.global_loader import get_global_loader
import threading


def with_loading(message="Chargement..."):
    """
    Décorateur qui affiche un loader pendant l'exécution de la fonction
    
    Usage:
        @with_loading("Chargement des véhicules...")
        def load_vehicles(self):
            return self.controller.get_all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Afficher le loader
            loader = get_global_loader()
            loader.show_loading(message)
            
            def execute():
                try:
                    result = func(*args, **kwargs)
                    # Retourner dans le thread principal
                    QTimer.singleShot(0, lambda: _on_success(result))
                except Exception as e:
                    QTimer.singleShot(0, lambda: _on_error(str(e)))
            
            def _on_success(result):
                loader.hide_loading()
                # Appeler le callback de succès si défini
                if hasattr(args[0], '_on_load_finished') if args else False:
                    args[0]._on_load_finished(result)
                return result
            
            def _on_error(error):
                loader.hide_loading()
                if hasattr(args[0], '_on_load_error') if args else False:
                    args[0]._on_load_error(error)
            
            thread = threading.Thread(target=execute, daemon=True)
            thread.start()
            
            return None  # Retour asynchrone
        return wrapper
    return decorator


def async_task(message="Chargement..."):
    """
    Décorateur pour exécuter une tâche asynchrone avec loader
    Version améliorée avec callback
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            loader = get_global_loader()
            loader.show_loading(message)
            
            def run():
                try:
                    result = func(self, *args, **kwargs)
                    QMetaObject.invokeMethod(
                        self,
                        "_on_task_finished",
                        Qt.QueuedConnection,
                        Qt.Argument(lambda: result)
                    )
                except Exception as e:
                    QMetaObject.invokeMethod(
                        self,
                        "_on_task_error",
                        Qt.QueuedConnection,
                        Qt.Argument(lambda: str(e))
                    )
            
            thread = threading.Thread(target=run, daemon=True)
            thread.start()
        return wrapper
    return decorator