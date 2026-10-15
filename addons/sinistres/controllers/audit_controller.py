"""
Contrôleur d'audit - Interface entre l'UI et AuditService
"""
from PySide6.QtCore import Signal
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from addons.sinistres.controllers.controleur_base import BaseController
from addons.sinistres.services.audit_service import AuditService


class AuditController(BaseController):
    """Contrôleur pour la gestion de l'audit"""
    
    logs_loaded = Signal(list)
    stats_loaded = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.service = AuditService()
    
    def get_all_logs(self, limit: int = 500) -> List[dict]:
        """Récupère tous les logs récents"""
        try:
            logs = self.service.get_logs(limit=limit, offset=0)
            result = [self._serialize(log) for log in logs]
            self.logs_loaded.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_logs_filtered(
        self,
        action: str = None,
        entite: str = None,
        utilisateur_id: int = None,
        date_debut: datetime = None,
        date_fin: datetime = None,
        limit: int = 500,
        offset: int = 0
    ) -> List[dict]:
        """Récupère les logs avec filtres"""
        try:
            logs = self.service.get_logs(
                utilisateur_id=utilisateur_id,
                entite=entite,
                action=action,
                date_debut=date_debut,
                date_fin=date_fin,
                limit=limit,
                offset=offset,
            )
            return [self._serialize(log) for log in logs]
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_statistiques(self, date_debut: datetime = None, date_fin: datetime = None) -> dict:
        """Récupère les statistiques d'audit"""
        try:
            stats = self.service.get_statistiques(date_debut=date_debut, date_fin=date_fin)
            self.stats_loaded.emit(stats)
            return stats
        except Exception as e:
            self.handle_error(e)
            return {}
    
    def get_logs_for_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère les logs liés à un sinistre"""
        try:
            logs = self.service.get_logs_for_sinistre(sinistre_id)
            return [self._serialize(log) for log in logs]
        except Exception as e:
            self.handle_error(e)
            return []
    
    def _serialize(self, log) -> dict:
        """Sérialise un LometaAuditLog en dict"""
        return {
            'id': log.id,
            'date': log.date_action.strftime('%Y-%m-%d %H:%M') if log.date_action else '',
            'date_iso': log.date_action.isoformat() if log.date_action else None,
            'user': log.utilisateur_nom or f"User#{log.utilisateur_id}",
            'user_id': log.utilisateur_id,
            'user_role': log.utilisateur_role,
            'action': log.action or '',
            'entite': log.entite or '',
            'entite_id': log.entite_id,
            'entite_nom': log.entite_nom or '',
            'entity': log.entite_nom or str(log.entite_id or ''),
            'champ': log.champ_modifie or '',
            'ancienne_valeur': log.ancienne_valeur or '',
            'nouvelle_valeur': log.nouvelle_valeur or '',
            'change': self._format_change(log),
            'commentaire': log.commentaire or '',
            'niveau': log.niveau or 'INFO',
        }
    
    def _format_change(self, log) -> str:
        """Formate la transition ancien → nouveau"""
        ancien = log.ancienne_valeur or ''
        nouveau = log.nouvelle_valeur or ''
        if ancien and nouveau:
            return f"{ancien} → {nouveau}"
        elif nouveau:
            return nouveau
        elif ancien:
            return ancien
        return ''