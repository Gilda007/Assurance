"""
Service de gestion des règlements (Tome 5 du CDC)
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any

from addons.sinistres.services.base_service import BaseService, func
from addons.sinistres.models.reglement import (
    LometaBeneficiaire, LometaCompteBancaire, LometaReglement, LometaLotPaiement, LometaNoteCredit
)
from addons.sinistres.models.sinistre import LometaSinistre
from addons.sinistres.models.expertise import LometaEvaluation


class ReglementService(BaseService):
    """Service de gestion des règlements"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # GESTION DES BÉNÉFICIAIRES
    # ============================================================
    
    def creer_beneficiaire(self, data: Dict[str, Any]) -> LometaBeneficiaire:
        """Crée un nouveau bénéficiaire"""
        try:
            beneficiaire = LometaBeneficiaire(**data)
            self.session.add(beneficiaire)
            self.session.commit()
            return beneficiaire
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_beneficiaire(self, beneficiaire_id: int) -> Optional[LometaBeneficiaire]:
        """Récupère un bénéficiaire par son ID"""
        try:
            return self.session.query(LometaBeneficiaire).filter(
                LometaBeneficiaire.id == beneficiaire_id,
                LometaBeneficiaire.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_beneficiaires(self, type_beneficiaire: str = None) -> List[LometaBeneficiaire]:
        """Récupère tous les bénéficiaires"""
        try:
            query = self.session.query(LometaBeneficiaire).filter(LometaBeneficiaire.is_active == True)
            if type_beneficiaire:
                query = query.filter(LometaBeneficiaire.type_beneficiaire == type_beneficiaire)
            return query.order_by(LometaBeneficiaire.nom).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # GESTION DES RÈGLEMENTS
    # ============================================================
    
    def creer_reglement(self, data: Dict[str, Any]) -> LometaReglement:
        """Crée une demande de règlement"""
        try:
            # Vérifier que le sinistre existe
            sinistre = self.session.query(LometaSinistre).filter(
                LometaSinistre.id == data.get('sinistre_id'),
                LometaSinistre.is_active == True
            ).first()
            if not sinistre:
                raise ValueError("Sinistre non trouvé")
            
            # Vérifier que l'évaluation est validée
            if data.get('evaluation_id'):
                evaluation = self.session.query(LometaEvaluation).filter(
                    LometaEvaluation.id == data.get('evaluation_id'),
                    LometaEvaluation.est_validee == True,
                    LometaEvaluation.is_active == True
                ).first()
                if not evaluation:
                    raise ValueError("Évaluation non trouvée ou non validée")
            
            # Vérifier que le bénéficiaire existe
            if data.get('beneficiaire_id'):
                beneficiaire = self.get_beneficiaire(data['beneficiaire_id'])
                if not beneficiaire:
                    raise ValueError("Bénéficiaire non trouvé")
            
            # Vérifier que le montant ne dépasse pas l'évaluation
            if data.get('evaluation_id') and data.get('montant'):
                evaluation = self.get_evaluation(data['evaluation_id'])
                if evaluation and data['montant'] > evaluation.montant_net:
                    raise ValueError(f"Le montant ({data['montant']}) dépasse l'évaluation ({evaluation.montant_net})")
            
            # Générer le numéro
            numero = self.generate_numero("REG", LometaReglement, 'numero_reglement')
            
            reglement = LometaReglement(
                numero_reglement=numero,
                statut="CREE",
                date_demande=datetime.utcnow(),
                **data
            )
            
            self.session.add(reglement)
            self.session.flush()
            
            # Mettre à jour le statut du sinistre
            if sinistre.statut not in ["EN_REGLEMENT", "CLOTURE"]:
                sinistre.statut = "EN_REGLEMENT"
                sinistre.updated_at = datetime.utcnow()
                sinistre.updated_by = data.get('created_by')
            
            self.log_audit(
                utilisateur_id=data.get('created_by'),
                action="CREATION",
                entite="Reglement",
                entite_id=reglement.id,
                entite_nom=reglement.numero_reglement,
                commentaire=f"Création du règlement {reglement.numero_reglement} - Montant: {reglement.montant}"
            )
            
            self.session.commit()
            return reglement
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_reglement(self, reglement_id: int) -> Optional[LometaReglement]:
        """Récupère un règlement par son ID"""
        try:
            return self.session.query(LometaReglement).filter(
                LometaReglement.id == reglement_id,
                LometaReglement.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_reglement_by_numero(self, numero: str) -> Optional[LometaReglement]:
        """Récupère un règlement par son numéro"""
        try:
            return self.session.query(LometaReglement).filter(
                LometaReglement.numero_reglement == numero,
                LometaReglement.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_reglements_by_sinistre(self, sinistre_id: int) -> List[LometaReglement]:
        """Récupère tous les règlements d'un sinistre"""
        try:
            return self.session.query(LometaReglement).filter(
                LometaReglement.sinistre_id == sinistre_id,
                LometaReglement.is_active == True
            ).order_by(LometaReglement.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_reglements_en_attente(self) -> List[LometaReglement]:
        """Récupère tous les règlements en attente de validation"""
        try:
            return self.session.query(LometaReglement).filter(
                LometaReglement.statut.in_(['CREE', 'VALIDE', 'EN_ATTENTE']),
                LometaReglement.is_active == True
            ).order_by(LometaReglement.date_demande.asc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def valider_reglement(self, reglement_id: int, utilisateur_id: int) -> Optional[LometaReglement]:
        """Valide un règlement"""
        try:
            reglement = self.get_reglement(reglement_id)
            if not reglement:
                raise ValueError("Règlement non trouvé")
            
            if reglement.statut != "CREE":
                raise ValueError("Seul un règlement créé peut être validé")
            
            reglement.statut = "VALIDE"
            reglement.date_validation = datetime.utcnow()
            reglement.valide_par = utilisateur_id
            reglement.updated_at = datetime.utcnow()
            reglement.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="VALIDATION",
                entite="Reglement",
                entite_id=reglement.id,
                entite_nom=reglement.numero_reglement,
                commentaire=f"Validation du règlement {reglement.numero_reglement}"
            )
            
            self.session.commit()
            return reglement
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def payer_reglement(self, reglement_id: int, utilisateur_id: int, data: Dict[str, Any]) -> Optional[LometaReglement]:
        """Exécute le paiement d'un règlement"""
        try:
            reglement = self.get_reglement(reglement_id)
            if not reglement:
                raise ValueError("Règlement non trouvé")
            
            if reglement.statut not in ["VALIDE", "EN_ATTENTE"]:
                raise ValueError("Seul un règlement validé peut être payé")
            
            # Mettre à jour selon le type de paiement
            if reglement.type_paiement == "CHEQUE" and data.get('numero_cheque'):
                reglement.numero_cheque = data['numero_cheque']
                reglement.banque_emetteur = data.get('banque_emetteur')
                reglement.date_emission_cheque = datetime.utcnow()
            elif reglement.type_paiement == "VIREMENT" and data.get('reference_virement'):
                reglement.reference_virement = data['reference_virement']
                reglement.date_virement = datetime.utcnow()
            elif reglement.type_paiement == "MOBILE_MONEY" and data.get('reference_mobile'):
                reglement.reference_mobile = data['reference_mobile']
                reglement.operateur_mobile = data.get('operateur_mobile')
            
            reglement.statut = "PAYE"
            reglement.date_paiement = datetime.utcnow()
            reglement.paiement_effectue_par = utilisateur_id
            reglement.updated_at = datetime.utcnow()
            reglement.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="PAIEMENT",
                entite="Reglement",
                entite_id=reglement.id,
                entite_nom=reglement.numero_reglement,
                commentaire=f"Paiement du règlement {reglement.numero_reglement} - {reglement.type_paiement}"
            )
            
            self.session.commit()
            return reglement
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def annuler_reglement(self, reglement_id: int, utilisateur_id: int, motif: str) -> Optional[LometaReglement]:
        """Annule un règlement"""
        try:
            reglement = self.get_reglement(reglement_id)
            if not reglement:
                raise ValueError("Règlement non trouvé")
            
            if reglement.statut == "PAYE":
                raise ValueError("Un règlement déjà payé ne peut pas être annulé")
            
            reglement.statut = "ANNULE"
            reglement.motif_annulation = motif
            reglement.updated_at = datetime.utcnow()
            reglement.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="ANNULATION",
                entite="Reglement",
                entite_id=reglement.id,
                entite_nom=reglement.numero_reglement,
                commentaire=f"Annulation du règlement {reglement.numero_reglement} - Motif: {motif}"
            )
            
            self.session.commit()
            return reglement
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # GESTION DES LOTS DE PAIEMENT
    # ============================================================
    
    def creer_lot_paiement(self, data: Dict[str, Any]) -> LometaLotPaiement:
        """Crée un lot de paiement"""
        try:
            numero = self.generate_numero("LOT", LometaLotPaiement, 'numero_lot')
            
            lot = LometaLotPaiement(
                numero_lot=numero,
                statut="OUVERT",
                date_creation=datetime.utcnow(),
                **data
            )
            
            self.session.add(lot)
            self.session.commit()
            return lot
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_lot_paiement(self, lot_id: int) -> Optional[LometaLotPaiement]:
        """Récupère un lot de paiement"""
        try:
            return self.session.query(LometaLotPaiement).filter(
                LometaLotPaiement.id == lot_id,
                LometaLotPaiement.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def ajouter_reglement_au_lot(self, reglement_id: int, lot_id: int, utilisateur_id: int) -> bool:
        """Ajoute un règlement à un lot"""
        try:
            reglement = self.get_reglement(reglement_id)
            if not reglement:
                raise ValueError("Règlement non trouvé")
            
            lot = self.get_lot_paiement(lot_id)
            if not lot:
                raise ValueError("Lot non trouvé")
            
            if lot.statut != "OUVERT":
                raise ValueError("Seul un lot ouvert peut recevoir des règlements")
            
            reglement.lot_paiement_id = lot_id
            reglement.updated_at = datetime.utcnow()
            reglement.updated_by = utilisateur_id
            
            # Mettre à jour les statistiques du lot
            lot.nombre_paiements += 1
            lot.montant_total += reglement.montant
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def valider_lot_paiement(self, lot_id: int, utilisateur_id: int) -> Optional[LometaLotPaiement]:
        """Valide un lot de paiement"""
        try:
            lot = self.get_lot_paiement(lot_id)
            if not lot:
                raise ValueError("Lot non trouvé")
            
            if lot.statut != "OUVERT":
                raise ValueError("Seul un lot ouvert peut être validé")
            
            lot.statut = "VALIDE"
            lot.date_validation = datetime.utcnow()
            lot.valide_par = utilisateur_id
            lot.updated_at = datetime.utcnow()
            lot.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="VALIDATION",
                entite="LometaLotPaiement",
                entite_id=lot.id,
                entite_nom=lot.numero_lot,
                commentaire=f"Validation du lot {lot.numero_lot} - {lot.nombre_paiements} paiements"
            )
            
            self.session.commit()
            return lot
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # MÉTHODES UTILITAIRES
    # ============================================================
    
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
    
    # ============================================================
    # STATISTIQUES
    # ============================================================
    
    def get_statistiques(self, sinistre_id: int = None) -> Dict[str, Any]:
        """Récupère les statistiques des règlements"""
        try:
            query = self.session.query(LometaReglement).filter(LometaReglement.is_active == True)
            
            if sinistre_id:
                query = query.filter(LometaReglement.sinistre_id == sinistre_id)
            
            total = query.count()
            
            # Par statut
            par_statut = {}
            for statut in ['CREE', 'VALIDE', 'EN_ATTENTE', 'TRAITE', 'PAYE', 'ANNULE', 'REJETE']:
                count = query.filter(LometaReglement.statut == statut).count()
                if count > 0:
                    par_statut[statut] = count
            
            # Montant total
            montant_total = query.with_entities(
                func.sum(LometaReglement.montant)
            ).scalar() or 0
            
            # Par type de paiement
            par_type = {}
            for type_ in ['CHEQUE', 'VIREMENT', 'MOBILE_MONEY']:
                count = query.filter(LometaReglement.type_paiement == type_).count()
                if count > 0:
                    par_type[type_] = count
            
            return {
                'total': total,
                'par_statut': par_statut,
                'montant_total': montant_total,
                'par_type_paiement': par_type
            }
        except Exception as e:
            self.session.rollback()
            raise e

    # Ajouter ces méthodes à la fin de la classe ReglementService

    def get_lot_by_numero(self, numero: str) -> Optional['LometaLotPaiement']:
        """Récupère un lot par son numéro"""
        try:
            return self.session.query(LometaLotPaiement).filter(
                LometaLotPaiement.numero_lot == numero,
                LometaLotPaiement.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_lots_by_statut(self, statut: str) -> List['LometaLotPaiement']:
        """Récupère les lots par statut"""
        try:
            return self.session.query(LometaLotPaiement).filter(
                LometaLotPaiement.statut == statut,
                LometaLotPaiement.is_active == True
            ).order_by(LometaLotPaiement.date_creation.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def traiter_lot_paiement(self, lot_id: int, utilisateur_id: int) -> Optional['LometaLotPaiement']:
        """Traite un lot de paiement (passage en TRAITE)"""
        try:
            lot = self.get_lot_paiement(lot_id)
            if not lot:
                raise ValueError("Lot non trouvé")
            
            if lot.statut != "VALIDE":
                raise ValueError("Seul un lot validé peut être traité")
            
            lot.statut = "TRAITE"
            lot.date_traitement = datetime.utcnow()
            lot.updated_at = datetime.utcnow()
            lot.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="TRAITEMENT",
                entite="LometaLotPaiement",
                entite_id=lot.id,
                entite_nom=lot.numero_lot,
                commentaire=f"Traitement du lot {lot.numero_lot}"
            )
            
            self.session.commit()
            return lot
            
        except Exception as e:
            self.session.rollback()
            raise e

    def comptabiliser_lot_paiement(self, lot_id: int, utilisateur_id: int) -> Optional['LometaLotPaiement']:
        """Comptabilise un lot de paiement"""
        try:
            lot = self.get_lot_paiement(lot_id)
            if not lot:
                raise ValueError("Lot non trouvé")
            
            if lot.statut != "TRAITE":
                raise ValueError("Seul un lot traité peut être comptabilisé")
            
            lot.statut = "COMPTABILISE"
            lot.date_comptabilisation = datetime.utcnow()
            lot.updated_at = datetime.utcnow()
            lot.updated_by = utilisateur_id
            
            # Marquer tous les règlements du lot comme comptabilisés
            for reg in lot.reglements:
                reg.est_comptabilise = True
                reg.date_comptabilisation = datetime.utcnow()
                reg.updated_at = datetime.utcnow()
                reg.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="COMPTABILISATION",
                entite="LometaLotPaiement",
                entite_id=lot.id,
                entite_nom=lot.numero_lot,
                commentaire=f"Comptabilisation du lot {lot.numero_lot}"
            )
            
            self.session.commit()
            return lot
            
        except Exception as e:
            self.session.rollback()
            raise e