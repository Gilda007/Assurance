"""
Modèles de recours - Adaptés pour Integer
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base, AuditableMixin


class LometaRecours(Base, AuditableMixin):
    """Recours contre un tiers responsable"""
    __tablename__ = "lometa_recours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    reglement_id = Column(
        Integer,
        ForeignKey("lometa_reglements.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    evaluation_id = Column(
        Integer,
        ForeignKey("lometa_evaluations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    debiteur_id = Column(Integer, nullable=True, index=True)

    numero_recours = Column(String(20), nullable=False, unique=True, index=True)
    type_recours = Column(String(30), nullable=False)
    
    debiteur_type = Column(
        String(20),
        nullable=False,
        default="TIERS"
    )
    # Valeurs : TIERS, COMPAGNIE

    # FK vers LometaTiers (débiteur personne physique/morale)
    debiteur_tiers_id = Column(
        Integer,
        ForeignKey("lometa_tiers.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )

    # FK vers Compagnie (débiteur assureur adverse)
    debiteur_compagnie_id = Column(
        Integer,
        ForeignKey("automobile_compagnies.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )
    debiteur_nom = Column(String(100), nullable=True)
    
    montant_reclame = Column(Numeric, nullable=False)
    montant_accepte = Column(Numeric, nullable=True)
    montant_encaisse = Column(Numeric, nullable=False, default=0.0)
    solde = Column(Numeric, nullable=False, default=0.0)
    
    date_ouverture = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_accord = Column(DateTime, nullable=True)
    date_derniere_relance = Column(DateTime, nullable=True)
    date_prochaine_relance = Column(DateTime, nullable=True)
    date_cloture = Column(DateTime, nullable=True)
    
    statut = Column(String(30), nullable=False, default="OUVERT", index=True)
    
    responsable_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    nombre_relances = Column(Integer, nullable=False, default=0)
    relance_max = Column(Integer, nullable=False, default=5)
    
    reference_accord = Column(String(50), nullable=True)
    document_justificatif = Column(String(255), nullable=True)
    observations = Column(Text, nullable=True)
    motif_cloture = Column(Text, nullable=True)
    
    # Audit
    reglement = relationship("LometaReglement", foreign_keys=[reglement_id])
    debiteur_tiers = relationship("LometaTiers", foreign_keys=[debiteur_tiers_id])
    debiteur_compagnie = relationship("Compagnie", foreign_keys=[debiteur_compagnie_id])

    
    sinistre = relationship(
        "LometaSinistre", 
        back_populates="recours"
    )
    encaissements = relationship(
        "LometaEncaissementRecours", 
        back_populates="recours", 
        cascade="all, delete-orphan"
    )
    reversements = relationship(
        "LometaReversementRecours", 
        back_populates="recours", 
        cascade="all, delete-orphan"
    )
    relances = relationship(
        "LometaRelanceRecours", 
        back_populates="recours", 
        cascade="all, delete-orphan"
    )
    repartitions = relationship(
        "LometaRepartitionRecours",
        back_populates="recours",
        cascade="all, delete-orphan"
    )
    ecritures_comptables = relationship(
        "LometaEcritureComptable",
        foreign_keys="LometaEcritureComptable.recours_id",
        back_populates="recours"
    )

    @property
    def debiteur(self):
        """Retourne le débiteur (tiers ou compagnie) selon le type"""
        if self.debiteur_type == "COMPAGNIE":
            return self.debiteur_compagnie
        return self.debiteur_tiers

    @property
    def debiteur_id(self):
        """Retourne l'ID du débiteur selon son type"""
        if self.debiteur_type == "COMPAGNIE":
            return self.debiteur_compagnie_id
        return self.debiteur_tiers_id

    @debiteur_id.setter
    def debiteur_id(self, value):
        """
        Setter pour debiteur_id.
        Redirige vers debiteur_tiers_id ou debiteur_compagnie_id
        selon le debiteur_type.
        """
        if self.debiteur_type == "COMPAGNIE":
            self.debiteur_compagnie_id = value
        else:
            self.debiteur_tiers_id = value


