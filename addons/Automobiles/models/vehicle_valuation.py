# # addons/Automobiles/models/vehicle_valuation.py

# from sqlalchemy import Column, Integer, Float, ForeignKey
# from sqlalchemy.orm import relationship
# from core.database import Base


# class VehicleValuation(Base):
#     """
#     Valeurs financières du véhicule
#     """
#     __tablename__ = 'vehicle_valuations'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False, unique=True)
    
#     # --- VALEURS ---
#     valeur_neuf = Column(Float, default=0.0)      # Valeur à neuf (FCFA)
#     valeur_venale = Column(Float, default=0.0)    # Valeur vénale (FCFA)
    
#     # --- RELATION ---
#     vehicle = relationship("Vehicle", back_populates="valuation")
    
#     def __repr__(self):
#         return f"<VehicleValuation(valeur_neuf={self.valeur_neuf})>"