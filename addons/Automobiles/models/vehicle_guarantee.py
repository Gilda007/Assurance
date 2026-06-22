# # addons/Automobiles/models/vehicle_guarantee.py

# from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean, ForeignKey
# from sqlalchemy.orm import relationship
# from core.database import Base
# from datetime import datetime, timedelta
# from sqlalchemy import func 


# class VehicleGuarantee(Base):
#     """Garanties principales du véhicule (Montants bruts)"""
#     __tablename__ = 'vehicle_guarantees'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, nullable=False)
    
#     # Montants bruts des garanties
#     rc = Column(Float, default=0.0)  # Responsabilité Civile
#     dr = Column(Float, default=0.0)  # Dommages
#     vol = Column(Float, default=0.0)  # Vol
#     vb = Column(Float, default=0.0)  # Verre Brisé
#     ipt = Column(Float, default=0.0)  # Incendie
#     bris = Column(Float, default=0.0)  # Bris de machine
#     ar = Column(Float, default=0.0)  # Assistance
#     dta = Column(Float, default=0.0)  # Défense et Recours
#     in_garantie = Column(Float, default=0.0)  # Garantie Individuelle
    
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
#     # Relations
#     vehicle = relationship("Vehicle", back_populates="guarantees", foreign_keys=[vehicle_id])

# class VehicleGuaranteeRate(Base):
#     """Taux des garanties"""
#     __tablename__ = 'vehicle_guarantee_rates'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, nullable=False)
    
#     # Taux des garanties
#     rc = Column(Float, default=0.0)
#     dr = Column(Float, default=0.0)
#     vol = Column(Float, default=0.0)
#     vb = Column(Float, default=0.0)
#     ipt = Column(Float, default=0.0)
#     bris = Column(Float, default=0.0)
#     ar = Column(Float, default=0.0)
#     dta = Column(Float, default=0.0)
#     in_garantie = Column(Float, default=0.0)
    
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
#     # Relations
#     vehicle = relationship("Vehicle", back_populates="guarantee_rates", foreign_keys=[vehicle_id])



# class VehicleGuaranteeOption(Base):
#     """Options des garanties (Checkbox)"""
#     __tablename__ = 'vehicle_guarantee_options'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, nullable=False)
    
#     # Checkbox des garanties
#     rc = Column(Boolean, default=False)
#     dr = Column(Boolean, default=False)
#     vol = Column(Boolean, default=False)
#     vb = Column(Boolean, default=False)
#     ipt = Column(Boolean, default=False)
#     bris = Column(Boolean, default=False)
#     ar = Column(Boolean, default=False)
#     dta = Column(Boolean, default=False)
#     in_garantie = Column(Boolean, default=False)
    
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
#     # Relations
#     vehicle = relationship("Vehicle", back_populates="guarantee_options", foreign_keys=[vehicle_id])


# class VehicleFleetGuarantee(Base):
#     """Garanties spécifiques à la flotte"""
#     __tablename__ = 'vehicle_fleet_guarantees'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, nullable=False)
    
#     # Montants des garanties flotte
#     rc = Column(Float, default=0.0)
#     dr = Column(Float, default=0.0)
#     vol = Column(Float, default=0.0)
#     vb = Column(Float, default=0.0)
#     ipt = Column(Float, default=0.0)
#     bris = Column(Float, default=0.0)
#     ar = Column(Float, default=0.0)
#     dta = Column(Float, default=0.0)
#     in_garantie = Column(Float, default=0.0)
    
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
#     # Relations
#     vehicle = relationship("Vehicle", back_populates="fleet_guarantees", foreign_keys=[vehicle_id])