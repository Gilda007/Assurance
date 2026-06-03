# core/workers/database_worker.py - Version corrigée

from PySide6.QtCore import QObject, Signal, Qt, QThread, QTimer, Q_ARG, QMetaObject, QThreadPool
from core.workers.workers_base import BaseWorker
from core.database import SessionLocal
from core.logger import logger
import traceback
import time


class DatabaseWorkerSignals(QObject):
    """Signaux pour DatabaseWorker"""
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(int, str)
    started = Signal()


class DatabaseWorker(BaseWorker):
    """Worker pour les requêtes base de données"""
    
    def __init__(self, func: callable, *args, **kwargs):
        super().__init__(func, *args, **kwargs)
        self.session = None
        self._start_time = None
        self._loader = None
        self._loader_message = None
        self._show_loader = False
        # Créer les signaux dans le thread principal
        self.signals = DatabaseWorkerSignals()
        
    def set_loader_info(self, loader, message, show):
        """Définit les informations du loader"""
        self._loader = loader
        self._loader_message = message
        self._show_loader = show
        
    def run(self):
        """Exécute la requête DB"""
        self.signals.started.emit()
        self._start_time = time.time()
        
        # Afficher le loader si demandé (depuis le thread principal)
        if self._show_loader and self._loader:
            QMetaObject.invokeMethod(self._loader, "show_loading", 
                                     Qt.ConnectionType.QueuedConnection,
                                     Q_ARG(str, self._loader_message))
        
        # Créer une nouvelle session pour ce thread
        self.session = SessionLocal()
        
        try:
            logger.debug(f"🔄 Début requête async: {self.func.__name__}")
            
            # Exécuter la fonction
            result = self.func(*self.args, **self.kwargs)
            
            # Vérifier si annulé
            if self._is_cancelled:
                logger.debug(f"⏹️ Requête annulée: {self.func.__name__}")
                return
            
            # Émettre le résultat
            elapsed = time.time() - self._start_time
            logger.debug(f"✅ Requête terminée en {elapsed:.2f}s: {self.func.__name__}")
            self.signals.finished.emit(result)
            
        except Exception as e:
            elapsed = time.time() - self._start_time
            error_msg = f"Erreur dans {self.func.__name__} (après {elapsed:.2f}s): {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            if not self._is_cancelled:
                self.signals.error.emit(error_msg)
        finally:
            if self.session:
                self.session.close()
                self.session = None

# core/workers/database_worker.py

# core/workers/database_worker.py

class AsyncQuery:
    """Gestionnaire de requêtes asynchrones"""
    
    def __init__(self):
        self.threadpool = QThreadPool.globalInstance()
        self._loading_overlay = None
        self._active_workers = []
    
    # ✅ AJOUTER CETTE MÉTHODE
    def set_loading_overlay(self, overlay):
        """Définit l'overlay de chargement global"""
        self._loading_overlay = overlay
    
    def execute(self, func, on_finished=None, on_error=None, 
                show_loader=True, loader_message="Chargement...", *args, **kwargs):
        
        # Afficher le loader si demandé
        if show_loader and self._loading_overlay:
            self._loading_overlay.show_loading(loader_message)
        
        # Créer et configurer le worker
        worker = DatabaseWorker(func, *args, **kwargs)
        
        def finished_wrapper(result):
            if show_loader and self._loading_overlay:
                QTimer.singleShot(100, self._loading_overlay.hide_loading)
            if on_finished:
                on_finished(result)
            self._cleanup_worker(worker)
        
        def error_wrapper(error):
            if show_loader and self._loading_overlay:
                self._loading_overlay.hide_loading()
            if on_error:
                on_error(error)
            self._cleanup_worker(worker)
        
        worker.signals.finished.connect(finished_wrapper)
        worker.signals.error.connect(error_wrapper)
        
        self._active_workers.append(worker)
        self.threadpool.start(worker)
        
        return worker
    
    def _cleanup_worker(self, worker):
        if worker in self._active_workers:
            self._active_workers.remove(worker)
    
    def cancel_all(self):
        for worker in self._active_workers:
            worker.cancel()
        self._active_workers.clear()
        if self._loading_overlay:
            self._loading_overlay.hide_loading()
    
    def is_running(self):
        return len(self._active_workers) > 0


# Instance globale
async_query = AsyncQuery()