"""
Services du module Sinistres LOMETA.

Regroupe tous les services métier accessibles depuis les contrôleurs.
"""

# ============================================================
# SERVICES DE BASE
# ============================================================
from addons.sinistres.services.base_service import BaseService

# ============================================================
# SERVICES MÉTIER
# ============================================================
from addons.sinistres.services.sinistre_service import SinistreService
from addons.sinistres.services.expertise_service import ExpertiseService
from addons.sinistres.services.evaluation_service import EvaluationService
from addons.sinistres.services.reglement_service import ReglementService
from addons.sinistres.services.recours_service import RecoursService
from addons.sinistres.services.referentiel_service import ReferentielService
from addons.sinistres.services.automobile_service import AutomobileService
from addons.sinistres.services.audit_service import AuditService
from addons.sinistres.services.session_service import SessionService
from addons.sinistres.services.workflow_service import WorkflowService

# ============================================================
# SERVICES UTILITAIRES
# ============================================================
from addons.sinistres.services.file_service import FileService, get_file_service
from addons.sinistres.services.impression_service import ImpressionService


__all__ = [
    # Base
    'BaseService',
    
    # Métier
    'SinistreService',
    'ExpertiseService',
    'EvaluationService',
    'ReglementService',
    'RecoursService',
    'ReferentielService',
    'AutomobileService',
    'AuditService',
    'SessionService',
    'WorkflowService',
    
    # Utilitaires
    'FileService',
    'get_file_service',
    'ImpressionService',
]