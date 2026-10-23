"""
Modèles LOMETA - Tous les modèles SQLAlchemy

⚠️ ORDRE D'IMPORT IMPORTANT :
1. Core (Base, AuditableMixin)
2. Modèles externes référencés (Vehicle, Fleet, Compagnie, User)
3. Référentiels et GED (indépendants)
4. Sinistre (référencé par tout le monde)
5. Expertises, Évaluations, Provisions
6. Règlements
7. Recours
8. Audit
"""
from core.database import Base, AuditableMixin
from addons.Parametres.models.models import User 

# ============================================================
# 1. MODÈLES EXTERNES (référencés par FK)
# ============================================================
from addons.Automobiles.models.automobile_models import Vehicle
from addons.Automobiles.models.flottes_models import Fleet
from addons.Automobiles.models.contract_models import Contrat
from addons.Automobiles.models.contact_models import Contact
from addons.Automobiles.models.compagnies_models import Compagnie
from addons.sinistres.models.parametre import LometaParametre
from addons.sinistres.models.comptabilite import LometaEcritureComptable
from addons.sinistres.models.recours import LometaRepartitionRecours
# from addons.Paramètres.models.models import User  # ← Décommenter si User n'est pas déjà importé ailleurs

# ============================================================
# 2. RÉFÉRENTIELS ET GED (indépendants)
# ============================================================
from addons.sinistres.models.referentiel import (
    LometaReferentiel,
    LometaReferentielHistorique
)
from addons.sinistres.models.workflow import (
    
    LometaWorkflow,
    LometaWorkflowTransition,
    )
from addons.sinistres.models.document import (
    LometaDocument,
)
from addons.sinistres.models.notification import (
    LometaNotification,
)
from addons.sinistres.models.tache import LometaTache
from addons.sinistres.models.referentiel_data import REFERENTIELS_INITIAUX

# ============================================================
# 3. SINISTRE (référencé par expertises, évaluations, etc.)
# ============================================================
from addons.sinistres.models.sinistre import (
    LometaSinistre,
    LometaDommage,
    LometaTiers,
    LometaCommentaireSinistre,
    LometaHistoriqueSinistre,
)

# ============================================================
# 4. EXPERTISES / ÉVALUATIONS / PROVISIONS
# ============================================================
from addons.sinistres.models.expertise import (
    LometaExpert,
    LometaExpertise,
    LometaDocumentExpertise,
    LometaEvaluation,
    LometaRevisionEvaluation,
    LometaProvision,
    LometaMouvementProvision,
    LometaAvocat,
)

# ============================================================
# 5. RÈGLEMENTS (dépend de sinistre + évaluation)
# ============================================================
from addons.sinistres.models.reglement import (
    LometaBeneficiaire,
    LometaCompteBancaire,
    LometaBanque,
    LometaReglement,
    LometaLotPaiement,
    LometaNoteCredit,
)

# ============================================================
# 6. RECOURS (dépend de sinistre + règlement + évaluation)
# ============================================================
from addons.sinistres.models.recours import (
    LometaRecours,
    LometaEncaissementRecours,
    LometaReversementRecours,
    LometaRelanceRecours,
)

# ============================================================
# 7. AUDIT
# ============================================================
from addons.sinistres.models.audit import LometaAuditLog

from addons.sinistres.models.permissions import (
    LometaRole,
    LometaPermission,
    LometaUserRole,
    role_permissions,
)
# ============================================================
# EXPORTS
# ============================================================
__all__ = [
    # --- Externes ---
    'Vehicle', 'Fleet', 'Contrat', 'Contact', 'Compagnie',
    
    # --- Référentiels & GED ---
    'LometaReferentiel', 'LometaReferentielHistorique',
    'LometaDocument', 'LometaTache', 'LometaNotification',
    'LometaWorkflow', 'LometaWorkflowTransition',
    
    # --- Sinistre ---
    'LometaSinistre', 'LometaDommage', 'LometaTiers',
    'LometaCommentaireSinistre', 'LometaHistoriqueSinistre',
    
    # --- Expertises / Évaluations / Provisions ---
    'LometaExpert', 'LometaExpertise', 'LometaDocumentExpertise',
    'LometaEvaluation', 'LometaRevisionEvaluation',
    'LometaProvision', 'LometaMouvementProvision',
    'LometaAvocat',
    
    # --- Règlements ---
    'LometaBeneficiaire', 'LometaCompteBancaire', 'LometaBanque',
    'LometaReglement', 'LometaLotPaiement', 'LometaNoteCredit',
    
    # --- Recours ---
    'LometaRecours', 'LometaEncaissementRecours',
    'LometaReversementRecours', 'LometaRelanceRecours',
    
    # --- Audit ---
    'LometaAuditLog',
    
    # --- Données initiales ---
    'REFERENTIELS_INITIAUX',
    'LometaRole',
    'LometaPermission',
    'LometaUserRole',
    'role_permissions',

    "LometaParametre",
    "LometaEcritureComptable",
    "LometaRepartitionRecours",
]