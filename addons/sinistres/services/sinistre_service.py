"""
Service de gestion des sinistres - Adapté pour votre infrastructure DB
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, between
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from addons.sinistres.models.expertise import LometaExpertise
from addons.sinistres.services.base_service import BaseService
from addons.sinistres.models.sinistre import (
    LometaSinistre, LometaDommage, LometaTiers, LometaCommentaireSinistre, LometaHistoriqueSinistre
)
from addons.sinistres.models.referentiel import LometaReferentiel
from addons.Paramètres.models.models import User


class SinistreService(BaseService):
    """Service de gestion des sinistres"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # CRUD PRINCIPAL
    # ============================================================
    
    def creer_sinistre(self, data: Dict[str, Any]) -> LometaSinistre:
        """Crée un nouveau sinistre"""
        try:
            # Vérifier que l'utilisateur existe
            if data.get('created_by'):
                user = self.get_user(data['created_by'])
                if not user:
                    raise ValueError(f"Utilisateur {data['created_by']} inexistant")
            
            # Générer le numéro unique
            numero = self.generate_numero("SIN", LometaSinistre, 'numero_sinistre')
            
            sinistre = LometaSinistre(
                numero_sinistre=numero,
                date_ouverture=datetime.utcnow(),
                statut="OUVERT",
                **data
            )
            
            self.session.add(sinistre)
            self.session.flush()
            
            # Enregistrer l'historique
            self._enregistrer_historique(
                sinistre_id=sinistre.id,
                utilisateur_id=data.get('created_by'),
                action="CREATION",
                entite="Sinistre",
                nouvelle_valeur=f"Création du sinistre {sinistre.numero_sinistre}"
            )
            
            self.session.commit()
            return sinistre
            
        except Exception as e:
            self.session.rollback()
            raise e

    def get_all_missions(self) -> List[LometaExpertise]:
        """Récupère toutes les missions d'expertise"""
        try:
            return self.session.query(LometaExpertise).filter(
                LometaExpertise.is_active == True
            ).order_by(LometaExpertise.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_sinistre(self, sinistre_id: int) -> Optional[LometaSinistre]:
        """Récupère un sinistre par son ID"""
        try:
            return self.session.query(LometaSinistre).filter(
                LometaSinistre.id == sinistre_id,
                LometaSinistre.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_sinistre_by_numero(self, numero: str) -> Optional[LometaSinistre]:
        """Récupère un sinistre par son numéro"""
        try:
            return self.session.query(LometaSinistre).filter(
                LometaSinistre.numero_sinistre == numero,
                LometaSinistre.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_sinistre(self, sinistre_id: int, data: Dict[str, Any]) -> Optional[LometaSinistre]:
        """Met à jour un sinistre"""
        try:
            sinistre = self.get_sinistre(sinistre_id)
            if not sinistre:
                return None
            
            # Enregistrer les modifications
            for key, value in data.items():
                if hasattr(sinistre, key) and getattr(sinistre, key) != value:
                    ancienne = getattr(sinistre, key)
                    setattr(sinistre, key, value)
                    self._enregistrer_historique(
                        sinistre_id=sinistre.id,
                        utilisateur_id=data.get('updated_by'),
                        action="MODIFICATION",
                        entite="Sinistre",
                        champ_modifie=key,
                        ancienne_valeur=str(ancienne) if ancienne else None,
                        nouvelle_valeur=str(value) if value else None
                    )
            
            sinistre.updated_at = datetime.utcnow()
            sinistre.updated_by = data.get('updated_by')
            sinistre.date_derniere_modification = datetime.utcnow()
            
            self.session.commit()
            return sinistre
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def rechercher_sinistres(self, criteres: Dict[str, Any]) -> List[LometaSinistre]:
        """Recherche des sinistres selon des critères"""
        try:
            query = self.session.query(LometaSinistre).filter(LometaSinistre.is_active == True)
            
            if criteres.get('numero_sinistre'):
                query = query.filter(LometaSinistre.numero_sinistre.ilike(f"%{criteres['numero_sinistre']}%"))
            
            if criteres.get('numero_reference'):
                query = query.filter(LometaSinistre.numero_reference.ilike(f"%{criteres['numero_reference']}%"))
            
            if criteres.get('client_id'):
                query = query.filter(LometaSinistre.client_id == criteres['client_id'])
            
            if criteres.get('contrat_id'):
                query = query.filter(LometaSinistre.contrat_id == criteres['contrat_id'])
            
            if criteres.get('statut'):
                query = query.filter(LometaSinistre.statut == criteres['statut'])
            
            if criteres.get('branche'):
                query = query.filter(LometaSinistre.branche == criteres['branche'])
            
            if criteres.get('categorie'):
                query = query.filter(LometaSinistre.categorie == criteres['categorie'])
            
            if criteres.get('responsable_id'):
                query = query.filter(LometaSinistre.responsable_id == criteres['responsable_id'])
            
            if criteres.get('date_debut') and criteres.get('date_fin'):
                query = query.filter(
                    between(LometaSinistre.date_survenance, criteres['date_debut'], criteres['date_fin'])
                )
            
            # Recherche par montant
            if criteres.get('montant_min'):
                from addons.sinistres.models.expertise import LometaEvaluation
                subquery = self.session.query(LometaEvaluation.sinistre_id).filter(
                    LometaEvaluation.montant_net >= criteres['montant_min']
                )
                query = query.filter(LometaSinistre.id.in_(subquery))
            
            return query.order_by(LometaSinistre.created_at.desc()).limit(100).all()
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # GESTION DU CYCLE DE VIE
    # ============================================================
    
    def changer_statut(
        self,
        sinistre_id: int,
        nouveau_statut: str,
        utilisateur_id: int,
        motif: str = None,
        ip_adresse: str = None
    ) -> LometaSinistre:
        """Change le statut d'un sinistre avec traçabilité"""
        try:
            sinistre = self.get_sinistre(sinistre_id)
            if not sinistre:
                raise ValueError("Sinistre non trouvé")
            
            ancien_statut = sinistre.statut
            
            # Vérifier la transition
            self._verifier_transition(ancien_statut, nouveau_statut)
            
            # Mettre à jour
            sinistre.statut = nouveau_statut
            sinistre.updated_by = utilisateur_id
            sinistre.updated_at = datetime.utcnow()
            
            if nouveau_statut == "CLOTURE":
                sinistre.date_cloture = datetime.utcnow()
            elif nouveau_statut == "REOUVERT":
                sinistre.date_reexamen = datetime.utcnow()
            
            self.session.flush()
            
            self._enregistrer_historique(
                sinistre_id=sinistre.id,
                utilisateur_id=utilisateur_id,
                action="CHANGEMENT_STATUT",
                entite="Sinistre",
                champ_modifie="statut",
                ancienne_valeur=ancien_statut,
                nouvelle_valeur=nouveau_statut,
                commentaire=motif,
                ip_adresse=ip_adresse
            )
            
            self.session.commit()
            return sinistre
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def cloturer_sinistre(
        self,
        sinistre_id: int,
        utilisateur_id: int,
        motif: str,
        ip_adresse: str = None
    ) -> LometaSinistre:
        """Clôture un sinistre"""
        try:
            sinistre = self.get_sinistre(sinistre_id)
            if not sinistre:
                raise ValueError("Sinistre non trouvé")
            
            # Vérifier que toutes les expertises sont terminées
            expertises_en_cours = self.session.query(LometaExpertise).filter(
                LometaExpertise.sinistre_id == sinistre_id,
                LometaExpertise.statut.in_(['CREEE', 'AFFECTEE', 'EN_COURS']),
                LometaExpertise.is_active == True
            ).count()
            
            if expertises_en_cours > 0:
                raise ValueError("Des expertises sont encore en cours")
            
            # Vérifier que tous les règlements sont payés
            from addons.sinistres.models.reglement import LometaReglement
            reglements_non_payes = self.session.query(LometaReglement).filter(
                LometaReglement.sinistre_id == sinistre_id,
                LometaReglement.statut.in_(['CREE', 'VALIDE', 'EN_ATTENTE']),
                LometaReglement.is_active == True
            ).count()
            
            if reglements_non_payes > 0:
                raise ValueError("Des règlements sont encore en attente")
            
            return self.changer_statut(
                sinistre_id=sinistre_id,
                nouveau_statut="CLOTURE",
                utilisateur_id=utilisateur_id,
                motif=motif,
                ip_adresse=ip_adresse
            )
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def reouvrir_sinistre(
        self,
        sinistre_id: int,
        utilisateur_id: int,
        motif: str,
        ip_adresse: str = None
    ) -> LometaSinistre:
        """Réouvre un sinistre clôturé"""
        try:
            sinistre = self.get_sinistre(sinistre_id)
            if not sinistre:
                raise ValueError("Sinistre non trouvé")
            
            if sinistre.statut != "CLOTURE":
                raise ValueError("Seul un sinistre clôturé peut être réouvert")
            
            return self.changer_statut(
                sinistre_id=sinistre_id,
                nouveau_statut="REOUVERT",
                utilisateur_id=utilisateur_id,
                motif=motif,
                ip_adresse=ip_adresse
            )
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def _verifier_transition(self, statut_actuel: str, nouveau_statut: str):
        """Vérifie si la transition est autorisée par le workflow"""
        try:
            # Récupérer les transitions depuis le référentiel
            workflow = self.session.query(LometaReferentiel).filter(
                LometaReferentiel.famille == "workflow",
                LometaReferentiel.code == statut_actuel,
                LometaReferentiel.est_actif == True
            ).first()
            
            if workflow and workflow.description:
                transitions_autorisees = [t.strip() for t in workflow.description.split(',')]
            else:
                transitions_autorisees = self._get_default_transitions(statut_actuel)
            
            if nouveau_statut not in transitions_autorisees:
                raise ValueError(
                    f"Transition non autorisée: {statut_actuel} -> {nouveau_statut}"
                )
        except Exception as e:
            raise e
    
    def _get_default_transitions(self, statut_actuel: str) -> List[str]:
        """Transitions par défaut (fallback)"""
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
    # GESTION DES DOMMAGES
    # ============================================================
    
    def ajouter_dommage(self, sinistre_id: int, data: Dict[str, Any]) -> LometaDommage:
        """Ajoute un dommage à un sinistre"""
        try:
            sinistre = self.get_sinistre(sinistre_id)
            if not sinistre:
                raise ValueError("Sinistre non trouvé")
            
            dommage = LometaDommage(
                sinistre_id=sinistre_id,
                **data
            )
            
            self.session.add(dommage)
            self.session.commit()
            return dommage
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_dommages(self, sinistre_id: int) -> List[LometaDommage]:
        """Récupère tous les dommages d'un sinistre"""
        try:
            return self.session.query(LometaDommage).filter(
                LometaDommage.sinistre_id == sinistre_id,
                LometaDommage.is_active == True
            ).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # GESTION DES TIERS
    # ============================================================
    
    def ajouter_tiers(self, sinistre_id: int, data: Dict[str, Any]) -> LometaTiers:
        """Ajoute un tiers à un sinistre"""
        try:
            sinistre = self.get_sinistre(sinistre_id)
            if not sinistre:
                raise ValueError("Sinistre non trouvé")
            
            tiers = LometaTiers(
                sinistre_id=sinistre_id,
                **data
            )
            
            self.session.add(tiers)
            self.session.commit()
            return tiers
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_tiers(self, sinistre_id: int) -> List[LometaTiers]:
        """Récupère tous les tiers d'un sinistre"""
        try:
            return self.session.query(LometaTiers).filter(
                LometaTiers.sinistre_id == sinistre_id,
                LometaTiers.is_active == True
            ).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # GESTION DES COMMENTAIRES
    # ============================================================
    
    def ajouter_commentaire(
        self,
        sinistre_id: int,
        utilisateur_id: int,
        contenu: str,
        type_commentaire: str
    ) -> LometaCommentaireSinistre:
        """Ajoute un commentaire au sinistre (versionné)"""
        try:
            sinistre = self.get_sinistre(sinistre_id)
            if not sinistre:
                raise ValueError("Sinistre non trouvé")
            
            # Récupérer la dernière version
            dernier = self.session.query(LometaCommentaireSinistre).filter(
                LometaCommentaireSinistre.sinistre_id == sinistre_id
            ).order_by(LometaCommentaireSinistre.version.desc()).first()
            
            version = (dernier.version + 1) if dernier else 1
            
            commentaire = LometaCommentaireSinistre(
                sinistre_id=sinistre_id,
                utilisateur_id=utilisateur_id,
                contenu=contenu,
                type_commentaire=type_commentaire,
                version=version,
                created_by=utilisateur_id
            )
            
            self.session.add(commentaire)
            self.session.commit()
            return commentaire
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_commentaires(self, sinistre_id: int) -> List[LometaCommentaireSinistre]:
        """Récupère tous les commentaires d'un sinistre"""
        try:
            return self.session.query(LometaCommentaireSinistre).filter(
                LometaCommentaireSinistre.sinistre_id == sinistre_id,
                LometaCommentaireSinistre.is_active == True
            ).order_by(LometaCommentaireSinistre.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # MÉTHODES PRIVÉES
    # ============================================================
    
    def _enregistrer_historique(
        self,
        sinistre_id: int,
        utilisateur_id: int,
        action: str,
        entite: str,
        champ_modifie: str = None,
        ancienne_valeur: str = None,
        nouvelle_valeur: str = None,
        commentaire: str = None,
        ip_adresse: str = None,
        session_id: str = None
    ):
        """Enregistre une entrée dans l'historique du sinistre"""
        try:
            # Récupérer le nom de l'utilisateur
            user_info = self.get_user_info(utilisateur_id)
            
            historique = LometaHistoriqueSinistre(
                sinistre_id=sinistre_id,
                utilisateur_id=utilisateur_id,
                utilisateur_nom=user_info.get('full_name') or user_info.get('username'),
                action=action,
                entite=entite,
                champ_modifie=champ_modifie,
                ancienne_valeur=ancienne_valeur,
                nouvelle_valeur=nouvelle_valeur,
                commentaire=commentaire,
                ip_adresse=ip_adresse,
                session_id=session_id,
                date_action=datetime.utcnow()
            )
            self.session.add(historique)
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # INDICATEURS ET STATISTIQUES
    # ============================================================
    
    def get_statistiques(self, branche: str = None) -> Dict[str, Any]:
        """Récupère les statistiques des sinistres"""
        try:
            query = self.session.query(LometaSinistre).filter(LometaSinistre.is_active == True)
            
            if branche:
                query = query.filter(LometaSinistre.branche == branche)
            
            total = query.count()
            
            # Par statut
            par_statut = {}
            for statut in ['OUVERT', 'EN_INSTRUCTION', 'EN_EXPERTISE', 'EN_EVALUATION', 
                          'VALIDE', 'EN_REGLEMENT', 'EN_RECOURS', 'CLOTURE']:
                count = query.filter(LometaSinistre.statut == statut).count()
                if count > 0:
                    par_statut[statut] = count
            
            # Délais moyens
            from sqlalchemy import func
            delai_moyen = query.filter(
                LometaSinistre.date_cloture.isnot(None)
            ).with_entities(
                func.avg(func.extract('epoch', LometaSinistre.date_cloture - LometaSinistre.date_ouverture) / 86400)
            ).scalar()
            
            return {
                'total': total,
                'par_statut': par_statut,
                'delai_moyen_cloture': round(delai_moyen, 1) if delai_moyen else None
            }
        except Exception as e:
            self.session.rollback()
            raise e