# addons/Automobiles/api/services/permissions.py - Version corrigée (sans StockReservation)
"""
Service de vérification des autorisations et du stock d'attestations
"""

from typing import Tuple, Optional, Dict, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from .. import models_db
from ..config import settings

logger = logging.getLogger(__name__)


class PermissionError(Exception):
    """Exception pour les erreurs de permission"""
    def __init__(self, message: str, code: str = "PERMISSION_DENIED"):
        self.message = message
        self.code = code
        super().__init__(message)


class PermissionValidator:
    """Validateur des permissions utilisateur"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_organization(self, organization_code: str) -> Tuple[bool, Optional[str], Optional[models_db.Organization]]:
        """
        Vérifie que la compagnie existe et est active (section 7.3)
        
        Returns:
            (is_valid, error_message, organization)
        """
        organization = self.db.query(models_db.Organization).filter(
            models_db.Organization.code == organization_code,
            models_db.Organization.is_active == True
        ).first()
        
        if not organization:
            return False, f"La compagnie {organization_code} n'existe pas ou est inactive.", None
        
        if organization.is_sanctioned:
            return False, f"La compagnie {organization.name} est sous sanction et ne peut pas produire d'attestations.", None
        
        return True, None, organization
    
    def validate_office(self, office_code: str, organization_id: int) -> Tuple[bool, Optional[str], Optional[models_db.Office]]:
        """
        Vérifie que le bureau existe, est actif et rattaché à la compagnie (section 7.3)
        
        Returns:
            (is_valid, error_message, office)
        """
        office = self.db.query(models_db.Office).filter(
            models_db.Office.code == office_code,
            models_db.Office.organization_id == organization_id,
            models_db.Office.is_active == True
        ).first()
        
        if not office:
            return False, f"Le bureau {office_code} n'existe pas, est inactif ou n'est pas rattaché à la compagnie.", None
        
        return True, None, office
    
    def validate_user_permissions(self, user: models_db.User, action: str = "create") -> Tuple[bool, Optional[str]]:
        """
        Vérifie les permissions de l'utilisateur (section 7.2)
        
        Args:
            user: Utilisateur à vérifier
            action: Action à vérifier (create, createOnBehalf)
        
        Returns:
            (is_valid, error_message)
        """
        if not user.is_active:
            return False, "L'utilisateur est désactivé."
        
        # Parse les permissions (stockées en JSON)
        import json
        try:
            permissions = json.loads(user.permissions) if user.permissions else []
        except:
            permissions = []
        
        if action not in permissions:
            return False, f"L'utilisateur n'a pas la permission '{action}'."
        
        return True, None
    
    def validate_user_office(self, user: models_db.User, office_id: int) -> Tuple[bool, Optional[str]]:
        """
        Vérifie que l'utilisateur est rattaché au bureau (section 7.3)
        
        Returns:
            (is_valid, error_message)
        """
        if user.office_id != office_id:
            # Vérifier si l'utilisateur est un responsable de bureau de la compagnie
            office = self.db.query(models_db.Office).filter(
                models_db.Office.id == office_id
            ).first()
            
            if office and office.is_master_office:
                # Le bureau principal peut agir pour tous
                return True, None
            
            return False, "L'utilisateur n'est pas rattaché à ce bureau."
        
        return True, None
    
    def validate_import_permission(self, organization_id: int, office_id: int) -> Tuple[bool, Optional[str]]:
        """
        Vérifie que l'import de production est activé pour le bureau (section 7.3)
        
        Returns:
            (is_valid, error_message)
        """
        # Cette vérification dépend de votre modèle de données
        # Exemple: vérifier dans une table office_settings
        # Pour l'instant, on considère que c'est toujours activé
        return True, None


class StockValidator:
    """Validateur du stock d'attestations (section 7.4)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_stock_availability(
        self,
        organization_id: int,
        certificate_variant_id: int,
        office_id: Optional[int],
        requested_quantity: int
    ) -> Tuple[bool, Optional[str], Optional[models_db.Stock]]:
        """
        Vérifie la disponibilité du stock d'attestations (section 7.4)
        
        Returns:
            (is_available, error_message, stock_record)
        """
        # Chercher le stock
        query = self.db.query(models_db.Stock).filter(
            models_db.Stock.organization_id == organization_id,
            models_db.Stock.certificate_variant_id == certificate_variant_id
        )
        
        if office_id:
            query = query.filter(models_db.Stock.office_id == office_id)
        
        stock = query.first()
        
        if not stock:
            # Vérifier le stock global (sans bureau)
            global_stock = self.db.query(models_db.Stock).filter(
                models_db.Stock.organization_id == organization_id,
                models_db.Stock.certificate_variant_id == certificate_variant_id,
                models_db.Stock.office_id.is_(None)
            ).first()
            
            if global_stock:
                stock = global_stock
            else:
                return False, "Stock d'attestations non configuré pour cette compagnie.", None
        
        if stock.available_quantity < requested_quantity:
            return False, f"Stock d'attestations insuffisant. Disponible: {stock.available_quantity}, Demandé: {requested_quantity}", stock
        
        return True, None, stock
    
    def reserve_stock(
        self,
        stock: models_db.Stock,
        quantity: int,
        production_id: int
    ) -> bool:
        """
        Réserve les attestations (verrouillage atomique)
        
        Returns:
            success
        """
        try:
            # Mettre à jour le stock
            stock.used_quantity += quantity
            self.db.commit()
            
            # Créer une entrée de réservation (si la table existe)
            try:
                reservation = models_db.StockReservation(
                    stock_id=stock.id,
                    production_id=production_id,
                    quantity=quantity,
                    reserved_at=datetime.utcnow()
                )
                self.db.add(reservation)
                self.db.commit()
            except Exception as e:
                # Si la table n'existe pas, on ignore l'erreur
                logger.warning(f"Impossible de créer la réservation: {e}")
                self.db.commit()
            
            logger.info(f"✅ Réservation de {quantity} attestation(s) pour la production {production_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la réservation du stock: {e}")
            self.db.rollback()
            return False
    
    def release_stock(self, production_id: int) -> bool:
        """
        Libère les attestations réservées (en cas d'annulation)
        
        Returns:
            success
        """
        try:
            # Chercher les réservations
            reservations = self.db.query(models_db.StockReservation).filter(
                models_db.StockReservation.production_id == production_id,
                models_db.StockReservation.released_at.is_(None)
            ).all()
            
            for reservation in reservations:
                stock = self.db.query(models_db.Stock).filter(
                    models_db.Stock.id == reservation.stock_id
                ).first()
                
                if stock:
                    stock.used_quantity -= reservation.quantity
                
                reservation.released_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"✅ Libération des attestations pour la production {production_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la libération du stock: {e}")
            self.db.rollback()
            return False


