"""
Contrôleur de base - Pont entre l'UI et les services
"""
from PySide6.QtCore import QObject, Signal
from typing import Optional, Dict, Any, List
from addons.Paramètres.models.models import User


class BaseController(QObject):
    """Contrôleur de base avec gestion de l'utilisateur courant"""
    
    # Signaux génériques
    error_occurred = Signal(str)
    success_occurred = Signal(str)
    data_updated = Signal(object)
    
    def __init__(self):
        super().__init__()
        self._current_user: Optional[User] = None
        self._session = None
    
    def set_current_user(self, user: User):
        """Définit l'utilisateur courant"""
        self._current_user = user
    
    def get_current_user(self) -> Optional[User]:
        """Récupère l'utilisateur courant"""
        return self._current_user
    
    def get_current_user_id(self) -> Optional[int]:
        """Récupère l'ID de l'utilisateur courant"""
        return self._current_user.id if self._current_user else None
    
    def get_current_user_name(self) -> str:
        """Récupère le nom de l'utilisateur courant"""
        if self._current_user:
            return self._current_user.full_name or self._current_user.username
        return "Utilisateur inconnu"
    
    def handle_error(self, error: Exception) -> None:
        """Gère une erreur et émet le signal correspondant"""
        self.error_occurred.emit(str(error))
    
    def handle_success(self, message: str) -> None:
        """Gère un succès et émet le signal correspondant"""
        self.success_occurred.emit(message)