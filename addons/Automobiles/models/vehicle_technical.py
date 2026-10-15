# # addons/Automobiles/models/vehicle_technical.py

# from sqlalchemy import Column, Integer, Float, ForeignKey
# from sqlalchemy.orm import relationship
# from core.database import Base


# class VehicleTechnical(Base):
#     """
#     Caractéristiques techniques du véhicule (section 3.7)
#     """
#     __tablename__ = 'vehicle_technicals'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False, unique=True)
    
#     # --- CARACTÉRISTIQUES TECHNIQUES ---
#     nb_of_seats = Column(Integer, nullable=False, default=5)        # NOMBRE_DE_PLACE_DU_VEHICULE
#     fiscal_power = Column(Integer, nullable=False, default=5)       # PUISSANCE_FISCALE (CV)
#     displacement = Column(Integer, default=0)                       # CYLINDREE (cm³)
#     gross_weight = Column(Integer, default=0)                       # POIDS_TOTAL_AUTORISE_EN_CHARGE (PTAC kg)
#     payload_capacity = Column(Integer, default=0)                   # CHARGE_UTILE (kg)
    
#     # --- RELATION ---
#     vehicle = relationship("Vehicle", back_populates="technical")
    
#     def __repr__(self):
#         return f"<VehicleTechnical(fiscal_power={self.fiscal_power})>"