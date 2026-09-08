"""
Service d'audit (Tome 7 du CDC)
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, between, func
from datetime import datetime, timedelta
import uuid
from typing import Optional, List, Dict, Any

from addons.sinistres.services.base_service import BaseService
from addons.sinistres.models.audit import LometaAuditLog
from addons.sinistres.models.sinistre import Sinistre


class AuditService(BaseService):
    """Service de gestion de l'audit"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # ENREGISTREMENT
    # ============================================================
    
    def log_action(
        self,
        utilisateur_id: int,
        action: str,
        entite: str,
        entite_id: int = None,
        entite_nom: str = None,
        utilisateur_nom: str = None,
        utilisateur_role: str = None,
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
        """
        Enregistre une action dans le journal d'audit
        """
        audit = LometaAuditLog(
            utilisateur_id=utilisateur_id,
            utilisateur_nom=utilisateur_nom,
            utilisateur_role=utilisateur_role,
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
    
    # ============================================================
    # CONSULTATION
    # ============================================================
    
    def get_logs(
        self,
        utilisateur_id: int = None,
        entite: str = None,
        entite_id: int = None,
        action: str = None,
        date_debut: datetime = None,
        date_fin: datetime = None,
        niveau: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LometaAuditLog]:
        """
        Récupère les logs d'audit selon des critères
        """
        query = self.session.query(LometaAuditLog)
        
        if utilisateur_id:
            query = query.filter(LometaAuditLog.utilisateur_id == utilisateur_id)
        
        if entite:
            query = query.filter(LometaAuditLog.entite == entite)
        
        if entite_id:
            query = query.filter(LometaAuditLog.entite_id == entite_id)
        
        if action:
            query = query.filter(LometaAuditLog.action == action)
        
        if date_debut and date_fin:
            query = query.filter(
                between(LometaAuditLog.date_action, date_debut, date_fin)
            )
        elif date_debut:
            query = query.filter(LometaAuditLog.date_action >= date_debut)
        elif date_fin:
            query = query.filter(LometaAuditLog.date_action <= date_fin)
        
        if niveau:
            query = query.filter(LometaAuditLog.niveau == niveau)
        
        return query.order_by(LometaAuditLog.date_action.desc()).offset(offset).limit(limit).all()
    
    def get_logs_for_entite(self, entite: str, entite_id: int) -> List[LometaAuditLog]:
        """
        Récupère tous les logs pour une entité donnée
        """
        return self.get_logs(entite=entite, entite_id=entite_id)
    
    def get_logs_for_sinistre(self, sinistre_id: int) -> List[LometaAuditLog]:
        """
        Récupère tous les logs pour un sinistre
        """
        # Récupérer le sinistre
        sinistre = self.session.query(Sinistre).filter(
            Sinistre.id == sinistre_id,
            Sinistre.is_active == True
        ).first()
        
        if not sinistre:
            return []
        
        # Logs directs sur le sinistre
        logs = self.get_logs(entite="Sinistre", entite_id=sinistre_id)
        
        # Logs sur les entités liées (expertises, évaluations, règlements, recours)
        from models.expertise import Expertise, Evaluation, Provision
        from models.reglement import Reglement
        from models.recours import Recours
        
        # Expertises
        expertises = self.session.query(Expertise).filter(
            Expertise.sinistre_id == sinistre_id,
            Expertise.is_active == True
        ).all()
        
        for exp in expertises:
            logs.extend(self.get_logs(entite="Expertise", entite_id=exp.id))
        
        # Évaluations
        evaluations = self.session.query(Evaluation).filter(
            Evaluation.sinistre_id == sinistre_id,
            Evaluation.is_active == True
        ).all()
        
        for eval_ in evaluations:
            logs.extend(self.get_logs(entite="Evaluation", entite_id=eval_.id))
        
        # Règlements
        reglements = self.session.query(Reglement).filter(
            Reglement.sinistre_id == sinistre_id,
            Reglement.is_active == True
        ).all()
        
        for reg in reglements:
            logs.extend(self.get_logs(entite="Reglement", entite_id=reg.id))
        
        # Recours
        recours = self.session.query(Recours).filter(
            Recours.sinistre_id == sinistre_id,
            Recours.is_active == True
        ).all()
        
        for rec in recours:
            logs.extend(self.get_logs(entite="Recours", entite_id=rec.id))
        
        # Trier par date
        logs.sort(key=lambda x: x.date_action, reverse=True)
        
        return logs
    
    # ============================================================
    # STATISTIQUES D'AUDIT
    # ============================================================
    
    def get_statistiques(
        self,
        date_debut: datetime = None,
        date_fin: datetime = None
    ) -> Dict[str, Any]:
        """
        Récupère les statistiques d'audit
        """
        query = self.session.query(LometaAuditLog)
        
        if date_debut and date_fin:
            query = query.filter(
                between(LometaAuditLog.date_action, date_debut, date_fin)
            )
        
        # Total
        total = query.count()
        
        # Par action
        par_action = {}
        for action in ['CREATION', 'MODIFICATION', 'VALIDATION', 'SUPPRESSION', 'CHANGEMENT_STATUT', 'PAIEMENT', 'ENCAISSEMENT']:
            count = query.filter(LometaAuditLog.action == action).count()
            if count > 0:
                par_action[action] = count
        
        # Par entité
        par_entite = {}
        for entite in ['Sinistre', 'Expertise', 'Evaluation', 'Reglement', 'Recours', 'Referentiel']:
            count = query.filter(LometaAuditLog.entite == entite).count()
            if count > 0:
                par_entite[entite] = count
        
        # Par utilisateur
        par_utilisateur = {}
        results = query.with_entities(
            LometaAuditLog.utilisateur_id,
            func.count(LometaAuditLog.id).label('count')
        ).group_by(LometaAuditLog.utilisateur_id).order_by(func.count(LometaAuditLog.id).desc()).limit(10).all()
        
        for r in results:
            par_utilisateur[str(r[0])] = r[1]
        
        return {
            'total': total,
            'par_action': par_action,
            'par_entite': par_entite,
            'top_utilisateurs': par_utilisateur
        }