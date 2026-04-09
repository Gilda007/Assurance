# addons/Automobiles/models/contract_models.py
# Ajoutez ceci au début du fichier, après les imports

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

# Ajoutez la classe Enum pour le statut du contrat
class ContractStatus(enum.Enum):
    PROFORMAT = "proformat"
    ACTIF = "actif"
    RESILIE = "resilie"
    EXPIRE = "expire"
    ANNULE = "annule"

class Contrat(Base):
    __tablename__ = "contrats"
    
    id = Column(Integer, primary_key=True)
    numero_police = Column(String(50), unique=True, nullable=False)
    
    # --- Relations ---
    owner_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("automobile_compagnies.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    fleet_id = Column(Integer, ForeignKey("fleets.id"), nullable=True)

    # --- Statut du contrat ---
    statut = Column(SQLEnum(ContractStatus), default=ContractStatus.PROFORMAT)
    date_proformat = Column(DateTime, default=datetime.now)
    date_debut = Column(DateTime, nullable=True)
    date_fin = Column(DateTime, nullable=True)

    # --- Finances ---
    prime_pure = Column(Float, default=0.0)
    accessoires = Column(Float, default=0.0)
    taxes_totales = Column(Float, default=0.0)
    commission_intermediaire = Column(Float, default=0.0)
    prime_totale_ttc = Column(Float, default=0.0)
    montant_paye = Column(Float, default=0.0)
    statut_paiement = Column(String(20), default="NON_PAYE")
    
    
    # --- BLOC AUDIT ---
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer, ForeignKey('utilisateurs.id'))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    updated_by = Column(Integer, ForeignKey('utilisateurs.id'))
    created_ip = Column(String(45))
    last_ip = Column(String(45))
    
    # --- RELATIONS ---
    owner = relationship("Contact", back_populates="contracts")
    company = relationship("Compagnie")
    vehicle = relationship("Vehicle", back_populates="contract")
    paiements = relationship("Paiement", back_populates="contrat", cascade="all, delete-orphan")
    fleet = relationship("Fleet", back_populates="contract")


class AuditContratLog(Base):
    __tablename__ = 'audit_contrat_logs'
    
    # Permet de recharger le modèle sans erreur si déjà présent dans MetaData
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # ex: 'CREATE', 'UPDATE', 'JOIN_VEHICLES'
    module = Column(String(50), default="CONTRAT")
    item_id = Column(Integer, nullable=False)    # ID de la flotte concernée
    
    # Stockage des changements au format JSON
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    
    # Traçabilité Réseau
    ip_local = Column(String(50), nullable=True)
    ip_public = Column(String(50), nullable=True)
    
    # Timestamp (Utilisation de timezone.utc pour Python 3.13+)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AuditContratLog(action={self.action}, contrat_id={self.item_id})>"