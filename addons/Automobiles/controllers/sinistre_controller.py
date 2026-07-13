# addons/Automobiles/controllers/sinistre_controller.py
"""
Contrôleur pour la gestion des sinistres
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, and_, or_

from core import logger
from addons.Automobiles.models.sinistre_models import Sinistre, TypeSinistre, StatutSinistre, Responsabilite, Indemnisation


class SinistreController:
    """Contrôleur des sinistres"""

    def __init__(self, session: Session, current_user_id: int = None):
        self.session = session
        self.current_user_id = current_user_id

    # ========================================================================
    # CRUD PRINCIPAL
    # ========================================================================

    def get_all(self, filters: Dict = None) -> List[Sinistre]:
        """
        Récupère tous les sinistres avec filtres optionnels
        
        Args:
            filters: {
                'statut': str,
                'type': str,
                'client_id': int,
                'vehicule_id': int,
                'contrat_id': int,
                'date_debut': datetime,
                'date_fin': datetime,
                'search': str,
                'limit': int,
                'offset': int
            }
        """
        try:
            query = self.session.query(Sinistre).options(
                joinedload(Sinistre.contrat),
                joinedload(Sinistre.vehicule),
                joinedload(Sinistre.client),
                selectinload(Sinistre.expertise),
                selectinload(Sinistre.paiements)
            )

            if filters:
                if filters.get('statut'):
                    query = query.filter_by(statut=filters['statut'])
                if filters.get('type'):
                    query = query.filter_by(type=filters['type'])
                if filters.get('client_id'):
                    query = query.filter_by(client_id=filters['client_id'])
                if filters.get('vehicule_id'):
                    query = query.filter_by(vehicule_id=filters['vehicule_id'])
                if filters.get('contrat_id'):
                    query = query.filter_by(contrat_id=filters['contrat_id'])
                if filters.get('date_debut'):
                    query = query.filter(Sinistre.date_survenue >= filters['date_debut'])
                if filters.get('date_fin'):
                    query = query.filter(Sinistre.date_survenue <= filters['date_fin'])
                if filters.get('search'):
                    search = filters['search']
                    query = query.filter(
                        or_(
                            Sinistre.numero_dossier.contains(search),
                            Sinistre.description.contains(search),
                            Sinistre.lieu.contains(search)
                        )
                    )
                if filters.get('limit'):
                    query = query.limit(filters['limit'])
                if filters.get('offset'):
                    query = query.offset(filters['offset'])

            return query.order_by(Sinistre.date_declaration.desc()).all()

        except Exception as e:
            logger.error(f"Erreur récupération sinistres: {e}")
            return []

    def get_by_id(self, sinistre_id: int) -> Optional[Sinistre]:
        """Récupère un sinistre par son ID avec toutes ses relations"""
        try:
            return self.session.query(Sinistre).options(
                joinedload(Sinistre.contrat),
                joinedload(Sinistre.vehicule),
                joinedload(Sinistre.client),
                selectinload(Sinistre.expertise),
                selectinload(Sinistre.paiements)
            ).filter_by(id=sinistre_id).first()
        except Exception as e:
            logger.error(f"Erreur récupération sinistre {sinistre_id}: {e}")
            return None

    def get_by_numero_dossier(self, numero_dossier: str) -> Optional[Sinistre]:
        """Récupère un sinistre par son numéro de dossier"""
        try:
            return self.session.query(Sinistre).filter_by(
                numero_dossier=numero_dossier
            ).first()
        except Exception as e:
            logger.error(f"Erreur récupération sinistre par dossier: {e}")
            return None

    def create(self, data: Dict) -> Optional[Sinistre]:
        """
        Crée un nouveau sinistre
        
        Args:
            data: {
                'contrat_id': int,
                'vehicule_id': int,
                'client_id': int,
                'type': TypeSinistre,
                'date_survenue': datetime,
                'lieu': str,
                'ville': str,
                'description': str,
                'circonstances': str,
                'estimation_preliminaire': float,
                'tiers_nom': str,
                'tiers_prenom': str,
                'tiers_telephone': str,
                'tiers_assurance': str,
                'tiers_police': str,
                'assigned_to': int,
                'creer_expertise': bool
            }
        """
        try:
            # Générer le numéro de dossier
            import time
            timestamp = int(time.time())
            numero_dossier = f"SIN-{timestamp}-{data.get('vehicule_id', '')}"

            sinistre = Sinistre(
                numero_dossier=numero_dossier,
                contrat_id=data['contrat_id'],
                vehicule_id=data['vehicule_id'],
                client_id=data['client_id'],
                type=data['type'],
                statut=StatutSinistre.DECLARE,
                date_survenue=data['date_survenue'],
                lieu=data.get('lieu'),
                ville=data.get('ville', 'Yaoundé'),
                pays=data.get('pays', 'Cameroun'),
                description=data.get('description'),
                circonstances=data.get('circonstances'),
                conditions_meteo=data.get('conditions_meteo'),
                tiers_nom=data.get('tiers_nom'),
                tiers_prenom=data.get('tiers_prenom'),
                tiers_telephone=data.get('tiers_telephone'),
                tiers_assurance=data.get('tiers_assurance'),
                tiers_police=data.get('tiers_police'),
                tiers_vehicule=data.get('tiers_vehicule'),
                temoins_noms=data.get('temoins_noms'),
                temoins_nombre=data.get('temoins_nombre', 0),
                estimation_preliminaire=data.get('estimation_preliminaire', 0.0),
                created_by=self.current_user_id,
                assigned_to=data.get('assigned_to'),
                notes=data.get('notes')
            )

            self.session.add(sinistre)
            self.session.flush()

            # Créer une expertise préliminaire automatiquement
            if data.get('creer_expertise', True):
                from addons.Automobiles.controllers.expertise_controller import ExpertiseController
                exp_controller = ExpertiseController(self.session, self.current_user_id)
                exp_controller.create_for_sinistre(
                    sinistre_id=sinistre.id,
                    data={
                        'type': 'preliminaire',
                        'statut': 'planifiee'
                    }
                )

            self.session.commit()
            logger.info(f"Sinistre créé: {sinistre.numero_dossier}")
            return sinistre

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur création sinistre: {e}")
            return None

    def update(self, sinistre_id: int, data: Dict) -> bool:
        """Met à jour un sinistre"""
        try:
            sinistre = self.get_by_id(sinistre_id)
            if not sinistre:
                return False

            editable_fields = [
                'type', 'statut', 'responsabilite', 'lieu', 'ville',
                'description', 'circonstances', 'conditions_meteo',
                'estimation_preliminaire', 'estimation_finale',
                'montant_indemnise', 'franchise', 'montant_net',
                'assigned_to', 'notes',
                'tiers_nom', 'tiers_prenom', 'tiers_telephone',
                'tiers_assurance', 'tiers_police', 'tiers_vehicule',
                'temoins_noms', 'temoins_nombre'
            ]

            for field in editable_fields:
                if field in data:
                    setattr(sinistre, field, data[field])

            sinistre.updated_at = datetime.utcnow()
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur mise à jour sinistre: {e}")
            return False

    def delete(self, sinistre_id: int) -> bool:
        """Supprime un sinistre (soft delete ou hard delete)"""
        try:
            sinistre = self.get_by_id(sinistre_id)
            if not sinistre:
                return False

            # Si le sinistre est clos, on peut le supprimer
            if sinistre.statut == StatutSinistre.CLOS:
                self.session.delete(sinistre)
            else:
                # Sinon on le passe en statut annulé
                sinistre.statut = StatutSinistre.REJETE
                sinistre.notes = (sinistre.notes or "") + "\n[SUPPRIMÉ] Dossier annulé"

            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur suppression sinistre: {e}")
            return False

    # ========================================================================
    # MÉTHODES DE STATUT
    # ========================================================================

    def changer_statut(self, sinistre_id: int, nouveau_statut: StatutSinistre, 
                       commentaire: str = None) -> bool:
        """Change le statut d'un sinistre"""
        try:
            sinistre = self.get_by_id(sinistre_id)
            if not sinistre:
                return False

            ancien_statut = sinistre.statut
            sinistre.statut = nouveau_statut

            if commentaire:
                sinistre.notes = (sinistre.notes or "") + f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M')}] {commentaire}"

            if nouveau_statut == StatutSinistre.CLOS:
                sinistre.date_fermeture = datetime.utcnow()

            if nouveau_statut == StatutSinistre.INDEMNISE:
                sinistre.date_fermeture = datetime.utcnow()

            self.session.commit()
            logger.info(f"Sinistre {sinistre.numero_dossier}: {ancien_statut.value} → {nouveau_statut.value}")
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur changement statut: {e}")
            return False

    def valider_sinistre(self, sinistre_id: int, montant_indemnise: float = None) -> bool:
        """Valide un sinistre (passage en VALIDE)"""
        try:
            sinistre = self.get_by_id(sinistre_id)
            if not sinistre:
                return False

            sinistre.statut = StatutSinistre.VALIDE
            if montant_indemnise is not None:
                sinistre.montant_indemnise = montant_indemnise

            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur validation sinistre: {e}")
            return False

    def rejeter_sinistre(self, sinistre_id: int, motif: str) -> bool:
        """Rejette un sinistre"""
        try:
            sinistre = self.get_by_id(sinistre_id)
            if not sinistre:
                return False

            sinistre.statut = StatutSinistre.REJETE
            sinistre.notes = (sinistre.notes or "") + f"\n[MOTIF REJET] {motif}"

            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur rejet sinistre: {e}")
            return False

    # ========================================================================
    # STATISTIQUES
    # ========================================================================

    def get_stats(self) -> Dict:
        """Statistiques des sinistres"""
        try:
            total = self.session.query(Sinistre).count()

            # Par statut
            by_status = {}
            for statut in StatutSinistre:
                count = self.session.query(Sinistre).filter_by(statut=statut).count()
                if count > 0:
                    by_status[statut.value] = count

            # Par type
            by_type = {}
            for type_ in TypeSinistre:
                count = self.session.query(Sinistre).filter_by(type=type_).count()
                if count > 0:
                    by_type[type_.value] = count

            # En cours (non clos)
            en_cours = self.session.query(Sinistre).filter(
                Sinistre.statut.in_([
                    StatutSinistre.DECLARE,
                    StatutSinistre.EN_INSTRUCTION,
                    StatutSinistre.EN_ATTENTE,
                    StatutSinistre.EXPERTISE
                ])
            ).count()

            # Clos
            clos = self.session.query(Sinistre).filter_by(statut=StatutSinistre.CLOS).count()

            # Urgents (> 15 jours)
            date_limite = datetime.utcnow() - timedelta(days=15)
            urgents = self.session.query(Sinistre).filter(
                Sinistre.date_declaration <= date_limite,
                Sinistre.statut.in_([
                    StatutSinistre.DECLARE,
                    StatutSinistre.EN_INSTRUCTION,
                    StatutSinistre.EN_ATTENTE,
                    StatutSinistre.EXPERTISE
                ])
            ).count()

            # Montant total indemnisé
            total_indemnise = self.session.query(
                func.sum(Sinistre.montant_indemnise)
            ).scalar() or 0.0

            return {
                'total': total,
                'en_cours': en_cours,
                'clos': clos,
                'urgents': urgents,
                'by_status': by_status,
                'by_type': by_type,
                'taux_traitement': round((clos / total * 100) if total > 0 else 0, 1),
                'total_indemnise': total_indemnise
            }

        except Exception as e:
            logger.error(f"Erreur statistiques sinistres: {e}")
            return {
                'total': 0,
                'en_cours': 0,
                'clos': 0,
                'urgents': 0,
                'by_status': {},
                'by_type': {},
                'taux_traitement': 0,
                'total_indemnise': 0.0
            }

    # ========================================================================
    # INDENNISATIONS
    # ========================================================================

    def ajouter_paiement_indemnisation(self, sinistre_id: int, data: Dict) -> Optional[Indemnisation]:
        """
        Ajoute un paiement d'indemnisation à un sinistre
        
        Args:
            sinistre_id: ID du sinistre
            data: {
                'montant': float,
                'franchise_appliquee': float,
                'mode_paiement': str,
                'reference_paiement': str,
                'beneficiaire': str,
                'justificatif': str
            }
        """
        try:
            sinistre = self.get_by_id(sinistre_id)
            if not sinistre:
                return None

            montant_net = data.get('montant', 0) - data.get('franchise_appliquee', 0)

            indemnisation = Indemnisation(
                sinistre_id=sinistre_id,
                montant=data.get('montant', 0),
                franchise_appliquee=data.get('franchise_appliquee', 0),
                montant_net=montant_net,
                mode_paiement=data.get('mode_paiement', 'virement'),
                reference_paiement=data.get('reference_paiement'),
                beneficiaire=data.get('beneficiaire'),
                justificatif=data.get('justificatif'),
                created_by=self.current_user_id
            )

            self.session.add(indemnisation)

            # Mettre à jour le montant indemnisé du sinistre
            sinistre.montant_indemnise = (sinistre.montant_indemnise or 0) + montant_net

            self.session.commit()
            return indemnisation

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur ajout indemnisation: {e}")
            return None

    # ========================================================================
    # RECHERCHES SPÉCIFIQUES
    # ========================================================================

    def get_sinistres_by_client(self, client_id: int) -> List[Sinistre]:
        """Récupère tous les sinistres d'un client"""
        try:
            return self.session.query(Sinistre).filter_by(
                client_id=client_id
            ).order_by(Sinistre.date_declaration.desc()).all()
        except Exception as e:
            logger.error(f"Erreur récupération sinistres client: {e}")
            return []

    def get_sinistres_by_vehicule(self, vehicule_id: int) -> List[Sinistre]:
        """Récupère tous les sinistres d'un véhicule"""
        try:
            return self.session.query(Sinistre).filter_by(
                vehicule_id=vehicule_id
            ).order_by(Sinistre.date_declaration.desc()).all()
        except Exception as e:
            logger.error(f"Erreur récupération sinistres véhicule: {e}")
            return []

    def get_sinistres_by_period(self, date_debut: datetime, date_fin: datetime) -> List[Sinistre]:
        """Récupère les sinistres sur une période"""
        try:
            return self.session.query(Sinistre).filter(
                Sinistre.date_survenue.between(date_debut, date_fin)
            ).order_by(Sinistre.date_survenue).all()
        except Exception as e:
            logger.error(f"Erreur récupération sinistres période: {e}")
            return []

    def get_sinistres_urgents(self) -> List[Sinistre]:
        """Récupère les sinistres urgents (> 15 jours sans action)"""
        try:
            date_limite = datetime.utcnow() - timedelta(days=15)
            return self.session.query(Sinistre).filter(
                Sinistre.date_declaration <= date_limite,
                Sinistre.statut.in_([
                    StatutSinistre.DECLARE,
                    StatutSinistre.EN_INSTRUCTION,
                    StatutSinistre.EN_ATTENTE,
                    StatutSinistre.EXPERTISE
                ])
            ).order_by(Sinistre.date_declaration).all()
        except Exception as e:
            logger.error(f"Erreur récupération sinistres urgents: {e}")
            return []

    # ========================================================================
    # EXPORT
    # ========================================================================

    def to_dict(self, sinistre: Sinistre) -> Dict:
        """Convertit un sinistre en dictionnaire pour export"""
        return {
            'id': sinistre.id,
            'numero_dossier': sinistre.numero_dossier,
            'type': sinistre.type.value if sinistre.type else None,
            'statut': sinistre.statut.value if sinistre.statut else None,
            'date_survenue': sinistre.date_survenue.isoformat() if sinistre.date_survenue else None,
            'date_declaration': sinistre.date_declaration.isoformat() if sinistre.date_declaration else None,
            'lieu': sinistre.lieu,
            'ville': sinistre.ville,
            'description': sinistre.description,
            'estimation_preliminaire': sinistre.estimation_preliminaire,
            'estimation_finale': sinistre.estimation_finale,
            'montant_indemnise': sinistre.montant_indemnise,
            'tiers_nom': sinistre.tiers_nom,
            'tiers_prenom': sinistre.tiers_prenom,
            'tiers_telephone': sinistre.tiers_telephone,
            'tiers_assurance': sinistre.tiers_assurance,
            'vehicule_immat': sinistre.vehicule.immatriculation if sinistre.vehicule else None,
            'client_nom': f"{sinistre.client.nom} {sinistre.client.prenom}" if sinistre.client else None,
            'created_at': sinistre.created_at.isoformat() if sinistre.created_at else None,
        }