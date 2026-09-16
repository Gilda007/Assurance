"""
Widget de sélection de client (recherche + détails)
Disposition horizontale : gauche = recherche + liste, droite = détails
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QListWidget, QListWidgetItem, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from typing import Optional, List, Dict


# ============================================================
# STYLES
# ============================================================

STYLE_GROUP = """
    QGroupBox {
        font-weight: bold;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        margin-top: 8px;
        padding-top: 14px;
        padding-left: 12px;
        padding-right: 12px;
        padding-bottom: 12px;
        background-color: white;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px;
        color: #1e293b;
        font-size: 13px;
    }
"""

STYLE_SEARCH = """
    QLineEdit {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 9px 12px;
        font-size: 13px;
        color: #1e293b;
    }
    QLineEdit:focus {
        border: 2px solid #1a73e8;
        background-color: white;
    }
"""

STYLE_BTN_REFRESH = """
    QPushButton {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-size: 14px;
        color: #64748b;
    }
    QPushButton:hover {
        background-color: #e8f0fe;
        border-color: #1a73e8;
        color: #1a73e8;
    }
    QPushButton:pressed {
        background-color: #d2e3fc;
    }
"""

STYLE_LIST = """
    QListWidget {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 4px;
        outline: none;
    }
    QListWidget::item {
        padding: 9px 12px;
        border-radius: 6px;
        color: #1e293b;
        font-size: 12px;
    }
    QListWidget::item:hover {
        background-color: #f1f5f9;
    }
    QListWidget::item:selected {
        background-color: #e8f0fe;
        color: #1a73e8;
        font-weight: bold;
        border-left: 3px solid #1a73e8;
    }
"""

STYLE_DETAILS_FRAME = """
    QFrame#ClientDetails {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
"""

STYLE_DETAIL_KEY = "color: #64748b; font-size: 11px; font-weight: 600;"
STYLE_DETAIL_VALUE = "color: #1e293b; font-size: 12px; font-weight: 500;"
STYLE_COUNT = "color: #64748b; font-size: 11px;"
STYLE_EMPTY = "color: #94a3b8; font-size: 12px; font-style: italic;"

STYLE_BANNER_OK = """
    QFrame {
        background-color: #dcfce7;
        border: 1px solid #86efac;
        border-radius: 6px;
    }
    QLabel {
        color: #166534;
        font-size: 12px;
        font-weight: bold;
    }
"""

STYLE_BANNER_EMPTY = """
    QFrame {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 6px;
    }
    QLabel {
        color: #991b1b;
        font-size: 12px;
        font-weight: bold;
    }
