# addons/Automobiles/models/expertise.py
"""
Modèles pour l'expertise automobile
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from core.database import Base


class TypeExpertise(str, enum.Enum):
    """Types d'expertise"""
    PRELIMINAIRE = "preliminaire"
    APPROFONDIE = "approfondie"
    CONTRADICTOIRE = "contradictoire"
    AMIABLE = "amiable"


class StatutExpertise(str, enum.Enum):
    """Statuts d'une expertise"""
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    VALIDEE = "validee"
    REJETEE = "rejetee"


class Expertise(Base):
    """Modèle d'expertise automobile"""
    __tablename__ = "expertises_auto"

    id = Column(Integer, primary_key=True, index=True)
    sinistre_id = Column(Integer, ForeignKey("sinistres_auto.id"), nullable=False)
    
    # Expert
    expert_id = Column(Integer, ForeignKey("utilisateurs.id"))
    expert_nom = Column(String(255))
    expert_specialite = Column(String(100))
    
    # Informations générales
    type = Column(Enum(TypeExpertise), default=TypeExpertise.PRELIMINAIRE)
    statut = Column(Enum(StatutExpertise), default=StatutExpertise.PLANIFIEE)
    
    # Dates
    date_planifiee = Column(DateTime)
    date_debut = Column(DateTime)
    date_fin = Column(DateTime)
    
    # Lieu
    lieu = Column(String(255))
    
    # Rapport
    rapport_url = Column(String(255))
    rapport_contenu = Column(Text)
    conclusion = Column(Text)
    recommandations = Column(Text)
    
    # Estimation
    estimation_vehicule = Column(Float, default=0.0)
    estimation_reparations = Column(Float, default=0.0)
    estimation_valeur_residuelle = Column(Float, default=0.0)
    
    # Détails des dommages
    dommages_carrosserie = Column(Text)
    dommages_mecanique = Column(Text)
    dommages_equipements = Column(Text)
    
    # Photos
    photos_urls = Column(Text)  # JSON
    
    # Pièces jointes
    pieces_joites = Column(Text)  # JSON
    
    # Frais
    frais_expertise = Column(Float, default=0.0)
    frais_deplacement = Column(Float, default=0.0)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("utilisateurs.id"))
    
    # Relations
    sinistre = relationship("Sinistre", back_populates="expertise")
    
    def __repr__(self):
        return f"<Expertise {self.id} - {self.type.value}>"
    
    @property
    def est_terminee(self):
        return self.statut in [StatutExpertise.TERMINEE, StatutExpertise.VALIDEE]
    
    @property
    def montant_total_estime(self):
        return self.estimation_vehicule + self.estimation_reparations