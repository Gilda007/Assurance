"""
Service de gestion des évaluations (Tome 4 du CDC)
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any

from addons.sinistres.services.base_service import BaseService, func
from addons.sinistres.models.expertise import LometaEvaluation, LometaProvision, LometaRevisionEvaluation
from addons.sinistres.models.sinistre import LometaSinistre


class EvaluationService(BaseService):
    """Service de gestion des évaluations"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # CRUD PRINCIPAL
    # ============================================================
    
    def creer_evaluation(self, data: Dict[str, Any]) -> LometaEvaluation:
        """Crée une nouvelle évaluation"""
        try:
            # Vérifier que le sinistre existe
            sinistre = self.session.query(LometaSinistre).filter(
                LometaSinistre.id == data.get('sinistre_id'),
                LometaSinistre.is_active == True
            ).first()
            if not sinistre:
                raise ValueError("Sinistre non trouvé")
            
            # Calculer le montant net
            montant_brut = data.get('montant_brut', 0)
            franchise = data.get('franchise', 0)
            taux_responsabilite = data.get('taux_responsabilite', 1.0)
            montant_net = self.calculer_montant_net(montant_brut, franchise, taux_responsabilite)
            
            # Générer le numéro
            numero = self.generate_numero("EVAL", LometaEvaluation, 'numero_evaluation')
            
            evaluation = LometaEvaluation(
                numero_evaluation=numero,
                montant_net=montant_net,
                date_evaluation=datetime.utcnow(),
                **data
            )
            
            self.session.add(evaluation)
            self.session.flush()
            
            # Mettre à jour le statut du sinistre
            if sinistre.statut not in ["EN_EVALUATION", "VALIDE", "CLOTURE"]:
                sinistre.statut = "EN_EVALUATION"
                sinistre.updated_at = datetime.utcnow()
                sinistre.updated_by = data.get('created_by')
            
            # Log d'audit
            self.log_audit(
                utilisateur_id=data.get('created_by'),
                action="CREATION",
                entite="Evaluation",
                entite_id=evaluation.id,
                entite_nom=evaluation.numero_evaluation,
                commentaire=f"Création de l'évaluation {evaluation.numero_evaluation} - Montant net: {montant_net}"
            )
            
            self.session.commit()
            return evaluation
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_evaluation(self, evaluation_id: int) -> Optional[LometaEvaluation]:
        """Récupère une évaluation par son ID"""
        try:
            return self.session.query(LometaEvaluation).filter(
                LometaEvaluation.id == evaluation_id,
                LometaEvaluation.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_evaluation_by_numero(self, numero: str) -> Optional[LometaEvaluation]:
        """Récupère une évaluation par son numéro"""
        try:
            return self.session.query(LometaEvaluation).filter(
                LometaEvaluation.numero_evaluation == numero,
                LometaEvaluation.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_revisions_by_evaluation(self, evaluation_id: int) -> List[LometaRevisionEvaluation]:
        """Récupère toutes les révisions d'une évaluation"""
        try:
            return self.session.query(LometaRevisionEvaluation).filter(
                LometaRevisionEvaluation.evaluation_id == evaluation_id,
                LometaRevisionEvaluation.is_active == True
            ).order_by(LometaRevisionEvaluation.date_revision.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_evaluations_by_sinistre(self, sinistre_id: int) -> List[LometaEvaluation]:
        """Récupère toutes les évaluations d'un sinistre"""
        try:
            return self.session.query(LometaEvaluation).filter(
                LometaEvaluation.sinistre_id == sinistre_id,
                LometaEvaluation.is_active == True
            ).order_by(LometaEvaluation.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_evaluation(self, evaluation_id: int, data: Dict[str, Any]) -> Optional[LometaEvaluation]:
        """Met à jour une évaluation"""
        try:
            evaluation = self.get_evaluation(evaluation_id)
            if not evaluation:
                raise ValueError("Évaluation non trouvée")
            
            if evaluation.est_validee:
                raise ValueError("Une évaluation validée ne peut pas être modifiée")
            
            # Recalculer le montant net si nécessaire
            if 'montant_brut' in data or 'franchise' in data or 'taux_responsabilite' in data:
                montant_brut = data.get('montant_brut', evaluation.montant_brut)
                franchise = data.get('franchise', evaluation.franchise)
                taux_responsabilite = data.get('taux_responsabilite', evaluation.taux_responsabilite)
                data['montant_net'] = self.calculer_montant_net(montant_brut, franchise, taux_responsabilite)
            
            for key, value in data.items():
                if hasattr(evaluation, key) and getattr(evaluation, key) != value:
                    setattr(evaluation, key, value)
            
            evaluation.updated_at = datetime.utcnow()
            evaluation.updated_by = data.get('updated_by')
            
            self.session.commit()
            return evaluation
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def reviser_evaluation(self, evaluation_id: int, data: Dict[str, Any], utilisateur_id: int) -> Optional[LometaEvaluation]:
        """Révisé une évaluation avec historisation"""
        try:
            evaluation = self.get_evaluation(evaluation_id)
            if not evaluation:
                raise ValueError("Évaluation non trouvée")
            
            if evaluation.est_validee:
                raise ValueError("Une évaluation validée ne peut pas être révisée")
            
            # Enregistrer la révision
            revision = LometaRevisionEvaluation(
                evaluation_id=evaluation_id,
                ancien_montant_brut=evaluation.montant_brut,
                ancien_montant_net=evaluation.montant_net,
                nouveau_montant_brut=data.get('montant_brut', evaluation.montant_brut),
                nouveau_montant_net=self.calculer_montant_net(
                    data.get('montant_brut', evaluation.montant_brut),
                    data.get('franchise', evaluation.franchise),
                    data.get('taux_responsabilite', evaluation.taux_responsabilite)
                ),
                motif=data.get('motif', 'Révision'),
                revise_par=utilisateur_id
            )
            self.session.add(revision)
            
            # Mettre à jour l'évaluation
            for key, value in data.items():
                if hasattr(evaluation, key) and getattr(evaluation, key) != value:
                    setattr(evaluation, key, value)
            
            # Recalculer le montant net
            evaluation.montant_net = self.calculer_montant_net(
                evaluation.montant_brut,
                evaluation.franchise,
                evaluation.taux_responsabilite
            )
            evaluation.updated_at = datetime.utcnow()
            evaluation.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="REVISION",
                entite="Evaluation",
                entite_id=evaluation.id,
                entite_nom=evaluation.numero_evaluation,
                champ_modifie="montant_brut",
                ancienne_valeur=str(revision.ancien_montant_brut),
                nouvelle_valeur=str(revision.nouveau_montant_brut),
                commentaire=f"Révision de l'évaluation {evaluation.numero_evaluation} - Motif: {revision.motif}"
            )
            
            self.session.commit()
            return evaluation
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def valider_evaluation(self, evaluation_id: int, utilisateur_id: int) -> Optional[LometaEvaluation]:
        """Valide une évaluation"""
        try:
            evaluation = self.get_evaluation(evaluation_id)
            if not evaluation:
                raise ValueError("Évaluation non trouvée")
            
            if evaluation.est_validee:
                raise ValueError("Cette évaluation est déjà validée")
            
            evaluation.est_validee = True
            evaluation.validee_par = utilisateur_id
            evaluation.date_validation = datetime.utcnow()
            evaluation.updated_at = datetime.utcnow()
            evaluation.updated_by = utilisateur_id
            
            # Mettre à jour le statut du sinistre
            sinistre = self.session.query(LometaSinistre).filter(
                LometaSinistre.id == evaluation.sinistre_id,
                LometaSinistre.is_active == True
            ).first()
            if sinistre and sinistre.statut == "EN_EVALUATION":
                sinistre.statut = "VALIDE"
                sinistre.updated_at = datetime.utcnow()
                sinistre.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="VALIDATION",
                entite="Evaluation",
                entite_id=evaluation.id,
                entite_nom=evaluation.numero_evaluation,
                commentaire=f"Validation de l'évaluation {evaluation.numero_evaluation} - Montant net: {evaluation.montant_net}"
            )
            
            self.session.commit()
            return evaluation
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # MÉTHODES UTILITAIRES
    # ============================================================
    
    def calculer_montant_net(self, montant_brut: float, franchise: float, taux_responsabilite: float) -> float:
        """
        Calcule le montant net selon la formule standard:
        Montant Net = (Montant Brut - Franchise) x Taux Responsabilité
        """
        return (montant_brut - franchise) * taux_responsabilite
    
    def get_revisions(self, evaluation_id: int) -> List[LometaRevisionEvaluation]:
        """Récupère toutes les révisions d'une évaluation"""
        try:
            return self.session.query(LometaRevisionEvaluation).filter(
                LometaRevisionEvaluation.evaluation_id == evaluation_id,
                LometaRevisionEvaluation.is_active == True
            ).order_by(LometaRevisionEvaluation.date_revision.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # STATISTIQUES
    # ============================================================
    
    def get_statistiques(self, sinistre_id: int = None) -> Dict[str, Any]:
        """Récupère les statistiques des évaluations"""
        try:
            query = self.session.query(LometaEvaluation).filter(LometaEvaluation.is_active == True)
            
            if sinistre_id:
                query = query.filter(LometaEvaluation.sinistre_id == sinistre_id)
            
            total = query.count()
            
            # Montant total
            montant_total = query.with_entities(
                func.sum(LometaEvaluation.montant_net)
            ).scalar() or 0
            
            # Validées vs non validées
            validees = query.filter(LometaEvaluation.est_validee == True).count()
            non_validees = total - validees
            
            # Montant moyen
            montant_moyen = query.with_entities(
                func.avg(LometaEvaluation.montant_net)
            ).scalar() or 0
            
            return {
                'total': total,
                'validees': validees,
                'non_validees': non_validees,
                'montant_total': montant_total,
                'montant_moyen': round(montant_moyen, 2)
            }
        except Exception as e:
            self.session.rollback()
            raise e

    # Ajouter ces méthodes à la fin de la classe EvaluationService

    def get_provisions_by_sinistre(self, sinistre_id: int) -> List['LometaProvision']:
        """Récupère toutes les provisions d'un sinistre"""
        try:
            from addons.sinistres.models.expertise import LometaProvision
            return self.session.query(LometaProvision).filter(
                LometaProvision.sinistre_id == sinistre_id,
                LometaProvision.is_active == True
            ).order_by(LometaProvision.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_provision(self, provision_id: int) -> Optional['LometaProvision']:
        """Récupère une provision par son ID"""
        try:
            from addons.sinistres.models.expertise import LometaProvision
            return self.session.query(LometaProvision).filter(
                LometaProvision.id == provision_id,
                LometaProvision.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e

    def creer_provision(self, data: Dict[str, Any]) -> 'LometaProvision':
        """Crée une nouvelle provision"""
        try:
            from addons.sinistres.models.expertise import LometaProvision
            
            # Vérifier que le sinistre existe
            sinistre = self.session.query(LometaSinistre).filter(
                LometaSinistre.id == data.get('sinistre_id'),
                LometaSinistre.is_active == True
            ).first()
            if not sinistre:
                raise ValueError("Sinistre non trouvé")
            
            # Générer le numéro
            numero = self.generate_numero("PROV", LometaProvision, 'numero_provision')
            
            provision = LometaProvision(
                numero_provision=numero,
                est_active=True,
                **data
            )
            
            self.session.add(provision)
            self.session.commit()
            return provision
            
        except Exception as e:
            self.session.rollback()
            raise e

    def update_provision(self, provision_id: int, data: Dict[str, Any]) -> Optional['LometaProvision']:
        """Met à jour une provision"""
        try:
            from addons.sinistres.models.expertise import LometaProvision
            provision = self.get_provision(provision_id)
            if not provision:
                raise ValueError("Provision non trouvée")
            
            for key, value in data.items():
                if hasattr(provision, key) and getattr(provision, key) != value:
                    setattr(provision, key, value)
            
            provision.updated_at = datetime.utcnow()
            provision.updated_by = data.get('updated_by')
            
            self.session.commit()
            return provision
            
        except Exception as e:
            self.session.rollback()
            raise e

    def cloturer_provision(self, provision_id: int, utilisateur_id: int, motif: str = None) -> Optional['LometaProvision']:
        """Clôture une provision"""
        try:
            from addons.sinistres.models.expertise import LometaProvision
            provision = self.get_provision(provision_id)
            if not provision:
                raise ValueError("Provision non trouvée")
            
            provision.est_active = False
            provision.date_cloture = datetime.utcnow()
            provision.updated_at = datetime.utcnow()
            provision.updated_by = utilisateur_id
            provision.motif = motif or "Clôture de la provision"
            
            self.session.commit()
            return provision
            
        except Exception as e:
            self.session.rollback()
            raise e

    def get_all_evaluations(self) -> List['LometaEvaluation']:
        """Récupère toutes les évaluations (tous sinistres)"""
        try:
            from addons.sinistres.models.expertise import LometaEvaluation
            return self.session.query(LometaEvaluation).filter(
                LometaEvaluation.is_active == True
            ).order_by(LometaEvaluation.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_all_provisions(self) -> List['LometaProvision']:
        """Récupère toutes les provisions (tous sinistres)"""
        try:
            from addons.sinistres.models.expertise import LometaProvision
            return self.session.query(LometaProvision).filter(
                LometaProvision.is_active == True
            ).order_by(LometaProvision.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

