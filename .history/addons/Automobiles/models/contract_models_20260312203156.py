# addons/contract_manager/models/models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, func, JSON
from sqlalchemy.orm import relationship
from core.database import Base

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    numero_police = Column(String(50), unique=True, nullable=False)
    
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    vehicle_id = Column(Integer, ForeignKey('vehicles.id')) # Lien vers la table vehicles
    fleet_id = Column(Integer, ForeignKey('fleets.id'), nullable=True)
    
    date_emission = Column(Date, default=func.now())
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    statut = Column(String(20), default="ACTIF")

    prime_nette = Column(Float, default=0.0)
    dta = Column(Float, default=0.0)
    tva = Column(Float, default=0.0)
    vignette = Column(Float, default=0.0)
    prime_totale_ttc = Column(Float, default=0.0)
    garanties = Column(JSON)

    vehicle = relationship("Vehicle", back_populates="contracts")

    # Relations
    contact = relationship("Contact", back_populates="contracts")
    fleet = relationship("Fleet", back_populates="contracts")