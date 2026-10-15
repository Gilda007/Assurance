# addons/Automobiles/api/models_db.py
"""
Modèles SQLAlchemy pour la base de données - Version corrigée
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, 
    Float, Text, Date, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from .database import Base


# ============================================================================
# MODÈLES DE RÉFÉRENCE
# ============================================================================

class Organization(Base):
    """Compagnie d'assurance"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    email = Column(String(255))
    telephone = Column(String(50))
    logo_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_sanctioned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    offices = relationship("Office", back_populates="organization")
    productions = relationship("Production", back_populates="organization")


class Office(Base):
    """Bureau / Agence"""
    __tablename__ = "offices"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    email = Column(String(255))
    telephone = Column(String(50))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    is_master_office = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    organization = relationship("Organization", back_populates="offices")
    users = relationship("User", back_populates="office")
    productions = relationship("Production", back_populates="office")


class User(Base):
    """Utilisateur de l'API"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    app_key = Column(String(255), nullable=False)
    office_id = Column(Integer, ForeignKey("offices.id"))
    is_active = Column(Boolean, default=True)
    permissions = Column(String(500))  # JSON list des permissions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relations
    office = relationship("Office", back_populates="users")
    productions = relationship("Production", back_populates="user")
    tokens = relationship("UserToken", back_populates="user")


class UserToken(Base):
    """Tokens JWT des utilisateurs"""
    __tablename__ = "user_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    token_name = Column(String(100))
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)
    
    # Relations
    user = relationship("User", back_populates="tokens")


class CertificateType(Base):
    """Type d'attestation (CIMA, carte rose)"""
    __tablename__ = "certificate_types"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    variants = relationship("CertificateVariant", back_populates="certificate_type")
    productions = relationship("Production", back_populates="certificate_type")


class CertificateVariant(Base):
    """Variante d'attestation (couleur)"""
    __tablename__ = "certificate_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    certificate_type_id = Column(Integer, ForeignKey("certificate_types.id"), nullable=False)
    quota_limit = Column(Integer, default=0)  # 0 = illimité
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    certificate_type = relationship("CertificateType", back_populates="variants")
    productions = relationship("Production", back_populates="certificate_variant")


class TariffMatrix(Base):
    """Matrice tarifaire pour le calcul RC"""
    __tablename__ = "tariff_matrices"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_category = Column(String(10), nullable=False)
    circulation_zone = Column(String(5), nullable=False)
    power_range_start = Column(Integer, nullable=False)
    power_range_end = Column(Integer, nullable=False)
    has_trailer = Column(Boolean, default=False)
    base_amount = Column(Integer, nullable=False)  # Montant en FCFA
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_tariff_lookup', 'vehicle_category', 'circulation_zone', 'power_range_start', 'has_trailer'),
    )


# ============================================================================
# MODÈLES DE PRODUCTION
# ============================================================================

class Production(Base):
    """Production d'attestation"""
    __tablename__ = "productions"
    
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(100), unique=True, nullable=False, index=True)
    channel = Column(String(20), default="api")
    quantity = Column(Integer, nullable=False)
    office_code = Column(String(50), nullable=False)
    organization_code = Column(String(50), nullable=False)
    certificate_type_id = Column(Integer, ForeignKey("certificate_types.id"), nullable=False)
    certificate_variant_id = Column(Integer, ForeignKey("certificate_variants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    office_id = Column(Integer, ForeignKey("offices.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    state = Column(String(50), default="pending")
    download_link = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relations
    user = relationship("User", back_populates="productions")
    office = relationship("Office", back_populates="productions")
    organization = relationship("Organization", back_populates="productions")
    certificate_type = relationship("CertificateType", back_populates="productions")
    certificate_variant = relationship("CertificateVariant", back_populates="productions")
    certificates = relationship("Certificate", back_populates="production", cascade="all, delete-orphan")


class Certificate(Base):
    """Attestation générée"""
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(100), unique=True, nullable=False, index=True)
    production_id = Column(Integer, ForeignKey("productions.id"), nullable=False)
    parent_certificate_id = Column(Integer, ForeignKey("certificates.id"), nullable=True)
    download_link = Column(String(500))
    
    # Données de l'attestation
    licence_plate = Column(String(50), nullable=False)
    chassis_number = Column(String(50), nullable=False)
    police_number = Column(String(50), nullable=False)
    insured_name = Column(String(255), nullable=False)
    insured_phone = Column(String(50), nullable=False)
    starts_at = Column(Date, nullable=False)
    ends_at = Column(Date, nullable=False)
    
    # Données complémentaires
    taxpayer_number = Column(String(50))
    dta_amount = Column(Integer, default=0)
    rc_amount = Column(Integer, default=0)
    fleet_discount = Column(Integer, default=0)
    
    # JSON pour stocker toutes les données de la production
    raw_data = Column(Text)
    
    state = Column(String(50), default="active")
    printed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations - CORRECTION ICI
    production = relationship("Production", back_populates="certificates")
    
    # Relation auto-référentielle corrigée
    parent = relationship(
        "Certificate", 
        remote_side=[id],
        backref="children",
        foreign_keys=[parent_certificate_id]
    )


class ProductionLog(Base):
    """Log des productions"""
    __tablename__ = "production_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    production_id = Column(Integer, ForeignKey("productions.id"), nullable=False)
    action = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    message = Column(Text)
    error_details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    production = relationship("Production")

# addons/Automobiles/api/models_db.py - Ajouter à la fin du fichier

class StockReservation(Base):
    """Réservation de stock d'attestations"""
    __tablename__ = "stock_reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    production_id = Column(Integer, ForeignKey("productions.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    reserved_at = Column(DateTime, default=datetime.utcnow)
    released_at = Column(DateTime, nullable=True)
    
    # Relations
    stock = relationship("Stock", backref="reservations")
    production = relationship("Production", backref="reservations")

    
class Stock(Base):
    """Stock d'attestations vierges"""
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    certificate_variant_id = Column(Integer, ForeignKey("certificate_variants.id"), nullable=False)
    office_id = Column(Integer, ForeignKey("offices.id"), nullable=True)
    quantity = Column(Integer, default=0)
    used_quantity = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    organization = relationship("Organization")
    certificate_variant = relationship("CertificateVariant")
    office = relationship("Office")
    
    @property
    def available_quantity(self):
        return self.quantity - self.used_quantity