"""


# ============================================================
# WIDGET
# ============================================================

class ClientSearchWidget(QWidget):
    """Sélecteur horizontal de client avec recherche, liste et détails"""
    
    client_selected = Signal(dict)
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._clients = []
        self._clients_filtres = []
        self._selected_client = None
        
        self._setup_ui()
        self._charger_clients()
    
    # ============================================================
    # UI
    # ============================================================
    
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)
        
        # ---------- Carte principale ----------
        self.group = QGroupBox("👤 Client")
        self.group.setStyleSheet(STYLE_GROUP)
        
        group_layout = QVBoxLayout(self.group)
        group_layout.setSpacing(10)
        
        # ---------- Corps horizontal ----------
        body = QHBoxLayout()
        body.setSpacing(12)
        
        # ==============================
        # COLONNE GAUCHE : Recherche + Liste
        # ==============================
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        
        # Barre de recherche + recharger
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("🔎 Rechercher par nom, code, téléphone, email...")
        self.input_search.setStyleSheet(STYLE_SEARCH)
        self.input_search.textChanged.connect(self._filtrer_clients)
        self.input_search.returnPressed.connect(self._rechercher_backend)
        search_row.addWidget(self.input_search, 1)
        
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setToolTip("Recharger la liste des clients")
        self.btn_refresh.setFixedSize(38, 38)
        self.btn_refresh.setStyleSheet(STYLE_BTN_REFRESH)
        self.btn_refresh.clicked.connect(self._recharger_clients)
        search_row.addWidget(self.btn_refresh)
        
        left_col.addLayout(search_row)
        
        # Compteur
        self.lbl_count = QLabel("0 client(s)")
        self.lbl_count.setStyleSheet(STYLE_COUNT)
        left_col.addWidget(self.lbl_count)
        
        # Liste
        self.list_clients = QListWidget()
        self.list_clients.setStyleSheet(STYLE_LIST)
        self.list_clients.setMinimumHeight(180)
        self.list_clients.currentItemChanged.connect(self._on_client_clicked)
        left_col.addWidget(self.list_clients, 1)
        
        # État vide
        self.lbl_empty = QLabel("Aucun client disponible")
        self.lbl_empty.setStyleSheet(STYLE_EMPTY)
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.lbl_empty.hide()
        left_col.addWidget(self.lbl_empty)
        
        # Ajout de la colonne gauche (2/3)
        body.addLayout(left_col, 2)
        
        # ==============================
        # COLONNE DROITE : Détails
        # ==============================
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        
        self.details_frame = QFrame()
        self.details_frame.setObjectName("ClientDetails")
        self.details_frame.setStyleSheet(STYLE_DETAILS_FRAME)
        self.details_frame.setMinimumWidth(280)
        
        details_layout = QVBoxLayout(self.details_frame)
        details_layout.setContentsMargins(14, 12, 14, 12)
        details_layout.setSpacing(10)
        
        details_title = QLabel("📋 Détails du client")
        details_title.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: bold;")
        details_layout.addWidget(details_title)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #e2e8f0; max-height: 1px; border: none;")
        details_layout.addWidget(sep)
        
        # Conteneur dynamique pour les détails
        self.details_content = QVBoxLayout()
        self.details_content.setSpacing(6)
        details_layout.addLayout(self.details_content)
        details_layout.addStretch()
        
        # Message quand rien n'est sélectionné
        self.lbl_no_selection = QLabel("👈 Sélectionnez un client\ndans la liste")
        self.lbl_no_selection.setStyleSheet(STYLE_EMPTY)
        self.lbl_no_selection.setAlignment(Qt.AlignCenter)
        details_layout.addWidget(self.lbl_no_selection)
        
        right_col.addWidget(self.details_frame, 1)
        
        # Ajout de la colonne droite (1/3)
        body.addLayout(right_col, 1)
        
        group_layout.addLayout(body)
        
        # ---------- Bandeau de confirmation ----------
        self.banner = QFrame()
        self.banner.setStyleSheet(STYLE_BANNER_EMPTY)
        banner_layout = QHBoxLayout(self.banner)
        banner_layout.setContentsMargins(10, 6, 10, 6)
        
        self.lbl_banner = QLabel("⚠️ Aucun client sélectionné")
        banner_layout.addWidget(self.lbl_banner)
        
        group_layout.addWidget(self.banner)
        
        root.addWidget(self.group)
    
    # ============================================================
    # API PUBLIQUE
    # ============================================================
    
    def clear_selection(self):
        """Réinitialise la sélection"""
        self.input_search.clear()
        self._selected_client = None
        self.list_clients.clearSelection()
        self._clear_details()
        self._update_banner(None)
        self._charger_clients()
    
    def get_selected_client(self) -> Optional[dict]:
        return self._selected_client
    
    def get_selected_client_id(self) -> Optional[int]:
        return self._selected_client.get('id') if self._selected_client else None
    
    def has_selection(self) -> bool:
        return self._selected_client is not None
    
    # ============================================================
    # CHARGEMENT
    # ============================================================
    
    def _charger_clients(self):
        """Charge la liste complète des clients"""
        try:
            self._clients = self.controller.rechercher_contacts() or []
            self._clients_filtres = list(self._clients)
            self._refresh_list()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement clients: {str(e)}")
            self._clients = []
            self._clients_filtres = []
            self._refresh_list()
    
    def _recharger_clients(self):
        """Recharge la liste depuis le backend (avec recherche si active)"""
        text = self.input_search.text().strip()
        
        if text:
            self._rechercher_backend()
        else:
            self._charger_clients()
    
    def _rechercher_backend(self):
        """Recherche côté backend (utile pour gros volumes)"""
        text = self.input_search.text().strip()
        
        try:
            if text:
                self._clients = self.controller.rechercher_contacts(text) or []
            else:
                self._clients = self.controller.rechercher_contacts() or []
            
            self._clients_filtres = list(self._clients)
            self._refresh_list()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur recherche: {str(e)}")
    
    def _filtrer_clients(self):
        """Filtre localement selon la recherche"""
        text = self.input_search.text().strip().lower()
        
        if not text:
            self._clients_filtres = list(self._clients)
        else:
            self._clients_filtres = [
                c for c in self._clients
                if (text in (c.get('nom') or '').lower()
                    or text in (c.get('prenom') or '').lower()
                    or text in (c.get('code_client') or '').lower()
                    or text in (c.get('telephone') or '').lower()
                    or text in (c.get('email') or '').lower())
            ]
        
        self._refresh_list()
    
    def _refresh_list(self):
        """Reconstruit la liste affichée"""
        self.list_clients.blockSignals(True)
        self.list_clients.clear()
        
        if not self._clients_filtres:
            self.list_clients.hide()
            self.lbl_empty.show()
            if not self._clients:
                self.lbl_empty.setText("Aucun client disponible")
            else:
                self.lbl_empty.setText("Aucun client ne correspond à la recherche")
        else:
            self.lbl_empty.hide()
            self.list_clients.show()
            
            for c in self._clients_filtres:
                item = QListWidgetItem(self._format_client_line(c))
                item.setData(Qt.UserRole, c)
                self.list_clients.addItem(item)
            
            # Resélectionner si déjà choisi
            if self._selected_client:
                for i in range(self.list_clients.count()):
                    item = self.list_clients.item(i)
                    data = item.data(Qt.UserRole)
                    if data and data.get('id') == self._selected_client.get('id'):
                        self.list_clients.setCurrentItem(item)
                        break
        
        self.lbl_count.setText(f"{len(self._clients_filtres)} client(s)")
        self.list_clients.blockSignals(False)
    
    def _format_client_line(self, c: dict) -> str:
        """Formate une ligne de la liste"""
        code = c.get('code_client', '')
        nom = c.get('nom', '')
        prenom = c.get('prenom', '')
        
        # Initiale du prénom
        initiale = f"{prenom[0]}." if prenom else ""
        nom_complet = f"{nom} {initiale}".strip()
        
        if code:
            return f"👤 {code}  |  {nom_complet}"
        return f"👤 {nom_complet}"
    
    # ============================================================
    # SÉLECTION / DÉTAILS
    # ============================================================
    
    def _on_client_clicked(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Gère la sélection d'un client"""
        if not current:
            self._selected_client = None
            self._clear_details()
            self._update_banner(None)
            return
        
        c = current.data(Qt.UserRole)
        if not c:
            return
        
        self._selected_client = c
        self._afficher_details(c)
        self._update_banner(c)
        self.client_selected.emit(c)
    
    def _clear_details(self):
        """Vide la zone des détails"""
        while self.details_content.count():
            item = self.details_content.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        
        self.lbl_no_selection.show()
    
    def _clear_layout(self, layout):
        """Nettoie un layout imbriqué"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    def _afficher_details(self, c: dict):
        """Affiche les détails en disposition verticale (clé/valeur)"""
        self._clear_details()
        self.lbl_no_selection.hide()
        
        # Construire nom complet
        nom_complet = f"{c.get('nom', '')} {c.get('prenom', '')}".strip()
        
        champs = [
            ("Code client", c.get('code_client')),
            ("Nom complet", nom_complet),
            ("Civilité", c.get('civilite')),
            ("Téléphone", c.get('telephone')),
            ("Portable", c.get('tel_portable')),
            ("Email", c.get('email')),
            ("Adresse", c.get('adresse')),
            ("Ville", c.get('ville')),
            ("Profession", c.get('profession')),
        ]
        
        for key, val in champs:
            if val in (None, '', 'N/A'):
                continue
            
            row = QHBoxLayout()
            row.setSpacing(8)
            
            lbl_key = QLabel(f"{key} :")
            lbl_key.setStyleSheet(STYLE_DETAIL_KEY)
            lbl_key.setFixedWidth(110)
            row.addWidget(lbl_key)
            
            lbl_val = QLabel(str(val))
            lbl_val.setStyleSheet(STYLE_DETAIL_VALUE)
            lbl_val.setWordWrap(True)
            row.addWidget(lbl_val, 1)
            
            container = QWidget()
            container.setLayout(row)
            self.details_content.addWidget(container)
    
    def _update_banner(self, c: Optional[dict]):
        """Met à jour le bandeau de confirmation"""
        if c:
            code = c.get('code_client', '')
            nom_complet = f"{c.get('nom', '')} {c.get('prenom', '')}".strip()
            
            texte = "✅ Client sélectionné :"
            if code:
                texte += f" {code}"
            if nom_complet:
                texte += f" - {nom_complet}"
            
            self.lbl_banner.setText(texte)
            self.banner.setStyleSheet(STYLE_BANNER_OK)
        else:
            self.lbl_banner.setText("⚠️ Aucun client sélectionné")
            self.banner.setStyleSheet(STYLE_BANNER_EMPTY)