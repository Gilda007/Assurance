"""
Modèles d'expertise, évaluation et provision (Tome 4 du CDC)
"""
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base, AuditableMixin


class LometaExpertise(Base, AuditableMixin):
    """
    Mission d'expertise
    """
    __tablename__ = "lometa_expertises"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    
    # Identification
    numero_mission = Column(String(20), unique=True, nullable=False, index=True)
    
    # Expert
    expert_id = Column(Integer, nullable=False, index=True)
    expert_nom = Column(String(100), nullable=True)  # Dénormalisation
    
    # Type d'expertise
    type_expertise = Column(String(50), nullable=False)  # auto_materiel, auto_corporel, batiment, transport, medical
    domaine = Column(String(50), nullable=True)
    
    # Dates
    date_mission = Column(DateTime, nullable=False)
    date_echeance = Column(DateTime, nullable=False)
    date_reception_rapport = Column(DateTime, nullable=True)
    date_validation = Column(DateTime, nullable=True)
    
    # Statut
    statut = Column(String(30), nullable=False, default="CREEE", index=True)
    # CREEE, AFFECTEE, EN_COURS, RAPPORT_REÇU, VALIDE, ANNULE
    
    # Rapport
    rapport_contenu = Column(Text, nullable=True)
    rapport_path = Column(String(255), nullable=True)
    montant_estime = Column(Float, nullable=True)
    
    # Documents associés
    photos_path = Column(String(255), nullable=True)
    constats_path = Column(String(255), nullable=True)
    devis_path = Column(String(255), nullable=True)
    
    # Observations
    observations = Column(Text, nullable=True)
    preconisations = Column(Text, nullable=True)
    
    # Validation
    valide_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    date_validation = Column(DateTime, nullable=True)
    motif_refus = Column(Text, nullable=True)
    
    # Relations
    sinistre = relationship(
        "LometaSinistre", 
        back_populates="expertises"
    )
    # Rapport d'expertise (documents)
    documents = relationship(
        "LometaDocumentExpertise", 
        back_populates="expertise", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Expertise {self.numero_mission} - {self.statut}>"


class LometaDocumentExpertise(Base, AuditableMixin):
    """
    Documents associés à une expertise
    """
    __tablename__ = "lometa_documents_expertise"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    expertise_id = Column(Integer, ForeignKey("lometa_expertises.id"), nullable=False, index=True)
    
    type_document = Column(String(30), nullable=False)  # rapport, photo, constat, devis
    nom_fichier = Column(String(255), nullable=False)
    chemin_fichier = Column(String(255), nullable=False)
    taille = Column(Integer, nullable=True)
    hash_fichier = Column(String(64), nullable=True)
    
    date_upload = Column(DateTime, default=datetime.utcnow)
    upload_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    
    expertise = relationship("LometaExpertise", back_populates="documents")


class LometaEvaluation(Base, AuditableMixin):
    """
    Évaluation financière du sinistre
    """
    __tablename__ = "lometa_evaluations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    
    # Identification
    numero_evaluation = Column(String(20), unique=True, nullable=False, index=True)
    
    # Type
    type_evaluation = Column(String(50), nullable=False)  # auto_materiel, auto_corporel, incendie, etc.
    categorie = Column(String(30), nullable=True)
    
    # Montants
    montant_brut = Column(Float, nullable=False)
    franchise = Column(Float, default=0.0)
    taux_responsabilite = Column(Float, default=1.0)
    montant_net = Column(Float, nullable=False)  # (montant_brut - franchise) * taux_responsabilite
    
    # Détails
    details = Column(Text, nullable=True)
    
    # Validation
    est_validee = Column(Boolean, default=False, index=True)
    validee_par = Column(Integer, nullable=True)
    date_validation = Column(DateTime, nullable=True)
    
    # Dates
    date_evaluation = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    sinistre = relationship(
        "LometaSinistre", 
        back_populates="evaluations"
    )
    revisions = relationship(
        "LometaRevisionEvaluation", 
        back_populates="evaluation", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Evaluation {self.numero_evaluation} - {self.montant_net}>"
    
    def calculer_montant_net(self):
        """Calcule le montant net selon la formule standard"""
        return (self.montant_brut - self.franchise) * self.taux_responsabilite


class LometaRevisionEvaluation(Base, AuditableMixin):
    """
    Révision d'une évaluation (historique des modifications)
    """
    __tablename__ = "lometa_revisions_evaluation"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(Integer, ForeignKey("lometa_evaluations.id"), nullable=False, index=True)
    
    # Anciennes valeurs
    ancien_montant_brut = Column(Float, nullable=False)
    ancien_montant_net = Column(Float, nullable=False)
    
    # Nouvelles valeurs
    nouveau_montant_brut = Column(Float, nullable=False)
    nouveau_montant_net = Column(Float, nullable=False)
    
    # Motif
    motif = Column(String(200), nullable=False)
    
    # Dates
    date_revision = Column(DateTime, default=datetime.utcnow)
    revise_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    
    # Relations
    evaluation = relationship(
        "LometaEvaluation", 
        back_populates="revisions"
    )
    
    def __repr__(self):
        return f"<RevisionEvaluation {self.motif[:30]}...>"


class LometaProvision(Base, AuditableMixin):
    """
    Provision technique (engagement financier estimé)
    """
    __tablename__ = "lometa_provisions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    
    # Identification
    numero_provision = Column(String(20), unique=True, nullable=False, index=True)
    
    # Type
    type_provision = Column(String(30), nullable=False)  # initiale, complementaire, revisee, finale
    categorie = Column(String(30), nullable=True)
    
    # Montant
    montant = Column(Float, nullable=False)
    
    # Statut
    est_active = Column(Boolean, default=True, index=True)
    est_comptabilisee = Column(Boolean, default=False)
    
    # Dates
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_cloture = Column(DateTime, nullable=True)
    
    # Références
    evaluation_id = Column(Integer, nullable=True)  # Évaluation à l'origine de la provision
    motif = Column(String(200), nullable=True)
    
    # Relations
    sinistre = relationship(
        "LometaSinistre", 
        back_populates="provisions"
    )
    mouvements = relationship(
        "LometaMouvementProvision", 
        back_populates="provision", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Provision {self.numero_provision} - {self.montant}>"


class LometaMouvementProvision(Base, AuditableMixin):
    """
    Mouvement sur une provision (historique des modifications)
    """
    __tablename__ = "lometa_mouvements_provision"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    provision_id = Column(Integer, ForeignKey("lometa_provisions.id"), nullable=False)
    
    type_mouvement = Column(String(30), nullable=False)  # creation, augmentation, diminution, cloture
    
    ancien_montant = Column(Float, nullable=True)
    nouveau_montant = Column(Float, nullable=False)
    variation = Column(Float, nullable=False)  # nouveau - ancien
    
    motif = Column(String(200), nullable=False)
    date_mouvement = Column(DateTime, default=datetime.utcnow)
    effectue_par = Column(Integer, nullable=False)
    
    provision = relationship(
        "LometaProvision", 
        back_populates="mouvements"
    )
    
    def __repr__(self):
        return f"<MouvementProvision {self.type_mouvement} - {self.variation}>"