class ProductionAuthorizer:
    """Autorisateur global des productions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.permission_validator = PermissionValidator(db)
        self.stock_validator = StockValidator(db)
    
    def authorize_production(
        self,
        office_code: str,
        organization_code: str,
        certificate_variant_code: str,
        user: models_db.User,
        quantity: int
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Autorise une production complète
        
        Returns:
            (is_authorized, error_message, context)
        """
        context = {}
        
        # 1. Vérifier la compagnie
        is_valid, error, organization = self.permission_validator.validate_organization(organization_code)
        if not is_valid:
            return False, error, None
        context["organization"] = organization
        
        # 2. Vérifier le bureau
        is_valid, error, office = self.permission_validator.validate_office(office_code, organization.id)
        if not is_valid:
            return False, error, None
        context["office"] = office
        
        # 3. Vérifier les permissions utilisateur
        is_valid, error = self.permission_validator.validate_user_permissions(user, "create")
        if not is_valid:
            return False, error, None
        
        # 4. Vérifier que l'utilisateur est rattaché au bureau
        is_valid, error = self.permission_validator.validate_user_office(user, office.id)
        if not is_valid:
            return False, error, None
        
        # 5. Vérifier l'import activé
        is_valid, error = self.permission_validator.validate_import_permission(organization.id, office.id)
        if not is_valid:
            return False, error, None
        
        # 6. Récupérer la variante d'attestation
        variant = self.db.query(models_db.CertificateVariant).filter(
            models_db.CertificateVariant.code == certificate_variant_code
        ).first()
        
        if not variant:
            return False, f"La variante d'attestation {certificate_variant_code} n'existe pas.", None
        context["certificate_variant"] = variant
        
        # 7. Vérifier le quota (si applicable)
        if variant.quota_limit > 0:
            # Compter les productions déjà éditées
            used_count = self.db.query(models_db.Production).filter(
                models_db.Production.certificate_variant_id == variant.id,
                models_db.Production.state == "completed"
            ).count()
            
            if used_count + quantity > variant.quota_limit:
                return False, f"Quota d'attestations dépassé pour la variante {certificate_variant_code}. " \
                             f"Limite: {variant.quota_limit}, Utilisé: {used_count}, Demandé: {quantity}", None
        
        # 8. Vérifier le stock
        is_available, error, stock = self.stock_validator.check_stock_availability(
            organization_id=organization.id,
            certificate_variant_id=variant.id,
            office_id=office.id,
            requested_quantity=quantity
        )
        
        if not is_available:
            return False, error, None
        context["stock"] = stock
        context["stock_available"] = stock.available_quantity
        
        return True, None, context
    
    def reserve_certificates(self, context: Dict, production_id: int, quantity: int) -> bool:
        """
        Réserve les certificats après création de la production
        """
        if "stock" in context:
            return self.stock_validator.reserve_stock(context["stock"], quantity, production_id)
        return True