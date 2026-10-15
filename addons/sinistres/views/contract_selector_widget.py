"""
Widget de sélection de contrat
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
    QFrame#ContractDetails {
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

STYLE_BADGE_ACTIF = """
    color: #166534;
    background-color: #dcfce7;
    font-size: 10px;
    font-weight: bold;
"""

STYLE_BADGE_INACTIF = """
    color: #991b1b;
    background-color: #fee2e2;
    font-size: 10px;
    font-weight: bold;
"""

STYLE_BADGE_FLOTTE = """
    color: #1e40af;
    background-color: #dbeafe;
    font-size: 10px;
    font-weight: bold;
"""


# ============================================================
# WIDGET
# ============================================================

class ContractSelectorWidget(QWidget):
    """Sélecteur horizontal de contrat avec recherche, liste et détails"""
    
    contract_selected = Signal(dict)
    vehicle_selected = Signal(dict)
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._current_client_id = None
        self._contrats = []
        self._contrats_filtres = []
        self._selected_contract = None
        
        # Sous-widget véhicule (affiché si le contrat est une flotte)
        from addons.sinistres.views.vehicle_selector_widget import VehicleSelectorWidget
        self.vehicle_selector = VehicleSelectorWidget(controller)
        self.vehicle_selector.vehicle_selected.connect(self._on_vehicle_changed)
        
        self._setup_ui()
    
    # ============================================================
    # UI
    # ============================================================
    
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)
        
        # ---------- Carte principale ----------
        self.group = QGroupBox("📄 Contrat")
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
        self.input_search.setPlaceholderText("🔎 Rechercher par n° police, type...")
        self.input_search.setStyleSheet(STYLE_SEARCH)
        self.input_search.textChanged.connect(self._filtrer_contrats)
        search_row.addWidget(self.input_search, 1)
        
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setToolTip("Recharger la liste des contrats")
        self.btn_refresh.setFixedSize(38, 38)
        self.btn_refresh.setStyleSheet(STYLE_BTN_REFRESH)
        self.btn_refresh.clicked.connect(self._recharger_contrats)
        search_row.addWidget(self.btn_refresh)
        
        left_col.addLayout(search_row)
        
        # Compteur
        self.lbl_count = QLabel("0 contrat(s)")
        self.lbl_count.setStyleSheet(STYLE_COUNT)
        left_col.addWidget(self.lbl_count)
        
        # Liste
        self.list_contrats = QListWidget()
        self.list_contrats.setStyleSheet(STYLE_LIST)
        self.list_contrats.setMinimumHeight(180)
        self.list_contrats.currentItemChanged.connect(self._on_contract_clicked)
        left_col.addWidget(self.list_contrats, 1)
        
        # État vide
        self.lbl_empty = QLabel("Sélectionnez d'abord un client")
        self.lbl_empty.setStyleSheet(STYLE_EMPTY)
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.lbl_empty.show()
        left_col.addWidget(self.lbl_empty)
        
        body.addLayout(left_col, 2)
        
        # ==============================
        # COLONNE DROITE : Détails
        # ==============================
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        
        self.details_frame = QFrame()
        self.details_frame.setObjectName("ContractDetails")
        self.details_frame.setStyleSheet(STYLE_DETAILS_FRAME)
        self.details_frame.setMinimumWidth(280)
        
        details_layout = QVBoxLayout(self.details_frame)
        details_layout.setContentsMargins(14, 12, 14, 12)
        details_layout.setSpacing(10)
        
        details_title = QLabel("📋 Détails du contrat")
        details_title.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: bold;")
        details_layout.addWidget(details_title)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #e2e8f0; max-height: 1px; border: none;")
        details_layout.addWidget(sep)
        
        self.details_content = QVBoxLayout()
        self.details_content.setSpacing(6)
        details_layout.addLayout(self.details_content)
        details_layout.addStretch()
        
        self.lbl_no_selection = QLabel("👈 Sélectionnez un contrat\ndans la liste")
        self.lbl_no_selection.setStyleSheet(STYLE_EMPTY)
        self.lbl_no_selection.setAlignment(Qt.AlignCenter)
        details_layout.addWidget(self.lbl_no_selection)
        
        right_col.addWidget(self.details_frame, 1)
        body.addLayout(right_col, 1)
        
        group_layout.addLayout(body)
        
        # ---------- Bandeau de confirmation ----------
        self.banner = QFrame()
        self.banner.setStyleSheet(STYLE_BANNER_EMPTY)
        banner_layout = QHBoxLayout(self.banner)
        banner_layout.setContentsMargins(10, 6, 10, 6)
        
        self.lbl_banner = QLabel("⚠️ Aucun contrat sélectionné")
        banner_layout.addWidget(self.lbl_banner)
        
        group_layout.addWidget(self.banner)
        
        root.addWidget(self.group)
        
        # ---------- Sous-widget véhicule (masqué par défaut) ----------
        self.vehicle_selector.hide()
        root.addWidget(self.vehicle_selector)
    
    # ============================================================
    # API PUBLIQUE
    # ============================================================
    
    def set_client(self, client_id: int):
        """Définit le client et charge ses contrats"""
        self._current_client_id = client_id
        self._recharger_contrats()
    
    def clear_selection(self):
        """Réinitialise tout"""
        self._current_client_id = None
        self._contrats = []
        self._contrats_filtres = []
        self._selected_contract = None
        self.list_contrats.clear()
        self.input_search.clear()
        self._clear_details()
        self._update_banner(None)
        self.lbl_count.setText("0 contrat(s)")
        self.lbl_empty.setText("Sélectionnez d'abord un client")
        self.lbl_empty.show()
        self.list_contrats.hide()
        self.vehicle_selector.clear()
        self.vehicle_selector.hide()
    
    def get_selected_contract(self) -> Optional[dict]:
        return self._selected_contract
    
    def get_selected_contract_id(self) -> Optional[int]:
        return self._selected_contract.get('id') if self._selected_contract else None
    
    def get_selected_vehicle(self) -> Optional[dict]:
        return self.vehicle_selector.get_selected_vehicle()
    
    def get_selected_vehicle_id(self) -> Optional[int]:
        return self.vehicle_selector.get_selected_vehicle_id()
    
    def has_contract(self) -> bool:
        return self._selected_contract is not None
    
    def _is_flotte(self, contract: dict) -> bool:
        """Détermine si un contrat est une flotte (préfixe FLT)"""
        if not contract:
            return False
        numero = contract.get('numero_police', '') or ''
        return numero.upper().startswith('FLT')
    
    # ============================================================
    # CHARGEMENT
    # ============================================================
    
    def _recharger_contrats(self):
        """Recharge la liste des contrats pour le client courant"""
        if not self._current_client_id:
            self._contrats = []
            self._contrats_filtres = []
            self.lbl_empty.setText("Sélectionnez d'abord un client")
            self._refresh_list()
            return
        
        try:
            self._contrats = self.controller.get_contrats_by_client(self._current_client_id) or []
            self._contrats_filtres = list(self._contrats)
            self.input_search.clear()
            self._refresh_list()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement contrats: {str(e)}")
            self._contrats = []
            self._contrats_filtres = []
            self._refresh_list()
    
    def _filtrer_contrats(self):
        """Filtre localement selon la recherche"""
        text = self.input_search.text().strip().lower()
        
        if not text:
            self._contrats_filtres = list(self._contrats)
        else:
            self._contrats_filtres = [
                c for c in self._contrats
                if (text in (c.get('numero_police') or '').lower()
                    or text in (c.get('type_contrat') or '').lower()
                    or text in (c.get('statut') or '').lower())
            ]
        
        self._refresh_list()
    
    def _refresh_list(self):
        """Reconstruit la liste affichée"""
        self.list_contrats.blockSignals(True)
        self.list_contrats.clear()
        
        if not self._current_client_id:
            self.list_contrats.hide()
            self.lbl_empty.show()
            self.lbl_empty.setText("Sélectionnez d'abord un client")
        elif not self._contrats_filtres:
            self.list_contrats.hide()
            self.lbl_empty.show()
            if not self._contrats:
                self.lbl_empty.setText("Aucun contrat pour ce client")
            else:
                self.lbl_empty.setText("Aucun contrat ne correspond à la recherche")
        else:
            self.lbl_empty.hide()
            self.list_contrats.show()
            
            for c in self._contrats_filtres:
                item = QListWidgetItem(self._format_contract_line(c))
                item.setData(Qt.UserRole, c)
                self.list_contrats.addItem(item)
            
            # Resélectionner si déjà choisi
            if self._selected_contract:
                for i in range(self.list_contrats.count()):
                    item = self.list_contrats.item(i)
                    data = item.data(Qt.UserRole)
                    if data and data.get('id') == self._selected_contract.get('id'):
                        self.list_contrats.setCurrentItem(item)
                        break
        
        self.lbl_count.setText(f"{len(self._contrats_filtres)} contrat(s)")
        self.list_contrats.blockSignals(False)
    
    def _format_contract_line(self, c: dict) -> str:
        """Formate une ligne de la liste"""
        police = c.get('numero_police', 'N/A')
        statut = str(c.get('statut', '')).upper()
        
        # Icône selon flotte ou non
        if police.upper().startswith('FLT'):
            prefix = "🚛"
        else:
            prefix = "📄"
        
        return f"{prefix} {police}  [{statut}]"
    
    # ============================================================
    # SÉLECTION / DÉTAILS
    # ============================================================
    
    def _on_contract_clicked(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Gère la sélection d'un contrat"""
        if not current:
            self._selected_contract = None
            self._clear_details()
            self._update_banner(None)
            self.vehicle_selector.hide()
            return
        
        c = current.data(Qt.UserRole)
        if not c:
            return
        
        self._selected_contract = c
        self._afficher_details(c)
        self._update_banner(c)
        self.contract_selected.emit(c)
        
        # ✅ Si flotte → afficher le sélecteur de véhicule
        if self._is_flotte(c):
            self.vehicle_selector.set_contract(c.get('id'))
            self.vehicle_selector.show()
        else:
            self.vehicle_selector.hide()
            self.vehicle_selector.clear()
    
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
        """Affiche les détails d'un contrat"""
        self._clear_details()
        self.lbl_no_selection.hide()
        
        # Infos véhicule si dispo
        vehicle_info = ""
        if c.get('vehicle_id'):
            vehicle_info = f"Véhicule ID: {c.get('vehicle_id')}"
        
        champs = [
            ("N° Police", c.get('numero_police')),
            ("Statut", str(c.get('statut', '')).upper() if c.get('statut') else None),
            ("Type contrat", c.get('type_contrat')),
            ("Date début", self._format_date(c.get('date_debut'))),
            ("Date fin", self._format_date(c.get('date_fin'))),
            ("Prime TTC", self._format_montant(c.get('prime_totale_ttc'))),
            ("Montant payé", self._format_montant(c.get('montant_paye'))),
            ("Véhicule ID", c.get('vehicle_id')),
        ]
        
        for key, val in champs:
            if val in (None, '', 'N/A', 'NONE'):
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
        
        # Bandeau spécial si flotte
        if self._is_flotte(c):
            banner = QLabel("🚛 Contrat FLOTTE - Sélection du véhicule requise ci-dessous")
            banner.setStyleSheet("""
                color: #1e40af;
                background-color: #dbeafe;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
                font-weight: bold;
            """)
            banner.setWordWrap(True)
            self.details_content.addWidget(banner)
    
    def _format_date(self, date_val) -> Optional[str]:
        """Formate une date ISO en jj/mm/aaaa"""
        if not date_val:
            return None
        try:
            s = str(date_val)
            if 'T' in s:
                s = s.split('T')[0]
            parts = s.split('-')
            if len(parts) == 3:
                return f"{parts[2]}/{parts[1]}/{parts[0]}"
            return s
        except Exception:
            return str(date_val)
    
    def _format_montant(self, montant) -> Optional[str]:
        """Formate un montant en FCFA"""
        if montant is None:
            return None
        try:
            return f"{float(montant):,.0f} FCFA".replace(",", " ")
        except (ValueError, TypeError):
            return str(montant)
    
    def _update_banner(self, c: Optional[dict]):
        """Met à jour le bandeau de confirmation"""
        if c:
            police = c.get('numero_police', 'N/A')
            statut = str(c.get('statut', '')).upper()
            texte = f"✅ Contrat sélectionné : {police} - {statut}"
            self.lbl_banner.setText(texte)
            self.banner.setStyleSheet(STYLE_BANNER_OK)
        else:
            self.lbl_banner.setText("⚠️ Aucun contrat sélectionné")
            self.banner.setStyleSheet(STYLE_BANNER_EMPTY)
    
    # ============================================================
    # RELAIS SIGNAL VÉHICULE
    # ============================================================
    
    def _on_vehicle_changed(self, vehicule: dict):
        """Relaye le signal vehicle_selected du sous-widget"""
        self.vehicle_selected.emit(vehicule)