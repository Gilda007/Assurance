# """
# Service de comptabilisation automatique.
# Génère les écritures comptables selon le CDC Tome 5 §11-12.
# """
# from sqlalchemy.orm import Session
# from datetime import datetime
# from typing import Optional, List, Dict, Any

# from addons.sinistres.services.base_service import BaseService
# from addons.sinistres.models.comptabilite import LometaEcritureComptable
# from addons.sinistres.services.parametre_service import ParametreService


# class ComptabiliteService(BaseService):
#     """Service de comptabilisation automatique"""
    
#     def __init__(self, session: Session = None):
#         super().__init__(session)
#         self.parametre_service = ParametreService(session)
    
#     # ============================================================
#     # GÉNÉRATION D'ÉCRITURES
#     # ============================================================
    
#     def generer_numero_ecriture(self) -> str:
#         """Génère un numéro d'écriture unique"""
#         return self.generate_numero(
#             "ECR",
#             LometaEcritureComptable,
#             'numero_ecriture'
#         )
    
#     def creer_ecriture(
#         self,
#         journal: str,
#         libelle: str,
#         compte_debit: str,
#         compte_credit: str,
#         montant: float,
#         reference_type: str,
#         reference_id: int = None,
#         reference_numero: str = None,
#         sinistre_id: int = None,
#         recours_id: int = None,
#         reglement_id: int = None,
#         utilisateur_id: int = None,
#         observations: str = None,
#     ) -> LometaEcritureComptable:
#         """
#         Crée une écriture comptable générique.
        
#         Args:
#             journal: BANQUE, SINISTRES, RECOURS, REGULARISATIONS
#             libelle: Libellé de l'écriture
#             compte_debit: Numéro de compte à débiter
#             compte_credit: Numéro de compte à créditer
#             montant: Montant (positif)
#             reference_type: REGLEMENT, ENCAISSEMENT_RECOURS, REVERSEMENT_CLIENT, HONORAIRES
#             reference_id: ID de l'objet référencé
#             ...
#         """
#         try:
#             if montant <= 0:
#                 raise ValueError("Le montant doit être positif")
            
#             numero = self.generer_numero_ecriture()
            
#             ecriture = LometaEcritureComptable(
#                 numero_ecriture=numero,
#                 date_ecriture=datetime.utcnow(),
#                 journal=journal,
#                 libelle=libelle,
#                 compte_debit=compte_debit,
#                 compte_credit=compte_credit,
#                 montant=montant,
#                 devise="XAF",
#                 reference_type=reference_type,
#                 reference_id=reference_id,
#                 reference_numero=reference_numero,
#                 sinistre_id=sinistre_id,
#                 recours_id=recours_id,
#                 reglement_id=reglement_id,
#                 observations=observations,
#                 is_active=True,
#                 created_by=utilisateur_id,
#             )
            
#             self.session.add(ecriture)
#             self.session.flush()
            
#             # Log d'audit
#             self.log_audit(
#                 utilisateur_id=utilisateur_id,
#                 action="CREATION",
#                 entite="EcritureComptable",
#                 entite_id=ecriture.id,
#                 entite_nom=ecriture.numero_ecriture,
#                 commentaire=f"Écriture {journal} : {libelle} ({montant:,.0f} FCFA)"
#             )
            
#             return ecriture
#         except Exception as e:
#             self.session.rollback()
#             raise e
    
#     # ============================================================
#     # ÉCRITURES SPÉCIFIQUES
#     # ============================================================
    
#     def ecriture_paiement_sinistre(
#         self,
#         reglement_id: int,
#         numero_reglement: str,
#         montant: float,
#         sinistre_id: int,
#         utilisateur_id: int,
#     ) -> LometaEcritureComptable:
#         """
#         Paiement Sinistre :
#         Débit  Charge Sinistre
#         Crédit Banque
#         """
#         compte_charge = self.parametre_service.get_compte_comptable('COMPTE_CHARGE_SINISTRE') or '616000'
#         compte_banque = self.parametre_service.get_compte_comptable('COMPTE_BANQUE') or '512000'
        
#         return self.creer_ecriture(
#             journal="SINISTRES",
#             libelle=f"Paiement sinistre - Règlement {numero_reglement}",
#             compte_debit=compte_charge,
#             compte_credit=compte_banque,
#             montant=montant,
#             reference_type="REGLEMENT",
#             reference_id=reglement_id,
#             reference_numero=numero_reglement,
#             sinistre_id=sinistre_id,
#             reglement_id=reglement_id,
#             utilisateur_id=utilisateur_id,
#         )
    
#     def ecriture_encaissement_recours(
#         self,
#         encaissement_id: int,
#         numero_recours: str,
#         montant: float,
#         recours_id: int,
#         sinistre_id: int,
#         utilisateur_id: int,
#     ) -> LometaEcritureComptable:
#         """
#         Encaissement Recours :
#         Débit  Banque
#         Crédit Compte Recours
#         """
#         compte_banque = self.parametre_service.get_compte_comptable('COMPTE_BANQUE') or '512000'
#         compte_recours = self.parametre_service.get_compte_comptable('COMPTE_RECOURS') or '758000'
        
#         return self.creer_ecriture(
#             journal="RECOURS",
#             libelle=f"Encaissement recours {numero_recours}",
#             compte_debit=compte_banque,
#             compte_credit=compte_recours,
#             montant=montant,
#             reference_type="ENCAISSEMENT_RECOURS",
#             reference_id=encaissement_id,
#             reference_numero=numero_recours,
#             sinistre_id=sinistre_id,
#             recours_id=recours_id,
#             utilisateur_id=utilisateur_id,
#         )
    
