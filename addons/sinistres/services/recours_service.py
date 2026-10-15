"""
Service de gestion des recours (Tome 6 du CDC)
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from addons.sinistres.services.base_service import BaseService
from addons.sinistres.models.recours import (
    LometaRecours, LometaEncaissementRecours, LometaReversementRecours, 
    LometaRelanceRecours, LometaRepartitionRecours
)
from addons.sinistres.models.sinistre import LometaSinistre
from addons.sinistres.models.reglement import LometaBeneficiaire


class RecoursService(BaseService):
    """Service de gestion des recours"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
        from addons.sinistres.services.parametre_service import ParametreService
        from addons.sinistres.services.comptabilite_service import ComptabiliteService
        self.parametre_service = ParametreService(self.session)
        self.comptabilite_service = ComptabiliteService(self.session)
    
    # ============================================================
    # GESTION DES RECOURS
    # ============================================================
    
    def creer_recours(self, data: Dict[str, Any]) -> LometaRecours:
        """
        Crée un nouveau recours (conforme CDC Tome 6 §5).
        
        Règles CDC :
        - REC-001 : Le sinistre doit exister
        - REC-002 : La responsabilité adverse doit être identifiée
        - REC-003 : Le montant récupérable doit être déterminé
        """
        try:
            # ============================================================
            # REC-001 : Vérifier que le sinistre existe
            # ============================================================
            sinistre_id = data.get('sinistre_id')
            if not sinistre_id:
                raise ValueError("REC-001 : Aucun sinistre associé")
            
            sinistre = self.session.query(LometaSinistre).filter(
                LometaSinistre.id == sinistre_id,
                LometaSinistre.is_active == True
            ).first()
            
            if not sinistre:
                raise ValueError("REC-001 : Sinistre non trouvé")
            
            # ============================================================
            # REC-002 : Vérifier la responsabilité adverse
            # ============================================================
            taux_resp = float(sinistre.taux_responsabilite or 1)
            if taux_resp >= 1.0:
                raise ValueError(
                    f"REC-002 : Aucune responsabilité adverse identifiée "
                    f"(taux = {taux_resp * 100:.0f}%)"
                )
            
            # ============================================================
            # REC-003 : Vérifier le montant récupérable
            # ============================================================
            montant_reclame = float(data.get('montant_reclame', 0))
            if montant_reclame <= 0:
                raise ValueError("REC-003 : Le montant réclamé doit être positif")
            
            from addons.sinistres.models.reglement import LometaReglement
            from sqlalchemy import func as sql_func
            montant_regle = self.session.query(
                sql_func.sum(LometaReglement.montant)
            ).filter(
                LometaReglement.sinistre_id == sinistre_id,
                LometaReglement.statut == 'PAYE',
                LometaReglement.is_active == True
            ).scalar() or 0
            
            if montant_regle <= 0:
                raise ValueError("REC-003 : Aucun montant réglé sur ce sinistre")
            
            # ============================================================
            # Vérifier le débiteur
            # ============================================================
            debiteur_type = data.get('debiteur_type', 'TIERS')
            
            if debiteur_type == 'TIERS':
                debiteur_id = data.get('debiteur_tiers_id')
                if not debiteur_id:
                    raise ValueError("Un tiers débiteur doit être sélectionné")
                from addons.sinistres.models.sinistre import LometaTiers
                tiers = self.session.query(LometaTiers).filter(
                    LometaTiers.id == debiteur_id,
                    LometaTiers.is_active == True
                ).first()
                if not tiers:
                    raise ValueError("Le tiers sélectionné est introuvable")
            elif debiteur_type == 'COMPAGNIE':
                debiteur_id = data.get('debiteur_compagnie_id')
                if not debiteur_id:
                    raise ValueError("Une compagnie débitrice doit être sélectionnée")
            else:
                raise ValueError(f"Type de débiteur invalide : {debiteur_type}")
            
            # ============================================================
            # Vérifier le responsable (CDC §5.2)
            # ============================================================
            responsable_id = data.get('responsable_id')
            if not responsable_id:
                raise ValueError(
                    "Un gestionnaire responsable doit être défini (CDC §5.2)"
                )
            
            # ============================================================
            # ✅ Générer le numéro + extraire sinistre_id de data
            # ============================================================
            numero = self.generate_numero("REC", LometaRecours, 'numero_recours')
            
            # ✅ RETIRER sinistre_id de data (car on le passe explicitement)
            data.pop('sinistre_id', None)
            data.pop('debiteur_id', None)   # ← AJOUTER
            data.pop('statut', None)         # ← au cas où
            data.pop('numero_recours', None)
            data.pop('date_ouverture', None)
            data.pop('solde', None)
            
            # ============================================================
            # Créer le recours (sans doublon sinistre_id)
            # ============================================================
            recours = LometaRecours(
                numero_recours=numero,
                sinistre_id=sinistre_id,          # ← une seule fois
                statut="OUVERT",
                date_ouverture=datetime.utcnow(),
                solde=montant_reclame,
                debiteur_id=debiteur_id, 
                **data                             # ← data sans sinistre_id
            )
            
            self.session.add(recours)
            self.session.flush()
            
            # Mettre à jour le statut du sinistre
            if sinistre.statut not in ["EN_RECOURS", "CLOTURE"]:
                sinistre.statut = "EN_RECOURS"
                sinistre.updated_at = datetime.utcnow()
                sinistre.updated_by = data.get('created_by')
            
            # Log audit
            self.log_audit(
                utilisateur_id=data.get('created_by'),
                action="CREATION",
                entite="Recours",
                entite_id=recours.id,
                entite_nom=recours.numero_recours,
                commentaire=(
                    f"Création du recours {recours.numero_recours} "
                    f"- Type: {recours.type_recours} "
                    f"- Débiteur: {recours.debiteur_nom} "
                    f"- Montant: {montant_reclame:,.0f} FCFA"
                )
            )
            
            self.session.commit()
            return recours
            
        except Exception as e:
            self.session.rollback()
            raise e

    def get_recours(self, recours_id: int) -> Optional[LometaRecours]:
        """Récupère un recours par son ID"""
        try:
            return self.session.query(LometaRecours).filter(
                LometaRecours.id == recours_id,
                LometaRecours.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_recours_by_numero(self, numero: str) -> Optional[LometaRecours]:
        """Récupère un recours par son numéro"""
        try:
            return self.session.query(LometaRecours).filter(
                LometaRecours.numero_recours == numero,
                LometaRecours.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_recours_by_sinistre(self, sinistre_id: int) -> List[LometaRecours]:
        """Récupère tous les recours d'un sinistre"""
        try:
            return self.session.query(LometaRecours).filter(
                LometaRecours.sinistre_id == sinistre_id,
                LometaRecours.is_active == True
            ).order_by(LometaRecours.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_recours(self, recours_id: int, data: Dict[str, Any]) -> Optional[LometaRecours]:
        """Met à jour un recours"""
        try:
            recours = self.get_recours(recours_id)
            if not recours:
                raise ValueError("Recours non trouvé")
            
            for key, value in data.items():
                if hasattr(recours, key) and getattr(recours, key) != value:
                    setattr(recours, key, value)
            
            recours.updated_at = datetime.utcnow()
            recours.updated_by = data.get('updated_by')
            
            self.session.commit()
            return recours
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def changer_statut_recours(self, recours_id: int, nouveau_statut: str, utilisateur_id: int, motif: str = None) -> Optional[LometaRecours]:
        """Change le statut d'un recours"""
        try:
            recours = self.get_recours(recours_id)
            if not recours:
                raise ValueError("Recours non trouvé")
            
            ancien_statut = recours.statut
            
            # Vérifier la transition
            transitions_autorisees = self._get_transitions_recours(ancien_statut)
            if nouveau_statut not in transitions_autorisees:
                raise ValueError(f"Transition non autorisée: {ancien_statut} -> {nouveau_statut}")
            
            recours.statut = nouveau_statut
            recours.updated_at = datetime.utcnow()
            recours.updated_by = utilisateur_id
            
            if nouveau_statut == "CLOTURE":
                recours.date_cloture = datetime.utcnow()
                recours.motif_cloture = motif
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="CHANGEMENT_STATUT",
                entite="Recours",
                entite_id=recours.id,
                entite_nom=recours.numero_recours,
                champ_modifie="statut",
                ancienne_valeur=ancien_statut,
                nouvelle_valeur=nouveau_statut,
                commentaire=motif
            )
            
            self.session.commit()
            return recours
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def _get_transitions_recours(self, statut_actuel: str) -> List[str]:
        """Retourne les transitions autorisées pour un recours"""
        transitions = {
            "OUVERT": ["EN_INSTRUCTION", "CLOTURE"],
            "EN_INSTRUCTION": ["RELANCE", "CONTESTE", "ABOUTI", "REFUSE", "CLOTURE"],
            "RELANCE": ["EN_INSTRUCTION", "ABOUTI", "REFUSE", "CLOTURE"],
            "CONTESTE": ["EN_INSTRUCTION", "ABOUTI", "REFUSE", "CLOTURE"],
            "REFUSE": ["CLOTURE"],
            "ABOUTI": ["EN_ATTENTE_ENCAISSEMENT", "CLOTURE"],
            "EN_ATTENTE_ENCAISSEMENT": ["PARTIELLEMENT_ENCAISSE", "ENCAISSE", "CLOTURE"],
            "PARTIELLEMENT_ENCAISSE": ["EN_ATTENTE_ENCAISSEMENT", "ENCAISSE", "CLOTURE"],
            "ENCAISSE": ["REVERSEMENT_EN_COURS", "COMPTABILISE", "CLOTURE"],
            "REVERSEMENT_EN_COURS": ["PAYE", "COMPTABILISE", "CLOTURE"],
            "PAYE": ["COMPTABILISE", "CLOTURE"],
            "COMPTABILISE": ["CLOTURE"],
        }
        return transitions.get(statut_actuel, ["CLOTURE"])
    
    # ============================================================
    # GESTION DES ENCAISSEMENTS
    # ============================================================
    
    def enregistrer_encaissement(
        self,
        recours_id: int,
        data: Dict[str, Any],
        utilisateur_id: int,
    ) -> Optional[LometaEncaissementRecours]:
        """
        Enregistre un encaissement de recours avec contrôles CDC.
        
        Règles appliquées :
        - REC-101 : Le montant encaissé ≤ montant accepté
        - REC-102 : Le montant encaissé ≤ solde restant
        - REC-030 : Le recours reste actif tant que le solde ≠ 0
        """
        try:
            # 1. Vérifier le recours
            recours = self.get_recours(recours_id)
            if not recours:
                raise ValueError("Recours non trouvé")
            
            # 2. Vérifier le statut
            if recours.statut not in ["EN_ATTENTE_ENCAISSEMENT", "PARTIELLEMENT_ENCAISSE"]:
                raise ValueError(
                    f"Le recours doit être en attente d'encaissement "
                    f"(statut actuel : {recours.statut})"
                )
            
            # 3. Valider le montant
            montant = float(data.get('montant', 0))
            if montant <= 0:
                raise ValueError("Le montant doit être positif")
            
            solde_restant = float(recours.solde or 0)
            if montant > solde_restant:
                raise ValueError(
                    f"Le montant ({montant:,.0f} FCFA) dépasse le solde restant "
                    f"({solde_restant:,.0f} FCFA) - règle REC-102"
                )
            
            # 4. REC-101 : Vérifier si montant accepté est défini
            if recours.montant_accepte:
                nouveau_total = float(recours.montant_encaisse or 0) + montant
                if nouveau_total > float(recours.montant_accepte):
                    raise ValueError(
                        f"Le cumul des encaissements ({nouveau_total:,.0f}) dépasse "
                        f"le montant accepté ({recours.montant_accepte:,.0f}) - règle REC-101"
                    )
            
            # 5. Déterminer si c'est partiel
            est_partiel = montant < solde_restant
            
            # 6. Créer l'encaissement
            encaissement = LometaEncaissementRecours(
                recours_id=recours_id,
                montant=montant,
                mode_encaissement=data.get('mode_encaissement'),
                reference_bancaire=data.get('reference_bancaire'),
                date_encaissement=data.get('date_encaissement') or datetime.utcnow(),
                banque=data.get('banque'),
                compte_bancaire_id=data.get('compte_bancaire_id'),
                est_partiel=est_partiel,
                solde_apres_encaissement=solde_restant - montant,
                observations=data.get('observations'),
                is_active=True,
                created_by=utilisateur_id,
            )
            
            self.session.add(encaissement)
            self.session.flush()
            
            # 7. Mettre à jour le recours
            recours.montant_encaisse = float(recours.montant_encaisse or 0) + montant
            recours.solde = float(recours.montant_accepte or recours.montant_reclame) - float(recours.montant_encaisse)
            
            if recours.solde <= 0:
                recours.statut = "ENCAISSE"
            else:
                recours.statut = "PARTIELLEMENT_ENCAISSE"
            
            recours.updated_at = datetime.utcnow()
            recours.updated_by = utilisateur_id
            
            # 8. Générer l'écriture comptable
            try:
                self.comptabilite_service.ecriture_encaissement_recours(
                    encaissement_id=encaissement.id,
                    numero_recours=recours.numero_recours,
                    montant=montant,
                    recours_id=recours.id,
                    sinistre_id=recours.sinistre_id,
                    utilisateur_id=utilisateur_id,
                )
            except Exception as e:
                print(f"⚠️ Écriture comptable non générée : {e}")
            
            # 9. Log audit
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="ENCAISSEMENT",
                entite="Recours",
                entite_id=recours.id,
                entite_nom=recours.numero_recours,
                commentaire=(
                    f"Encaissement de {montant:,.0f} FCFA - "
                    f"Solde restant : {recours.solde:,.0f} FCFA - "
                    f"Statut : {recours.statut}"
                )
            )
            
            self.session.commit()
            return encaissement
            
        except Exception as e:
            self.session.rollback()
            raise e

    def get_encaissements(self, recours_id: int) -> List[LometaEncaissementRecours]:
        """Récupère tous les encaissements d'un recours"""
        try:
            return self.session.query(LometaEncaissementRecours).filter(
                LometaEncaissementRecours.recours_id == recours_id,
                LometaEncaissementRecours.is_active == True
            ).order_by(LometaEncaissementRecours.date_encaissement.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # GESTION DES REVERSEMENTS
    # ============================================================
    
    def creer_reversement(self, recours_id: int, data: Dict[str, Any], utilisateur_id: int) -> Optional[LometaReversementRecours]:
        """Crée un reversement pour un recours"""
        try:
            recours = self.get_recours(recours_id)
            if not recours:
                raise ValueError("Recours non trouvé")
            
            if recours.statut not in ["ENCAISSE", "REVERSEMENT_EN_COURS"]:
                raise ValueError("Le recours n'est pas encaissé")
            
            montant = data.get('montant', 0)
            if montant <= 0:
                raise ValueError("Le montant doit être positif")
            
            # Vérifier que le bénéficiaire existe
            beneficiaire = self.session.query(LometaBeneficiaire).filter(
                LometaBeneficiaire.id == data.get('beneficiaire_id'),
                LometaBeneficiaire.is_active == True
            ).first()
            if not beneficiaire:
                raise ValueError("Bénéficiaire non trouvé")
            
            reversement = LometaReversementRecours(
                recours_id=recours_id,
                **data
            )
            
            self.session.add(reversement)
            self.session.flush()

            try:
                self.comptabilite_service.ecriture_reversement_client(
                    reversement_id=reversement.id,
                    numero_recours=recours.numero_recours,
                    montant=montant,
                    recours_id=recours.id,
                    sinistre_id=recours.sinistre_id,
                    utilisateur_id=utilisateur_id,
                )
            except Exception as e:
                print(f"⚠️ Écriture comptable reversement non générée : {e}")
            
            # Mettre à jour le statut du recours
            recours.statut = "REVERSEMENT_EN_COURS"
            recours.date_reversement = datetime.utcnow()
            recours.updated_at = datetime.utcnow()
            recours.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="REVERSEMENT_CREATION",
                entite="Recours",
                entite_id=recours.id,
                entite_nom=recours.numero_recours,
                commentaire=f"Création du reversement de {montant} pour {beneficiaire.nom}"
            )
            
            self.session.commit()
            return reversement
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_reversements(self, recours_id: int) -> List[LometaReversementRecours]:
        """Récupère tous les reversements d'un recours"""
        try:
            return self.session.query(LometaReversementRecours).filter(
                LometaReversementRecours.recours_id == recours_id,
                LometaReversementRecours.is_active == True
            ).order_by(LometaReversementRecours.date_reversement.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def marquer_reversement_paye(self, reversement_id: int, utilisateur_id: int) -> bool:
        """Marque un reversement comme payé"""
        try:
            reversement = self.session.query(LometaReversementRecours).filter(
                LometaReversementRecours.id == reversement_id,
                LometaReversementRecours.is_active == True
            ).first()
            if not reversement:
                raise ValueError("Reversement non trouvé")
            
            reversement.est_paye = True
            reversement.updated_at = datetime.utcnow()
            reversement.updated_by = utilisateur_id
            
            # Vérifier si tous les reversements sont payés
            recours = self.get_recours(reversement.recours_id)
            if recours:
                reversements = self.get_reversements(recours.id)
                tous_payes = all(r.est_paye for r in reversements)
                if tous_payes and recours.statut == "REVERSEMENT_EN_COURS":
                    recours.statut = "PAYE"
                    recours.updated_at = datetime.utcnow()
                    recours.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="REVERSEMENT_PAYE",
                entite="Recours",
                entite_id=reversement.recours_id,
                commentaire=f"Reversement payé pour {reversement.beneficiaire_nom} - Montant: {reversement.montant}"
            )
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # GESTION DES RELANCES
    # ============================================================
    
    def ajouter_relance(self, recours_id: int, data: Dict[str, Any], utilisateur_id: int) -> Optional[LometaRelanceRecours]:
        """Ajoute une relance à un recours (conforme CDC Tome 6 §6)"""
        try:
            # ============================================================
            # 1. Vérifier le recours
            # ============================================================
            recours = self.get_recours(recours_id)
            if not recours:
                raise ValueError("Recours non trouvé")
            
            # ============================================================
            # 2. Extraire et nettoyer les données
            # ============================================================
            # ✅ Retirer les champs qui ne sont PAS des colonnes du modèle
            data.pop('recours_id', None)          # ← déjà passé explicitement
            data.pop('delai_prochain', None)      # ← champ UI, pas BD
            data.pop('envoyer_email', None)       # ← champ UI, pas BD
            data.pop('created_by', None)          # ← géré par AuditableMixin
            
            # ✅ S'assurer que date_relance est un datetime, pas une date
            date_relance = data.get('date_relance')
            if date_relance and not isinstance(date_relance, datetime):
                # Convertir datetime.date → datetime.datetime
                data['date_relance'] = datetime.combine(date_relance, datetime.min.time())
            
            # ✅ Idem pour prochaine_relance
            prochaine = data.get('prochaine_relance')
            if prochaine and not isinstance(prochaine, datetime):
                data['prochaine_relance'] = datetime.combine(prochaine, datetime.min.time())
            
            # ============================================================
            # 3. Créer la relance
            # ============================================================
            relance = LometaRelanceRecours(
                recours_id=recours_id,              # ← explicite (une seule fois)
                effectue_par=utilisateur_id,
                created_by=utilisateur_id,          # ← audit
                **data                              # ← data nettoyée
            )
            
            self.session.add(relance)
            self.session.flush()
            
            # ============================================================
            # 4. Mettre à jour le recours
            # ============================================================
            recours.nombre_relances += 1
            recours.date_derniere_relance = datetime.utcnow()
            
            if data.get('prochaine_relance'):
                recours.date_prochaine_relance = data['prochaine_relance']
            
            if recours.statut == "EN_INSTRUCTION":
                recours.statut = "RELANCE"
            
            recours.updated_at = datetime.utcnow()
            recours.updated_by = utilisateur_id
            
            # ============================================================
            # 5. Log audit
            # ============================================================
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="RELANCE",
                entite="Recours",
                entite_id=recours.id,
                entite_nom=recours.numero_recours,
                commentaire=(
                    f"Relance {recours.nombre_relances} "
                    f"- Type: {data.get('type_relance', 'inconnu')}"
                )
            )
            
            self.session.commit()
            return relance
            
        except Exception as e:
            self.session.rollback()
            raise e

    def get_relances(self, recours_id: int) -> List[LometaRelanceRecours]:
        """Récupère toutes les relances d'un recours"""
        try:
            return self.session.query(LometaRelanceRecours).filter(
                LometaRelanceRecours.recours_id == recours_id,
                LometaRelanceRecours.is_active == True
            ).order_by(LometaRelanceRecours.date_relance.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # STATISTIQUES
    # ============================================================
    
    def get_statistiques(self, sinistre_id: int = None) -> Dict[str, Any]:
        """Récupère les statistiques des recours"""
        try:
            query = self.session.query(LometaRecours).filter(LometaRecours.is_active == True)
            
            if sinistre_id:
                query = query.filter(LometaRecours.sinistre_id == sinistre_id)
            
            total = query.count()
            
            # Par statut
            par_statut = {}
            for statut in ['OUVERT', 'EN_INSTRUCTION', 'RELANCE', 'CONTESTE', 'REFUSE',
                          'ABOUTI', 'EN_ATTENTE_ENCAISSEMENT', 'PARTIELLEMENT_ENCAISSE',
                          'ENCAISSE', 'REVERSEMENT_EN_COURS', 'PAYE', 'COMPTABILISE', 'CLOTURE']:
                count = query.filter(LometaRecours.statut == statut).count()
                if count > 0:
                    par_statut[statut] = count
            
            # Montants
            from sqlalchemy import func
            montant_reclame_total = query.with_entities(
                func.sum(LometaRecours.montant_reclame)
            ).scalar() or 0
            
            montant_encaisse_total = query.with_entities(
                func.sum(LometaRecours.montant_encaisse)
            ).scalar() or 0
            
            # Taux de récupération
            taux_recuperation = (montant_encaisse_total / montant_reclame_total * 100) if montant_reclame_total > 0 else 0
            
            return {
                'total': total,
                'par_statut': par_statut,
                'montant_reclame_total': montant_reclame_total,
                'montant_encaisse_total': montant_encaisse_total,
                'taux_recuperation': round(taux_recuperation, 2)
            }
        except Exception as e:
            self.session.rollback()
            raise e

    # Dans RecoursService
    def verifier_conditions_recours(self, sinistre_id: int) -> Dict[str, Any]:
        """Vérifie les conditions préalables au recours (CDC Tome 6 §5)."""
        result = {
            'peut_creer': False,
            'raison': '',
            'montant_regle': 0,
            'taux_responsabilite': 0,
        }
        
        sinistre = self.session.query(LometaSinistre).filter(
            LometaSinistre.id == sinistre_id,
            LometaSinistre.is_active == True
        ).first()
        
        if not sinistre:
            result['raison'] = "Sinistre non trouvé"
            return result
        
        taux_resp = float(sinistre.taux_responsabilite or 1)
        result['taux_responsabilite'] = taux_resp
        
        if taux_resp >= 1.0:
            result['raison'] = (
                f"REC-002 : Aucune responsabilité adverse "
                f"(taux = {taux_resp * 100:.0f}%)"
            )
            return result
        
        from addons.sinistres.models.reglement import LometaReglement
        montant_regle = self.session.query(
            func.sum(LometaReglement.montant)
        ).filter(
            LometaReglement.sinistre_id == sinistre_id,
            LometaReglement.statut == 'PAYE',
            LometaReglement.is_active == True
        ).scalar() or 0
        
        result['montant_regle'] = float(montant_regle)
        
        if montant_regle <= 0:
            result['raison'] = "REC-003 : Aucun montant réglé sur ce sinistre"
            return result
        
        result['peut_creer'] = True
        return result

    def get_recours_by_statut(self, statut: str) -> List['LometaRecours']:
        """Récupère les recours par statut"""
        try:
            return self.session.query(LometaRecours).filter(
                LometaRecours.statut == statut,
                LometaRecours.is_active == True
            ).order_by(LometaRecours.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_recours_by_debiteur(self, debiteur_id: int) -> List['LometaRecours']:
        """Récupère les recours par débiteur"""
        try:
            return self.session.query(LometaRecours).filter(
                LometaRecours.debiteur_id == debiteur_id,
                LometaRecours.is_active == True
            ).order_by(LometaRecours.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_recours_en_relance(self) -> List['LometaRecours']:
        """Récupère les recours nécessitant une relance"""
        try:
            from datetime import datetime, timedelta
            today = datetime.utcnow()
            return self.session.query(LometaRecours).filter(
                LometaRecours.date_prochaine_relance <= today,
                LometaRecours.statut.in_(['EN_INSTRUCTION', 'RELANCE', 'EN_ATTENTE_ENCAISSEMENT']),
                LometaRecours.is_active == True
            ).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_taux_recuperation_global(self) -> float:
        """Calcule le taux de récupération global"""
        try:
            from sqlalchemy import func
            result = self.session.query(
                func.sum(LometaRecours.montant_reclame).label('total_reclame'),
                func.sum(LometaRecours.montant_encaisse).label('total_encaisse')
            ).filter(LometaRecours.is_active == True).first()
            
            total_reclame = result.total_reclame or 0
            total_encaisse = result.total_encaisse or 0
            
            if total_reclame > 0:
                return (total_encaisse / total_reclame) * 100
            return 0.0
        except Exception as e:
            self.session.rollback()
            raise e

    def get_recours_a_relancer(self) -> List['LometaRecours']:
        """Récupère les recours nécessitant une relance"""
        try:
            from datetime import datetime, timedelta
            today = datetime.utcnow()
            
            # Recours avec date de prochaine relance dépassée
            recours = self.session.query(LometaRecours).filter(
                LometaRecours.date_prochaine_relance <= today,
                LometaRecours.statut.in_(['EN_INSTRUCTION', 'RELANCE', 'EN_ATTENTE_ENCAISSEMENT']),
                LometaRecours.is_active == True
            ).all()
            
            # Recours sans relance depuis plus de 30 jours
            seuil = today - timedelta(days=30)
            recours_sans_relance = self.session.query(LometaRecours).filter(
                LometaRecours.date_derniere_relance < seuil,
                LometaRecours.statut.in_(['EN_INSTRUCTION', 'EN_ATTENTE_ENCAISSEMENT']),
                LometaRecours.is_active == True
            ).all()
            
            # Fusionner les deux listes sans doublons
            result = list(set(recours + recours_sans_relance))
            
            for r in result:
                print(f"🔔 Recours {r.numero_recours} nécessite une relance")
            
            return result
            
        except Exception as e:
            self.session.rollback()
            raise e

    def get_relances_en_attente(self, recours_id: int) -> List['LometaRelanceRecours']:
        """Récupère les relances en attente de réponse"""
        try:
            return self.session.query(LometaRelanceRecours).filter(
                LometaRelanceRecours.recours_id == recours_id,
                LometaRelanceRecours.reponse_recue == False,
                LometaRelanceRecours.is_active == True
            ).order_by(LometaRelanceRecours.date_relance.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def marquer_reponse_relance(self, relance_id: int, contenu_reponse: str, utilisateur_id: int) -> Optional['LometaRelanceRecours']:
        """Marque une relance comme ayant reçu une réponse"""
        try:
            relance = self.session.query(LometaRelanceRecours).filter(
                LometaRelanceRecours.id == relance_id,
                LometaRelanceRecours.is_active == True
            ).first()
            if not relance:
                raise ValueError("Relance non trouvée")
            
            relance.reponse_recue = True
            relance.date_reponse = datetime.utcnow()
            relance.contenu_reponse = contenu_reponse
            relance.updated_at = datetime.utcnow()
            relance.updated_by = utilisateur_id
            relance.statut = "REPONDU"
            
            # Mettre à jour le statut du recours
            recours = self.get_recours(relance.recours_id)
            if recours:
                recours.updated_at = datetime.utcnow()
                recours.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="REPONSE_RELANCE",
                entite="Recours",
                entite_id=relance.recours_id,
                commentaire=f"Réponse reçue pour la relance {relance_id}"
            )
            
            self.session.commit()
            return relance
            
        except Exception as e:
            self.session.rollback()
            raise e

    def planifier_relances_auto(self) -> Dict[str, int]:
        """Planifie automatiquement les relances pour tous les recours"""
        try:
            recours_a_relancer = self.get_recours_a_relancer()
            stats = {'planifiees': 0, 'erreurs': 0}
            
            for rec in recours_a_relancer:
                try:
                    # Créer une relance automatique
                    relance = LometaRelanceRecours(
                        recours_id=rec.id,
                        date_relance=datetime.utcnow(),
                        type_relance="AUTOMATIQUE",
                        contenu=f"Relance automatique pour le recours {rec.numero_recours}",
                        effectue_par=1,  # ID de l'utilisateur système
                        prochaine_relance=datetime.utcnow() + timedelta(days=15),
                        statut="EN_ATTENTE"
                    )
                    self.session.add(relance)
                    
                    # Mettre à jour le recours
                    rec.nombre_relances += 1
                    rec.date_derniere_relance = datetime.utcnow()
                    rec.date_prochaine_relance = datetime.utcnow() + timedelta(days=15)
                    rec.statut = "RELANCE"
                    rec.updated_at = datetime.utcnow()
                    
                    stats['planifiees'] += 1
                    
                except Exception as e:
                    stats['erreurs'] += 1
                    print(f"❌ Erreur planification relance pour {rec.numero_recours}: {e}")
            
            self.session.commit()
            return stats
            
        except Exception as e:
            self.session.rollback()
            raise e

    def get_recours_by_debiteur(self, debiteur_type: str, debiteur_id: int = None) -> List[LometaRecours]:
        """Récupère les recours par type de débiteur"""
        try:
            query = self.session.query(LometaRecours).filter(
                LometaRecours.debiteur_type == debiteur_type,
                LometaRecours.is_active == True
            )
            if debiteur_id is not None:
                if debiteur_type == "TIERS":
                    query = query.filter(LometaRecours.debiteur_tiers_id == debiteur_id)
                elif debiteur_type == "COMPAGNIE":
                    query = query.filter(LometaRecours.debiteur_compagnie_id == debiteur_id)
            
            return query.order_by(LometaRecours.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_recours_by_type(self, type_recours: str) -> List[LometaRecours]:
        """Récupère les recours par type"""
        try:
            return self.session.query(LometaRecours).filter(
                LometaRecours.type_recours == type_recours,
                LometaRecours.is_active == True
            ).order_by(LometaRecours.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_recours_by_evaluation(self, evaluation_id: int) -> List[LometaRecours]:
        """Récupère les recours liés à une évaluation"""
        try:
            return self.session.query(LometaRecours).filter(
                LometaRecours.evaluation_id == evaluation_id,
                LometaRecours.is_active == True
            ).order_by(LometaRecours.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def creer_recours_depuis_reglement(self, reglement_id: int, data: Dict[str, Any]) -> LometaRecours:
        """Crée un recours à partir d'un règlement existant"""
        try:
            from addons.sinistres.models.reglement import LometaReglement
            reglement = self.session.query(LometaReglement).filter(
                LometaReglement.id == reglement_id
            ).first()
            if not reglement:
                raise ValueError("Règlement non trouvé")
            
            data['reglement_id'] = reglement_id
            data['sinistre_id'] = reglement.sinistre_id
            if reglement.evaluation_id:
                data['evaluation_id'] = reglement.evaluation_id
            
            return self.creer_recours(data)
        except Exception as e:
            self.session.rollback()
            raise e

    def calculer_repartition(
        self,
        recours_id: int,
        quote_parts: Dict[str, float],
        utilisateur_id: int,
    ) -> List[LometaRepartitionRecours]:
        """
        Calcule et enregistre la répartition d'un recours encaissé.
        
        Règle CDC Tome 6 §8 (REC-020) :
        La somme des répartitions doit être égale au montant encaissé.
        
        Args:
            recours_id: ID du recours
            quote_parts: Dict {type_beneficiaire: pourcentage}
                Exemple : {'CLIENT': 70, 'COMPAGNIE': 20, 'HONORAIRES': 10}
            utilisateur_id: ID utilisateur pour audit
        
        Returns:
            Liste des répartitions créées
        """
        try:
            # 1. Vérifier le recours
            recours = self.get_recours(recours_id)
            if not recours:
                raise ValueError("Recours non trouvé")
            
            if recours.statut not in ["ENCAISSE", "PARTIELLEMENT_ENCAISSE"]:
                raise ValueError(
                    f"Le recours doit être encaissé pour être réparti "
                    f"(statut actuel : {recours.statut})"
                )
            
            # 2. Vérifier que la somme des quote-parts = 100%
            total_quote = sum(quote_parts.values())
            if abs(total_quote - 100.0) > 0.01:
                raise ValueError(
                    f"La somme des quote-parts doit être égale à 100% "
                    f"(actuel : {total_quote}%)"
                )
            
            # 3. Supprimer les anciennes répartitions si elles existent
            anciennes = self.session.query(LometaRepartitionRecours).filter(
                LometaRepartitionRecours.recours_id == recours_id,
                LometaRepartitionRecours.is_active == True
            ).all()
            for a in anciennes:
                a.is_active = False
            
            # 4. Créer les nouvelles répartitions
            repartitions = []
            montant_encaisse = float(recours.montant_encaisse or 0)
            
            for type_ben, quote in quote_parts.items():
                if quote <= 0:
                    continue  # Ignorer les quote-parts à 0
                
                montant = round(montant_encaisse * quote / 100, 2)
                
                repartition = LometaRepartitionRecours(
                    recours_id=recours_id,
                    type_beneficiaire=type_ben.upper(),
                    beneficiaire_nom=self._get_beneficiaire_nom(type_ben, recours),
                    quote_part=quote,
                    montant=montant,
                    est_reverse=False,
                    is_active=True,
                    created_by=utilisateur_id,
                )
                self.session.add(repartition)
                repartitions.append(repartition)
            
            self.session.flush()
            
            # 5. Vérifier REC-020 (contrôle final)
            total_montants = sum(r.montant for r in repartitions)
            if abs(total_montants - montant_encaisse) > 0.01:
                raise ValueError(
                    f"Erreur de calcul : Σ répartitions = {total_montants:,.0f} "
                    f"≠ montant encaissé ({montant_encaisse:,.0f}) (règle REC-020)"
                )

            for rep in repartitions:
                if rep.type_beneficiaire == 'HONORAIRES' and rep.montant > 0:
                    try:
                        self.comptabilite_service.ecriture_honoraires(
                            repartition_id=rep.id,
                            numero_recours=recours.numero_recours,
                            montant=rep.montant,
                            recours_id=recours.id,
                            sinistre_id=recours.sinistre_id,
                            utilisateur_id=utilisateur_id,
                        )
                    except Exception as e:
                        print(f"⚠️ Écriture honoraires non générée : {e}")
            
            # 6. Log audit
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="REPARTITION",
                entite="Recours",
                entite_id=recours.id,
                entite_nom=recours.numero_recours,
                commentaire=(
                    f"Répartition du recours {recours.numero_recours} : "
                    f"{len(repartitions)} part(s) - Total {total_montants:,.0f} FCFA"
                )
            )
            
            self.session.commit()
            return repartitions
            
        except Exception as e:
            self.session.rollback()
            raise e

    def _get_beneficiaire_nom(self, type_beneficiaire: str, recours) -> str:
        """Retourne un nom de bénéficiaire par défaut selon le type"""
        mapping = {
            'CLIENT': f"Client du sinistre {recours.sinistre_id}",
            'COMPAGNIE': "Compagnie",
            'HONORAIRES': "Honoraires",
            'COASSUREUR': "Coassureur",
            'AUTRE': "Autre bénéficiaire",
        }
        return mapping.get(type_beneficiaire.upper(), type_beneficiaire)

    def get_repartitions(self, recours_id: int) -> List[LometaRepartitionRecours]:
        """Récupère les répartitions actives d'un recours"""
        try:
            return self.session.query(LometaRepartitionRecours).filter(
                LometaRepartitionRecours.recours_id == recours_id,
                LometaRepartitionRecours.is_active == True
            ).order_by(LometaRepartitionRecours.quote_part.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e


    def get_quoteparts_defaut(self) -> Dict[str, float]:
        """Retourne les quote-parts par défaut depuis les paramètres"""
        return {
            'CLIENT': self.parametre_service.get_quotepart_defaut('CLIENT'),
            'COMPAGNIE': self.parametre_service.get_quotepart_defaut('COMPAGNIE'),
            'HONORAIRES': self.parametre_service.get_quotepart_defaut('HONORAIRES'),
            'COASSUREUR': self.parametre_service.get_quotepart_defaut('COASSUREUR'),
        }


    # ============================================================
    # ALERTES (CDC Tome 6 §17)
    # ============================================================

    def get_alertes_recours(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les alertes actives sur les recours.
        
        Alertes CDC :
        - REC-AL-001 : Recours sans relance depuis 30 jours
        - REC-AL-002 : Recours sans réponse depuis 60 jours
        - REC-AL-003 : Recours proche prescription
        - REC-AL-004 : Encaissement attendu mais non reçu
        - REC-AL-005 : Paiement client en attente
        """
        try:
            from datetime import datetime, timedelta
            
            alertes = []
            today = datetime.utcnow()
            
            # Paramètres
            delai_relance = self.parametre_service.get_valeur('DELAI_RELANCE_AUTO_JOURS', 30)
            delai_reponse = self.parametre_service.get_valeur('DELAI_REPONSE_RELANCE_JOURS', 60)
            seuil_prescription = self.parametre_service.get_valeur('SEUIL_ALERTE_PRESCRIPTION_JOURS', 60)
            delai_prescription_mois = self.parametre_service.get_valeur('DELAI_PRESCRIPTION_RECOURS_MOIS', 24)
            
            # REC-AL-001 : Sans relance depuis X jours
            seuil_relance = today - timedelta(days=delai_relance)
            recours_sans_relance = self.session.query(LometaRecours).filter(
                LometaRecours.statut.in_(['EN_INSTRUCTION', 'RELANCE']),
                LometaRecours.date_derniere_relance < seuil_relance,
                LometaRecours.is_active == True,
            ).all()
            
            for r in recours_sans_relance:
                alertes.append({
                    'code': 'REC-AL-001',
                    'niveau': 'WARNING',
                    'recours_id': r.id,
                    'numero_recours': r.numero_recours,
                    'message': f"Sans relance depuis plus de {delai_relance} jours",
                    'date_reference': r.date_derniere_relance.isoformat() if r.date_derniere_relance else None,
                })
            
            # REC-AL-002 : Sans réponse depuis X jours
            seuil_reponse = today - timedelta(days=delai_reponse)
            relances_sans_reponse = self.session.query(LometaRelanceRecours).filter(
                LometaRelanceRecours.date_relance < seuil_reponse,
                LometaRelanceRecours.reponse_recue == False,
                LometaRelanceRecours.is_active == True,
            ).all()
            
            for rel in relances_sans_reponse:
                alertes.append({
                    'code': 'REC-AL-002',
                    'niveau': 'WARNING',
                    'recours_id': rel.recours_id,
                    'relance_id': rel.id,
                    'message': f"Sans réponse depuis plus de {delai_reponse} jours",
                    'date_reference': rel.date_relance.isoformat() if rel.date_relance else None,
                })
            
            # REC-AL-003 : Proche prescription
            seuil_prescription_date = today + timedelta(days=seuil_prescription)
            recours_proches = self.session.query(LometaRecours).filter(
                LometaRecours.statut.notin_(['CLOTURE', 'REFUSE', 'PAYE', 'COMPTABILISE']),
                LometaRecours.date_ouverture < seuil_prescription_date,
                LometaRecours.is_active == True,
            ).all()
            
            for r in recours_proches:
                mois_ecoules = (today - r.date_ouverture).days // 30 if r.date_ouverture else 0
                if mois_ecoules >= (delai_prescription_mois - 2):
                    alertes.append({
                        'code': 'REC-AL-003',
                        'niveau': 'CRITICAL',
                        'recours_id': r.id,
                        'numero_recours': r.numero_recours,
                        'message': f"Prescription dans moins de {seuil_prescription} jours",
                        'date_reference': r.date_ouverture.isoformat() if r.date_ouverture else None,
                    })
            
            # REC-AL-004 : Encaissement attendu non reçu
            seuil_accord = today - timedelta(days=30)
            recours_accordes = self.session.query(LometaRecours).filter(
                LometaRecours.statut == 'EN_ATTENTE_ENCAISSEMENT',
                LometaRecours.date_accord < seuil_accord,
                LometaRecours.is_active == True,
            ).all()
            
            for r in recours_accordes:
                alertes.append({
                    'code': 'REC-AL-004',
                    'niveau': 'WARNING',
                    'recours_id': r.id,
                    'numero_recours': r.numero_recours,
                    'message': "Encaissement attendu mais non reçu (> 30 jours)",
                    'date_reference': r.date_accord.isoformat() if r.date_accord else None,
                })
            
            # REC-AL-005 : Paiement client en attente
            seuil_reversement = today - timedelta(days=15)
            reversements_attente = self.session.query(LometaReversementRecours).filter(
                LometaReversementRecours.est_paye == False,
                LometaReversementRecours.date_reversement < seuil_reversement,
                LometaReversementRecours.is_active == True,
            ).all()
            
            for rev in reversements_attente:
                alertes.append({
                    'code': 'REC-AL-005',
                    'niveau': 'WARNING',
                    'recours_id': rev.recours_id,
                    'reversement_id': rev.id,
                    'message': f"Paiement client en attente depuis plus de 15 jours",
                    'date_reference': rev.date_reversement.isoformat() if rev.date_reversement else None,
                })
            
            return alertes
            
        except Exception as e:
            self.session.rollback()
            raise e


    def get_statistiques_alertes(self) -> Dict[str, int]:
        """Retourne un compteur d'alertes par type"""
        try:
            alertes = self.get_alertes_recours()
            compteur = {}
            for a in alertes:
                code = a['code']
                compteur[code] = compteur.get(code, 0) + 1
            return compteur
        except Exception as e:
            return {}

    # ============================================================
    # GESTION DES TIERS
    # ============================================================

    def get_all_tiers(self, actifs_only: bool = True) -> List[dict]:
        """
        Récupère tous les tiers actifs.
        
        Returns:
            Liste de dicts sérialisés
        """
        try:
            from addons.sinistres.models.sinistre import LometaTiers
            
            query = self.session.query(LometaTiers).filter(
                LometaTiers.is_active == True
            )
            if actifs_only:
                query = query.filter(LometaTiers.is_active == True)
            
            tiers = query.order_by(LometaTiers.nom).all()
            
            return [
                {
                    'id': t.id,
                    'code': getattr(t, 'code', None),
                    'nom': t.nom or '',
                    'prenom': t.prenom or '',
                    'nom_complet': f"{t.nom or ''} {t.prenom or ''}".strip(),
                    'type_tiers': getattr(t, 'type_tiers', None),
                    'telephone': getattr(t, 'telephone', None),
                    'email': getattr(t, 'email', None),
                    'adresse': getattr(t, 'adresse', None),
                    'is_active': t.is_active,
                }
                for t in tiers
            ]
        except Exception as e:
            self.session.rollback()
            raise e

    def get_historique_recours(self, recours_id: int) -> List[Dict[str, Any]]:
        """
        Récupère l'historique complet d'un recours.
        
        Retourne une liste d'événements triés chronologiquement :
        - CREATION : création du recours
        - RELANCE : relances effectuées
        - CHANGEMENT_STATUT : changements de statut
        - ENCAISSEMENT : encaissements
        - REPARTITION : répartitions calculées
        - REVERSEMENT : reversements créés/payés
        - COMPTABILISATION : écritures comptables
        """
        try:
            recours = self.get_recours(recours_id)
            if not recours:
                return []
            
            evenements = []
            
            # ============================================================
            # 1. Création
            # ============================================================
            evenements.append({
                'date': recours.date_ouverture.isoformat() if recours.date_ouverture else None,
                'type': 'CREATION',
                'titre': 'Création du recours',
                'description': f"Montant réclamé : {float(recours.montant_reclame or 0):,.0f} FCFA",
                'icone': '🆕',
                'couleur': '#1a73e8',
                'montant': float(recours.montant_reclame or 0),
            })
            
            # ============================================================
            # 2. Accord (si présent)
            # ============================================================
            if recours.date_accord:
                evenements.append({
                    'date': recours.date_accord.isoformat(),
                    'type': 'ACCORD',
                    'titre': 'Accord obtenu',
                    'description': f"Montant accepté : {float(recours.montant_accepte or 0):,.0f} FCFA",
                    'icone': '🤝',
                    'couleur': '#22c55e',
                    'montant': float(recours.montant_accepte or 0),
                })
            
            # ============================================================
            # 3. Encaissements
            # ============================================================
            encaissements = self.get_encaissements(recours_id)
            for enc in encaissements:
                evenements.append({
                    'date': enc.date_encaissement.isoformat() if enc.date_encaissement else None,
                    'type': 'ENCAISSEMENT',
                    'titre': f"Encaissement {enc.mode_encaissement}",
                    'description': (
                        f"Montant : {float(enc.montant or 0):,.0f} FCFA"
                        + (f" | Réf : {enc.reference_bancaire}" if enc.reference_bancaire else "")
                        + (" | Partiel" if enc.est_partiel else "")
                    ),
                    'icone': '💰',
                    'couleur': '#22c55e',
                    'montant': float(enc.montant or 0),
                })
            
            # ============================================================
            # 4. Répartitions
            # ============================================================
            repartitions = self.get_repartitions(recours_id)
            if repartitions:
                # Grouper toutes les répartitions en un seul événement
                details = ", ".join([
                    f"{r.type_beneficiaire} {r.quote_part}%"
                    for r in repartitions
                ])
                montant_total = sum(float(r.montant or 0) for r in repartitions)
                evenements.append({
                    'date': max(
                        (r.created_at.isoformat() for r in repartitions if r.created_at),
                        default=None
                    ),
                    'type': 'REPARTITION',
                    'titre': f"Répartition calculée ({len(repartitions)} part(s))",
                    'description': details,
                    'icone': '📊',
                    'couleur': '#06b6d4',
                    'montant': montant_total,
                })
            
            # ============================================================
            # 5. Reversements
            # ============================================================
            reversements = self.get_reversements(recours_id)
            for rev in reversements:
                statut = "✅ Payé" if rev.est_paye else "⏳ En attente"
                evenements.append({
                    'date': rev.date_reversement.isoformat() if rev.date_reversement else None,
                    'type': 'REVERSEMENT',
                    'titre': f"Reversement {rev.beneficiaire_nom or ''} ({statut})",
                    'description': (
                        f"Montant : {float(rev.montant or 0):,.0f} FCFA "
                        f"({rev.quote_part}%) | Mode : {rev.mode_paiement}"
                    ),
                    'icone': '💸',
                    'couleur': '#8b5cf6' if not rev.est_paye else '#22c55e',
                    'montant': float(rev.montant or 0),
                })
            
            # ============================================================
            # 6. Relances
            # ============================================================
            relances = self.get_relances(recours_id)
            for rel in relances:
                evenements.append({
                    'date': rel.date_relance.isoformat() if rel.date_relance else None,
                    'type': 'RELANCE',
                    'titre': f"Relance {rel.type_relance}",
                    'description': (rel.contenu or '')[:100] + ('...' if rel.contenu and len(rel.contenu) > 100 else ''),
                    'icone': '🔔',
                    'couleur': '#f59e0b',
                    'montant': None,
                })
            
            # ============================================================
            # 7. Écritures comptables
            # ============================================================
            try:
                from addons.sinistres.services.comptabilite_service import ComptabiliteService
                comptabilite_service = ComptabiliteService(self.session)
                ecritures = comptabilite_service.get_ecritures_by_recours(recours_id)
                
                for ecr in ecritures:
                    evenements.append({
                        'date': ecr.date_ecriture.isoformat() if ecr.date_ecriture else None,
                        'type': 'COMPTABILISATION',
                        'titre': f"Écriture comptable {ecr.numero_ecriture}",
                        'description': (
                            f"Débit {ecr.compte_debit} / Crédit {ecr.compte_credit} "
                            f"| {float(ecr.montant or 0):,.0f} FCFA"
                        ),
                        'icone': '📒',
                        'couleur': '#6366f1',
                        'montant': float(ecr.montant or 0),
                    })
            except Exception as e:
                print(f"⚠️ Erreur chargement écritures: {e}")
            
            # ============================================================
            # 8. Clôture (si présente)
            # ============================================================
            if recours.date_cloture:
                evenements.append({
                    'date': recours.date_cloture.isoformat(),
                    'type': 'CLOTURE',
                    'titre': 'Recours clôturé',
                    'description': recours.motif_cloture or 'Aucun motif',
                    'icone': '🔒',
                    'couleur': '#64748b',
                    'montant': None,
                })
            
            # ============================================================
            # Trier chronologiquement
            # ============================================================
            evenements.sort(key=lambda e: e.get('date') or '')
            
            return evenements
            
        except Exception as e:
            self.session.rollback()
            raise e