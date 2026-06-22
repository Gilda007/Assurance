# # addons/Automobiles/models/vehicle_identification.py

# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from core.database import Base


# class VehicleIdentification(Base):
#     """
#     Identification du véhicule (section 3.5)
#     """
#     __tablename__ = 'vehicle_identifications'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False, unique=True)
    
#     # --- IDENTIFICATION ---
#     licence_plate = Column(String(50), nullable=False, unique=True)  # IMMATRICULATION_DU_VEHICULE
#     chassis = Column(String(100), nullable=False)                    # NUMERO_DE_CHASSIS_DU_VEHICULE
#     brand = Column(String(100), nullable=False)                     # MARQUE_DU_VEHICULE
#     model = Column(String(100), nullable=False)                     # MODELE_DU_VEHICULE
#     year = Column(Integer)                                          # Année de fabrication
#     first_registration_date = Column(DateTime)                     # DATE_PREMIERE_MISE_EN_CIRCULATION
    
#     # --- RELATION ---
#     vehicle = relationship("Vehicle", back_populates="identification")
    
#     def __repr__(self):
#         return f"<VehicleIdentification(licence_plate={self.licence_plate})>"