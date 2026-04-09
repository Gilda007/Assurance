# addons/Automobiles/controllers/contract_controller.py
import socket
import json
import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, extract
from core.database import SessionLocal
from core.logger import logger
from addons.Automobiles.models.contract_models import Contrat, AuditContratLog, ContractStatus
from datetime import datetime, timedelta


class ContractController:
    """Contrôleur pour la gestion des contrats d'assurance"""
    
    def __init__(self, db_session: Session = None, current_user: int = None):
        self.db = db_session or SessionLocal()
        self.current_user = getattr(current_user, 'id', current_user)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    # ==================== CRUD CONTRAT ====================
    
    def create_contract(self, data: Dict, user_id: int) -> Tuple[bool, Optional[Contrat], str]:
        """Crée un nouveau contrat"""
        try:
            numero_police = self._generate_police_number(data.get('company_id'))
            ip_local, ip_public = self._get_ips()
            
            nouveau_contrat = Contrat(
                numero_police=numero_police,
                owner_id=data.get('owner_id'),
                company_id=data.get('company_id'),
                vehicle_id=data.get('vehicle_id'),
                fleet_id=data.get('fleet_id'),
                prime_pure=data.get('prime_pure', 0.0),
                accessoires=data.get('accessoires', 0.0),
                taxes_totales=data.get('taxes_totales', 0.0),
                commission_intermediaire=data.get('commission_intermediaire', 0.0),
                prime_totale_ttc=data.get('prime_totale_ttc', 0.0),
                montant_paye=data.get('montant_paye', 0.0),
                statut_paiement=data.get('statut_paiement', 'NON_PAYE'),
                created_by=user_id,
                updated_by=user_id,
                created_ip=ip_local,
                last_ip=ip_local
            )
            
            # Recalculer les totaux
            nouveau_contrat = self._recalculate_totals(nouveau_contrat)
            
            self.db.add(nouveau_contrat)
            self.db.commit()
            self.db.refresh(nouveau_contrat)
            
            # Journaliser l'audit
            self._log_audit(
                user_id=user_id,
                action='CREATE',
                item_id=nouveau_contrat.id,
                old_values=None,
                new_values=self._contract_to_dict(nouveau_contrat),
                ip_local=ip_local,
                ip_public=ip_public
            )
            
            logger.info(f"Contrat créé: {nouveau_contrat.numero_police}")
            return True, nouveau_contrat, "Contrat créé avec succès"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur création contrat: {e}")
            return False, None, str(e)
    
    def update_contract(self, contract_id: int, data: Dict, user_id: int) -> Tuple[bool, Optional[Contrat], str]:
        """Met à jour un contrat"""
        try:
            contrat = self.get_contract_by_id(contract_id)
            if not contrat:
                return False, None, "Contrat non trouvé"
            
            old_values = self._contract_to_dict(contrat)
            
            # Champs modifiables
            updatable_fields = [
                'prime_pure', 'accessoires', 'taxes_totales',
                'commission_intermediaire', 'prime_totale_ttc',
                'fleet_id', 'statut_paiement'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(contrat, field, data[field])
            
            # Recalculer les totaux
            contrat = self._recalculate_totals(contrat)
            
            ip_local, ip_public = self._get_ips()
            contrat.updated_by = user_id
            contrat.last_ip = ip_local
            
            self.db.commit()
            self.db.refresh(contrat)
            
            self._log_audit(
                user_id=user_id,
                action='UPDATE',
                item_id=contract_id,
                old_values=old_values,
                new_values=self._contract_to_dict(contrat),
                ip_local=ip_local,
                ip_public=ip_public
            )
            
            logger.info(f"Contrat mis à jour: {contrat.numero_police}")
            return True, contrat, "Contrat mis à jour avec succès"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur mise à jour contrat: {e}")
            return False, None, str(e)
    
    def delete_contract(self, contract_id: int, user_id: int) -> Tuple[bool, str]:
        """Supprime un contrat (soft delete)"""
        try:
            contrat = self.get_contract_by_id(contract_id)
            if not contrat:
                return False, "Contrat non trouvé"
            
            ip_local, ip_public = self._get_ips()
            
            self._log_audit(
                user_id=user_id,
                action='DELETE',
                item_id=contract_id,
                old_values=self._contract_to_dict(contrat),
                new_values=None,
                ip_local=ip_local,
                ip_public=ip_public
            )
            
            self.db.delete(contrat)
            self.db.commit()
            
            logger.info(f"Contrat supprimé: {contrat.numero_police}")
            return True, "Contrat supprimé avec succès"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur suppression contrat: {e}")
            return False, str(e)
    
    # ==================== RECHERCHE ET LECTURE ====================
    
    def get_contract_by_id(self, contract_id: int) -> Optional[Contrat]:
        """Récupère un contrat par son ID"""
        return self.db.query(Contrat).options(
            joinedload(Contrat.owner),
            joinedload(Contrat.company),
            joinedload(Contrat.vehicle),
            joinedload(Contrat.fleet)
        ).filter(Contrat.id == contract_id).first()
    
    def get_contract_by_police(self, numero_police: str) -> Optional[Contrat]:
        """Récupère un contrat par son numéro de police"""
        return self.db.query(Contrat).filter(Contrat.numero_police == numero_police).first()
    
    def get_contracts_by_owner(self, owner_id: int, limit: int = 100) -> List[Contrat]:
        """Récupère tous les contrats d'un propriétaire"""
        return self.db.query(Contrat).filter(
            Contrat.owner_id == owner_id
        ).order_by(Contrat.created_at.desc()).limit(limit).all()
    
    def get_contracts_by_vehicle(self, vehicle_id: int) -> List[Contrat]:
        """Récupère l'historique des contrats d'un véhicule"""
        return self.db.query(Contrat).filter(
            Contrat.vehicle_id == vehicle_id
        ).order_by(Contrat.created_at.desc()).all()
    
   
    def get_active_contract_by_vehicle(self, vehicle_id: int) -> Optional[Contrat]:
        """
        Récupère le contrat actif d'un véhicule
        Un contrat est considéré actif s'il n'est pas expiré ou annulé
        """
        from datetime import date
        
        try:
            # Récupérer tous les contrats du véhicule
            contrats = self.db.query(Contrat).filter(
                Contrat.vehicle_id == vehicle_id
            ).order_by(Contrat.created_at.desc()).all()
            
            print(f"Nombre de contrats trouvés pour le véhicule {vehicle_id}: {len(contrats)}")
            
            for contrat in contrats:
                print(f"  - Contrat ID: {contrat.id}, Police: {contrat.numero_police}")
            
            # Retourner le premier contrat trouvé (le plus récent)
            # Vous pouvez ajouter des conditions supplémentaires ici
            if contrats:
                return contrats[0]
            
            return None
            
        except Exception as e:
            print(f"Erreur get_active_contract_by_vehicle: {e}")
            return None

    # Dans contract_controller.py, modifiez la méthode get_contract_by_vehicle

    def get_contract_by_vehicle(self, vehicle_id: int) -> Optional[Contrat]:
        """Récupère le contrat associé à un véhicule"""
        if not vehicle_id:
            print("⚠️ get_contract_by_vehicle appelé avec vehicle_id None")
            return None
        
        try:
            print(f"=== get_contract_by_vehicle ===")
            print(f"Recherche contrat pour vehicle_id: {vehicle_id}")
            
            # Vérifier d'abord combien de contrats existent dans la table
            total_contrats = self.db.query(Contrat).count()
            print(f"Total des contrats dans la table: {total_contrats}")
            
            # Afficher tous les contrats pour déboguer
            all_contrats = self.db.query(Contrat).all()
            for c in all_contrats:
                print(f"  Contrat ID: {c.id}, Police: {c.numero_police}, Vehicle ID: {c.vehicle_id}")
            
            # Rechercher le contrat spécifique
            contrat = self.db.query(Contrat).filter(
                Contrat.vehicle_id == vehicle_id
            ).first()
            
            if contrat:
                print(f"✓ Contrat est trouvé: {contrat.id}")
            else:
                print(f"❌ Aucun contrat avec vehicle_id = {vehicle_id}")
                
                # Vérifier le type de la colonne vehicle_id
                print(f"Type de la colonne vehicle_id: {type(Contrat.vehicle_id)}")
                
            return contrat
            
        except Exception as e:
            # self.db.rollback()
            print(f"Erreur get_contract_by_vehicle: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_contracts_by_fleet(self, fleet_id: int) -> List[Contrat]:
        """Récupère tous les contrats d'une flotte"""
        return self.db.query(Contrat).filter(Contrat.fleet_id == fleet_id).all()
    
    def search_contracts(self, filters: Dict) -> List[Contrat]:
        """Recherche avancée de contrats"""
        query = self.db.query(Contrat)
        
        if filters.get('numero_police'):
            query = query.filter(Contrat.numero_police.ilike(f"%{filters['numero_police']}%"))
        
        if filters.get('owner_id'):
            query = query.filter(Contrat.owner_id == filters['owner_id'])
        
        if filters.get('company_id'):
            query = query.filter(Contrat.company_id == filters['company_id'])
        
        if filters.get('vehicle_id'):
            query = query.filter(Contrat.vehicle_id == filters['vehicle_id'])
        
        if filters.get('fleet_id'):
            query = query.filter(Contrat.fleet_id == filters['fleet_id'])
        
        if filters.get('statut_paiement'):
            query = query.filter(Contrat.statut_paiement == filters['statut_paiement'])
        
        if filters.get('date_debut_min'):
            query = query.filter(Contrat.created_at >= filters['date_debut_min'])
        
        if filters.get('date_debut_max'):
            query = query.filter(Contrat.created_at <= filters['date_debut_max'])
        
        if filters.get('prime_min'):
            query = query.filter(Contrat.prime_totale_ttc >= filters['prime_min'])
        
        if filters.get('prime_max'):
            query = query.filter(Contrat.prime_totale_ttc <= filters['prime_max'])
        
        return query.order_by(Contrat.created_at.desc()).all()
    
    # ==================== STATISTIQUES ====================
    
    def get_statistics(self, company_id: int = None, start_date: date = None, end_date: date = None) -> Dict:
        """Génère des statistiques sur les contrats"""
        query = self.db.query(Contrat)
        
        if company_id:
            query = query.filter(Contrat.company_id == company_id)
        
        if start_date:
            query = query.filter(Contrat.created_at >= start_date)
        
        if end_date:
            query = query.filter(Contrat.created_at <= end_date)
        
        total_contrats = query.count()
        total_prime_ttc = query.with_entities(func.sum(Contrat.prime_totale_ttc)).scalar() or 0
        total_montant_paye = query.with_entities(func.sum(Contrat.montant_paye)).scalar() or 0
        
        # Statistiques par statut de paiement
        stats_paiement = {}
        for statut in ['NON_PAYE', 'PARTIEL', 'PAYE']:
            count = query.filter(Contrat.statut_paiement == statut).count()
            montant = query.filter(Contrat.statut_paiement == statut).with_entities(
                func.sum(Contrat.prime_totale_ttc)
            ).scalar() or 0
            stats_paiement[statut] = {
                'count': count,
                'montant_total': montant,
                'pourcentage': (count / total_contrats * 100) if total_contrats > 0 else 0
            }
        
        return {
            'total_contrats': total_contrats,
            'total_prime_ttc': total_prime_ttc,
            'total_montant_paye': total_montant_paye,
            'total_impaye': total_prime_ttc - total_montant_paye,
            'taux_recouvrement': (total_montant_paye / total_prime_ttc * 100) if total_prime_ttc > 0 else 0,
            'stats_paiement': stats_paiement
        }
    
    def get_financial_summary(self, contract_id: int) -> Dict:
        """Récupère un résumé financier du contrat"""
        contrat = self.get_contract_by_id(contract_id)
        if not contrat:
            return {}
        
        return {
            'contract_info': {
                'id': contrat.id,
                'numero_police': contrat.numero_police,
                'created_at': contrat.created_at.strftime('%Y-%m-%d %H:%M:%S') if contrat.created_at else None
            },
            'amounts': {
                'prime_pure': contrat.prime_pure,
                'accessoires': contrat.accessoires,
                'taxes_totales': contrat.taxes_totales,
                'commission_intermediaire': contrat.commission_intermediaire,
                'prime_totale_ttc': contrat.prime_totale_ttc
            },
            'payment': {
                'montant_paye': contrat.montant_paye,
                'reste_a_payer': contrat.prime_totale_ttc - contrat.montant_paye,
                'statut': contrat.statut_paiement,
                'statut_label': self._get_payment_status_label(contrat.statut_paiement)
            },
            'fleet': {
                'fleet_id': contrat.fleet_id,
                'is_in_fleet': contrat.fleet_id is not None
            }
        }
    
    # ==================== GESTION DES FLOTTES ====================
    
    def add_vehicle_to_fleet(self, contract_id: int, fleet_id: int, user_id: int) -> Tuple[bool, str]:
        """Ajoute un véhicule à une flotte"""
        try:
            contrat = self.get_contract_by_id(contract_id)
            if not contrat:
                return False, "Contrat non trouvé"
            
            old_values = self._contract_to_dict(contrat)
            
            contrat.fleet_id = fleet_id
            ip_local, ip_public = self._get_ips()
            contrat.updated_by = user_id
            contrat.last_ip = ip_local
            
            self.db.commit()
            
            self._log_audit(
                user_id=user_id,
                action='JOIN_FLEET',
                item_id=contract_id,
                old_values=old_values,
                new_values=self._contract_to_dict(contrat),
                ip_local=ip_local,
                ip_public=ip_public
            )
            
            logger.info(f"Véhicule ajouté à la flotte {fleet_id}")
            return True, "Véhicule ajouté à la flotte avec succès"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur ajout à la flotte: {e}")
            return False, str(e)
    
    def remove_vehicle_from_fleet(self, contract_id: int, user_id: int) -> Tuple[bool, str]:
        """Retire un véhicule d'une flotte"""
        try:
            contrat = self.get_contract_by_id(contract_id)
            if not contrat:
                return False, "Contrat non trouvé"
            
            if not contrat.fleet_id:
                return False, "Ce véhicule n'est pas associé à une flotte"
            
            old_values = self._contract_to_dict(contrat)
            
            contrat.fleet_id = None
            ip_local, ip_public = self._get_ips()
            contrat.updated_by = user_id
            contrat.last_ip = ip_local
            
            self.db.commit()
            
            self._log_audit(
                user_id=user_id,
                action='LEAVE_FLEET',
                item_id=contract_id,
                old_values=old_values,
                new_values=self._contract_to_dict(contrat),
                ip_local=ip_local,
                ip_public=ip_public
            )
            
            logger.info(f"Véhicule retiré de la flotte")
            return True, "Véhicule retiré de la flotte avec succès"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur retrait de flotte: {e}")
            return False, str(e)
    
    # ==================== MÉTHODES UTILITAIRES ====================
    
    def _generate_police_number(self, company_id: int) -> str:
        """Génère un numéro de police unique"""
        annee = datetime.now().strftime('%Y')
        mois = datetime.now().strftime('%m')
        
        count = self.db.query(Contrat).filter(
            Contrat.numero_police.like(f'POL-{company_id}-{annee}{mois}%')
        ).count() + 1
        
        return f"POL-{company_id}-{annee}{mois}-{count:04d}"
    
    def _get_ips(self) -> Tuple[str, str]:
        """Récupère les IPs"""
        ip_local = self._get_local_ip()
        ip_public = self._get_public_ip()
        return ip_local, ip_public
    
    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _get_public_ip(self) -> str:
        try:
            response = requests.get('https://api.ipify.org', timeout=3)
            return response.text
        except:
            return ""
    
    def _recalculate_totals(self, contrat: Contrat) -> Contrat:
        """Recalcule les totaux du contrat"""
        if contrat.prime_pure > 0 and contrat.taxes_totales == 0:
            contrat.taxes_totales = contrat.prime_pure * 0.1925
        
        contrat.prime_totale_ttc = (
            contrat.prime_pure + 
            contrat.accessoires + 
            contrat.taxes_totales + 
            contrat.commission_intermediaire
        )
        
        return contrat
    
    def _log_audit(self, user_id: int, action: str, item_id: int,
                   old_values: Dict, new_values: Dict, ip_local: str, ip_public: str):
        """Journalise une action d'audit"""
        try:
            audit_log = AuditContratLog(
                user_id=user_id,
                action=action,
                module="CONTRAT",
                item_id=item_id,
                old_values=json.dumps(old_values, default=str) if old_values else None,
                new_values=json.dumps(new_values, default=str) if new_values else None,
                ip_local=ip_local,
                ip_public=ip_public
            )
            self.db.add(audit_log)
            self.db.commit()
        except Exception as e:
            logger.error(f"Erreur journalisation audit: {e}")
    
    def _contract_to_dict(self, contrat: Contrat) -> Dict:
        """Convertit un contrat en dictionnaire"""
        if not contrat:
            return {}
        
        return {
            'id': contrat.id,
            'numero_police': contrat.numero_police,
            'owner_id': contrat.owner_id,
            'company_id': contrat.company_id,
            'vehicle_id': contrat.vehicle_id,
            'fleet_id': contrat.fleet_id,
            'prime_pure': contrat.prime_pure,
            'accessoires': contrat.accessoires,
            'taxes_totales': contrat.taxes_totales,
            'commission_intermediaire': contrat.commission_intermediaire,
            'prime_totale_ttc': contrat.prime_totale_ttc,
            'montant_paye': contrat.montant_paye,
            'statut_paiement': contrat.statut_paiement
        }
    
    def _get_payment_status_label(self, status: str) -> str:
        """Retourne le libellé du statut de paiement"""
        labels = {
            'NON_PAYE': 'Non payé',
            'PARTIEL': 'Paiement partiel',
            'PAYE': 'Entièrement payé'
        }
        return labels.get(status, 'Inconnu')

    def create_proformat_contract(self, vehicle_id: int, user_id: int, data: Dict = None) -> Tuple[bool, Optional[Contrat], str]:
        """
        Crée un contrat en statut proformat pour un véhicule
        
        Args:
            vehicle_id: ID du véhicule
            user_id: ID de l'utilisateur
            data: Données supplémentaires du contrat
        
        Returns:
            Tuple (succès, contrat, message)
        """
        try:
            # Vérifier si un contrat existe déjà pour ce véhicule
            existing_contract = self.get_contract_by_vehicle(vehicle_id)
            if existing_contract:
                return False, None, f"Un contrat existe déjà pour ce véhicule: {existing_contract.numero_police}"
            
            # Générer un numéro de proformat
            numero_proformat = self._generate_proformat_number()
            
            # Récupérer les IPs
            ip_local, ip_public = self._get_ips()
            
            # Préparer les données du contrat
            contrat_data = data or {}
            
            nouveau_contrat = Contrat(
                numero_police=numero_proformat,
                owner_id=contrat_data.get('owner_id'),
                company_id=contrat_data.get('company_id', 1),
                vehicle_id=vehicle_id,
                fleet_id=contrat_data.get('fleet_id'),
                statut=ContractStatus.PROFORMAT,
                date_proformat=datetime.now(),
                prime_pure=contrat_data.get('prime_pure', 0.0),
                accessoires=contrat_data.get('accessoires', 0.0),
                taxes_totales=contrat_data.get('taxes_totales', 0.0),
                commission_intermediaire=contrat_data.get('commission_intermediaire', 0.0),
                prime_totale_ttc=contrat_data.get('prime_totale_ttc', 0.0),
                montant_paye=0.0,
                statut_paiement='NON_PAYE',
                created_by=user_id,
                updated_by=user_id,
                created_ip=ip_local,
                last_ip=ip_local
            )
            
            self.db.add(nouveau_contrat)
            self.db.commit()
            self.db.refresh(nouveau_contrat)
            
            # Journaliser l'audit
            self._log_audit(
                user_id=user_id,
                action='CREATE_PROFORMAT',
                item_id=nouveau_contrat.id,
                old_values=None,
                new_values=self._contract_to_dict(nouveau_contrat),
                ip_local=ip_local,
                ip_public=ip_public
            )
            
            logger.info(f"Proformat créé: {nouveau_contrat.numero_police} pour véhicule {vehicle_id}")
            return True, nouveau_contrat, "Proformat créé avec succès"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur création proformat: {e}")
            return False, None, str(e)

    def update_proformat_to_active(self, contrat_id: int, user_id: int, data: Dict = None) -> Tuple[bool, str]:
        """
        Transforme un contrat proformat en contrat actif
        
        Args:
            contrat_id: ID du contrat
            user_id: ID de l'utilisateur
            data: Données finales du contrat (dates, montants ajustés, etc.)
        
        Returns:
            Tuple (succès, message)
        """
        try:
            contrat = self.get_contract_by_id(contrat_id)
            if not contrat:
                return False, "Contrat non trouvé"
            
            if contrat.statut != ContractStatus.PROFORMAT:
                return False, f"Le contrat n'est pas en statut proformat (actuel: {contrat.statut.value})"
            
            # Sauvegarder les anciennes valeurs
            old_values = self._contract_to_dict(contrat)
            
            # Mettre à jour le contrat
            if data:
                # Dates de validité
                contrat.date_debut = data.get('date_debut', datetime.now())
                contrat.date_fin = data.get('date_fin', datetime.now() + timedelta(days=365))
                
                # Montants ajustés
                if 'prime_pure' in data:
                    contrat.prime_pure = data['prime_pure']
                if 'accessoires' in data:
                    contrat.accessoires = data['accessoires']
                if 'taxes_totales' in data:
                    contrat.taxes_totales = data['taxes_totales']
                if 'prime_totale_ttc' in data:
                    contrat.prime_totale_ttc = data['prime_totale_ttc']
            
            # Passer en actif
            contrat.statut = ContractStatus.ACTIF
            
            # Générer un nouveau numéro de police (format définitif)
            ancien_numero = contrat.numero_police
            contrat.numero_police = self._generate_police_number(contrat.company_id)
            
            # Mettre à jour l'audit
            ip_local, ip_public = self._get_ips()
            contrat.updated_by = user_id
            contrat.last_ip = ip_local
            
            self.db.commit()
            
            # Journaliser l'audit
            self._log_audit(
                user_id=user_id,
                action='PROFORMAT_TO_ACTIVE',
                item_id=contrat.id,
                old_values=old_values,
                new_values=self._contract_to_dict(contrat),
                ip_local=ip_local,
                ip_public=ip_public,
                notes=f"Ancien numéro: {ancien_numero}"
            )
            
            logger.info(f"Proformat {ancien_numero} transformé en contrat actif: {contrat.numero_police}")
            return True, f"Contrat validé avec succès. Nouveau numéro: {contrat.numero_police}"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur transformation proformat: {e}")
            return False, str(e)

    def get_proformat_by_vehicle(self, vehicle_id: int) -> Optional[Contrat]:
        """Récupère le proformat actif d'un véhicule"""
        return self.db.query(Contrat).filter(
            Contrat.vehicle_id == vehicle_id,
            Contrat.statut == ContractStatus.PROFORMAT
        ).first()

    def _generate_proformat_number(self) -> str:
        """Génère un numéro de proformat unique"""
        annee = datetime.now().strftime('%Y')
        mois = datetime.now().strftime('%m')
        
        # Compter les proformats du mois
        count = self.db.query(Contrat).filter(
            Contrat.numero_police.like(f'PF-{annee}{mois}%')
        ).count() + 1
        
        return f"PF-{annee}{mois}-{count:04d}"
    
    def get_all_proformats(self, limit: int = 100) -> List[Dict]:
        """Récupère tous les contrats en statut proformat"""
        proformats = self.db.query(Contrat).filter(
            Contrat.statut == ContractStatus.PROFORMAT
        ).order_by(Contrat.date_proformat.desc()).limit(limit).all()
        
        return [self._contract_to_dict(p) for p in proformats]

    def get_expired_proformats(self, days: int = 30) -> List[Contrat]:
        """Récupère les proformats expirés (plus de X jours)"""
        from datetime import timedelta
        expiry_date = datetime.now() - timedelta(days=days)
        
        return self.db.query(Contrat).filter(
            Contrat.statut == ContractStatus.PROFORMAT,
            Contrat.date_proformat <= expiry_date
        ).all()

    def delete_proformat(self, contrat_id: int, user_id: int) -> Tuple[bool, str]:
        """Supprime un proformat (uniquement si en statut proformat)"""
        try:
            contrat = self.get_contract_by_id(contrat_id)
            if not contrat:
                return False, "Contrat non trouvé"
            
            if contrat.statut != ContractStatus.PROFORMAT:
                return False, "Seuls les proformats peuvent être supprimés"
            
            ip_local, ip_public = self._get_ips()
            
            self._log_audit(
                user_id=user_id,
                action='DELETE_PROFORMAT',
                item_id=contrat.id,
                old_values=self._contract_to_dict(contrat),
                new_values=None,
                ip_local=ip_local,
                ip_public=ip_public
            )
            
            self.db.delete(contrat)
            self.db.commit()
            
            logger.info(f"Proformat supprimé: {contrat.numero_police}")
            return True, "Proformat supprimé avec succès"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur suppression proformat: {e}")
            return False, str(e)    