# # addons/Automobiles/models/vehicle_options.py

# from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
# from sqlalchemy.orm import relationship
# from core.database import Base


# class VehicleOptions(Base):
#     """
#     Options et compléments du véhicule (section 3.8)
#     """
#     __tablename__ = 'vehicle_options'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False, unique=True)
    
#     # --- OPTIONS ---
#     has_trailer = Column(Boolean, default=False)                    # REMORQUE
#     trailer_flammable = Column(Boolean, default=False)              # REMORQUE_MATIERE_INFLAMMABLE
#     trailer_licence_plate = Column(String(50))                      # IMMATRICULATION_REMORQUE
#     dual_control = Column(Boolean, default=False)                   # DOUBLE_COMMANDE (auto-école)
#     engine_type = Column(Boolean, default=False)                    # TYPE_ENGIN (portuaire)
#     civil_liability = Column(Boolean, default=False)                # RESPONSABILITE_CIVILE (auto-école)
    
#     # --- RELATION ---
#     vehicle = relationship("Vehicle", back_populates="options")
    
#     def __repr__(self):
#         return f"<VehicleOptions(has_trailer={self.has_trailer})>"