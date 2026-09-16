"""Modèles du module."""
"""
Modèles LOMETA - Tous les modèles SQLAlchemy
"""
from core.database import Base, AuditableMixin

from addons.Automobiles.models.automobile_models import Vehicle
from addons.Automobiles.models.flottes_models import Fleet
from addons.Automobiles.models.contract_models import Contrat
from addons.Automobiles.models.contact_models import Contact

# Sinistres
from addons.sinistres.models.sinistre import (
    LometaSinistre, LometaDommage, LometaTiers, LometaCommentaireSinistre, LometaHistoriqueSinistre
)

# Expertises
from addons.sinistres.models.expertise import (
    LometaExpertise, LometaDocumentExpertise, LometaEvaluation, LometaRevisionEvaluation,
    LometaProvision, LometaMouvementProvision
)

# Règlements
from addons.sinistres.models.reglement import (
    LometaBeneficiaire, LometaCompteBancaire, LometaReglement, LometaLotPaiement, LometaNoteCredit
)

# Recours
from addons.sinistres.models.recours import (
    LometaRecours, LometaEncaissementRecours, LometaReversementRecours, LometaRelanceRecours
)

# Référentiels
from addons.sinistres.models.referentiel import LometaReferentiel, LometaReferentielHistorique
from addons.sinistres.models.referentiel_data import REFERENTIELS_INITIAUX

# Audit
from addons.sinistres.models.audit import LometaAuditLog



__all__ = [
    'LometaSinistre', 'LometaDommage', 'LometaTiers',
    'LometaCommentaireSinistre', 'LometaHistoriqueSinistre',
    'LometaExpertise', 'LometaDocumentExpertise', 'LometaEvaluation',
    'LometaRevisionEvaluation', 'LometaProvision', 'LometaMouvementProvision',
    'LometaBeneficiaire', 'LometaCompteBancaire', 'LometaReglement',
    'LometaLotPaiement', 'LometaNoteCredit',
    'LometaRecours', 'LometaEncaissementRecours',
    'LometaReversementRecours', 'LometaRelanceRecours',
    'LometaReferentiel', 'LometaReferentielHistorique',
    'LometaAuditLog',
]