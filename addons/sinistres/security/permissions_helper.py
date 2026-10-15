"""
Helper pour appliquer les permissions dans l'UI
"""
from typing import Optional, List, Tuple, Set
from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtGui import QColor, QIcon, QFont, QAction


class PermissionsUI:
    """
    Helper pour appliquer les permissions dans l'UI.
    
    Usage :
        perm_ui = PermissionsUI(user, permission_service)
        perm_ui.masquer_si_non_autorise(self.btn_creer, 'sinistre', 'CREATE')
    """
    
    def __init__(self, user, permission_service):
        self.user = user
        self.service = permission_service
        self._user_id = getattr(user, 'id', None)
    
    # ============================================================
    # VÉRIFICATIONS SIMPLES
    # ============================================================
    
    def peut(self, resource: str, action: str) -> bool:
        """Vérifie si l'utilisateur a la permission"""
        if not self._user_id:
            return False
        return self.service.has_permission(self._user_id, resource, action)
    
    def peut_une_de(self, permissions: List[Tuple[str, str]]) -> bool:
        """Vérifie si l'utilisateur a AU MOINS UNE permission"""
        if not self._user_id:
            return False
        return self.service.has_any_permission(self._user_id, permissions)
    
    def peut_toutes(self, permissions: List[Tuple[str, str]]) -> bool:
        """Vérifie si l'utilisateur a TOUTES les permissions"""
        if not self._user_id:
            return False
        return self.service.has_all_permissions(self._user_id, permissions)
    
    # ============================================================
    # MASQUER / AFFICHER
    # ============================================================
    
    def masquer_si_non_autorise(
        self, widget: QWidget, resource: str, action: str
    ) -> bool:
        """
        Masque le widget si l'utilisateur n'a PAS la permission.
        Retourne True si visible, False sinon.
        """
        autorise = self.peut(resource, action)
        widget.setVisible(autorise)
        return autorise
    
    def desactiver_si_non_autorise(
        self, widget: QWidget, resource: str, action: str
    ) -> bool:
        """
        Désactive le widget (setEnabled(False)) si pas autorisé.
        Alternative à masquer_si_non_autorise() — le bouton reste visible
        mais grisé, ce qui indique à l'utilisateur qu'il existe.
        """
        autorise = self.peut(resource, action)
        widget.setEnabled(autorise)
        return autorise
    
    def masquer_bouton_si_non_autorise(
        self, btn: QPushButton, resource: str, action: str,
        tooltip_refus: str = None
    ) -> bool:
        """Masque un QPushButton si non autorisé"""
        autorise = self.peut(resource, action)
        btn.setVisible(autorise)
        if not autorise and tooltip_refus:
            btn.setToolTip(tooltip_refus)
        return autorise
    
    def masquer_action_si_non_autorise(
        self, action: QAction, resource: str, action_code: str
    ) -> bool:
        """Masque une QAction si non autorisé"""
        autorise = self.peut(resource, action_code)
        action.setVisible(autorise)
        return autorise
    
    # ============================================================
    # ACCESSIBLE POUR UNE PAGE
    # ============================================================
    
    def peut_acceder_page(self, page_id: str) -> bool:
        """Vérifie si l'utilisateur peut accéder à une page"""
        return page_id in self.service.get_accessible_pages(self._user_id)
    
    # ============================================================
    # BADGES DE PERMISSIONS
    # ============================================================
    
    def get_badge_role(self) -> str:
        """Retourne un badge avec le(s) rôle(s) de l'utilisateur"""
        if not self._user_id:
            return ""
        roles = self.service.get_user_roles(self._user_id)
        if not roles:
            return "Aucun rôle"
        return " • ".join(r.libelle for r in roles)