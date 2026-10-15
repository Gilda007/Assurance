# from core.logger import logger

# class Session:
#     """
#     Gestionnaire de session statique. 
#     Permet d'accéder à l'utilisateur connecté depuis n'importe quel module.
#     """
#     _current_user = None

#     @classmethod
#     def start(cls, user):
#         """Initialise la session avec l'objet utilisateur."""
#         cls._current_user = user
#         logger.info(f"🚀 Session active pour l'utilisateur : {user.username} (Rôle: {user.role})")

#     @classmethod
#     def get_user(cls):
#         """Récupère l'utilisateur actuel."""
#         return cls._current_user

#     @classmethod
#     def is_logged_in(cls):
#         """Vérifie si une session est active."""
#         return cls._current_user is not None

#     @classmethod
#     def logout(cls):
#         """Détruit la session actuelle."""
#         if cls._current_user:
#             logger.info(f"👋 Déconnexion de l'utilisateur : {cls._current_user.username}")
#         cls._current_user = None


# core/session.py
"""
Gestionnaire de session sécurisé avec chiffrement et validation
"""

import hashlib
import secrets
import base64
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from core.logger import logger


# ============================================================================
# CLASSE DE SESSION SÉCURISÉE
# ============================================================================

class Session:
    """
    Gestionnaire de session statique avec chiffrement et sécurité renforcée.
    """
    
    _current_user = None
    _session_token = None
    _session_expiry = None
    _session_id = None
    _fernet = None
    _user_permissions = {}
    _session_data = {}
    
    # Configuration de sécurité
    SESSION_DURATION_HOURS = 8          # Session expire après 8h
    REMEMBER_DURATION_DAYS = 30         # "Se souvenir de moi" = 30 jours
    TOKEN_LENGTH = 32                   # Longueur du token en bytes
    
    @classmethod
    def _init_crypto(cls):
        """Initialise le système de chiffrement avec une clé dérivée"""
        if cls._fernet is None:
            # Clé de chiffrement (à stocker dans une variable d'environnement en production)
            master_key = os.environ.get('SESSION_SECRET_KEY', 'lometa-secret-key-2024-change-me')
            
            # Dériver une clé de chiffrement forte
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'lometa_salt_2024',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
            cls._fernet = Fernet(key)
    
    @classmethod
    def start(cls, user, remember: bool = False):
        """
        Initialise la session avec l'objet utilisateur.
        
        Args:
            user: Objet utilisateur (doit avoir id, username, role)
            remember: Si True, session plus longue (30 jours)
        """
        cls._init_crypto()
        
        # Générer un token de session sécurisé
        raw_token = secrets.token_bytes(cls.TOKEN_LENGTH)
        cls._session_token = base64.urlsafe_b64encode(raw_token).decode()
        
        # Token chiffré pour stockage en base
        encrypted_token = cls._fernet.encrypt(cls._session_token.encode())
        
        # Définir la durée de session
        if remember:
            expiry_delta = timedelta(days=cls.REMEMBER_DURATION_DAYS)
        else:
            expiry_delta = timedelta(hours=cls.SESSION_DURATION_HOURS)
        
        cls._session_expiry = datetime.now() + expiry_delta
        cls._session_id = hashlib.sha256(cls._session_token.encode()).hexdigest()[:16]
        cls._current_user = user
        
        # Stocker les permissions de l'utilisateur
        cls._load_user_permissions(user)
        
        logger.info(f"🔐 Session sécurisée démarrée pour : {user.username}")
        logger.debug(f"   ID Session: {cls._session_id}")
        logger.debug(f"   Expiration: {cls._session_expiry.strftime('%d/%m/%Y %H:%M:%S')}")
        logger.debug(f"   Remember: {remember}")
        
        return encrypted_token.decode()
    
    @classmethod
    def restore_from_token(cls, encrypted_token: str, db_session) -> bool:
        """
        Restaure une session à partir d'un token chiffré.
        
        Args:
            encrypted_token: Token chiffré stocké en base
            db_session: Session SQLAlchemy pour vérifier le token
        
        Returns:
            True si restauration réussie, False sinon
        """
        cls._init_crypto()
        
        try:
            # Déchiffrer le token
            session_token = cls._fernet.decrypt(encrypted_token.encode()).decode()
            
            # Vérifier le token en base
            from addons.Paramètres.models.models import Session as SessionModel
            session_record = db_session.query(SessionModel).filter(
                SessionModel.token_encrypted == encrypted_token,
                SessionModel.expires_at > datetime.now()
            ).first()
            
            if not session_record:
                logger.warning("❌ Tentative de restauration de session avec token invalide")
                return False
            
            # Récupérer l'utilisateur
            from addons.Paramètres.models.models import User
            user = db_session.query(User).filter(
                User.id == session_record.user_id,
                User.is_active == True
            ).first()
            
            if not user:
                logger.warning("❌ Utilisateur introuvable ou désactivé")
                return False
            
            # Restaurer la session
            cls._session_token = session_token
            cls._session_expiry = session_record.expires_at
            cls._session_id = hashlib.sha256(session_token.encode()).hexdigest()[:16]
            cls._current_user = user
            
            cls._load_user_permissions(user)
            
            logger.info(f"✅ Session restaurée pour : {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur restauration session: {e}")
            return False
    
    @classmethod
    def _load_user_permissions(cls, user):
        """Charge les permissions de l'utilisateur"""
        cls._user_permissions = {
            'can_view': user.role in ['admin', 'manager', 'user'],
            'can_create': user.role in ['admin', 'manager'],
            'can_edit': user.role in ['admin', 'manager'],
            'can_delete': user.role in ['admin'],
            'can_export': user.role in ['admin', 'manager'],
            'can_manage_users': user.role in ['admin'],
            'can_manage_compagnies': user.role in ['admin', 'manager'],
        }
    
    @classmethod
    def get_user(cls) -> Optional[Any]:
        """Récupère l'utilisateur actuel."""
        if cls._is_expired():
            cls.logout()
            return None
        return cls._current_user
    
    @classmethod
    def get_user_id(cls) -> Optional[int]:
        """Récupère l'ID de l'utilisateur actuel."""
        user = cls.get_user()
        return user.id if user else None
    
    @classmethod
    def get_username(cls) -> Optional[str]:
        """Récupère le nom d'utilisateur actuel."""
        user = cls.get_user()
        return user.username if user else None
    
    @classmethod
    def get_user_role(cls) -> Optional[str]:
        """Récupère le rôle de l'utilisateur actuel."""
        user = cls.get_user()
        return user.role if user else None
    
    @classmethod
    def get_session_token(cls) -> Optional[str]:
        """Récupère le token de session (pour transmission au serveur)"""
        if cls._is_expired():
            return None
        return cls._session_token
    
    @classmethod
    def get_session_id(cls) -> Optional[str]:
        """Récupère l'ID de session (pour logs)"""
        return cls._session_id
    
    @classmethod
    def is_logged_in(cls) -> bool:
        """Vérifie si une session est active et valide."""
        return cls._current_user is not None and not cls._is_expired()
    
    @classmethod
    def _is_expired(cls) -> bool:
        """Vérifie si la session a expiré."""
        if cls._session_expiry is None:
            return True
        return datetime.now() > cls._session_expiry
    
    @classmethod
    def get_session_time_left(cls) -> Optional[timedelta]:
        """Retourne le temps restant avant expiration."""
        if cls._session_expiry is None:
            return None
        left = cls._session_expiry - datetime.now()
        return left if left.total_seconds() > 0 else timedelta(0)
    
    @classmethod
    def can(cls, permission: str) -> bool:
        """
        Vérifie si l'utilisateur a une permission spécifique.
        
        Args:
            permission: 'view', 'create', 'edit', 'delete', 'export', 'manage_users', 'manage_compagnies'
        
        Returns:
            True si autorisé, False sinon
        """
        if not cls.is_logged_in():
            return False
        
        perm_key = f'can_{permission}'
        return cls._user_permissions.get(perm_key, False)
    
    @classmethod
    def require_permission(cls, permission: str):
        """
        Décorateur pour vérifier les permissions sur les méthodes.
        
        Usage:
            @Session.require_permission('edit')
            def edit_contract(self, contract_id):
                ...
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not cls.can(permission):
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        None, 
                        "Accès refusé", 
                        f"Vous n'avez pas la permission de {permission} cet élément."
                    )
                    return None
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @classmethod
    def set_session_data(cls, key: str, value: Any):
        """Stocke des données dans la session (chiffrées)"""
        cls._init_crypto()
        serialized = json.dumps(value)
        encrypted = cls._fernet.encrypt(serialized.encode())
        cls._session_data[key] = encrypted
    
    @classmethod
    def get_session_data(cls, key: str, default: Any = None) -> Any:
        """Récupère des données de session"""
        cls._init_crypto()
        encrypted = cls._session_data.get(key)
        if encrypted:
            try:
                decrypted = cls._fernet.decrypt(encrypted).decode()
                return json.loads(decrypted)
            except:
                return default
        return default
    
    @classmethod
    def clear_session_data(cls):
        """Efface toutes les données de session"""
        cls._session_data.clear()
    
    @classmethod
    def refresh(cls, db_session):
        """
        Rafraîchit la session (prolonge l'expiration).
        À appeler lors d'actions utilisateur.
        """
        if cls.is_logged_in():
            cls._session_expiry = datetime.now() + timedelta(hours=cls.SESSION_DURATION_HOURS)
            logger.debug(f"🔄 Session rafraîchie: {cls._session_id}")
            
            # Mettre à jour en base si nécessaire
            if cls._session_token:
                from addons.Paramètres.models.models import Session as SessionModel
                session_record = db_session.query(SessionModel).filter(
                    SessionModel.token_encrypted == cls.get_session_token()
                ).first()
                if session_record:
                    session_record.expires_at = cls._session_expiry
                    db_session.commit()
    
    @classmethod
    def logout(cls):
        """Détruit la session actuelle et nettoie les données."""
        if cls._current_user:
            logger.info(f"👋 Déconnexion de l'utilisateur : {cls._current_user.username}")
            logger.debug(f"   Session ID: {cls._session_id}")
        
        cls._current_user = None
        cls._session_token = None
        cls._session_expiry = None
        cls._session_id = None
        cls._user_permissions = {}
        cls._session_data = {}
    
    @classmethod
    def get_info(cls) -> Dict:
        """Retourne les informations de session (pour debug)"""
        return {
            'logged_in': cls.is_logged_in(),
            'username': cls.get_username(),
            'role': cls.get_user_role(),
            'session_id': cls._session_id,
            'expires_at': cls._session_expiry.isoformat() if cls._session_expiry else None,
            'time_left': str(cls.get_session_time_left()) if cls.get_session_time_left() else None,
            'permissions': cls._user_permissions
        }


# ============================================================================
# DÉCORATEUR POUR LES VUES (PYTHON)
# ============================================================================

def login_required(func):
    """
    Décorateur pour les méthodes nécessitant une connexion.
    
    Usage:
        @login_required
        def delete_contract(self, contract_id):
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not Session.is_logged_in():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(None, "Accès refusé", "Veuillez vous connecter.")
            return None
        return func(*args, **kwargs)
    return wrapper