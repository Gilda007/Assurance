"""
Service de base - Adapté pour utiliser votre infrastructure de base de données
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List, Dict, Any, Type, TypeVar

from core.database import SessionLocal, ScopedSession, get_db, execute_with_retry
from addons.sinistres.models.audit import LometaAuditLog
from addons.Paramètres.models.models import User  # Votre modèle User existant

T = TypeVar('T')


class BaseService:
    """Service de base avec fonctions communes"""
    
    def __init__(self, session: Session = None):
        self._session = session
        self._external_session = session is not None
    
    @property
    def session(self) -> Session:
        """Retourne une session, crée une nouvelle si nécessaire"""
        if self._session is None:
            self._session = SessionLocal()
            self._external_session = False
        return self._session
    
    def close(self):
        """Ferme la session si elle a été créée par le service"""
        if not self._external_session and self._session is not None:
            self._session.close()
            self._session = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Récupère un utilisateur par son ID"""
        try:
            return self.session.query(User).filter(
                User.id == user_id,
                User.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """Récupère les informations d'un utilisateur pour l'affichage"""
        try:
            user = self.get_user(user_id)
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'role': user.role,
                    'email': user.email
                }
            return {'id': user_id, 'username': 'Inconnu', 'full_name': 'Utilisateur inconnu'}
        except Exception:
            return {'id': user_id, 'username': 'Inconnu', 'full_name': 'Utilisateur inconnu'}
    
    def get_by_id(self, model: Type[T], id: int) -> Optional[T]:
        """Récupère une entité par son ID"""
        try:
            return self.session.query(model).filter(
                model.id == id,
                model.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_all(self, model: Type[T], limit: int = 100, offset: int = 0) -> List[T]:
        """Récupère toutes les entités actives"""
        try:
            return self.session.query(model).filter(
                model.is_active == True
            ).order_by(model.created_at.desc()).offset(offset).limit(limit).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def soft_delete(self, entity) -> bool:
        """Suppression logique d'une entité"""
        try:
            entity.is_active = False
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    def generate_numero(self, prefix: str, model: Type, field: str = 'numero') -> str:
        """Génère un numéro unique avec un préfixe"""
        try:
            annee = datetime.now().year
            dernier = self.session.query(model).filter(
                getattr(model, field).like(f"{prefix}-{annee}-%")
            ).order_by(getattr(model, field).desc()).first()
            
            if dernier:
                num = int(getattr(dernier, field).split('-')[-1]) + 1
            else:
                num = 1
            
            return f"{prefix}-{annee}-{num:06d}"
        except Exception as e:
            self.session.rollback()
            raise e
    
    def log_audit(
        self,
        utilisateur_id: int,
        action: str,
        entite: str,
        entite_id: int = None,
        entite_nom: str = None,
        champ_modifie: str = None,
        ancienne_valeur: str = None,
        nouvelle_valeur: str = None,
        ip_adresse: str = None,
        user_agent: str = None,
        session_id: str = None,
        application: str = "desktop",
        commentaire: str = None,
        niveau: str = "INFO"
    ) -> LometaAuditLog:
        """Enregistre une entrée dans le journal d'audit"""
        try:
            # Récupérer les infos de l'utilisateur
            user_info = self.get_user_info(utilisateur_id)
            
            audit = LometaAuditLog(
                utilisateur_id=utilisateur_id,
                utilisateur_nom=user_info.get('full_name') or user_info.get('username'),
                utilisateur_role=user_info.get('role'),
                action=action,
                entite=entite,
                entite_id=entite_id,
                entite_nom=entite_nom,
                champ_modifie=champ_modifie,
                ancienne_valeur=ancienne_valeur,
                nouvelle_valeur=nouvelle_valeur,
                ip_adresse=ip_adresse,
                user_agent=user_agent,
                session_id=session_id,
                application=application,
                commentaire=commentaire,
                niveau=niveau,
                date_action=datetime.utcnow()
            )
            self.session.add(audit)
            self.session.commit()
            return audit
        except Exception as e:
            self.session.rollback()
            raise e
    
    def execute_with_retry(self, func, *args, **kwargs):
        """Exécute une fonction avec retry automatique"""
        return execute_with_retry(func, *args, **kwargs)