#     def ecriture_reversement_client(
#         self,
#         reversement_id: int,
#         numero_recours: str,
#         montant: float,
#         recours_id: int,
#         sinistre_id: int,
#         utilisateur_id: int,
#     ) -> LometaEcritureComptable:
#         """
#         Reversement Client :
#         Débit  Compte Recours Client
#         Crédit Banque
#         """
#         compte_recours_client = self.parametre_service.get_compte_comptable('COMPTE_RECOURS_CLIENT') or '419000'
#         compte_banque = self.parametre_service.get_compte_comptable('COMPTE_BANQUE') or '512000'
        
#         return self.creer_ecriture(
#             journal="RECOURS",
#             libelle=f"Reversement client - Recours {numero_recours}",
#             compte_debit=compte_recours_client,
#             compte_credit=compte_banque,
#             montant=montant,
#             reference_type="REVERSEMENT_CLIENT",
#             reference_id=reversement_id,
#             reference_numero=numero_recours,
#             sinistre_id=sinistre_id,
#             recours_id=recours_id,
#             utilisateur_id=utilisateur_id,
#         )
    
#     def ecriture_honoraires(
#         self,
#         repartition_id: int,
#         numero_recours: str,
#         montant: float,
#         recours_id: int,
#         sinistre_id: int,
#         utilisateur_id: int,
#     ) -> LometaEcritureComptable:
#         """
#         Honoraires :
#         Débit  Compte Recours
#         Crédit Produits Honoraires
#         """
#         compte_recours = self.parametre_service.get_compte_comptable('COMPTE_RECOURS') or '758000'
#         compte_produits = self.parametre_service.get_compte_comptable('COMPTE_PRODUITS_HONORAIRES') or '708000'
        
#         return self.creer_ecriture(
#             journal="RECOURS",
#             libelle=f"Honoraires - Recours {numero_recours}",
#             compte_debit=compte_recours,
#             compte_credit=compte_produits,
#             montant=montant,
#             reference_type="HONORAIRES",
#             reference_id=repartition_id,
#             reference_numero=numero_recours,
#             sinistre_id=sinistre_id,
#             recours_id=recours_id,
#             utilisateur_id=utilisateur_id,
#         )
    
#     # ============================================================
#     # CONSULTATION
#     # ============================================================
    
#     def get_ecritures_by_recours(self, recours_id: int) -> List[LometaEcritureComptable]:
#         """Récupère toutes les écritures liées à un recours"""
#         try:
#             return self.session.query(LometaEcritureComptable).filter(
#                 LometaEcritureComptable.recours_id == recours_id,
#                 LometaEcritureComptable.is_active == True,
#                 LometaEcritureComptable.est_annulee == False,
#             ).order_by(LometaEcritureComptable.date_ecriture).all()
#         except Exception as e:
#             self.session.rollback()
#             raise e
    
#     def get_ecritures_by_journal(
#         self,
#         journal: str,
#         date_debut: datetime = None,
#         date_fin: datetime = None,
#     ) -> List[LometaEcritureComptable]:
#         """Récupère les écritures d'un journal avec filtre date"""
#         try:
#             query = self.session.query(LometaEcritureComptable).filter(
#                 LometaEcritureComptable.journal == journal,
#                 LometaEcritureComptable.is_active == True,
#                 LometaEcritureComptable.est_annulee == False,
#             )
#             if date_debut:
#                 query = query.filter(LometaEcritureComptable.date_ecriture >= date_debut)
#             if date_fin:
#                 query = query.filter(LometaEcritureComptable.date_ecriture <= date_fin)
#             return query.order_by(LometaEcritureComptable.date_ecriture.desc()).all()
#         except Exception as e:
#             self.session.rollback()
#             raise e
    
#     def valider_ecriture(self, ecriture_id: int, utilisateur_id: int) -> Optional[LometaEcritureComptable]:
#         """Valide une écriture"""
#         try:
#             ecriture = self.session.query(LometaEcritureComptable).filter(
#                 LometaEcritureComptable.id == ecriture_id,
#                 LometaEcritureComptable.is_active == True
#             ).first()
            
#             if not ecriture:
#                 raise ValueError("Écriture non trouvée")
            
#             if ecriture.est_annulee:
#                 raise ValueError("Impossible de valider une écriture annulée")
            
#             ecriture.est_valide = True
#             ecriture.updated_at = datetime.utcnow()
#             ecriture.updated_by = utilisateur_id
            
#             self.session.commit()
#             return ecriture
#         except Exception as e:
#             self.session.rollback()
#             raise e






"""
Service de comptabilisation automatique.
Génère les écritures comptables selon le CDC Tome 5 §11-12.
"""
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import func, and_, or_

from addons.sinistres.models.referentiel import LometaReferentiel
from addons.sinistres.services.base_service import BaseService
from addons.sinistres.models.comptabilite import (
    LometaEcritureComptable
)
from addons.sinistres.services.parametre_service import ParametreService


