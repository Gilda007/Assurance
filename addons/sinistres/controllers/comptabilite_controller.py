"""
Contrôleur de comptabilité - Version complète
Couvre le CDC Tome 5 (Règlements, Comptabilité) et Tome 7 (§6 États, §8 Exports)
"""
from PySide6.QtCore import Signal
from typing import Optional, List, Dict, Any
from datetime import datetime

from addons.sinistres.controllers.controleur_base import BaseController
from addons.sinistres.services.comptabilite_service import ComptabiliteService


class ComptabiliteController(BaseController):
    """
    Contrôleur pour la comptabilité.
    
    Expose :
    - 8 méthodes de création d'écriture (Tome 5 §11)
    - 5 méthodes de consultation (Tome 7 §6)
    - 2 méthodes de rapprochement bancaire (Tome 5 §14)
    - 1 méthode d'annulation (NC-001)
    - 1 méthode d'export (Tome 7 §8)
    - 1 méthode de statistiques (Tome 7 §6)
    """
    
    # ============================================================
    # SIGNAUX
    # ============================================================
    
    ecritures_loaded = Signal(list)
    ecriture_created = Signal(dict)
    ecriture_validated = Signal(int)
    ecriture_cancelled = Signal(int)
    ecriture_reconciled = Signal(int)
    balance_loaded = Signal(list)
    grand_livre_loaded = Signal(dict)
    stats_loaded = Signal(dict)
    export_completed = Signal(dict)
    
    # ============================================================
    # INITIALISATION
    # ============================================================
    
    def __init__(self):
        super().__init__()
        self.service = ComptabiliteService()
    
    # ============================================================
    # CRÉATION D'ÉCRITURES (Tome 5 §11)
    # ============================================================
    
    def creer_ecriture_generique(
        self,
        journal: str,
        libelle: str,
        compte_debit: str,
        compte_credit: str,
        montant: float,
        reference_type: str,
        reference_id: int = None,
        reference_numero: str = None,
        sinistre_id: int = None,
        recours_id: int = None,
        reglement_id: int = None,
        provision_id: int = None,
        note_credit_id: int = None,
        observations: str = None,
    ) -> Optional[dict]:
        """
        Crée une écriture comptable générique (partie double).
        
        Args:
            journal: BANQUE, SINISTRES, RECOURS, REGULARISATIONS
            libelle: Libellé de l'écriture
            compte_debit: Numéro de compte à débiter
            compte_credit: Numéro de compte à créditer
            montant: Montant (strictement positif)
            reference_type: REGLEMENT, PROVISION, ENCAISSEMENT_RECOURS, etc.
        
        Returns:
            Dict sérialisé ou None
        """
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            ecriture = self.service.creer_ecriture(
                journal=journal,
                libelle=libelle,
                compte_debit=compte_debit,
                compte_credit=compte_credit,
                montant=montant,
                reference_type=reference_type,
                reference_id=reference_id,
                reference_numero=reference_numero,
                sinistre_id=sinistre_id,
                recours_id=recours_id,
                reglement_id=reglement_id,
                provision_id=provision_id,
                note_credit_id=note_credit_id,
                observations=observations,
                utilisateur_id=self.get_current_user_id(),
            )
            
            if ecriture:
                result = self._serialize(ecriture)
                self.ecriture_created.emit(result)
                self.handle_success(f"Écriture {ecriture.numero_ecriture} créée")
                return result
            return None
        
        except Exception as e:
            self.handle_error(e)
            return None
    
    def creer_ecriture_paiement_sinistre(
        self,
        reglement_id: int,
        numero_reglement: str,
        montant: float,
        sinistre_id: int,
        branche: str = None,
    ) -> Optional[dict]:
        """
        Crée l'écriture de paiement d'un sinistre.
        
        Écriture :
            Débit  Charge Sinistre
            Crédit Banque
        """
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            ecriture = self.service.ecriture_paiement_sinistre(
                reglement_id=reglement_id,
                numero_reglement=numero_reglement,
                montant=montant,
                sinistre_id=sinistre_id,
                utilisateur_id=self.get_current_user_id(),
                branche=branche,
            )
            
            if ecriture:
                result = self._serialize(ecriture)
                self.ecriture_created.emit(result)
                self.handle_success(f"Écriture paiement {ecriture.numero_ecriture} créée")
                return result
            return None
        
        except Exception as e:
            self.handle_error(e)
            return None
    
    def creer_ecriture_encaissement(
        self,
        encaissement_id: int,
        numero_recours: str,
        montant: float,
        recours_id: int,
        sinistre_id: int,
        branche: str = None,
    ) -> Optional[dict]:
        """
        Crée l'écriture d'encaissement d'un recours.
        
        Écriture :
            Débit  Banque
            Crédit Compte Recours
        """
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            ecriture = self.service.ecriture_encaissement_recours(
                encaissement_id=encaissement_id,
                numero_recours=numero_recours,
                montant=montant,
                recours_id=recours_id,
                sinistre_id=sinistre_id,
                utilisateur_id=self.get_current_user_id(),
                branche=branche,
            )
            
            if ecriture:
                result = self._serialize(ecriture)
                self.ecriture_created.emit(result)
                self.handle_success(f"Écriture encaissement {ecriture.numero_ecriture} créée")
                return result
            return None
        
        except Exception as e:
            self.handle_error(e)
            return None
    
    def creer_ecriture_reversement(
        self,
        reversement_id: int,
        numero_recours: str,
        montant: float,
        recours_id: int,
        sinistre_id: int,
        branche: str = None,
    ) -> Optional[dict]:
        """
        Crée l'écriture de reversement client.
        
        Écriture :
            Débit  Compte Recours Client
            Crédit Banque
        """
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            ecriture = self.service.ecriture_reversement_client(
                reversement_id=reversement_id,
                numero_recours=numero_recours,
                montant=montant,
                recours_id=recours_id,
                sinistre_id=sinistre_id,
                utilisateur_id=self.get_current_user_id(),
                branche=branche,
            )
            
            if ecriture:
                result = self._serialize(ecriture)
                self.ecriture_created.emit(result)
                self.handle_success(f"Écriture reversement {ecriture.numero_ecriture} créée")
                return result
            return None
        
        except Exception as e:
            self.handle_error(e)
            return None
    
    def creer_ecriture_honoraires(
        self,
        repartition_id: int,
        numero_recours: str,
        montant: float,
        recours_id: int,
        sinistre_id: int,
    ) -> Optional[dict]:
        """
        Crée l'écriture des honoraires.
        
        Écriture :
            Débit  Compte Recours
            Crédit Produits Honoraires
        """
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            ecriture = self.service.ecriture_honoraires(
                repartition_id=repartition_id,
                numero_recours=numero_recours,
                montant=montant,
                recours_id=recours_id,
                sinistre_id=sinistre_id,
                utilisateur_id=self.get_current_user_id(),
            )
            
            if ecriture:
                result = self._serialize(ecriture)
                self.ecriture_created.emit(result)
                self.handle_success(f"Écriture honoraires {ecriture.numero_ecriture} créée")
                return result
            return None
        
        except Exception as e:
            self.handle_error(e)
            return None
    
    def creer_ecriture_provision(
        self,
        provision_id: int,
        numero_provision: str,
        montant: float,
        sinistre_id: int,
        type_provision: str = "INITIALE",
    ) -> Optional[dict]:
        """
        Crée l'écriture d'une provision (Tome 4 §6).
        
        Écriture :
            Débit  Charge Provision
            Crédit Compte Provision
        """
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            ecriture = self.service.ecriture_provision(
                provision_id=provision_id,
                numero_provision=numero_provision,
                montant=montant,
                sinistre_id=sinistre_id,
                utilisateur_id=self.get_current_user_id(),
                type_provision=type_provision,
            )
            
            if ecriture:
                result = self._serialize(ecriture)
                self.ecriture_created.emit(result)
                self.handle_success(f"Écriture provision {ecriture.numero_ecriture} créée")
                return result
            return None
        
        except Exception as e:
            self.handle_error(e)
            return None
    
    def creer_ecriture_reprise_provision(
        self,
        provision_id: int,
        numero_provision: str,
        montant: float,
        sinistre_id: int,
        motif: str = None,
    ) -> Optional[dict]:
        """
        Crée l'écriture de reprise de provision (Tome 4 §6.5).
        
        Écriture (inverse) :
            Débit  Compte Provision
            Crédit Charge Provision
        """
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            ecriture = self.service.ecriture_reprise_provision(
                provision_id=provision_id,
                numero_provision=numero_provision,
                montant=montant,
                sinistre_id=sinistre_id,
                utilisateur_id=self.get_current_user_id(),
                motif=motif,
            )
            
            if ecriture:
                result = self._serialize(ecriture)
                self.ecriture_created.emit(result)
                self.handle_success(f"Reprise provision {ecriture.numero_ecriture} créée")
                return result
            return None
        
        except Exception as e:
            self.handle_error(e)
            return None
    
    def creer_ecriture_note_credit(
        self,
        note_credit_id: int,
        numero_note: str,
        montant: float,
        reglement_origine_id: int,
        sinistre_id: int,
        motif: str = None,
    ) -> Optional[dict]:
        """
        Crée l'écriture d'une note de crédit (Tome 5 §10).
        
        Écriture (inverse du paiement) :
            Débit  Banque
            Crédit Charge Sinistre
        """
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return None
            
            ecriture = self.service.ecriture_note_credit(
                note_credit_id=note_credit_id,
                numero_note=numero_note,
                montant=montant,
                reglement_origine_id=reglement_origine_id,
                sinistre_id=sinistre_id,
                utilisateur_id=self.get_current_user_id(),
                motif=motif,
            )
            
            if ecriture:
                result = self._serialize(ecriture)
                self.ecriture_created.emit(result)
                self.handle_success(f"Note de crédit {ecriture.numero_ecriture} créée")
                return result
            return None
        
        except Exception as e:
            self.handle_error(e)
            return None
    
    # ============================================================
    # CONSULTATION (Tome 7 §6)
    # ============================================================
    
    def get_ecriture(self, ecriture_id: int) -> Optional[dict]:
        """Récupère une écriture par son ID."""
        try:
            ecriture = self.service.get_ecriture(ecriture_id)
            if ecriture:
                return self._serialize(ecriture)
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_ecritures_by_recours(self, recours_id: int) -> List[dict]:
        """Récupère les écritures liées à un recours."""
        try:
            ecritures = self.service.get_ecritures_by_recours(recours_id)
            result = [self._serialize(e) for e in ecritures]
            self.ecritures_loaded.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_ecritures_by_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère toutes les écritures d'un sinistre."""
        try:
            ecritures = self.service.get_ecritures_by_sinistre(sinistre_id)
            result = [self._serialize(e) for e in ecritures]
            self.ecritures_loaded.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_ecritures_by_journal(
        self,
        journal: str,
        date_debut: datetime = None,
        date_fin: datetime = None,
    ) -> List[dict]:
        """Récupère les écritures d'un journal avec filtre date."""
        try:
            ecritures = self.service.get_ecritures_by_journal(
                journal, date_debut, date_fin
            )
            result = [self._serialize(e) for e in ecritures]
            self.ecritures_loaded.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_grand_livre(
        self,
        compte: str,
        date_debut: datetime = None,
        date_fin: datetime = None,
    ) -> Optional[dict]:
        """
        Récupère le grand livre d'un compte (Tome 7 §6).
        
        Returns:
            {
                'compte': '616000',
                'total_debit': ...,
                'total_credit': ...,
                'solde_final': ...,
                'mouvements': [...]
            }
        """
        try:
            result = self.service.get_grand_livre(compte, date_debut, date_fin)
            self.grand_livre_loaded.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_balance(
        self,
        date_debut: datetime = None,
        date_fin: datetime = None,
    ) -> List[dict]:
        """
        Récupère la balance comptable (Tome 7 §6).
        
        Returns:
            Liste de dicts :
            [{'compte': ..., 'total_debit': ..., 'total_credit': ..., 'solde': ...}, ...]
        """
        try:
            balance = self.service.get_balance(date_debut, date_fin)
            self.balance_loaded.emit(balance)
            return balance
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_statistiques(
        self,
        date_debut: datetime = None,
        date_fin: datetime = None,
    ) -> dict:
        """
        Récupère les statistiques comptables (Tome 7 §6).
        
        Returns:
            {
                'total_ecritures': int,
                'par_journal': {...},
                'montant_total': float,
                'non_rapprochees': int
            }
        """
        try:
            stats = self.service.get_statistiques(date_debut, date_fin)
            self.stats_loaded.emit(stats)
            return stats
        except Exception as e:
            self.handle_error(e)
            return {}
    
    # ============================================================
    # RAPPROCHEMENT BANCAIRE (Tome 5 §14)
    # ============================================================
    
    def get_ecritures_non_rapprochees(self, journal: str = None) -> List[dict]:
        """Récupère les écritures non rapprochées."""
        try:
            ecritures = self.service.get_ecritures_non_rapprochees(journal)
            return [self._serialize(e) for e in ecritures]
        except Exception as e:
            self.handle_error(e)
            return []
    
    def rapprocher_ecriture(
        self,
        ecriture_id: int,
        reference_bancaire: str,
    ) -> bool:
        """
        Marque une écriture comme rapprochée (Tome 5 §14).
        
        Args:
            ecriture_id: ID de l'écriture
            reference_bancaire: Référence du relevé bancaire
        """
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            if not reference_bancaire or not reference_bancaire.strip():
                self.error_occurred.emit("La référence bancaire est obligatoire")
                return False
            
            ecriture = self.service.rapprocher_ecriture(
                ecriture_id=ecriture_id,
                reference_bancaire=reference_bancaire,
                utilisateur_id=self.get_current_user_id(),
            )
            
            if ecriture:
                self.ecriture_reconciled.emit(ecriture_id)
                self.handle_success(
                    f"Écriture {ecriture.numero_ecriture} rapprochée "
                    f"(Réf: {reference_bancaire})"
                )
                return True
            return False
        except Exception as e:
            self.handle_error(e)
            return False
    
    # ============================================================
    # RÉGULARISATION
    # ============================================================
    
    def annuler_ecriture(self, ecriture_id: int, motif: str) -> bool:
        """
        Annule une écriture avec contrepassation.
        
        Règles CDC :
        - NC-001 : Justification obligatoire
        - NC-002 : Toute note de crédit doit être auditée
        """
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            if not motif or not motif.strip():
                self.error_occurred.emit(
                    "Un motif est obligatoire pour annuler une écriture (NC-001)"
                )
                return False
            
            ecriture = self.service.annuler_ecriture(
                ecriture_id=ecriture_id,
                motif=motif,
                utilisateur_id=self.get_current_user_id(),
            )
            
            if ecriture:
                self.ecriture_cancelled.emit(ecriture_id)
                self.handle_success(
                    f"Écriture {ecriture.numero_ecriture} annulée "
                    f"(contrepassation créée)"
                )
                return True
            return False
        except Exception as e:
            self.handle_error(e)
            return False
    
    def valider_ecriture(self, ecriture_id: int) -> bool:
        """Valide une écriture."""
        try:
            if not self.get_current_user_id():
                self.error_occurred.emit("Aucun utilisateur connecté")
                return False
            
            ecriture = self.service.valider_ecriture(
                ecriture_id=ecriture_id,
                utilisateur_id=self.get_current_user_id(),
            )
            
            if ecriture:
                self.ecriture_validated.emit(ecriture_id)
                self.handle_success(f"Écriture {ecriture.numero_ecriture} validée")
                return True
            return False
        except Exception as e:
            self.handle_error(e)
            return False
    
    # ============================================================
    # EXPORT (Tome 7 §8)
    # ============================================================
    
    def export_etats_comptables(
        self,
        date_debut: datetime,
        date_fin: datetime,
        output_dir: str = "exports/comptabilite",
    ) -> Optional[dict]:
        """
        Exporte les états comptables en CSV.
        
        Génère :
        - balance.csv
        - journal_banque.csv
        - journal_sinistres.csv
        - journal_recours.csv
        
        Returns:
            {'balance': chemin, 'journal_banque': chemin, ...} ou None
        """
        try:
            result = self.service.export_etats_comptables(
                date_debut=date_debut,
                date_fin=date_fin,
                output_dir=output_dir,
            )
            
            if result:
                self.export_completed.emit(result)
                self.handle_success(f"{len(result)} fichier(s) exporté(s)")
                return result
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    # ============================================================
    # SÉRIALISATION
    # ============================================================
    
    def _serialize(self, e) -> dict:
        """
        Sérialise une écriture comptable.
        
        Notes :
        - Utilise `getattr` pour les champs optionnels (compatibilité ascendante)
        - Ne référence que les champs existants dans LometaEcritureComptable
        """
        return {
            'id': e.id,
            'numero_ecriture': e.numero_ecriture,
            'date_ecriture': (
                e.date_ecriture.isoformat() if e.date_ecriture else None
            ),
            'date_comptabilisation': (
                e.date_comptabilisation.isoformat()
                if getattr(e, 'date_comptabilisation', None) else None
            ),
            'journal': e.journal,
            'libelle': e.libelle,
            'compte_debit': e.compte_debit,
            'compte_credit': e.compte_credit,
            'montant': e.montant,
            'devise': e.devise,
            'reference_type': e.reference_type,
            'reference_id': e.reference_id,
            'reference_numero': e.reference_numero,
            'sinistre_id': e.sinistre_id,
            'recours_id': getattr(e, 'recours_id', None),
            'reglement_id': getattr(e, 'reglement_id', None),
            'provision_id': getattr(e, 'provision_id', None),
            'note_credit_id': getattr(e, 'note_credit_id', None),
            'est_valide': e.est_valide,
            'est_annulee': e.est_annulee,
            'est_rapprochee': getattr(e, 'est_rapprochee', False),
            'date_rapprochement': (
                e.date_rapprochement.isoformat()
                if getattr(e, 'date_rapprochement', None) else None
            ),
            'reference_bancaire': getattr(e, 'reference_bancaire', None),
            'motif_annulation': getattr(e, 'motif_annulation', None),
            'ecriture_contrepartie_id': getattr(e, 'ecriture_contrepartie_id', None),
            'observations': e.observations,
            'created_at': (
                e.created_at.isoformat() if e.created_at else None
            ),
            'created_by': e.created_by,
            'updated_at': (
                e.updated_at.isoformat()
                if getattr(e, 'updated_at', None) else None
            ),
            'updated_by': getattr(e, 'updated_by', None),
            'is_active': getattr(e, 'is_active', True),
        }