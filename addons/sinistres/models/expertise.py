

"""
Modèles d'expertise, évaluation et provision (Tome 4 du CDC)
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base, AuditableMixin


# ============================================================
# ✅ Constantes UI (uniquement pour préfixes/couleurs par défaut)
# Les VRAIES données métier viennent de lometa_referentiels
# ============================================================
TYPE_MISSION_UI_DEFAULTS = {
    "EXPERTISE":        {"prefixe_numero": "EXP", "couleur": "#2563eb"},
    "GARAGISTE":        {"prefixe_numero": "GAR", "couleur": "#ea580c"},
    "CONTRE_EXPERTISE": {"prefixe_numero": "CEX", "couleur": "#7c3aed"},
    "MEDICALE":         {"prefixe_numero": "MED", "couleur": "#0891b2"},
    "JUDICIAIRE":       {"prefixe_numero": "JUD", "couleur": "#dc2626"},
}


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

    telephone = Column(String(20), nullable=True)
    portable = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    adresse = Column(Text, nullable=True)
    code_postal = Column(String(10), nullable=True)
    ville = Column(String(50), nullable=True)
    pays = Column(String(50), nullable=True)
    photo_path = Column(String(255), nullable=True)

    domaines = Column(JSON, nullable=True)
    zones = Column(JSON, nullable=True)
    tarif_horaire = Column(Numeric, default=0.0)
    frais_deplacement = Column(Numeric, default=0.0)
    observations = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Expert {self.code} - {self.nom} {self.prenom or ''}>"


class LometaExpertise(Base, AuditableMixin):
    """Mission d'expertise"""
    __tablename__ = "lometa_expertises"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)

    numero_mission = Column(String(20), unique=True, nullable=False, index=True)

    # ✅ Seul le code est conservé (FK logique vers lometa_referentiels.code)
    # Les métadonnées (libellé, couleur, préfixe) sont lues via le service
    type_mission_code = Column(String(30), nullable=False, default="EXPERTISE", index=True)

    # ✅ Mission parente (contre-expertise)
    mission_parente_id = Column(
        Integer,
        ForeignKey("lometa_expertises.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    expert_id = Column(Integer, ForeignKey("lometa_experts.id"), nullable=False, index=True)
    expert_nom = Column(String(100), nullable=True)

    type_expertise = Column(String(50), nullable=False)
    domaine = Column(String(50), nullable=True)

    date_mission = Column(DateTime, nullable=False)
    date_echeance = Column(DateTime, nullable=False)
    date_reception_rapport = Column(DateTime, nullable=True)

    statut = Column(String(30), nullable=False, default="CREEE", index=True)

    rapport_contenu = Column(Text, nullable=True)
    rapport_path = Column(String(255), nullable=True)
    montant_estime = Column(Numeric, nullable=True)
    montant_devis_garagiste = Column(Numeric, nullable=True)

    photos_path = Column(String(255), nullable=True)
    constats_path = Column(String(255), nullable=True)
    devis_path = Column(String(255), nullable=True)

    observations = Column(Text, nullable=True)
    preconisations = Column(Text, nullable=True)
    motif_contre_expertise = Column(Text, nullable=True)

    valide_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    date_validation = Column(DateTime, nullable=True)
    motif_refus = Column(Text, nullable=True)

    # Relations
    sinistre = relationship("LometaSinistre", back_populates="expertises")
    documents = relationship(
        "LometaDocumentExpertise",
        back_populates="expertise",
        cascade="all, delete-orphan",
    )
    expert = relationship("LometaExpert", foreign_keys=[expert_id])

    # Relation auto-référencée
    mission_parente = relationship(
        "LometaExpertise",
        remote_side=[id],
        backref="contre_expertises",
        foreign_keys=[mission_parente_id],
    )

    @property
    def est_contre_expertise(self) -> bool:
        return self.type_mission_code == "CONTRE_EXPERTISE"

    @property
    def est_garagiste(self) -> bool:
        return self.type_mission_code == "GARAGISTE"

    def __repr__(self):
        return f"<Expertise {self.numero_mission} [{self.type_mission_code}] - {self.statut}>"


class LometaDocumentExpertise(Base, AuditableMixin):
    """Liaison document ↔ expertise"""
    __tablename__ = "lometa_documents_expertise"

    id = Column(Integer, primary_key=True, autoincrement=True)
    expertise_id = Column(
        Integer,
        ForeignKey("lometa_expertises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id = Column(
        Integer,
        ForeignKey("lometa_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type_lien = Column(String(30), nullable=False)

    expertise = relationship("LometaExpertise", back_populates="documents")
    document = relationship("LometaDocument", foreign_keys=[document_id])

    def __repr__(self):
        return f"<LometaDocumentExpertise expertise={self.expertise_id} doc={self.document_id}>"


class LometaEvaluation(Base, AuditableMixin):
    """Évaluation financière du sinistre"""
    __tablename__ = "lometa_evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    dommage_id = Column(
        Integer,
        ForeignKey("lometa_dommages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    numero_evaluation = Column(String(20), unique=True, nullable=False, index=True)
    type_evaluation = Column(String(50), nullable=False)
    categorie = Column(String(30), nullable=True)
    statut = Column(String(20), nullable=False, default="BROUILLON", index=True)

    montant_brut = Column(Numeric, nullable=False)
    montant_expert = Column(Numeric, nullable=True)
    franchise = Column(Numeric, default=0.0)
    taux_responsabilite = Column(Numeric, default=1.0)
    montant_net = Column(Numeric, nullable=False)
    details = Column(Text, nullable=True)

    # Document de proposition (PDF généré, toujours disponible)
    document_proposition_path = Column(String(500), nullable=True)
    document_proposition_generee_le = Column(DateTime, nullable=True)

    # Avis du client
    avis_client = Column(String(20), nullable=True)  # "ACCEPTE" | "REFUSE"
    date_avis_client = Column(DateTime, nullable=True)
    commentaire_client = Column(Text, nullable=True)

    # Pièce jointe du client (photo ou PDF)
    piece_jointe_client_path = Column(String(500), nullable=True)
    piece_jointe_client_nom = Column(String(255), nullable=True)
    piece_jointe_client_type = Column(String(50), nullable=True)  # MIME type

    est_validee = Column(Boolean, default=False, index=True)
    validee_par = Column(Integer, nullable=True)
    date_validation = Column(DateTime, nullable=True)
    date_evaluation = Column(DateTime, default=datetime.utcnow)

    mission_id = Column(
        Integer,
        ForeignKey("lometa_expertises.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    mission = relationship("LometaExpertise", foreign_keys=[mission_id])

    sinistre = relationship("LometaSinistre", back_populates="evaluations")
    revisions = relationship(
        "LometaRevisionEvaluation",
        back_populates="evaluation",
        cascade="all, delete-orphan",
    )
    dommage = relationship("LometaDommage", foreign_keys=[dommage_id])

    def __repr__(self):
        return f"<Evaluation {self.numero_evaluation} - {self.montant_net}>"

    def calculer_montant_net(self):
        return (self.montant_brut - self.franchise) * self.taux_responsabilite


class LometaRevisionEvaluation(Base, AuditableMixin):
    """Révision d'une évaluation"""
    __tablename__ = "lometa_revisions_evaluation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(Integer, ForeignKey("lometa_evaluations.id"), nullable=False, index=True)

    ancien_montant_brut = Column(Numeric, nullable=False)
    ancien_montant_net = Column(Numeric, nullable=False)
    nouveau_montant_brut = Column(Numeric, nullable=False)
    nouveau_montant_net = Column(Numeric, nullable=False)
    motif = Column(String(200), nullable=False)
    date_revision = Column(DateTime, default=datetime.utcnow)
    revise_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)

    evaluation = relationship("LometaEvaluation", back_populates="revisions")

    def __repr__(self):
        return f"<RevisionEvaluation {self.motif[:30]}...>"


class LometaProvision(Base, AuditableMixin):
    """Provision technique"""
    __tablename__ = "lometa_provisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    numero_provision = Column(String(20), unique=True, nullable=False, index=True)
    type_provision = Column(String(30), nullable=False)
    categorie = Column(String(30), nullable=True)
    montant = Column(Numeric, nullable=False)
    est_active = Column(Boolean, default=True, index=True)
    est_comptabilisee = Column(Boolean, default=False)
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_cloture = Column(DateTime, nullable=True)

    evaluation_id = Column(
        Integer,
        ForeignKey("lometa_evaluations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    motif = Column(String(200), nullable=True)

    sinistre = relationship("LometaSinistre", back_populates="provisions")
    mouvements = relationship(
        "LometaMouvementProvision",
        back_populates="provision",
        cascade="all, delete-orphan",
    )
    evaluation = relationship("LometaEvaluation", foreign_keys=[evaluation_id])

    def __repr__(self):
        return f"<Provision {self.numero_provision} - {self.montant}>"


class LometaAvocat(Base, AuditableMixin):
    """Référentiel des avocats"""
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
    """Mouvement sur une provision"""
    __tablename__ = "lometa_mouvements_provision"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provision_id = Column(Integer, ForeignKey("lometa_provisions.id"), nullable=False)
    effectue_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    type_mouvement = Column(String(30), nullable=False)
    ancien_montant = Column(Numeric, nullable=True)
    nouveau_montant = Column(Numeric, nullable=False)
    variation = Column(Numeric, nullable=False)
    motif = Column(String(200), nullable=False)
    date_mouvement = Column(DateTime, default=datetime.utcnow)

    provision = relationship("LometaProvision", back_populates="mouvements")

    def __repr__(self):
        return f"<MouvementProvision {self.type_mouvement} - {self.variation}>"