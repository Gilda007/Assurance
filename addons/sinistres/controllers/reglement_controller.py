"""
Contrôleur des règlements - Interface entre l'UI et ReglementService
"""
from PySide6.QtCore import Signal
from typing import Optional, List, Dict, Any

from addons.sinistres.controllers.controleur_base import BaseController
from addons.sinistres.services.reglement_service import ReglementService


class ReglementController(BaseController):
    """Contrôleur pour la gestion des règlements"""
    
    # Signaux spécifiques
    reglement_created = Signal(dict)
    reglement_updated = Signal(dict)
    reglement_validated = Signal(int)
    reglement_paid = Signal(int)
    reglement_list_updated = Signal(list)
    lot_created = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.service = ReglementService()
    
    # ============================================================
    # GESTION DES BÉNÉFICIAIRES
    # ============================================================
    
    def creer_beneficiaire(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée un nouveau bénéficiaire"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            beneficiaire = self.service.creer_beneficiaire(data)
            
            return {
                'id': beneficiaire.id,
                'type_beneficiaire': beneficiaire.type_beneficiaire,
                'nom': beneficiaire.nom,
                'prenom': beneficiaire.prenom,
                'iban': beneficiaire.iban
            }
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_beneficiaires(self, type_beneficiaire: str = None) -> List[dict]:
        """Récupère tous les bénéficiaires"""
        try:
            beneficiaires = self.service.get_beneficiaires(type_beneficiaire)
            return [
                {
                    'id': b.id,
                    'type_beneficiaire': b.type_beneficiaire,
                    'nom': b.nom,
                    'prenom': b.prenom,
                    'iban': b.iban,
                    'est_actif': b.est_actif
                }
                for b in beneficiaires
            ]
        except Exception as e:
            self.handle_error(e)
            return []
    
    # ============================================================
    # GESTION DES RÈGLEMENTS
    # ============================================================
    
    def creer_reglement(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée une demande de règlement"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            reglement = self.service.creer_reglement(data)
            result = self._serialize_reglement(reglement)
            
            self.reglement_created.emit(result)
            self.handle_success(f"Règlement {reglement.numero_reglement} créé avec succès")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_reglement(self, reglement_id: int) -> Optional[dict]:
        """Récupère un règlement par son ID"""
        try:
            reglement = self.service.get_reglement(reglement_id)
            if reglement:
                return self._serialize_reglement(reglement)
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_reglements_by_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère tous les règlements d'un sinistre"""
        try:
            reglements = self.service.get_reglements_by_sinistre(sinistre_id)
            result = [self._serialize_reglement(r) for r in reglements]
            self.reglement_list_updated.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_reglements_en_attente(self) -> List[dict]:
        """Récupère tous les règlements en attente de validation"""
        try:
            reglements = self.service.get_reglements_en_attente()
            return [self._serialize_reglement(r) for r in reglements]
        except Exception as e:
            self.handle_error(e)
            return []
    
    def valider_reglement(self, reglement_id: int) -> bool:
        """Valide un règlement"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            reglement = self.service.valider_reglement(
                reglement_id=reglement_id,
                utilisateur_id=self.get_current_user_id()
            )
            
            if reglement:
                self.reglement_validated.emit(reglement_id)
                self.handle_success("Règlement validé")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def payer_reglement(self, reglement_id: int, data: Dict[str, Any]) -> bool:
        """Exécute le paiement d'un règlement"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            reglement = self.service.payer_reglement(
                reglement_id=reglement_id,
                utilisateur_id=self.get_current_user_id(),
                data=data
            )
            
            if reglement:
                self.reglement_paid.emit(reglement_id)
                self.handle_success("Paiement effectué avec succès")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def annuler_reglement(self, reglement_id: int, motif: str) -> bool:
        """Annule un règlement"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            reglement = self.service.annuler_reglement(
                reglement_id=reglement_id,
                utilisateur_id=self.get_current_user_id(),
                motif=motif
            )
            
            if reglement:
                self.reglement_updated.emit(self._serialize_reglement(reglement))
                self.handle_success("Règlement annulé")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    # ============================================================
    # GESTION DES LOTS DE PAIEMENT
    # ============================================================
    
    def creer_lot_paiement(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée un lot de paiement"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            data['created_by'] = self.get_current_user_id()
            lot = self.service.creer_lot_paiement(data)
            result = {
                'id': lot.id,
                'numero_lot': lot.numero_lot,
                'date_creation': lot.date_creation.isoformat() if lot.date_creation else None,
                'nombre_paiements': lot.nombre_paiements,
                'montant_total': lot.montant_total,
                'statut': lot.statut
            }
            
            self.lot_created.emit(result)
            self.handle_success(f"Lot {lot.numero_lot} créé avec succès")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return None
    
    def ajouter_reglement_au_lot(self, reglement_id: int, lot_id: int) -> bool:
        """Ajoute un règlement à un lot"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            result = self.service.ajouter_reglement_au_lot(
                reglement_id=reglement_id,
                lot_id=lot_id,
                utilisateur_id=self.get_current_user_id()
            )
            
            if result:
                self.handle_success("Règlement ajouté au lot")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def valider_lot_paiement(self, lot_id: int) -> bool:
        """Valide un lot de paiement"""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            lot = self.service.valider_lot_paiement(
                lot_id=lot_id,
                utilisateur_id=self.get_current_user_id()
            )
            
            if lot:
                self.handle_success(f"Lot {lot.numero_lot} validé")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def get_statistiques(self, sinistre_id: int = None) -> Dict[str, Any]:
        """Récupère les statistiques des règlements"""
        try:
            return self.service.get_statistiques(sinistre_id)
        except Exception as e:
            self.handle_error(e)
            return {}
    
    # ============================================================
    # MÉTHODE PRIVÉE
    # ============================================================
    
    def _serialize_reglement(self, reglement) -> dict:
        """Sérialise un règlement en dictionnaire"""
        # Récupérer le nom du bénéficiaire
        beneficiaire_nom = reglement.beneficiaire_nom
        if reglement.beneficiaire_id and not beneficiaire_nom:
            beneficiaire = self.service.get_beneficiaire(reglement.beneficiaire_id)
            if beneficiaire:
                beneficiaire_nom = f"{beneficiaire.nom} {beneficiaire.prenom or ''}".strip()
        
        return {
            'id': reglement.id,
            'numero_reglement': reglement.numero_reglement,
            'sinistre_id': reglement.sinistre_id,
            'beneficiaire_id': reglement.beneficiaire_id,
            'beneficiaire_nom': beneficiaire_nom or reglement.beneficiaire_nom,
            'montant': reglement.montant,
            'type_paiement': reglement.type_paiement,
            'date_demande': reglement.date_demande.isoformat() if reglement.date_demande else None,
            'date_validation': reglement.date_validation.isoformat() if reglement.date_validation else None,
            'date_paiement': reglement.date_paiement.isoformat() if reglement.date_paiement else None,
            'statut': reglement.statut,
            'numero_cheque': reglement.numero_cheque,
            'reference_virement': reglement.reference_virement,
            'reference_mobile': reglement.reference_mobile,
            'est_comptabilise': reglement.est_comptabilise,
            'observations': reglement.observations,
            'created_at': reglement.created_at.isoformat() if reglement.created_at else None,
            'created_by': reglement.created_by,
            'is_active': reglement.is_active
        }
    
    def get_sinistres_recents(self, limit: int = 50) -> List[dict]:
        """Récupère les sinistres récents (délégation)"""
        try:
            from addons.sinistres.controllers.sinistre_controller import SinistreController
            sc = SinistreController()
            sc.set_current_user(self.get_current_user())
            return sc.get_sinistres_recents(limit)
        except Exception as e:
            self.handle_error(e)
            return []

    def get_lots_by_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère les lots de paiement d'un sinistre"""
        try:
            # Récupérer les règlements du sinistre
            reglements = self.service.get_reglements_by_sinistre(sinistre_id)
            # Extraire les lots uniques
            lots_ids = set()
            for reg in reglements:
                if reg.lot_paiement_id:
                    lots_ids.add(reg.lot_paiement_id)
            
            lots = []
            for lot_id in lots_ids:
                lot = self.service.get_lot_paiement(lot_id)
                if lot:
                    lots.append({
                        'id': lot.id,
                        'numero_lot': lot.numero_lot,
                        'date_creation': lot.date_creation.isoformat() if lot.date_creation else None,
                        'nombre_paiements': lot.nombre_paiements,
                        'montant_total': lot.montant_total,
                        'statut': lot.statut,
                        'type_lot': lot.type_lot
                    })
            return lots
        except Exception as e:
            self.handle_error(e)
            return []

    def get_reglement_by_numero(self, numero: str) -> Optional[dict]:
        """Récupère un règlement par son numéro"""
        try:
            reglement = self.service.get_reglement_by_numero(numero)
            if reglement:
                return self._serialize_reglement(reglement)
            return None
        except Exception as e:
            self.handle_error(e)
            return None

    def get_beneficiaires_by_type(self, type_beneficiaire: str) -> List[dict]:
        """Récupère les bénéficiaires par type"""
        try:
            beneficiaires = self.service.get_beneficiaires(type_beneficiaire)
            return [
                {
                    'id': b.id,
                    'type_beneficiaire': b.type_beneficiaire,
                    'nom': b.nom,
                    'prenom': b.prenom,
                    'iban': b.iban,
                    'est_actif': b.est_actif
                }
                for b in beneficiaires
            ]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_all_lots(self) -> List[dict]:
        """Récupère tous les lots de paiement"""
        try:
            lots = self.service.get_all_lots()
            return [
                {
                    'id': l.id,
                    'numero_lot': l.numero_lot,
                    'date_creation': l.date_creation.isoformat() if l.date_creation else None,
                    'nombre_paiements': l.nombre_paiements,
                    'montant_total': l.montant_total,
                    'statut': l.statut,
                    'type_lot': l.type_lot
                }
                for l in lots
            ]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_lots_by_statut(self, statut: str) -> List[dict]:
        """Récupère les lots par statut"""
        try:
            lots = self.service.get_lots_by_statut(statut)
            return [
                {
                    'id': l.id,
                    'numero_lot': l.numero_lot,
                    'date_creation': l.date_creation.isoformat() if l.date_creation else None,
                    'nombre_paiements': l.nombre_paiements,
                    'montant_total': l.montant_total,
                    'statut': l.statut,
                    'type_lot': l.type_lot
                }
                for l in lots
            ]
        except Exception as e:
            self.handle_error(e)
            return []

    def get_lot(self, lot_id: int) -> Optional[dict]:
        """Récupère un lot par son ID"""
        try:
            lot = self.service.get_lot_paiement(lot_id)
            if lot:
                return {
                    'id': lot.id,
                    'numero_lot': lot.numero_lot,
                    'date_creation': lot.date_creation.isoformat() if lot.date_creation else None,
                    'nombre_paiements': lot.nombre_paiements,
                    'montant_total': lot.montant_total,
                    'statut': lot.statut,
                    'type_lot': lot.type_lot,
                    'reglements': [
                        {
                            'numero_reglement': r.numero_reglement,
                            'beneficiaire_nom': r.beneficiaire_nom,
                            'montant': r.montant,
                            'statut': r.statut
                        }
                        for r in lot.reglements
                    ]
                }
            return None
        except Exception as e:
            self.handle_error(e)
            return None