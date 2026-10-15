"""
Constantes RBAC — Rôles, ressources, actions
"""

# ============================================================
# RÔLES SYSTÈME
# ============================================================
class Roles:
    ADMIN = "admin"
    GESTIONNAIRE = "gestionnaire"
    RESPONSABLE = "responsable"
    COMPTABLE = "comptable"
    EXPERT = "expert"
    LECTEUR = "lecteur"
    
    ALL = [ADMIN, GESTIONNAIRE, RESPONSABLE, COMPTABLE, EXPERT, LECTEUR]


# ============================================================
# ACTIONS CRUD
# ============================================================
class Actions:
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VALIDATE = "VALIDATE"
    CANCEL = "CANCEL"
    RECONCILE = "RECONCILE"
    EXPORT = "EXPORT"
    PAY = "PAY"             # Action spéciale (paiement)
    CLOSE = "CLOSE"         # Action spéciale (clôture)
    
    ALL = [CREATE, READ, UPDATE, DELETE, VALIDATE, CANCEL, RECONCILE, EXPORT, PAY, CLOSE]


# ============================================================
# RESSOURCES MÉTIER
# ============================================================
class Resources:
    SINISTRE = "sinistre"
    DOMMAGE = "dommage"
    TIERS = "tiers"
    EXPERTISE = "expertise"
    EXPERT = "expert"
    AVOCAT = "avocat"
    EVALUATION = "evaluation"
    PROVISION = "provision"
    REGLEMENT = "reglement"
    RECOURS = "recours"
    BENEFICIAIRE = "beneficiaire"
    BANQUE = "banque"
    COMPTE_BANCAIRE = "compte_bancaire"
    NOTE_CREDIT = "note_credit"
    DOCUMENT = "document"
    TACHE = "tache"
    NOTIFICATION = "notification"
    REFERENTIEL = "referentiel"
    UTILISATEUR = "utilisateur"
    ROLE = "role"
    ECRITURE = "ecriture"
    COMPTABILITE = "comptabilite"
    
    ALL = [
        SINISTRE, DOMMAGE, TIERS, EXPERTISE, EXPERT, AVOCAT,
        EVALUATION, PROVISION, REGLEMENT, RECOURS,
        BENEFICIAIRE, BANQUE, COMPTE_BANCAIRE, NOTE_CREDIT,
        DOCUMENT, TACHE, NOTIFICATION, REFERENTIEL,
        UTILISATEUR, ROLE, ECRITURE, COMPTABILITE,
    ]


# ============================================================
# MATRICE DES PERMISSIONS PAR DÉFAUT
# ============================================================
# Format : role_code -> {resource: [actions]}
DEFAULT_PERMISSIONS = {
    Roles.ADMIN: {
        # Admin a TOUT
        Resources.SINISTRE: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE, Actions.VALIDATE, Actions.CLOSE],
        Resources.DOMMAGE: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.TIERS: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.EXPERTISE: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE, Actions.VALIDATE],
        Resources.EXPERT: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.AVOCAT: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.EVALUATION: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE, Actions.VALIDATE],
        Resources.PROVISION: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.REGLEMENT: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE, Actions.VALIDATE, Actions.PAY],
        Resources.RECOURS: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE, Actions.CLOSE],
        Resources.BENEFICIAIRE: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.BANQUE: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.COMPTE_BANCAIRE: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.NOTE_CREDIT: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.DOCUMENT: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.TACHE: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.NOTIFICATION: [Actions.CREATE, Actions.READ, Actions.DELETE],
        Resources.REFERENTIEL: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.UTILISATEUR: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.ROLE: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE],
        Resources.ECRITURE: [
            Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE,
            Actions.VALIDATE, Actions.CANCEL, Actions.RECONCILE, Actions.EXPORT,
        ],
        Resources.COMPTABILITE: [
            Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.DELETE,
            Actions.EXPORT,
        ],
    },
    Roles.GESTIONNAIRE: {
        Resources.SINISTRE: [Actions.CREATE, Actions.READ, Actions.UPDATE],
        Resources.DOMMAGE: [Actions.CREATE, Actions.READ, Actions.UPDATE],
        Resources.TIERS: [Actions.CREATE, Actions.READ, Actions.UPDATE],
        Resources.EXPERTISE: [Actions.CREATE, Actions.READ, Actions.UPDATE],
        Resources.EVALUATION: [Actions.CREATE, Actions.READ, Actions.UPDATE],
        Resources.PROVISION: [Actions.CREATE, Actions.READ, Actions.UPDATE],
        Resources.REGLEMENT: [Actions.CREATE, Actions.READ],
        Resources.RECOURS: [Actions.CREATE, Actions.READ, Actions.UPDATE],
        Resources.DOCUMENT: [Actions.CREATE, Actions.READ, Actions.UPDATE],
        Resources.TACHE: [Actions.CREATE, Actions.READ, Actions.UPDATE],
        Resources.NOTIFICATION: [Actions.READ],
        Resources.REFERENTIEL: [Actions.READ],
        Resources.ECRITURE: [Actions.READ],
        Resources.COMPTABILITE: [Actions.READ],
    },
    Roles.RESPONSABLE: {
        Resources.SINISTRE: [Actions.READ, Actions.VALIDATE, Actions.CLOSE],
        Resources.EXPERTISE: [Actions.READ, Actions.VALIDATE],
        Resources.EVALUATION: [Actions.READ, Actions.VALIDATE],
        Resources.REGLEMENT: [Actions.READ, Actions.VALIDATE],
        Resources.RECOURS: [Actions.READ, Actions.CLOSE],
        Resources.TACHE: [Actions.READ, Actions.UPDATE],
        Resources.REFERENTIEL: [Actions.READ],
        Resources.ECRITURE: [Actions.READ, Actions.EXPORT],
        Resources.COMPTABILITE: [Actions.READ],
    },
    Roles.COMPTABLE: {
        Resources.REGLEMENT: [Actions.CREATE, Actions.READ, Actions.UPDATE, Actions.PAY],
        Resources.RECOURS: [Actions.READ],
        Resources.COMPTE_BANCAIRE: [Actions.READ, Actions.UPDATE],
        Resources.NOTE_CREDIT: [Actions.CREATE, Actions.READ, Actions.UPDATE],
        Resources.BANQUE: [Actions.READ],
        Resources.ECRITURE: [
            Actions.CREATE,
            Actions.READ,
            Actions.UPDATE,
            Actions.VALIDATE,
            Actions.CANCEL,
            Actions.RECONCILE,
            Actions.EXPORT,
        ],
        Resources.COMPTABILITE: [
            Actions.READ,
            Actions.EXPORT,
        ],
        Resources.SINISTRE: [Actions.READ],
        Resources.EVALUATION: [Actions.READ],
        Resources.PROVISION: [Actions.READ],
        Resources.TACHE: [Actions.READ],
    },
    Roles.EXPERT: {
        Resources.EXPERTISE: [Actions.READ, Actions.UPDATE],
        Resources.DOCUMENT: [Actions.CREATE, Actions.READ],
        Resources.TACHE: [Actions.READ],
        Resources.SINISTRE: [Actions.READ],
    },
    Roles.LECTEUR: {
        Resources.SINISTRE: [Actions.READ],
        Resources.EXPERTISE: [Actions.READ],
        Resources.EVALUATION: [Actions.READ],
        Resources.REGLEMENT: [Actions.READ],
        Resources.RECOURS: [Actions.READ],
        Resources.REFERENTIEL: [Actions.READ],
        Resources.ECRITURE: [Actions.READ],
        Resources.COMPTABILITE: [Actions.READ],
    },
}