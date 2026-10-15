"""
Modèles d'expertise, évaluation et provision (Tome 4 du CDC)
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base, AuditableMixin

class LometaExpert(Base, AuditableMixin):
    """Référentiel des experts"""
    __tablename__ = "lometa_experts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    civilite = Column(String(10), nullable=True)
    nom = Column(String(100), nullable=False, index=True)
    prenom = Column(String(100), nullable=True)
    agrement = Column(String(50), nullable=False, unique=True, index=True)
    date_agrement = Column(DateTime, nullable=True)
    est_actif = Column(Boolean, nullable=False, default=True, index=True)
    
    # Coordonnées
    telephone = Column(String(20), nullable=True)
    portable = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    adresse = Column(Text, nullable=True)
    code_postal = Column(String(10), nullable=True)
    ville = Column(String(50), nullable=True)
    pays = Column(String(50), nullable=True)
    photo_path = Column(String(255), nullable=True)
    
    # Métier
    domaines = Column(JSON, nullable=True)  # ["Automobile", "Bâtiment"]
    zones = Column(JSON, nullable=True)     # ["Douala", "Yaoundé"]
    tarif_horaire = Column(Numeric, default=0.0)
    frais_deplacement = Column(Numeric, default=0.0)
    observations = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Expert {self.code} - {self.nom} {self.prenom or ''}>"


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
    expert_id = Column(Integer, ForeignKey("lometa_experts.id"), nullable=False, index=True)
    expert_nom = Column(String(100), nullable=True)  # Dénormalisation
    
    # Type d'expertise
    type_expertise = Column(String(50), nullable=False)  # auto_materiel, auto_corporel, batiment, transport, medical
    domaine = Column(String(50), nullable=True)
    
    # Dates
    date_mission = Column(DateTime, nullable=False)
    date_echeance = Column(DateTime, nullable=False)
    date_reception_rapport = Column(DateTime, nullable=True)
    
    # Statut
    statut = Column(String(30), nullable=False, default="CREEE", index=True)
    # CREEE, AFFECTEE, EN_COURS, RAPPORT_REÇU, VALIDE, ANNULE
    
    # Rapport
    rapport_contenu = Column(Text, nullable=True)
    rapport_path = Column(String(255), nullable=True)
    montant_estime = Column(Numeric, nullable=True)
    
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
    expert = relationship("LometaExpert", foreign_keys=[expert_id])

    def __repr__(self):
        return f"<Expertise {self.numero_mission} - {self.statut}>"


class LometaDocumentExpertise(Base, AuditableMixin):
    """Liaison document ↔ expertise"""
    __tablename__ = "lometa_documents_expertise"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    expertise_id = Column(
        Integer,
        ForeignKey("lometa_expertises.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    document_id = Column(
        Integer,
        ForeignKey("lometa_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    type_lien = Column(String(30), nullable=False)  # RAPPORT, PHOTO, CONSTAT, DEVIS
    
    # ✅ AJOUT : relations bidirectionnelles
    expertise = relationship(
        "LometaExpertise",
        back_populates="documents"
    )
    document = relationship(
        "LometaDocument",
        foreign_keys=[document_id]
    )
    
    def __repr__(self):
        return f"<LometaDocumentExpertise expertise={self.expertise_id} doc={self.document_id}>"


class LometaEvaluation(Base, AuditableMixin):
    """
    Évaluation financière du sinistre
    """
    __tablename__ = "lometa_evaluations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    dommage_id = Column(
        Integer,
        ForeignKey("lometa_dommages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Identification
    numero_evaluation = Column(String(20), unique=True, nullable=False, index=True)
    
    # Type
    type_evaluation = Column(String(50), nullable=False)  # auto_materiel, auto_corporel, incendie, etc.
    categorie = Column(String(30), nullable=True)
    statut = Column(String(20), nullable=False, default="BROUILLON", index=True)
    
    # Montants
    montant_brut = Column(Numeric, nullable=False)
    franchise = Column(Numeric, default=0.0)
    taux_responsabilite = Column(Numeric, default=1.0)
    montant_net = Column(Numeric, nullable=False)  # (montant_brut - franchise) * taux_responsabilite
    
    
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
    dommage = relationship("LometaDommage", foreign_keys=[dommage_id])
    
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
    ancien_montant_brut = Column(Numeric, nullable=False)
    ancien_montant_net = Column(Numeric, nullable=False)
    
    # Nouvelles valeurs
    nouveau_montant_brut = Column(Numeric, nullable=False)
    nouveau_montant_net = Column(Numeric, nullable=False)
    
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
    montant = Column(Numeric, nullable=False)
    
    # Statut
    est_active = Column(Boolean, default=True, index=True)
    est_comptabilisee = Column(Boolean, default=False)
    
    # Dates
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_cloture = Column(DateTime, nullable=True)
    
    # Références
    evaluation_id = Column(
        Integer,
        ForeignKey("lometa_evaluations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )  # Évaluation à l'origine de la provision
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
    evaluation = relationship("LometaEvaluation", foreign_keys=[evaluation_id])
    
    def __repr__(self):
        return f"<Provision {self.numero_provision} - {self.montant}>"


class LometaAvocat(Base, AuditableMixin):
    """Référentiel des avocats (Tome 2 §12)"""
    __tablename__ = "lometa_avocats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    cabinet = Column(String(200), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=True)
    agrement = Column(String(50), nullable=True)
    specialite = Column(String(100), nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    adresse = Column(Text, nullable=True)
    ville = Column(String(50), nullable=True)
    code_postal = Column(String(10), nullable=True)
    pays = Column(String(50), nullable=True)
    est_actif = Column(Boolean, default=True, nullable=False)


class LometaMouvementProvision(Base, AuditableMixin):
    """
    Mouvement sur une provision (historique des modifications)
    """
    __tablename__ = "lometa_mouvements_provision"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    provision_id = Column(Integer, ForeignKey("lometa_provisions.id"), nullable=False)
    effectue_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    
    type_mouvement = Column(String(30), nullable=False)  # creation, augmentation, diminution, cloture
    
    ancien_montant = Column(Numeric, nullable=True)
    nouveau_montant = Column(Numeric, nullable=False)
    variation = Column(Numeric, nullable=False)  # nouveau - ancien
    
    motif = Column(String(200), nullable=False)
    date_mouvement = Column(DateTime, default=datetime.utcnow)
    
    provision = relationship(
        "LometaProvision", 
        back_populates="mouvements"
    )
    
    def __repr__(self):
        return f"<MouvementProvision {self.type_mouvement} - {self.variation}>"