# addons/Automobiles/models/sinistre.py
"""
Modèles pour la gestion des sinistres dans le module automobile
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from core.database import Base


class TypeSinistre(str, enum.Enum):
    """Types de sinistres possibles"""
    ACCIDENT = "accident"
    VOL = "vol"
    INCENDIE = "incendie"
    DEGAT_NATUREL = "degat_naturel"
    BRIS_GLACE = "bris_glace"
    VANDALISME = "vandalisme"
    COLLISION = "collision"
    AUTRE = "autre"


class StatutSinistre(str, enum.Enum):
    """Statuts d'un sinistre"""
    DECLARE = "declare"
    EN_INSTRUCTION = "en_instruction"
    EN_ATTENTE = "en_attente"
    EXPERTISE = "expertise"
    VALIDE = "valide"
    REJETE = "rejete"
    INDEMNISE = "indemnise"
    CLOS = "clos"


class Responsabilite(str, enum.Enum):
    """Responsabilité dans le sinistre"""
    ASSURE = "assure"
    TIERS = "tiers"
    PARTAGE = "partage"
    INDETERMINEE = "indeterminee"


class Sinistre(Base):
    """Modèle principal des sinistres"""
    __tablename__ = "sinistres_auto"

    id = Column(Integer, primary_key=True, index=True)
    numero_dossier = Column(String(50), unique=True, nullable=False)
    
    # Liens
    contrat_id = Column(Integer, ForeignKey("contrats.id"), nullable=False)
    vehicule_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    
    # Informations générales
    type = Column(Enum(TypeSinistre), nullable=False)
    statut = Column(Enum(StatutSinistre), default=StatutSinistre.DECLARE)
    responsabilite = Column(Enum(Responsabilite), default=Responsabilite.INDETERMINEE)
    
    # Dates
    date_survenue = Column(DateTime, nullable=False)
    date_declaration = Column(DateTime, default=datetime.utcnow)
    date_expertise = Column(DateTime, nullable=True)
    date_fermeture = Column(DateTime, nullable=True)
    
    # Détails du sinistre
    lieu = Column(String(255))
    ville = Column(String(100))
    pays = Column(String(50), default="Cameroun")
    description = Column(Text)
    circonstances = Column(Text)
    conditions_meteo = Column(String(50))
    
    # Tiers impliqués
    tiers_nom = Column(String(255))
    tiers_prenom = Column(String(255))
    tiers_telephone = Column(String(50))
    tiers_assurance = Column(String(100))
    tiers_police = Column(String(50))
    tiers_vehicule = Column(String(100))
    
    # Témoins
    temoins_noms = Column(Text)  # JSON
    temoins_nombre = Column(Integer, default=0)
    
    # Montants
    estimation_preliminaire = Column(Float, default=0.0)
    estimation_finale = Column(Float, default=0.0)
    montant_indemnise = Column(Float, default=0.0)
    franchise = Column(Float, default=0.0)
    montant_net = Column(Float, default=0.0)
    
    # Documents
    pieces_joites = Column(Text)  # JSON des chemins
    nombre_pieces = Column(Integer, default=0)
    
    # Sinistres précédents
    sinistre_precedent = Column(Boolean, default=False)
    nombre_sinistres_anterieurs = Column(Integer, default=0)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("utilisateurs.id"))
    assigned_to = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    # Notes internes
    notes = Column(Text)
    
    # Relations
    contrat = relationship("Contrat", back_populates="sinistres")
    vehicule = relationship("Vehicle", back_populates="sinistres")
    client = relationship("Contact", back_populates="sinistres")
    expertise = relationship("Expertise", back_populates="sinistre", uselist=False)
    paiements = relationship("Indemnisation", back_populates="sinistre")
    
    def __repr__(self):
        return f"<Sinistre {self.numero_dossier} - {self.statut.value}>"
    
    @property
    def jours_ecoules(self):
        """Nombre de jours depuis la déclaration"""
        if self.date_declaration:
            return (datetime.utcnow() - self.date_declaration).days
        return 0
    
    @property
    def est_en_cours(self):
        """Vérifie si le sinistre est en cours"""
        return self.statut not in [StatutSinistre.CLOS, StatutSinistre.INDEMNISE, StatutSinistre.REJETE]
    
    @property
    def besoin_indemnisation(self):
        """Vérifie si une indemnisation est nécessaire"""
        return self.estimation_finale > 0 and self.statut == StatutSinistre.VALIDE
    
    @property
    def est_urgent(self):
        """Vérifie si le sinistre est urgent (> 15 jours sans action)"""
        return self.jours_ecoules > 15 and self.est_en_cours
    
    def get_type_label(self):
        """Retourne le libellé du type"""
        labels = {
            TypeSinistre.ACCIDENT: "Accident",
            TypeSinistre.VOL: "Vol",
            TypeSinistre.INCENDIE: "Incendie",
            TypeSinistre.DEGAT_NATUREL: "Dégât naturel",
            TypeSinistre.BRIS_GLACE: "Bris de glace",
            TypeSinistre.VANDALISME: "Vandalisme",
            TypeSinistre.COLLISION: "Collision",
            TypeSinistre.AUTRE: "Autre"
        }
        return labels.get(self.type, str(self.type))


class Indemnisation(Base):
    """Paiements d'indemnisation"""
    __tablename__ = "indemnisations_auto"
    
    id = Column(Integer, primary_key=True, index=True)
    sinistre_id = Column(Integer, ForeignKey("sinistres_auto.id"), nullable=False)
    
    # Montants
    montant = Column(Float, nullable=False)
    franchise_appliquee = Column(Float, default=0.0)
    montant_net = Column(Float, nullable=False)
    
    # Paiement
    date_paiement = Column(DateTime, default=datetime.utcnow)
    mode_paiement = Column(String(50))  # "virement", "cheque", "especes", "mobile_money"
    reference_paiement = Column(String(100))
    beneficiaire = Column(String(255))
    
    # Justificatifs
    justificatif = Column(String(255))  # Chemin du fichier
    
    # Statut
    statut = Column(String(50), default="en_attente")
    valide_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    date_validation = Column(DateTime, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("utilisateurs.id"))
    
    # Relations
    sinistre = relationship("Sinistre", back_populates="paiements")