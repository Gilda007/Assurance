from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base
from sqlalchemy import Boolean

class AutomobileTarif(Base):
    __tablename__ = 'automobile_tarifs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # --- LIAISON ET IDENTIFICATION ---
    cie_id = Column(Integer, ForeignKey('automobile_compagnies.id'), nullable=False)
    tarif_code = Column(String(20))     # 'Tarif' dans le CSV
    lib_tarif = Column(String(255))
    categorie = Column(String(20))
    zone = Column(String(10))
    nbre_place = Column(Integer, default=0)
    libelle_option = Column(String(100))

    # --- MATRICE TARIFAIRE (RC, REMORQUAGE, INFLAMMABLE) ---
    # Primes 1 à 10
    prime1 = Column(Float, default=0.0); prime2 = Column(Float, default=0.0)
    prime3 = Column(Float, default=0.0); prime4 = Column(Float, default=0.0)
    prime5 = Column(Float, default=0.0); prime6 = Column(Float, default=0.0)
    prime7 = Column(Float, default=0.0); prime8 = Column(Float, default=0.0)
    prime9 = Column(Float, default=0.0); prime10 = Column(Float, default=0.0)

    # Remorquage 1 à 10
    remorq1 = Column(Float, default=0.0); remorq2 = Column(Float, default=0.0)
    remorq3 = Column(Float, default=0.0); remorq4 = Column(Float, default=0.0)
    remorq5 = Column(Float, default=0.0); remorq6 = Column(Float, default=0.0)
    remorq7 = Column(Float, default=0.0); remorq8 = Column(Float, default=0.0)
    remorq9 = Column(Float, default=0.0); remorq10 = Column(Float, default=0.0)

    # Inflammable 1 à 10
    inflamble1 = Column(Float, default=0.0); inflamble2 = Column(Float, default=0.0)
    inflamble3 = Column(Float, default=0.0); inflamble4 = Column(Float, default=0.0)
    inflamble5 = Column(Float, default=0.0); inflamble6 = Column(Float, default=0.0)
    inflamble7 = Column(Float, default=0.0); inflamble8 = Column(Float, default=0.0)
    inflamble9 = Column(Float, default=0.0); inflamble10 = Column(Float, default=0.0)

    # --- ÉNERGIE (ESSENCE / DIESEL) ---
    essence_1 = Column(Float, default=0.0); essence_2 = Column(Float, default=0.0)
    essence_3 = Column(Float, default=0.0); essence_4 = Column(Float, default=0.0)
    essence_5 = Column(Float, default=0.0); essence_6 = Column(Float, default=0.0)
    essence_7 = Column(Float, default=0.0); essence_8 = Column(Float, default=0.0)
    essence_9 = Column(Float, default=0.0); essence_10 = Column(Float, default=0.0)

    diesel_1 = Column(Float, default=0.0); diesel_2 = Column(Float, default=0.0)
    diesel_3 = Column(Float, default=0.0); diesel_4 = Column(Float, default=0.0)
    diesel_5 = Column(Float, default=0.0); diesel_6 = Column(Float, default=0.0)
    diesel_7 = Column(Float, default=0.0); diesel_8 = Column(Float, default=0.0)
    diesel_9 = Column(Float, default=0.0); diesel_10 = Column(Float, default=0.0)

    # --- AUTRES LIMITES ---
    max_corpo = Column(String(50))
    max_materiel = Column(Float, default=0.0)
    surprime_1 = Column(Float, default=0.0)
    surprime_2 = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True, nullable=True)

    # --- BLOC DE TRAÇABILITÉ ---
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(String(50))
    modify_at = Column(DateTime, onupdate=datetime.now)
    modify_by = Column(String(50))
    local_ip = Column(String(45))
    network_ip = Column(String(45))

    # Relation inverse
    compagnie = relationship("Compagnie", back_populates="tarifs")