class ComptabiliteService(BaseService):
    """Service de comptabilisation automatique"""
    
    # Journaux standards (Tome 5 §12)
    JOURNAL_BANQUE = "BANQUE"
    JOURNAL_SINISTRES = "SINISTRES"
    JOURNAL_RECOURS = "RECOURS"
    JOURNAL_REGULARISATIONS = "REGULARISATIONS"
    
    def __init__(self, session: Session = None):
        super().__init__(session)
        self.parametre_service = ParametreService(session)
    
    # ============================================================
    # GÉNÉRATION D'ÉCRITURES — GÉNÉRIQUE
    # ============================================================
    
    def generer_numero_ecriture(self) -> str:
        """Génère un numéro d'écriture unique"""
        return self.generate_numero("ECR", LometaEcritureComptable, 'numero_ecriture')
    
    # def _resoudre_schema_comptable(
    #     self,
    #     type_operation: str,
    #     branche: str = None,
    # ) -> Dict[str, str]:
    #         """
    #         Résout le schéma comptable depuis le référentiel (EXIG-REF-001).
            
    #         Le schéma est lu depuis `lometa_referentiels` famille='schemas_comptables'.
    #         Le champ `donnees_supplementaires` contient le JSON avec les comptes.
            
    #         Returns:
    #             {'journal': ..., 'compte_debit': ..., 'compte_credit': ...}
    #         """
    #         import json
            
    #         try:
    #             # Chercher un schéma spécifique à la branche
    #             query = self.session.query(LometaReferentiel).filter(
    #                 LometaReferentiel.famille == "schemas_comptables",
    #                 LometaReferentiel.est_actif == True,
    #                 LometaReferentiel.is_active == True,
    #             )
                
    #             # Filtrer par type d'opération (dans donnees_supplementaires)
    #             schemas = query.all()
                
    #             for schema in schemas:
    #                 try:
    #                     data = json.loads(schema.donnees_supplementaires or "{}")
    #                     if data.get("type_operation") != type_operation:
    #                         continue
                        
    #                     # Vérifier la branche si spécifiée
    #                     if branche and schema.branche and schema.branche != branche:
    #                         continue
                        
    #                     return {
    #                         'journal': data.get('journal', self.JOURNAL_SINISTRES),
    #                         'compte_debit': data.get('compte_debit', ''),
    #                         'compte_credit': data.get('compte_credit', ''),
    #                         'code_schema': schema.code,
    #                     }
    #                 except (json.JSONDecodeError, AttributeError):
    #                     continue
                
    #             # Fallback : paramètres
    #             return None
            
    #         except Exception:
    #             return None

    def _resoudre_schema_comptable(
        self,
        type_operation: str,
        branche: str = None,
    ) -> Optional[Dict[str, str]]:
        """
        Résout le schéma comptable depuis le référentiel (EXIG-REF-001).
        
        Le schéma est lu depuis `lometa_referentiels` famille='schemas_comptables'.
        Le champ `donnees_supplementaires` contient le JSON avec les comptes.
        
        Args:
            type_operation : PAIEMENT_SINISTRE, ENCAISSEMENT_RECOURS, etc.
            branche        : Filtre optionnel par branche
        
        Returns:
            {'journal': ..., 'compte_debit': ..., 'compte_credit': ..., 'code_schema': ...}
            ou None si aucun schéma n'est trouvé.
        """
        import json
        
        try:
            schemas = self.session.query(LometaReferentiel).filter(
                LometaReferentiel.famille == "schemas_comptables",
                LometaReferentiel.est_actif == True,
                LometaReferentiel.is_active == True,
            ).all()
            
            for schema in schemas:
                try:
                    data = json.loads(schema.donnees_supplementaires or "{}")
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"⚠️ Schéma {schema.code} : JSON invalide ({e})")
                    continue
                
                if data.get("type_operation") != type_operation:
                    continue
                
                if branche and schema.branche and schema.branche != branche:
                    continue
                
                return {
                    'journal': data.get('journal', self.JOURNAL_SINISTRES),
                    'compte_debit': data.get('compte_debit', ''),
                    'compte_credit': data.get('compte_credit', ''),
                    'code_schema': schema.code,
                }
            
            # Aucun schéma trouvé : pas une erreur, fallback sur les paramètres
            return None
        
        except Exception as e:
            # Erreur inattendue : logger sans avaler
            print(f"❌ Erreur _resoudre_schema_comptable : {e}")
            import traceback
            traceback.print_exc()
            return None

    def creer_ecriture(
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
        utilisateur_id: int = None,
        observations: str = None,
    ) -> LometaEcritureComptable:
        """
        Crée une écriture comptable générique (partie double).
        
        Vérifie l'équilibre débit/crédit et journalise automatiquement.
        """
        try:
            # Validation
            if montant <= 0:
                raise ValueError("Le montant doit être strictement positif")
            
            if journal not in (
                self.JOURNAL_BANQUE,
                self.JOURNAL_SINISTRES,
                self.JOURNAL_RECOURS,
                self.JOURNAL_REGULARISATIONS,
            ):
                raise ValueError(f"Journal invalide : {journal}")
            
            numero = self.generer_numero_ecriture()
            
            ecriture = LometaEcritureComptable(
                numero_ecriture=numero,
                date_ecriture=datetime.utcnow(),
                date_comptabilisation=datetime.utcnow(),
                journal=journal,
                libelle=libelle,
                compte_debit=compte_debit,
                compte_credit=compte_credit,
                montant=montant,
                devise="XAF",
                reference_type=reference_type,
                reference_id=reference_id,
                reference_numero=reference_numero,
                sinistre_id=sinistre_id,
                recours_id=recours_id,
                reglement_id=reglement_id,
                provision_id=provision_id,
                note_credit_id=note_credit_id,
                observations=observations,
                is_active=True,
                created_by=utilisateur_id,
            )
            
            self.session.add(ecriture)
            self.session.flush()
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="CREATION",
                entite="EcritureComptable",
                entite_id=ecriture.id,
                entite_nom=ecriture.numero_ecriture,
                commentaire=(
                    f"Écriture {journal} : {libelle} "
                    f"({montant:,.0f} FCFA) "
                    f"[Débit {compte_debit} / Crédit {compte_credit}]"
                ),
            )
            
            return ecriture
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # ÉCRITURES SPÉCIFIQUES (CDC Tome 5 §11)
    # ============================================================
    
    def ecriture_paiement_sinistre(
        self,
        reglement_id: int,
        numero_reglement: str,
        montant: float,
        sinistre_id: int,
        utilisateur_id: int,
        branche: str = None,
    ) -> LometaEcritureComptable:
        """Paiement Sinistre (Tome 5 §11.1)"""
        # 1. Essayer le référentiel (EXIG-REF-001)
        schema = self._resoudre_schema_comptable("PAIEMENT_SINISTRE", branche)
        
        if schema:
            journal = schema['journal']
            compte_debit = schema['compte_debit']
            compte_credit = schema['compte_credit']
        else:
            # 2. Fallback : paramètres
            journal = self.JOURNAL_SINISTRES
            compte_debit = self.parametre_service.get_compte_comptable(
                'COMPTE_CHARGE_SINISTRE'
            ) or '616000'
            compte_credit = self.parametre_service.get_compte_comptable(
                'COMPTE_BANQUE'
            ) or '512000'
        
        return self.creer_ecriture(
            journal=journal,
            libelle=f"Paiement sinistre - Règlement {numero_reglement}",
            compte_debit=compte_debit,
            compte_credit=compte_credit,
            montant=montant,
            reference_type="REGLEMENT",
            reference_id=reglement_id,
            reference_numero=numero_reglement,
            sinistre_id=sinistre_id,
            reglement_id=reglement_id,
            utilisateur_id=utilisateur_id,
        )

    def ecriture_encaissement_recours(
        self,
        encaissement_id: int,
        numero_recours: str,
        montant: float,
        recours_id: int,
        sinistre_id: int,
        utilisateur_id: int,
        branche: str = None,
    ) -> LometaEcritureComptable:
        """
        Encaissement Recours (Tome 6 §14) :
        Débit  Banque
        Crédit Compte Recours
        """
        schema = self._resoudre_schema_comptable("ENCAISSEMENT_RECOURS", branche)
        
        if schema:
            compte_banque = schema['compte_debit']
            compte_recours = schema['compte_credit']
        else:
            compte_banque = self.parametre_service.get_compte_comptable(
                'COMPTE_BANQUE'
            ) or '512000'
            compte_recours = self.parametre_service.get_compte_comptable(
                'COMPTE_RECOURS'
            ) or '758000'
        
        return self.creer_ecriture(
            journal=self.JOURNAL_RECOURS,
            libelle=f"Encaissement recours {numero_recours}",
            compte_debit=compte_banque,
            compte_credit=compte_recours,
            montant=montant,
            reference_type="ENCAISSEMENT_RECOURS",
            reference_id=encaissement_id,
            reference_numero=numero_recours,
            sinistre_id=sinistre_id,
            recours_id=recours_id,
            utilisateur_id=utilisateur_id,
        )
    
    def ecriture_reversement_client(
        self,
        reversement_id: int,
        numero_recours: str,
        montant: float,
        recours_id: int,
        sinistre_id: int,
        utilisateur_id: int,
        branche: str = None,
    ) -> LometaEcritureComptable:
        """
        Reversement Client (Tome 6 §14) :
        Débit  Compte Recours Client
        Crédit Banque
        """
        schema = self._resoudre_schema_comptable("REVERSEMENT_CLIENT", branche)
        
        if schema:
            compte_recours_client = schema['compte_debit']
            compte_banque = schema['compte_credit']
        else:
            compte_recours_client = self.parametre_service.get_compte_comptable(
                'COMPTE_RECOURS_CLIENT'
            ) or '419000'
            compte_banque = self.parametre_service.get_compte_comptable(
                'COMPTE_BANQUE'
            ) or '512000'
        
        return self.creer_ecriture(
            journal=self.JOURNAL_RECOURS,
            libelle=f"Reversement client - Recours {numero_recours}",
            compte_debit=compte_recours_client,
            compte_credit=compte_banque,
            montant=montant,
            reference_type="REVERSEMENT_CLIENT",
            reference_id=reversement_id,
            reference_numero=numero_recours,
            sinistre_id=sinistre_id,
            recours_id=recours_id,
            utilisateur_id=utilisateur_id,
        )
    
    def ecriture_honoraires(
        self,
        repartition_id: int,
        numero_recours: str,
        montant: float,
        recours_id: int,
        sinistre_id: int,
        utilisateur_id: int,
    ) -> LometaEcritureComptable:
        """
        Honoraires (Tome 6 §14) :
        Débit  Compte Recours
        Crédit Produits Honoraires
        """
        schema = self._resoudre_schema_comptable("HONORAIRES")
        
        if schema:
            compte_recours = schema['compte_debit']
            compte_produits = schema['compte_credit']
        else:
            compte_recours = self.parametre_service.get_compte_comptable(
                'COMPTE_RECOURS'
            ) or '758000'
            compte_produits = self.parametre_service.get_compte_comptable(
                'COMPTE_PRODUITS_HONORAIRES'
            ) or '708000'
        
        return self.creer_ecriture(
            journal=self.JOURNAL_RECOURS,
            libelle=f"Honoraires - Recours {numero_recours}",
            compte_debit=compte_recours,
            compte_credit=compte_produits,
            montant=montant,
            reference_type="HONORAIRES",
            reference_id=repartition_id,
            reference_numero=numero_recours,
            sinistre_id=sinistre_id,
            recours_id=recours_id,
            utilisateur_id=utilisateur_id,
        )
    
    # ============================================================
    # ✅ NOUVELLES ÉCRITURES : PROVISIONS (Tome 4)
    # ============================================================
    
    def ecriture_provision(
        self,
        provision_id: int,
        numero_provision: str,
        montant: float,
        sinistre_id: int,
        utilisateur_id: int,
        type_provision: str = "INITIALE",
    ) -> LometaEcritureComptable:
        """
        Comptabilisation d'une provision (Tome 4 §6).
        
        Écriture :
        Débit  Charge Provision (616xxx)
        Crédit Compte Provision (151xxx)
        
        PROV-001 : Toute évaluation doit générer une provision
        """
        schema = self._resoudre_schema_comptable(
            f"PROVISION_{type_provision}"
        ) or self._resoudre_schema_comptable("PROVISION_INITIALE")
        
        if schema:
            compte_debit = schema['compte_debit']
            compte_credit = schema['compte_credit']
        else:
            compte_debit = self.parametre_service.get_compte_comptable(
                'COMPTE_CHARGE_PROVISION'
            ) or '616100'
            compte_credit = self.parametre_service.get_compte_comptable(
                'COMPTE_PROVISION'
            ) or '151000'
        
        return self.creer_ecriture(
            journal=self.JOURNAL_SINISTRES,
            libelle=f"Provision {type_provision} - {numero_provision}",
            compte_debit=compte_debit,
            compte_credit=compte_credit,
            montant=montant,
            reference_type="PROVISION",
            reference_id=provision_id,
            reference_numero=numero_provision,
            sinistre_id=sinistre_id,
            provision_id=provision_id,
            utilisateur_id=utilisateur_id,
        )
    
    def ecriture_reprise_provision(
        self,
        provision_id: int,
        numero_provision: str,
        montant: float,
        sinistre_id: int,
        utilisateur_id: int,
        motif: str = None,
    ) -> LometaEcritureComptable:
        """
        Reprise de provision (Tome 4 §6.5).
        
        Écriture inverse :
        Débit  Compte Provision
        Crédit Charge Provision
        """
        compte_debit = self.parametre_service.get_compte_comptable(
            'COMPTE_PROVISION'
        ) or '151000'
        compte_credit = self.parametre_service.get_compte_comptable(
            'COMPTE_CHARGE_PROVISION'
        ) or '616100'
        
        return self.creer_ecriture(
            journal=self.JOURNAL_REGULARISATIONS,
            libelle=f"Reprise provision {numero_provision}" + (f" - {motif}" if motif else ""),
            compte_debit=compte_debit,
            compte_credit=compte_credit,
            montant=montant,
            reference_type="REPRISE_PROVISION",
            reference_id=provision_id,
            reference_numero=numero_provision,
            sinistre_id=sinistre_id,
            provision_id=provision_id,
            utilisateur_id=utilisateur_id,
        )
    
    # ============================================================
    # ✅ NOUVELLES ÉCRITURES : NOTES DE CRÉDIT (Tome 5 §10)
    # ============================================================
    
    def ecriture_note_credit(
        self,
        note_credit_id: int,
        numero_note: str,
        montant: float,
        reglement_origine_id: int,
        sinistre_id: int,
        utilisateur_id: int,
        motif: str = None,
    ) -> LometaEcritureComptable:
        """
        Note de crédit (Tome 5 §10) :
        Écriture inverse du paiement d'origine.
        
        Si le paiement d'origine était :
            Débit Charge / Crédit Banque
        La note de crédit est :
            Débit Banque / Crédit Charge
        """
        schema = self._resoudre_schema_comptable("NOTE_CREDIT")
        
        if schema:
            compte_debit = schema['compte_debit']
            compte_credit = schema['compte_credit']
        else:
            compte_debit = self.parametre_service.get_compte_comptable(
                'COMPTE_BANQUE'
            ) or '512000'
            compte_credit = self.parametre_service.get_compte_comptable(
                'COMPTE_CHARGE_SINISTRE'
            ) or '616000'
        
        return self.creer_ecriture(
            journal=self.JOURNAL_REGULARISATIONS,
            libelle=f"Note de crédit {numero_note}" + (f" - {motif}" if motif else ""),
            compte_debit=compte_debit,
            compte_credit=compte_credit,
            montant=montant,
            reference_type="NOTE_CREDIT",
            reference_id=note_credit_id,
            reference_numero=numero_note,
            sinistre_id=sinistre_id,
            reglement_id=reglement_origine_id,
            note_credit_id=note_credit_id,
            utilisateur_id=utilisateur_id,
        )
    
    # ============================================================
    # CONSULTATION
    # ============================================================
    
    def get_ecriture(self, ecriture_id: int) -> Optional[LometaEcritureComptable]:
        """Récupère une écriture par son ID"""
        try:
            return self.session.query(LometaEcritureComptable).filter(
                LometaEcritureComptable.id == ecriture_id,
                LometaEcritureComptable.is_active == True,
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_ecritures_by_recours(self, recours_id: int) -> List[LometaEcritureComptable]:
        """Récupère toutes les écritures liées à un recours"""
        try:
            return self.session.query(LometaEcritureComptable).filter(
                LometaEcritureComptable.recours_id == recours_id,
                LometaEcritureComptable.is_active == True,
                LometaEcritureComptable.est_annulee == False,
            ).order_by(LometaEcritureComptable.date_ecriture).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_ecritures_by_sinistre(self, sinistre_id: int) -> List[LometaEcritureComptable]:
        """Récupère toutes les écritures d'un sinistre"""
        try:
            return self.session.query(LometaEcritureComptable).filter(
                LometaEcritureComptable.sinistre_id == sinistre_id,
                LometaEcritureComptable.is_active == True,
                LometaEcritureComptable.est_annulee == False,
            ).order_by(LometaEcritureComptable.date_ecriture).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_ecritures_by_journal(
        self,
        journal: str,
        date_debut: datetime = None,
        date_fin: datetime = None,
    ) -> List[LometaEcritureComptable]:
        """Récupère les écritures d'un journal avec filtre date"""
        try:
            query = self.session.query(LometaEcritureComptable).filter(
                LometaEcritureComptable.journal == journal,
                LometaEcritureComptable.is_active == True,
                LometaEcritureComptable.est_annulee == False,
            )
            if date_debut:
                query = query.filter(LometaEcritureComptable.date_ecriture >= date_debut)
            if date_fin:
                query = query.filter(LometaEcritureComptable.date_ecriture <= date_fin)
            return query.order_by(LometaEcritureComptable.date_ecriture.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # ✅ NOUVEAU : GRAND LIVRE
    # ============================================================
    
    def get_grand_livre(
        self,
        compte: str,
        date_debut: datetime = None,
        date_fin: datetime = None,
    ) -> Dict[str, Any]:
        """
        Retourne le grand livre d'un compte (Tome 7 §6).
        
        Returns:
            {
                'compte': '616000',
                'date_debut': ...,
                'date_fin': ...,
                'solde_initial': 0,
                'total_debit': ...,
                'total_credit': ...,
                'solde_final': ...,
                'mouvements': [...]
            }
        """
        try:
            # Écritures au débit du compte
            debit_query = self.session.query(LometaEcritureComptable).filter(
                LometaEcritureComptable.compte_debit == compte,
                LometaEcritureComptable.is_active == True,
                LometaEcritureComptable.est_annulee == False,
            )
            
            # Écritures au crédit du compte
            credit_query = self.session.query(LometaEcritureComptable).filter(
                LometaEcritureComptable.compte_credit == compte,
                LometaEcritureComptable.is_active == True,
                LometaEcritureComptable.est_annulee == False,
            )
            
            if date_debut:
                debit_query = debit_query.filter(LometaEcritureComptable.date_ecriture >= date_debut)
                credit_query = credit_query.filter(LometaEcritureComptable.date_ecriture >= date_debut)
            if date_fin:
                debit_query = debit_query.filter(LometaEcritureComptable.date_ecriture <= date_fin)
                credit_query = credit_query.filter(LometaEcritureComptable.date_ecriture <= date_fin)
            
            ecritures_debit = debit_query.all()
            ecritures_credit = credit_query.all()
            
            total_debit = sum(e.montant for e in ecritures_debit)
            total_credit = sum(e.montant for e in ecritures_credit)
            solde_final = total_debit - total_credit
            
            mouvements = []
            for e in ecritures_debit:
                mouvements.append({
                    'date': e.date_ecriture.isoformat() if e.date_ecriture else None,
                    'numero': e.numero_ecriture,
                    'libelle': e.libelle,
                    'journal': e.journal,
                    'debit': e.montant,
                    'credit': 0,
                })
            for e in ecritures_credit:
                mouvements.append({
                    'date': e.date_ecriture.isoformat() if e.date_ecriture else None,
                    'numero': e.numero_ecriture,
                    'libelle': e.libelle,
                    'journal': e.journal,
                    'debit': 0,
                    'credit': e.montant,
                })
            
            mouvements.sort(key=lambda m: m['date'] or '')
            
            return {
                'compte': compte,
                'date_debut': date_debut.isoformat() if date_debut else None,
                'date_fin': date_fin.isoformat() if date_fin else None,
                'total_debit': total_debit,
                'total_credit': total_credit,
                'solde_final': solde_final,
                'mouvements': mouvements,
            }
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # ✅ NOUVEAU : BALANCE COMPTABLE
    # ============================================================
    
    def get_balance(
        self,
        date_debut: datetime = None,
        date_fin: datetime = None,
    ) -> List[Dict[str, Any]]:
        """
        Retourne la balance comptable (Tome 7 §6).
        
        Pour chaque compte :
        - Total débit
        - Total crédit
        - Solde (débit - crédit)
        """
        try:
            # Agréger les débits
            debit_result = self.session.query(
                LometaEcritureComptable.compte_debit.label('compte'),
                func.sum(LometaEcritureComptable.montant).label('total_debit'),
            ).filter(
                LometaEcritureComptable.is_active == True,
                LometaEcritureComptable.est_annulee == False,
            )
            
            # Agréger les crédits
            credit_result = self.session.query(
                LometaEcritureComptable.compte_credit.label('compte'),
                func.sum(LometaEcritureComptable.montant).label('total_credit'),
            ).filter(
                LometaEcritureComptable.is_active == True,
                LometaEcritureComptable.est_annulee == False,
            )
            
            if date_debut:
                debit_result = debit_result.filter(
                    LometaEcritureComptable.date_ecriture >= date_debut
                )
                credit_result = credit_result.filter(
                    LometaEcritureComptable.date_ecriture >= date_debut
                )
            if date_fin:
                debit_result = debit_result.filter(
                    LometaEcritureComptable.date_ecriture <= date_fin
                )
                credit_result = credit_result.filter(
                    LometaEcritureComptable.date_ecriture <= date_fin
                )
            
            debits = {row.compte: float(row.total_debit) for row in debit_result.group_by('compte').all()}
            credits = {row.compte: float(row.total_credit) for row in credit_result.group_by('compte').all()}
            
            # Fusionner
            comptes = set(debits.keys()) | set(credits.keys())
            balance = []
            for compte in sorted(comptes):
                d = debits.get(compte, 0)
                c = credits.get(compte, 0)
                balance.append({
                    'compte': compte,
                    'total_debit': d,
                    'total_credit': c,
                    'solde': d - c,
                })
            
            return balance
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # ✅ NOUVEAU : RAPPROCHEMENT BANCAIRE
    # ============================================================
    
    def get_ecritures_non_rapprochees(
        self,
        journal: str = None,
    ) -> List[LometaEcritureComptable]:
        """Récupère les écritures non rapprochées"""
        try:
            query = self.session.query(LometaEcritureComptable).filter(
                LometaEcritureComptable.est_rapprochee == False,
                LometaEcritureComptable.is_active == True,
                LometaEcritureComptable.est_annulee == False,
            )
            if journal:
                query = query.filter(LometaEcritureComptable.journal == journal)
            return query.order_by(LometaEcritureComptable.date_ecriture).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def rapprocher_ecriture(
        self,
        ecriture_id: int,
        reference_bancaire: str,
        utilisateur_id: int,
    ) -> Optional[LometaEcritureComptable]:
        """Marque une écriture comme rapprochée"""
        try:
            ecriture = self.get_ecriture(ecriture_id)
            if not ecriture:
                raise ValueError("Écriture non trouvée")
            
            ecriture.est_rapprochee = True
            ecriture.date_rapprochement = datetime.utcnow()
            ecriture.reference_bancaire = reference_bancaire
            ecriture.updated_at = datetime.utcnow()
            ecriture.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="RAPPROCHEMENT",
                entite="EcritureComptable",
                entite_id=ecriture.id,
                entite_nom=ecriture.numero_ecriture,
                commentaire=f"Rapprochement bancaire - Réf: {reference_bancaire}",
            )
            
            self.session.commit()
            return ecriture
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # VALIDATION / ANNULATION
    # ============================================================
    
    def export_etats_comptables(
        self,
        date_debut: datetime,
        date_fin: datetime,
        output_dir: str = "exports/comptabilite",
    ) -> Dict[str, str]:
        """
        Exporte les états comptables (Tome 7 §6).
        
        Returns:
            Dict {type_etat: chemin_fichier}
        """
        import os
        import csv
        from pathlib import Path
        
        os.makedirs(output_dir, exist_ok=True)
        exports = {}
        
        # 1. Balance comptable
        balance = self.get_balance(date_debut, date_fin)
        balance_path = os.path.join(output_dir, "balance.csv")
        with open(balance_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Compte', 'Total Débit', 'Total Crédit', 'Solde'])
            for ligne in balance:
                writer.writerow([
                    ligne['compte'],
                    f"{ligne['total_debit']:.2f}",
                    f"{ligne['total_credit']:.2f}",
                    f"{ligne['solde']:.2f}",
                ])
        exports['balance'] = balance_path
        
        # 2. Journal BANQUE
        journal_banque = self.get_ecritures_by_journal(
            self.JOURNAL_BANQUE, date_debut, date_fin
        )
        banque_path = os.path.join(output_dir, "journal_banque.csv")
        with open(banque_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['N° Écriture', 'Date', 'Libellé', 'Débit', 'Crédit', 'Montant'])
            for e in journal_banque:
                writer.writerow([
                    e.numero_ecriture,
                    e.date_ecriture.strftime('%d/%m/%Y') if e.date_ecriture else '',
                    e.libelle,
                    e.compte_debit,
                    e.compte_credit,
                    f"{e.montant:.2f}",
                ])
        exports['journal_banque'] = banque_path
        
        # 3. Journal SINISTRES
        journal_sinistres = self.get_ecritures_by_journal(
            self.JOURNAL_SINISTRES, date_debut, date_fin
        )
        sinistres_path = os.path.join(output_dir, "journal_sinistres.csv")
        with open(sinistres_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['N° Écriture', 'Date', 'Libellé', 'Débit', 'Crédit', 'Montant'])
            for e in journal_sinistres:
                writer.writerow([
                    e.numero_ecriture,
                    e.date_ecriture.strftime('%d/%m/%Y') if e.date_ecriture else '',
                    e.libelle,
                    e.compte_debit,
                    e.compte_credit,
                    f"{e.montant:.2f}",
                ])
        exports['journal_sinistres'] = sinistres_path
        
        # 4. Journal RECOURS
        journal_recours = self.get_ecritures_by_journal(
            self.JOURNAL_RECOURS, date_debut, date_fin
        )
        recours_path = os.path.join(output_dir, "journal_recours.csv")
        with open(recours_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['N° Écriture', 'Date', 'Libellé', 'Débit', 'Crédit', 'Montant'])
            for e in journal_recours:
                writer.writerow([
                    e.numero_ecriture,
                    e.date_ecriture.strftime('%d/%m/%Y') if e.date_ecriture else '',
                    e.libelle,
                    e.compte_debit,
                    e.compte_credit,
                    f"{e.montant:.2f}",
                ])
        exports['journal_recours'] = recours_path
        
        return exports

    def get_statistiques(
        self,
        date_debut: datetime = None,
        date_fin: datetime = None,
    ) -> Dict[str, Any]:
        """
        Statistiques comptables (Tome 7 §6).
        """
        try:
            query = self.session.query(LometaEcritureComptable).filter(
                LometaEcritureComptable.is_active == True,
                LometaEcritureComptable.est_annulee == False,
            )
            if date_debut:
                query = query.filter(LometaEcritureComptable.date_ecriture >= date_debut)
            if date_fin:
                query = query.filter(LometaEcritureComptable.date_ecriture <= date_fin)
            
            total = query.count()
            
            # Par journal
            par_journal = {}
            for j in [self.JOURNAL_BANQUE, self.JOURNAL_SINISTRES,
                    self.JOURNAL_RECOURS, self.JOURNAL_REGULARISATIONS]:
                count = query.filter(LometaEcritureComptable.journal == j).count()
                if count > 0:
                    par_journal[j] = count
            
            # Montant total
            montant_total = query.with_entities(
                func.sum(LometaEcritureComptable.montant)
            ).scalar() or 0
            
            # Non rapprochées
            non_rapprochees = query.filter(
                LometaEcritureComptable.est_rapprochee == False
            ).count()
            
            return {
                'total_ecritures': total,
                'par_journal': par_journal,
                'montant_total': montant_total,
                'non_rapprochees': non_rapprochees,
            }
        except Exception as e:
            self.session.rollback()
            raise e

    def valider_ecriture(
        self,
        ecriture_id: int,
        utilisateur_id: int,
    ) -> Optional[LometaEcritureComptable]:
        """Valide une écriture (passage en est_valide=True)"""
        try:
            ecriture = self.get_ecriture(ecriture_id)
            if not ecriture:
                raise ValueError("Écriture non trouvée")
            
            if ecriture.est_annulee:
                raise ValueError("Impossible de valider une écriture annulée")
            
            if ecriture.est_valide:
                return ecriture
            
            ecriture.est_valide = True
            ecriture.updated_at = datetime.utcnow()
            ecriture.updated_by = utilisateur_id
            
            self.session.commit()
            return ecriture
        except Exception as e:
            self.session.rollback()
            raise e
    
    def annuler_ecriture(
        self,
        ecriture_id: int,
        motif: str,
        utilisateur_id: int,
    ) -> Optional[LometaEcritureComptable]:
        """
        Annule une écriture (soft delete + contrepassation).
        
        Règle NC-001 : Justification obligatoire.
        Règle NC-002 : Audit obligatoire.
        """
        try:
            if not motif:
                raise ValueError("Un motif est obligatoire pour annuler une écriture (NC-001)")
            
            ecriture = self.get_ecriture(ecriture_id)
            if not ecriture:
                raise ValueError("Écriture non trouvée")
            
            if ecriture.est_annulee:
                raise ValueError("Cette écriture est déjà annulée")
            
            # Créer l'écriture de contrepassation
            contrepartie = LometaEcritureComptable(
                numero_ecriture=self.generer_numero_ecriture(),
                date_ecriture=datetime.utcnow(),
                date_comptabilisation=datetime.utcnow(),
                journal=self.JOURNAL_REGULARISATIONS,
                libelle=f"CONTREPASSATION - {ecriture.libelle}",
                compte_debit=ecriture.compte_credit,   # inversé
                compte_credit=ecriture.compte_debit,   # inversé
                montant=ecriture.montant,
                devise=ecriture.devise,
                reference_type="CONTREPASSATION",
                reference_id=ecriture.id,
                reference_numero=ecriture.numero_ecriture,
                sinistre_id=ecriture.sinistre_id,
                recours_id=ecriture.recours_id,
                reglement_id=ecriture.reglement_id,
                provision_id=ecriture.provision_id,
                note_credit_id=ecriture.note_credit_id,
                observations=f"Contrepassation de {ecriture.numero_ecriture} - Motif: {motif}",
                is_active=True,
                created_by=utilisateur_id,
            )
            self.session.add(contrepartie)
            self.session.flush()
            
            # Marquer l'écriture originale comme annulée
            ecriture.est_annulee = True
            ecriture.date_annulation = datetime.utcnow()
            ecriture.motif_annulation = motif
            ecriture.ecriture_contrepartie_id = contrepartie.id
            ecriture.updated_at = datetime.utcnow()
            ecriture.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="ANNULATION",
                entite="EcritureComptable",
                entite_id=ecriture.id,
                entite_nom=ecriture.numero_ecriture,
                commentaire=f"Annulation - Motif: {motif} - Contrepartie: {contrepartie.numero_ecriture}",
            )
            
            self.session.commit()
            return ecriture
        except Exception as e:
            self.session.rollback()
            raise e