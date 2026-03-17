# addons/contact_manager/security/access_control.py

class Roles:
    ADMIN = "admin"
    MANAGER = "MANAGER"
    AGENT = "agent"

class Permissions:
    # Liste des actions possibles dans le module
    CONTACT_VIEW = "contact_view"
    CONTACT_ADD = "contact_add"
    CONTACT_EDIT = "contact_edit"
    CONTACT_DELETE = "contact_delete"
    AUDIT_VIEW = "audit_view"
    EXPORT_PDF = "export_pdf"

# Mapping des permissions par rôle
ROLE_PERMISSIONS = {
    Roles.ADMIN: [
        Permissions.CONTACT_VIEW,
        Permissions.CONTACT_ADD, 
        Permissions.CONTACT_EDIT,Permissions.CONTACT_DELETE, 
        Permissions.AUDIT_VIEW, Permissions.EXPORT_PDF
    ],
    Roles.MANAGER: [
        Permissions.CONTACT_VIEW, Permissions.CONTACT_ADD, 
        Permissions.CONTACT_EDIT, Permissions.EXPORT_PDF
    ],
    Roles.AGENT: [
        Permissions.CONTACT_ADD
    ]
}

# Suite de access_control.py

class SecurityManager:
    @staticmethod
    def has_permission(user_role, permission):
        """Vérifie si le rôle de l'utilisateur l'autorise à faire une action."""
        allowed_permissions = ROLE_PERMISSIONS.get(user_role, [])
        return permission in allowed_permissions

    @staticmethod
    def filter_contacts_by_role(query, user_id, user_role):
        """
        Exemple de sécurité au niveau des données avec SQLAlchemy :
        Les agents ne voient que leurs propres contacts, les admins voient tout.
        """
        if user_role == Roles.AGENT:
            return query.filter_by(created_by_id=user_id)
        return query