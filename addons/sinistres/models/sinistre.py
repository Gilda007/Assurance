"""
Modèles du dossier sinistre (Tome 3 du CDC)
"""
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, Boolean, Integer, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base, AuditableMixin


class LometaSinistre(Base, AuditableMixin):
    """
    Dossier sinistre - Cœur du système
    Correspond au Tome 3 du CDC
    """
    __tablename__ = "lometa_sinistres"
    
    # --- ID et identification ---
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_sinistre = Column(String(20), unique=True, nullable=False, index=True)
    numero_reference = Column(String(20), nullable=True, index=True)  # Référence agence
    
    # --- Informations générales ---
    date_survenance = Column(DateTime, nullable=False)
    date_declaration = Column(DateTime, nullable=False)
    date_ouverture = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # --- Liens ---
    contrat_id = Column(Integer, nullable=False, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    compagnie_id = Column(Integer, nullable=True)
    agence_id = Column(Integer, nullable=True)
    
    # --- Classification ---
    branche = Column(String(50), nullable=False, index=True)  # Auto, RC, Incendie, Transport, Santé
    categorie = Column(String(50), nullable=False, index=True)
    sous_categorie = Column(String(50), nullable=True)
    
    # --- Statut (cycle de vie) ---
    statut = Column(String(30), nullable=False, default="OUVERT", index=True)
    # Valeurs: OUVERT, EN_INSTRUCTION, EN_EXPERTISE, EN_EVALUATION, 
    #          VALIDE, EN_REGLEMENT, EN_RECOURS, CLOTURE, REOPENED
    
    # --- Responsabilité ---
    taux_responsabilite = Column(Float, default=0.0)  # 0% à 100%
    
    # --- Circonstances ---
    circonstance_principale = Column(String(100), nullable=False)
    circonstance_secondaire = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    est_flotte = Column(
        Boolean, 
        nullable=False, 
        default=False, 
        index=True,
        comment="Indique si le sinistre concerne un contrat flotte"
    )
    
    
    # --- Dates importantes ---
    date_cloture = Column(DateTime, nullable=True)
    date_reexamen = Column(DateTime, nullable=True)
    date_derniere_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # --- Responsable ---

    vehicule_sinistre_id = Column(
        Integer, 
        ForeignKey("vehicles.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True,
        comment="Véhicule sinistré (obligatoire si est_flotte=True)"
    )
    
    flotte_id = Column(
        Integer, 
        ForeignKey("fleets.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True,
        comment="Flotte associée au sinistre"
    )
    responsable_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True, index=True)  # Gestionnaire actuel
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # --- Relations ---
    dommages = relationship(
        "LometaDommage", 
        back_populates="sinistre", 
        cascade="all, delete-orphan"
    )
    vehicule_sinistre = relationship(
        "Vehicle",
        foreign_keys=[vehicule_sinistre_id],
        lazy="joined"
    )
    
    flotte = relationship(
        "Fleet",
        foreign_keys=[flotte_id],
        lazy="joined"
    )
    tiers = relationship(
        "LometaTiers", 
        back_populates="sinistre", 
        cascade="all, delete-orphan"
    )
    expertises = relationship(
        "LometaExpertise", 
        back_populates="sinistre", 
        cascade="all, delete-orphan"
    )
    evaluations = relationship(
        "LometaEvaluation", 
        back_populates="sinistre", 
        cascade="all, delete-orphan"
    )
    provisions = relationship(
        "LometaProvision", 
        back_populates="sinistre", 
        cascade="all, delete-orphan"
    )
    reglements = relationship(
        "LometaReglement", 
        back_populates="sinistre", 
        cascade="all, delete-orphan"
    )
    recours = relationship(
        "LometaRecours", 
        back_populates="sinistre", 
        cascade="all, delete-orphan"
    )
    historique = relationship(
        "LometaHistoriqueSinistre", 
        back_populates="sinistre", 
        cascade="all, delete-orphan"
    )
    commentaires = relationship(
        "LometaCommentaireSinistre", 
        back_populates="sinistre", 
        cascade="all, delete-orphan"
    )
    responsable = relationship("User", foreign_keys=[responsable_id])
    
    def __repr__(self):
        return f"<Sinistre {self.numero_sinistre} - {self.statut}>"


class LometaDommage(Base, AuditableMixin):
    """
    Dommage subi dans le cadre d'un sinistre
    """
    __tablename__ = "lometa_dommages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    
    # Type de dommage (référentiel)
    type_dommage = Column(String(50), nullable=False)  # materiel, corporel, immateriel
    code_dommage = Column(String(20), nullable=True)   # Référence du référentiel
    
    # Description
    description = Column(Text, nullable=True)
    photos = Column(JSON, nullable=True)
    
    # Évaluation
    montant_estime = Column(Float, default=0.0)
    montant_accepte = Column(Float, nullable=True)
    
    # Liens
    evaluation_id = Column(Integer, nullable=True)  # Référence vers l'évaluation associée
    
    # Relations
    sinistre = relationship("LometaSinistre", back_populates="dommages")
    
    def __repr__(self):
        return f"<Dommage {self.type_dommage} - {self.montant_estime}>"


class LometaTiers(Base, AuditableMixin):
    """
    Tiers impliqué dans le sinistre
    """
    __tablename__ = "lometa_tiers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    
    # Type de tiers
    type_tiers = Column(String(30), nullable=False)  # responsable, victime, temoin, assureur_adverse
    code_tiers = Column(String(20), nullable=True)   # Référence du référentiel
    
    # Identité
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=True)
    civilite = Column(String(10), nullable=True)
    
    # Coordonnées
    adresse = Column(Text, nullable=True)
    code_postal = Column(String(10), nullable=True)
    ville = Column(String(50), nullable=True)
    pays = Column(String(50), nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    
    # Assurance (pour tiers responsable ou victime)
    assurance = Column(String(100), nullable=True)
    police_assurance = Column(String(50), nullable=True)
    compagnie_assurance_id = Column(Integer, nullable=True)
    
    # Informations complémentaires
    date_naissance = Column(DateTime, nullable=True)
    profession = Column(String(50), nullable=True)
    observations = Column(Text, nullable=True)
    
    # Relations
    sinistre = relationship("LometaSinistre", back_populates="tiers")
    
    def __repr__(self):
        return f"<Tiers {self.type_tiers} - {self.nom} {self.prenom or ''}>"


class LometaCommentaireSinistre(Base, AuditableMixin):
    """
    Commentaires de gestion sur le sinistre
    """
    __tablename__ = "lometa_commentaires"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    
    # Contenu
    contenu = Column(Text, nullable=False)
    
    # Type de commentaire
    type_commentaire = Column(String(30), nullable=False)  # gestionnaire, expert, comptable, responsable
    
    # Versionnement
    version = Column(Integer, default=1)
    version_precedente_id = Column(Integer, nullable=True)
    
    # Relations
    sinistre = relationship("LometaSinistre", back_populates="commentaires")
    
    def __repr__(self):
        return f"<CommentaireSinistre v{self.version}>"


class LometaHistoriqueSinistre(Base):
    """
    Historique des actions sur un sinistre (traçabilité totale)
    """
    __tablename__ = "lometa_historique"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    
    # Qui
    utilisateur_id = Column(Integer, nullable=False, index=True)
    utilisateur_nom = Column(String(100), nullable=True)  # Dénormalisation pour l'affichage
    
    # Quand
    date_action = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_adresse = Column(String(45), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Quoi
    action = Column(String(50), nullable=False, index=True)  # CREATION, MODIFICATION, VALIDATION, etc.
    entite = Column(String(50), nullable=False)  # Sinistre, Evaluation, Reglement, etc.
    entite_id = Column(Integer, nullable=True)
    
    # Ancienne valeur / Nouvelle valeur
    champ_modifie = Column(String(50), nullable=True)
    ancienne_valeur = Column(Text, nullable=True)
    nouvelle_valeur = Column(Text, nullable=True)
    
    # Commentaire
    commentaire = Column(Text, nullable=True)
    
    # Relations
    sinistre = relationship("LometaSinistre", back_populates="historique")
    
    def __repr__(self):
        return f"<Historique {self.action} - {self.utilisateur_id} - {self.date_action}>"