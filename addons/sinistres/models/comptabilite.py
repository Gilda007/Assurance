"""
Modèles de comptabilité - Écritures comptables
"""
from sqlalchemy import (
    Column, String, DateTime, Numeric, ForeignKey, Text, Boolean, Integer
)
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base, AuditableMixin


class LometaEcritureComptable(Base, AuditableMixin):
    """
    Écriture comptable générée automatiquement.
    
    Règle CDC Tome 5 §11-12 :
    - Paiement Sinistre     : Débit Charge Sinistre  / Crédit Banque
    - Paiement Expert       : Débit Honoraires Exp.  / Crédit Banque
    - Paiement Avocat       : Débit Honoraires Jur.  / Crédit Banque
    - Encaissement Recours  : Débit Banque           / Crédit Compte Recours
    - Reversement Client    : Débit Recours Client   / Crédit Banque
    - Honoraires            : Débit Compte Recours   / Crédit Produits Honoraires
    """
    __tablename__ = "lometa_ecritures_comptables"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_ecriture = Column(String(30), unique=True, nullable=False, index=True)
    
    # Date et journal
    date_ecriture = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    journal = Column(String(20), nullable=False, index=True)
    # BANQUE, SINISTRES, RECOURS, REGULARISATIONS
    
    # Libellé
    libelle = Column(String(255), nullable=False)
    
    # Comptes
    compte_debit = Column(String(20), nullable=False)
    compte_credit = Column(String(20), nullable=False)
    montant = Column(Numeric, nullable=False)
    devise = Column(String(3), nullable=False, default="XAF")
    
    # Référence à l'opération source
    reference_type = Column(String(30), nullable=False, index=True)
    # REGLEMENT, ENCAISSEMENT_RECOURS, REVERSEMENT_CLIENT, HONORAIRES, LETTRAGE
    
    reference_id = Column(Integer, nullable=True, index=True)
    reference_numero = Column(String(50), nullable=True)
    
    # État
    est_valide = Column(Boolean, nullable=False, default=False, index=True)
    est_comptabilise = Column(Boolean, nullable=False, default=False, index=True)
    date_comptabilisation = Column(DateTime, nullable=True)
    comptabilise_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    # Rattachements (optionnels mais utiles pour le reporting)
    sinistre_id = Column(
        Integer,
        ForeignKey("lometa_sinistres.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    recours_id = Column(
        Integer,
        ForeignKey("lometa_recours.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    reglement_id = Column(
        Integer,
        ForeignKey("lometa_reglements.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    provision_id = Column(
        Integer,
        ForeignKey("lometa_provisions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # ✅ NOUVEAU : note de crédit
    note_credit_id = Column(
        Integer,
        ForeignKey("lometa_notes_credit.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    ecriture_contrepartie_id = Column(
        Integer,
        ForeignKey("lometa_ecritures_comptables.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Annulation (soft delete avec motif)
    est_annulee = Column(Boolean, nullable=False, default=False, index=True)
    date_annulation = Column(DateTime, nullable=True)
    motif_annulation = Column(Text, nullable=True)
    annulee_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    observations = Column(Text, nullable=True)
    
    # Relations
    sinistre = relationship("LometaSinistre", foreign_keys=[sinistre_id])
    recours = relationship("LometaRecours", foreign_keys=[recours_id])
    reglement = relationship("LometaReglement", foreign_keys=[reglement_id])
    provision = relationship("LometaProvision", foreign_keys=[provision_id])
    note_credit = relationship("LometaNoteCredit", foreign_keys=[note_credit_id])
    ecriture_contrepartie = relationship("LometaEcritureComptable", foreign_keys=[ecriture_contrepartie_id])

    def __repr__(self):
        return (
            f"<LometaEcritureComptable {self.numero_ecriture} "
            f"{self.journal} D:{self.compte_debit} C:{self.compte_credit} "
            f"{self.montant}>"
        )