class LometaEncaissementRecours(Base, AuditableMixin):
    """Encaissement d'un recours"""
    __tablename__ = "lometa_encaissements_recours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recours_id = Column(Integer, ForeignKey("lometa_recours.id"), nullable=False, index=True)
    
    montant = Column(Numeric, nullable=False)
    mode_encaissement = Column(String(20), nullable=False)
    reference_bancaire = Column(String(50), nullable=True)
    date_encaissement = Column(DateTime, nullable=False)
    banque = Column(String(100), nullable=True)
    compte_bancaire_id = Column(
        Integer,
        ForeignKey("lometa_comptes_bancaires.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    est_partiel = Column(Boolean, nullable=False, default=False)
    solde_apres_encaissement = Column(Numeric, nullable=False)
    
    journal_comptable = Column(String(20), nullable=True)
    est_comptabilise = Column(Boolean, nullable=False, default=False)
    date_comptabilisation = Column(DateTime, nullable=True)
    note_credit_id = Column(
        Integer,
        ForeignKey("lometa_notes_credit.id", ondelete="SET NULL"),
        nullable=True
    )
    observations = Column(Text, nullable=True)
    
    # Audit

    compte_bancaire = relationship("LometaCompteBancaire", foreign_keys=[compte_bancaire_id])
    note_credit = relationship("LometaNoteCredit", foreign_keys=[note_credit_id])
    recours = relationship(
        "LometaRecours", 
        back_populates="encaissements"
    )
    ecritures = relationship(
        "LometaEcritureComptable",
        primaryjoin=(
            "and_("
            "LometaEncaissementRecours.id == foreign(LometaEcritureComptable.reference_id), "
            "LometaEcritureComptable.reference_type == 'ENCAISSEMENT_RECOURS'"
            ")"
        ),
        viewonly=True,
    )


class LometaRepartitionRecours(Base, AuditableMixin):
    """
    Répartition d'un recours encaissé entre les parties prenantes.
    
    Règle CDC Tome 6 §8 (REC-020) :
    La somme des répartitions doit être égale au montant encaissé.
    
    Types de bénéficiaires :
    - CLIENT     : Part restituée au client
    - COMPAGNIE  : Part conservée par la compagnie
    - HONORAIRES : Honoraires (agence, gestionnaire)
    - COASSUREUR : Part reversée aux coassureurs
    - AUTRE      : Autres bénéficiaires
    """
    __tablename__ = "lometa_repartitions_recours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recours_id = Column(
        Integer,
        ForeignKey("lometa_recours.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Type de bénéficiaire
    type_beneficiaire = Column(String(30), nullable=False, index=True)
    # CLIENT, COMPAGNIE, HONORAIRES, COASSUREUR, AUTRE
    
    # Bénéficiaire (FK optionnelle selon type)
    beneficiaire_id = Column(
        Integer,
        ForeignKey("lometa_beneficiaires.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    beneficiaire_nom = Column(String(100), nullable=False)
    
    # Répartition
    quote_part = Column(Numeric(5, 2), nullable=False)   # Pourcentage (0.00 à 100.00)
    montant = Column(Numeric, nullable=False)             # Valeur calculée
    
    # État du reversement
    est_reverse = Column(Boolean, nullable=False, default=False, index=True)
    date_reversement = Column(DateTime, nullable=True)
    reversement_id = Column(
        Integer,
        ForeignKey("lometa_reversements_recours.id", ondelete="SET NULL"),
        nullable=True
    )
    
    observations = Column(Text, nullable=True)
    
    # Relations
    recours = relationship("LometaRecours", back_populates="repartitions")
    beneficiaire = relationship("LometaBeneficiaire", foreign_keys=[beneficiaire_id])
    reversement = relationship("LometaReversementRecours", foreign_keys=[reversement_id])
    
    def __repr__(self):
        return (
            f"<LometaRepartitionRecours {self.type_beneficiaire} "
            f"{self.quote_part}% = {self.montant}>"
        )


class LometaReversementRecours(Base, AuditableMixin):
    """Reversement au client"""
    __tablename__ = "lometa_reversements_recours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recours_id = Column(Integer, ForeignKey("lometa_recours.id"), nullable=False, index=True)
    
    beneficiaire_id = Column(
        Integer,
        ForeignKey("lometa_beneficiaires.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    beneficiaire_nom = Column(String(100), nullable=True)
    montant = Column(Numeric, nullable=False)
    quote_part = Column(Numeric, nullable=False)
    type_reversement = Column(String(20), nullable=False)
    
    reglement_id = Column(
        Integer,
        ForeignKey("lometa_reglements.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    mode_paiement = Column(String(20), nullable=False)
    reference_paiement = Column(String(50), nullable=True)
    
    date_reversement = Column(DateTime, nullable=False)
    date_comptabilisation = Column(DateTime, nullable=True)
    
    est_paye = Column(Boolean, nullable=False, default=False)
    est_comptabilise = Column(Boolean, nullable=False, default=False)
    observations = Column(Text, nullable=True)
    
    # Audit
    
    recours = relationship(
        "LometaRecours", 
        back_populates="reversements"
    )
    beneficiaire = relationship("LometaBeneficiaire", foreign_keys=[beneficiaire_id])
    reglement = relationship("LometaReglement", foreign_keys=[reglement_id])


class LometaRelanceRecours(Base, AuditableMixin):
    """Historique des relances"""
    __tablename__ = "lometa_relances_recours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recours_id = Column(Integer, ForeignKey("lometa_recours.id"), nullable=False, index=True)
    
    date_relance = Column(DateTime, nullable=False, default=datetime.utcnow)
    type_relance = Column(String(20), nullable=False)
    contenu = Column(Text, nullable=True)
    
    reponse_recue = Column(Boolean, nullable=False, default=False)
    date_reponse = Column(DateTime, nullable=True)
    contenu_reponse = Column(Text, nullable=True)
    
    effectue_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    prochaine_relance = Column(DateTime, nullable=True)
    statut = Column(String(20), nullable=False, default="EN_ATTENTE")
    
    # Audit
    
    recours = relationship(
        "LometaRecours", 
        back_populates="relances"
    )