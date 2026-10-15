# # addons/Automobiles/models/vehicle_tariff.py

# from sqlalchemy import Column, Integer, String, Float, ForeignKey
# from sqlalchemy.orm import relationship
# from core.database import Base


# class VehicleTariff(Base):
#     """
#     Informations tarifaires du véhicule
#     """
#     __tablename__ = 'vehicle_tariffs'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False, unique=True)
    
#     # --- INFORMATIONS TARIFAIRES ---
#     code_tarif = Column(String(50))              # Code ministériel du tarif
#     libele_tarif = Column(String(255))           # Libellé du tarif
#     code_assure = Column(String(50))             # Code interne de l'assuré
    
#     # --- RELATION ---
#     vehicle = relationship("Vehicle", back_populates="tariff")
    
#     def __repr__(self):
#         return f"<VehicleTariff(code_tarif={self.code_tarif})>"