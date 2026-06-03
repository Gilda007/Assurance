# addons/Automobiles/api/crud.py
"""
Opérations CRUD pour la base de données
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
import json

from . import models_db
from .schemas import ProductionRequestSchema, ProductionItemSchema


# ============================================================================
# CRUD - ORGANISATIONS
# ============================================================================

def get_organization_by_code(db: Session, code: str) -> Optional[models_db.Organization]:
    """Récupère une organisation par son code"""
    return db.query(models_db.Organization).filter(
        models_db.Organization.code == code,
        models_db.Organization.is_active == True
    ).first()


def get_office_by_code(db: Session, code: str) -> Optional[models_db.Office]:
    """Récupère un bureau par son code"""
    return db.query(models_db.Office).filter(
        models_db.Office.code == code,
        models_db.Office.is_active == True
    ).first()


def get_user_by_app_key(db: Session, app_key: str) -> Optional[models_db.User]:
    """Récupère un utilisateur par sa clé applicative"""
    return db.query(models_db.User).filter(
        models_db.User.app_key == app_key,
        models_db.User.is_active == True
    ).first()


def get_user_by_username(db: Session, username: str) -> Optional[models_db.User]:
    """Récupère un utilisateur par son nom"""
    return db.query(models_db.User).filter(
        models_db.User.username == username,
        models_db.User.is_active == True
    ).first()


def create_user_token(
    db: Session, 
    user_id: int, 
    token: str, 
    token_name: str,
    expires_at: datetime
) -> models_db.UserToken:
    """Crée un token utilisateur"""
    db_token = models_db.UserToken(
        user_id=user_id,
        token=token,
        token_name=token_name,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_valid_token(db: Session, token: str) -> Optional[models_db.UserToken]:
    """Vérifie si un token est valide"""
    return db.query(models_db.UserToken).filter(
        models_db.UserToken.token == token,
        models_db.UserToken.is_revoked == False,
        models_db.UserToken.expires_at > datetime.utcnow()
    ).first()


# ============================================================================
# CRUD - CERTIFICATES VARIANTS
# ============================================================================

def get_certificate_type_by_code(db: Session, code: str) -> Optional[models_db.CertificateType]:
    """Récupère un type d'attestation par son code"""
    return db.query(models_db.CertificateType).filter(
        models_db.CertificateType.code == code
    ).first()


def get_certificate_variant_by_code(db: Session, code: str) -> Optional[models_db.CertificateVariant]:
    """Récupère une variante d'attestation par son code"""
    return db.query(models_db.CertificateVariant).filter(
        models_db.CertificateVariant.code == code
    ).first()


def check_stock_availability(
    db: Session,
    organization_id: int,
    certificate_variant_id: int,
    office_id: Optional[int],
    requested_quantity: int
) -> bool:
    """Vérifie la disponibilité du stock d'attestations"""
    query = db.query(models_db.Stock).filter(
        models_db.Stock.organization_id == organization_id,
        models_db.Stock.certificate_variant_id == certificate_variant_id
    )
    
    if office_id:
        query = query.filter(models_db.Stock.office_id == office_id)
    
    stock = query.first()
    
    if not stock:
        return False
    
    return stock.available_quantity >= requested_quantity


# ============================================================================
# CRUD - PRODUCTIONS
# ============================================================================

def create_production(
    db: Session,
    request: ProductionRequestSchema,
    user_id: int,
    organization_id: int,
    office_id: int,
    certificate_type_id: int,
    certificate_variant_id: int
) -> models_db.Production:
    """Crée une production en base de données"""
    
    # Générer une référence unique
    reference = f"PROD-{datetime.now().strftime('%m%Y')}-{uuid.uuid4().hex[:10].upper()}"
    
    db_production = models_db.Production(
        reference=reference,
        channel=request.channel,
        quantity=len(request.productions),
        office_code=request.office_code,
        organization_code=request.organization_code,
        certificate_type_id=certificate_type_id,
        certificate_variant_id=certificate_variant_id,
        user_id=user_id,
        office_id=office_id,
        organization_id=organization_id,
        state="pending"
    )
    
    db.add(db_production)
    db.commit()
    db.refresh(db_production)
    
    return db_production


def create_certificates(
    db: Session,
    production_id: int,
    items: List[ProductionItemSchema],
    raw_data: Dict[str, Any]
) -> List[models_db.Certificate]:
    """Crée les certificats pour une production"""
    certificates = []
    
    for item in items:
        cert_ref = f"ATD-{uuid.uuid4().hex[:10].upper()}"
        
        db_certificate = models_db.Certificate(
            reference=cert_ref,
            production_id=production_id,
            licence_plate=item.licence_plate,
            chassis_number=item.vehicle_chassis,
            police_number=item.police_number,
            insured_name=item.insured_name,
            insured_phone=item.insured_phone,
            starts_at=item.starts_at,
            ends_at=item.ends_at,
            taxpayer_number=item.taxpayer_number,
            dta_amount=item.dta,
            rc_amount=item.rc,
            fleet_discount=item.fleet_discount or 0,
            raw_data=json.dumps(item.model_dump(), default=str),
            state="active"
        )
        
        db.add(db_certificate)
        certificates.append(db_certificate)
    
    db.commit()
    
    # Rafraîchir les certificats
    for cert in certificates:
        db.refresh(cert)
    
    return certificates


def update_production_state(
    db: Session,
    production_id: int,
    state: str,
    download_link: Optional[str] = None
) -> models_db.Production:
    """Met à jour l'état d'une production"""
    production = db.query(models_db.Production).filter(
        models_db.Production.id == production_id
    ).first()
    
    if production:
        production.state = state
        if download_link:
            production.download_link = download_link
        if state == "completed":
            production.completed_at = datetime.utcnow()
        production.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(production)
    
    return production


def create_production_log(
    db: Session,
    production_id: int,
    action: str,
    status: str,
    message: Optional[str] = None,
    error_details: Optional[str] = None
) -> models_db.ProductionLog:
    """Crée un log pour une production"""
    db_log = models_db.ProductionLog(
        production_id=production_id,
        action=action,
        status=status,
        message=message,
        error_details=error_details
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_production_by_reference(db: Session, reference: str) -> Optional[models_db.Production]:
    """Récupère une production par sa référence"""
    return db.query(models_db.Production).filter(
        models_db.Production.reference == reference
    ).first()