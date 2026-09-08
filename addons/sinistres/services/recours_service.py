"""
Service de gestion des recours (Tome 6 du CDC)
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from addons.sinistres.services.base_service import BaseService
from addons.sinistres.models.recours import (
    LometaRecours, LometaEncaissementRecours, LometaReversementRecours, LometaRelanceRecours
)
from addons.sinistres.models.sinistre import LometaSinistre
from addons.sinistres.models.reglement import LometaBeneficiaire


class RecoursService(BaseService):
    """Service de gestion des recours"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # GESTION DES RECOURS
    # ============================================================
    
    def creer_recours(self, data: Dict[str, Any]) -> LometaRecours:
        """Crée un nouveau recours"""
        try:
            # Vérifier que le sinistre existe
            sinistre = self.session.query(LometaSinistre).filter(
                LometaSinistre.id == data.get('sinistre_id'),
                LometaSinistre.is_active == True
            ).first()
            if not sinistre:
                raise ValueError("Sinistre non trouvé")
            
            # Générer le numéro
            numero = self.generate_numero("REC", LometaRecours, 'numero_recours')
            
            recours = LometaRecours(
                numero_recours=numero,
                statut="OUVERT",
                date_ouverture=datetime.utcnow(),
                solde=data.get('montant_reclame', 0),
                **data
            )
            
            self.session.add(recours)
            self.session.flush()
            
            # Mettre à jour le statut du sinistre
            if sinistre.statut not in ["EN_RECOURS", "CLOTURE"]:
                sinistre.statut = "EN_RECOURS"
                sinistre.updated_at = datetime.utcnow()
                sinistre.updated_by = data.get('created_by')
            
            self.log_audit(
                utilisateur_id=data.get('created_by'),
                action="CREATION",
                entite="Recours",
                entite_id=recours.id,
                entite_nom=recours.numero_recours,
                commentaire=f"Création du recours {recours.numero_recours} - Montant réclamé: {recours.montant_reclame}"
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
    
    def enregistrer_encaissement(self, recours_id: int, data: Dict[str, Any], utilisateur_id: int) -> Optional[LometaEncaissementRecours]:
        """Enregistre un encaissement"""
        try:
            recours = self.get_recours(recours_id)
            if not recours:
                raise ValueError("Recours non trouvé")
            
            if recours.statut not in ["EN_ATTENTE_ENCAISSEMENT", "PARTIELLEMENT_ENCAISSE"]:
                raise ValueError("Le recours n'est pas en attente d'encaissement")
            
            montant = data.get('montant', 0)
            if montant <= 0:
                raise ValueError("Le montant doit être positif")
            
            if montant > recours.solde:
                raise ValueError(f"Le montant ({montant}) dépasse le solde restant ({recours.solde})")
            
            # Créer l'encaissement
            encaissement = LometaEncaissementRecours(
                recours_id=recours_id,
                solde_apres_encaissement=recours.solde - montant,
                **data
            )
            
            self.session.add(encaissement)
            self.session.flush()
            
            # Mettre à jour le recours
            recours.montant_encaisse += montant
            recours.solde = recours.montant_reclame - recours.montant_encaisse
            
            if recours.solde == 0:
                recours.statut = "ENCAISSE"
            else:
                recours.statut = "PARTIELLEMENT_ENCAISSE"
            
            recours.updated_at = datetime.utcnow()
            recours.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="ENCAISSEMENT",
                entite="Recours",
                entite_id=recours.id,
                entite_nom=recours.numero_recours,
                commentaire=f"Encaissement de {montant} - Solde restant: {recours.solde}"
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
        """Ajoute une relance à un recours"""
        try:
            recours = self.get_recours(recours_id)
            if not recours:
                raise ValueError("Recours non trouvé")
            
            relance = LometaRelanceRecours(
                recours_id=recours_id,
                effectue_par=utilisateur_id,
                **data
            )
            
            self.session.add(relance)
            self.session.flush()
            
            # Mettre à jour le recours
            recours.nombre_relances += 1
            recours.date_derniere_relance = datetime.utcnow()
            recours.date_prochaine_relance = datetime.utcnow() + timedelta(days=data.get('delai_prochain', 30))
            
            if recours.statut == "EN_INSTRUCTION":
                recours.statut = "RELANCE"
            
            recours.updated_at = datetime.utcnow()
            recours.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="RELANCE",
                entite="Recours",
                entite_id=recours.id,
                entite_nom=recours.numero_recours,
                commentaire=f"Relance {recours.nombre_relances} - Type: {data.get('type_relance', 'inconnu')}"
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

    # Ajouter ces méthodes à la fin de la classe RecoursService

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