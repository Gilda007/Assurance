"""
Service de workflow (Tome 2 et 7 du CDC)
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from typing import Optional, List, Dict, Any

from addons.sinistres.services.base_service import BaseService
from addons.sinistres.models.referentiel import LometaReferentiel
from addons.sinistres.models.sinistre import LometaSinistre
from addons.sinistres.models.audit import LometaAuditLog


class WorkflowService(BaseService):
    """Service de gestion des workflows paramétrables"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # GESTION DES WORKFLOWS
    # ============================================================
    
    def get_transitions(self, statut_actuel: str) -> List[str]:
        """
        Récupère les transitions autorisées pour un statut
        """
        workflow = self.session.query(LometaReferentiel).filter(
            LometaReferentiel.famille == "workflow",
            LometaReferentiel.code == statut_actuel,
            LometaReferentiel.est_actif == True
        ).first()
        
        if workflow and workflow.description:
            return [t.strip() for t in workflow.description.split(',')]
        
        # Fallback
        return self._get_default_transitions(statut_actuel)
    
    def get_workflow_etats(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les états du workflow
        """
        etats = self.session.query(LometaReferentiel).filter(
            LometaReferentiel.famille == "workflow_etats",
            LometaReferentiel.est_actif == True
        ).order_by(LometaReferentiel.code).all()
        
        return [
            {
                'code': e.code,
                'libelle': e.libelle,
                'description': e.description,
                'transitions': self.get_transitions(e.code)
            }
            for e in etats
        ]
    
    def get_suites_a_donner(self) -> List[Dict[str, Any]]:
        """
        Récupère les suites à donner paramétrables
        """
        suites = self.session.query(LometaReferentiel).filter(
            LometaReferentiel.famille == "suites_a_donner",
            LometaReferentiel.est_actif == True
        ).all()
        
        return [
            {
                'code': s.code,
                'libelle': s.libelle,
                'description': s.description,
                'duree_defaut': s.valeur or 0
            }
            for s in suites
        ]
    
    def _get_default_transitions(self, statut_actuel: str) -> List[str]:
        """Transitions par défaut"""
        transitions = {
            "OUVERT": ["EN_INSTRUCTION", "CLOTURE"],
            "EN_INSTRUCTION": ["EN_EXPERTISE", "EN_EVALUATION", "CLOTURE"],
            "EN_EXPERTISE": ["EN_EVALUATION", "EN_INSTRUCTION", "CLOTURE"],
            "EN_EVALUATION": ["VALIDE", "EN_INSTRUCTION", "CLOTURE"],
            "VALIDE": ["EN_REGLEMENT", "REOUVERT", "CLOTURE"],
            "EN_REGLEMENT": ["EN_RECOURS", "CLOTURE", "REOUVERT"],
            "EN_RECOURS": ["EN_REGLEMENT", "CLOTURE", "REOUVERT"],
            "CLOTURE": ["REOUVERT"],
            "REOUVERT": ["EN_INSTRUCTION", "CLOTURE"]
        }
        return transitions.get(statut_actuel, [])
    
    # ============================================================
    # GÉNÉRATION DE TÂCHES
    # ============================================================
    
    def generer_taches_auto(self, sinistre: LometaSinistre, action: str) -> List[Dict[str, Any]]:
        """
        Génère des tâches automatiques suite à une action
        """
        taches = []
        
        # Récupérer les suites à donner
        suites = self.session.query(LometaReferentiel).filter(
            LometaReferentiel.famille == "suites_a_donner",
            LometaReferentiel.est_actif == True
        ).all()
        
        for suite in suites:
            if suite.code in action or action in suite.code:
                taches.append({
                    'type': suite.libelle,
                    'code': suite.code,
                    'description': suite.description,
                    'sinistre_id': str(sinistre.id),
                    'numero_sinistre': sinistre.numero_sinistre,
                    'date_echeance': datetime.now() + timedelta(days=int(suite.valeur or 7)),
                    'priorite': 'NORMALE'
                })
        
        return taches
    
    # ============================================================
    # VALIDATION DES TRANSITIONS
    # ============================================================
    
    def valider_transition(
        self,
        sinistre: LometaSinistre,
        nouveau_statut: str,
        utilisateur_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Valide une transition de statut et retourne les actions à effectuer
        """
        result = {
            'valide': True,
            'message': 'Transition validée',
            'taches': [],
            'notifications': []
        }
        
        # Vérifier la transition
        try:
            transitions = self.get_transitions(sinistre.statut)
            if nouveau_statut not in transitions:
                result['valide'] = False
                result['message'] = f"Transition non autorisée: {sinistre.statut} -> {nouveau_statut}"
                return result
        except Exception as e:
            result['valide'] = False
            result['message'] = str(e)
            return result
        
        # Générer les tâches automatiques
        if nouveau_statut in ['EN_EXPERTISE', 'EN_EVALUATION', 'EN_REGLEMENT', 'EN_RECOURS']:
            result['taches'] = self.generer_taches_auto(sinistre, nouveau_statut)
        
        # Générer les notifications
        result['notifications'] = self._generer_notifications(sinistre, nouveau_statut)
        
        return result
    
    def _generer_notifications(self, sinistre: LometaSinistre, nouveau_statut: str) -> List[Dict[str, Any]]:
        """Génère les notifications pour un changement de statut"""
        notifications = []
        
        notifications_map = {
            'EN_EXPERTISE': {
                'type': 'EXPERTISE_DEBUT',
                'titre': f"Début d'expertise - {sinistre.numero_sinistre}",
                'message': f"Le sinistre {sinistre.numero_sinistre} est en cours d'expertise."
            },
            'EN_EVALUATION': {
                'type': 'EVALUATION_DEBUT',
                'titre': f"Évaluation en cours - {sinistre.numero_sinistre}",
                'message': f"Le sinistre {sinistre.numero_sinistre} est en cours d'évaluation."
            },
            'VALIDE': {
                'type': 'EVALUATION_VALIDEE',
                'titre': f"Évaluation validée - {sinistre.numero_sinistre}",
                'message': f"L'évaluation du sinistre {sinistre.numero_sinistre} a été validée."
            },
            'EN_REGLEMENT': {
                'type': 'REGLEMENT_DEBUT',
                'titre': f"Début du règlement - {sinistre.numero_sinistre}",
                'message': f"Le règlement du sinistre {sinistre.numero_sinistre} est en cours."
            },
            'CLOTURE': {
                'type': 'SINISTRE_CLOTURE',
                'titre': f"Sinistre clôturé - {sinistre.numero_sinistre}",
                'message': f"Le sinistre {sinistre.numero_sinistre} a été clôturé."
            }
        }
        
        if nouveau_statut in notifications_map:
            notif = notifications_map[nouveau_statut]
            notifications.append({
                'destinataire_id': sinistre.responsable_id or sinistre.created_by,
                'type': notif['type'],
                'titre': notif['titre'],
                'message': notif['message'],
                'sinistre_id': str(sinistre.id),
                'canaux': ['email', 'notification']
            })
        
        return notifications