"""
Service de gestion des sessions utilisateurs - ORM SQLAlchemy
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from addons.sinistres.services.base_service import BaseService
from addons.Paramètres.models.models import User, Session as UserSession
from addons.sinistres.models.audit import LometaAuditLog


class SessionService(BaseService):
    """Service de gestion des sessions (ORM SQLAlchemy)"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # LECTURE
    # ============================================================
    
    def get_active_users(self, minutes: int = 30) -> List[dict]:
        """
        Récupère les utilisateurs ayant une session active.
        Utilise uniquement l'ORM SQLAlchemy.
        """
        try:
            seuil = datetime.now() - timedelta(minutes=minutes)
            
            # Requête ORM : jointure sessions + utilisateurs
            results = (
                self.session.query(UserSession, User)
                .join(User, User.id == UserSession.user_id)
                .filter(
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.now(),
                    UserSession.last_activity > seuil,
                    User.is_active == True,
                )
                .order_by(UserSession.last_activity.desc())
                .all()
            )
            
            # Dédupliquer par utilisateur (garder la session la plus récente)
            users_by_id = {}
            now = datetime.now()
            
            for sess, user in results:
                if user.id in users_by_id:
                    continue
                
                delta = (now - sess.last_activity).total_seconds() if sess.last_activity else 999999
                
                if delta < 300:
                    status = 'online'
                elif delta < 1800:
                    status = 'idle'
                else:
                    status = 'offline'
                
                users_by_id[user.id] = {
                    'id': user.id,
                    'username': user.username,
                    'nom': user.full_name or user.username or 'Utilisateur',
                    'email': user.email,
                    'role': user.role or 'Utilisateur',
                    'last_activity': sess.last_activity.isoformat() if sess.last_activity else None,
                    'ip_address': sess.ip_address,
                    'status': status,
                    'session_id': sess.id,
                }
            
            users = list(users_by_id.values())
            
            # Tri : online d'abord, puis par activité récente
            users.sort(
                key=lambda u: (
                    0 if u['status'] == 'online' else 1,
                    u['last_activity'] or ''
                )
            )
            
            return users
        
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_user_sessions(self, user_id: int) -> List[dict]:
        """Récupère toutes les sessions actives d'un utilisateur"""
        try:
            sessions = (
                self.session.query(UserSession)
                .filter(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.now(),
                )
                .order_by(UserSession.last_activity.desc())
                .all()
            )
            
            return [
                {
                    'id': s.id,
                    'user_id': s.user_id,
                    'last_activity': s.last_activity.isoformat() if s.last_activity else None,
                    'expires_at': s.expires_at.isoformat() if s.expires_at else None,
                    'ip_address': s.ip_address,
                    'user_agent': s.user_agent,
                    'created_at': s.created_at.isoformat() if s.created_at else None,
                }
                for s in sessions
            ]
        except Exception as e:
            self.session.rollback()
            raise e
    
    def count_active_sessions(self, user_id: int) -> int:
        """Compte les sessions actives d'un utilisateur"""
        try:
            return (
                self.session.query(UserSession)
                .filter(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.now(),
                )
                .count()
            )
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # DÉCONNEXION
    # ============================================================
    
    def disconnect_user(
        self,
        user_id: int,
        current_user_id: int,
        current_user_role: str,
        reason: str = "Déconnexion administrative"
    ) -> int:
        """
        Déconnecte toutes les sessions d'un utilisateur.
        
        Returns:
            Nombre de sessions désactivées
        
        Raises:
            ValueError: Si droits insuffisants ou action interdite
        """
        try:
            # ============================================================
            # 1. Vérifications de sécurité
            # ============================================================
            
            # Ne pas se déconnecter soi-même
            if current_user_id == user_id:
                raise ValueError(
                    "Vous ne pouvez pas vous déconnecter vous-même via cette interface."
                )
            
            # Seul un admin peut déconnecter
            if current_user_role != 'admin':
                raise ValueError(
                    "Seul un administrateur peut déconnecter un utilisateur."
                )
            
            # Vérifier que l'utilisateur cible existe
            target_user = self.session.query(User).filter(User.id == user_id).first()
            if not target_user:
                raise ValueError("Utilisateur introuvable")
            
            # ============================================================
            # 2. Désactiver toutes les sessions
            # ============================================================
            
            sessions = (
                self.session.query(UserSession)
                .filter(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                )
                .all()
            )
            
            nb = 0
            for sess in sessions:
                sess.is_active = False
                nb += 1
            
            # ============================================================
            # 3. Audit
            # ============================================================
            
            self.log_audit(
                utilisateur_id=current_user_id,
                action="DISCONNECT_USER",
                entite="User",
                entite_id=user_id,
                entite_nom=target_user.username,
                commentaire=f"{nb} session(s) déconnectée(s). Motif: {reason}",
            )
            
            self.session.commit()
            return nb
        
        except Exception as e:
            self.session.rollback()
            raise e
    
    def disconnect_session(
        self,
        session_id: int,
        current_user_id: int,
        current_user_role: str,
        reason: str = "Déconnexion administrative"
    ) -> bool:
        """Déconnecte une session spécifique"""
        try:
            if current_user_role != 'admin':
                raise ValueError("Seul un administrateur peut déconnecter une session.")
            
            sess = (
                self.session.query(UserSession)
                .filter(
                    UserSession.id == session_id,
                    UserSession.is_active == True,
                )
                .first()
            )
            
            if not sess:
                raise ValueError("Session introuvable ou déjà inactive")
            
            if sess.user_id == current_user_id:
                raise ValueError("Vous ne pouvez pas fermer votre propre session.")
            
            sess.is_active = False
            
            self.log_audit(
                utilisateur_id=current_user_id,
                action="DISCONNECT_SESSION",
                entite="Session",
                entite_id=session_id,
                commentaire=f"Motif: {reason}",
            )
            
            self.session.commit()
            return True
        
        except Exception as e:
            self.session.rollback()
            raise e
    
    def block_user(
        self,
        user_id: int,
        current_user_id: int,
        current_user_role: str,
        reason: str = "Blocage administratif"
    ) -> bool:
        """
        Bloque un utilisateur : déconnecte toutes ses sessions + désactive le compte.
        """
        try:
            # Vérifications
            if current_user_id == user_id:
                raise ValueError("Vous ne pouvez pas bloquer votre propre compte.")
            
            if current_user_role != 'admin':
                raise ValueError("Seul un administrateur peut bloquer un utilisateur.")
            
            user = self.session.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("Utilisateur introuvable")
            
            # Déconnecter toutes les sessions
            sessions = (
                self.session.query(UserSession)
                .filter(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                )
                .all()
            )
            for sess in sessions:
                sess.is_active = False
            
            # Désactiver le compte
            user.is_active = False
            
            # Audit
            self.log_audit(
                utilisateur_id=current_user_id,
                action="BLOCK_USER",
                entite="User",
                entite_id=user_id,
                entite_nom=user.username,
                commentaire=f"Compte bloqué. Motif: {reason}",
            )
            
            self.session.commit()
            return True
        
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # HEARTBEAT
    # ============================================================
    
    def heartbeat(self, user_id: int, session_token: str = None) -> bool:
        """
        Met à jour last_activity de la session courante.
        Appelé périodiquement par l'application.
        """
        try:
            query = self.session.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
            )
            
            if session_token:
                query = query.filter(UserSession.token_encrypted == session_token)
            
            # Prendre la session la plus récente
            sess = query.order_by(UserSession.last_activity.desc()).first()
            
            if sess:
                sess.last_activity = datetime.now()
                self.session.commit()
                return True
            return False
        
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # NETTOYAGE
    # ============================================================
    
    def cleanup_expired_sessions(self) -> int:
        """Désactive les sessions expirées"""
        try:
            sessions = (
                self.session.query(UserSession)
                .filter(
                    UserSession.expires_at <= datetime.now(),
                    UserSession.is_active == True,
                )
                .all()
            )
            
            for sess in sessions:
                sess.is_active = False
            
            self.session.commit()
            return len(sessions)
        
        except Exception as e:
            self.session.rollback()
            raise e