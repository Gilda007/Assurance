# addons/Automobiles/models/driver_models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Driver(Base):
    """Modèle Conducteur (section 3.4)"""
    __tablename__ = 'drivers'
    
    id = Column(Integer, primary_key=True)
    
    # Informations conducteur
    driver_name = Column(String(255), nullable=False)
    driver_birth_date = Column(DateTime, nullable=False)
    driver_licence_number = Column(String(100), nullable=False)
    driver_licence_category = Column(String(20), nullable=False)
    driver_licence_issued_at = Column(DateTime, nullable=False)
    driver_licence_issued_by = Column(String(255))
    
    # Relations - CORRIGER le nom de la table : 'contrats' au lieu de 'contracts'
    contract_id = Column(Integer, ForeignKey('contrats.id'))  # ← 'contrats.id'
    contract = relationship("Contrat", back_populates="drivers")  # ← "Contrat" avec C majuscule

    # ✅ Relation inverse avec Vehicle
    vehicles = relationship("Vehicle", back_populates="driver", foreign_keys="[Vehicle.driver_id]")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_api_dict(self):
        """Convertit en dictionnaire pour l'API"""
        return {
            "driver_name": self.driver_name,
            "driver_birth_date": self.driver_birth_date.strftime("%Y-%m-%d") if self.driver_birth_date else None,
            "driver_licence_number": self.driver_licence_number,
            "driver_licence_category": self.driver_licence_category,
            "driver_licence_issued_at": self.driver_licence_issued_at.strftime("%Y-%m-%d") if self.driver_licence_issued_at else None,
            "driver_licence_issued_by": self.driver_licence_issued_by
        }