# core/workers/worker_base.py
"""
Worker générique utilisant QRunnable pour les opérations asynchrones
Ne bloque jamais l'interface utilisateur
"""

from PySide6.QtCore import QRunnable, QObject, Signal, Slot, QThreadPool
import traceback
from core.logger import logger


class WorkerSignals(QObject):
    """Signaux pour communiquer avec le thread principal"""
    finished = Signal(object)  # Données chargées
    error = Signal(str)        # Message d'erreur
    progress = Signal(int, str)  # Progression (pourcentage, message)
    started = Signal()         # Début de l'opération


class BaseWorker(QRunnable):
    """Worker générique pour toutes les opérations asynchrones"""
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self._is_cancelled = False
        
    def cancel(self):
        """Annule l'opération en cours"""
        self._is_cancelled = True
        
    @Slot()
    def run(self):
        """Exécuté dans un thread séparé"""
        self.signals.started.emit()
        
        try:
            logger.debug(f"🔄 Début du worker: {self.func.__name__}")
            result = self.func(*self.args, **self.kwargs)
            
            if not self._is_cancelled:
                self.signals.finished.emit(result)
                logger.debug(f"✅ Worker terminé: {self.func.__name__}")
            else:
                logger.debug(f"⏹️ Worker annulé: {self.func.__name__}")
                
        except Exception as e:
            error_msg = f"Erreur dans {self.func.__name__}: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            if not self._is_cancelled:
                self.signals.error.emit(str(e))


class DatabaseWorker(BaseWorker):
    """Worker spécialisé pour les requêtes base de données"""
    
    def __init__(self, func, session_maker, *args, **kwargs):
        super().__init__(func, *args, **kwargs)
        self.session_maker = session_maker
        self._session = None
        
    def run(self):
        """Exécute la requête avec sa propre session DB"""
        self.signals.started.emit()
        
        try:
            # Créer une session DANS le thread (thread-safe)
            self._session = self.session_maker()
            
            # Ajouter la session aux kwargs si la fonction l'accepte
            if 'session' in self.kwargs:
                self.kwargs['session'] = self._session
            elif self.func.__code__.co_argcount > 0:
                # Passer la session comme premier argument si possible
                self.args = (self._session,) + self.args
            
            logger.debug(f"🔄 Requête DB: {self.func.__name__}")
            result = self.func(*self.args, **self.kwargs)
            
            if not self._is_cancelled:
                self.signals.finished.emit(result)
                logger.debug(f"✅ Requête DB terminée: {self.func.__name__}")
            else:
                logger.debug(f"⏹️ Requête DB annulée: {self.func.__name__}")
                
        except Exception as e:
            error_msg = f"Erreur DB dans {self.func.__name__}: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            if not self._is_cancelled:
                self.signals.error.emit(str(e))
        finally:
            if self._session:
                self._session.close()


class AsyncExecutor:
    """Gestionnaire central des opérations asynchrones"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._threadpool = QThreadPool.globalInstance()
            cls._instance._active_workers = []
            logger.info(f"✅ AsyncExecutor initialisé avec {cls._instance._threadpool.maxThreadCount()} threads")
        return cls._instance
    
    def execute(self, func, on_finished=None, on_error=None, on_progress=None, 
                on_started=None, is_db_operation=False, session_maker=None, 
                *args, **kwargs):
        """
        Exécute une fonction de manière asynchrone
        
        Args:
            func: Fonction à exécuter
            on_finished: Callback en cas de succès
            on_error: Callback en cas d'erreur
            on_progress: Callback de progression
            on_started: Callback au démarrage
            is_db_operation: Si True, utilise DatabaseWorker
            session_maker: Session maker pour les opérations DB
            *args, **kwargs: Arguments pour la fonction
        """
        # Créer le worker approprié
        if is_db_operation and session_maker:
            worker = DatabaseWorker(func, session_maker, *args, **kwargs)
        else:
            worker = BaseWorker(func, *args, **kwargs)
        
        # Connecter les signaux
        if on_finished:
            worker.signals.finished.connect(on_finished)
        if on_error:
            worker.signals.error.connect(on_error)
        if on_progress:
            worker.signals.progress.connect(on_progress)
        if on_started:
            worker.signals.started.connect(on_started)
        
        # Nettoyage automatique
        worker.signals.finished.connect(lambda _: self._cleanup_worker(worker))
        worker.signals.error.connect(lambda _: self._cleanup_worker(worker))
        
        self._active_workers.append(worker)
        self._threadpool.start(worker)
        
        return worker
    
    def _cleanup_worker(self, worker):
        """Nettoie un worker terminé"""
        if worker in self._active_workers:
            self._active_workers.remove(worker)
    
    def cancel_all(self):
        """Annule toutes les opérations en cours"""
        for worker in self._active_workers:
            worker.cancel()
        self._active_workers.clear()
        logger.info("⏹️ Toutes les opérations asynchrones ont été annulées")
    
    @property
    def active_count(self):
        return len(self._active_workers)


# Instance globale
async_executor = AsyncExecutor()