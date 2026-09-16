"""
Widget de sélection de véhicule sinistré (flottes)
Disposition horizontale : gauche = recherche + liste, droite = détails
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QListWidget, QListWidgetItem, QGroupBox, QMessageBox,
    QGridLayout, QSizePolicy
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
    QFrame#VehicleDetails {
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

class VehicleSelectorWidget(QWidget):
    """Sélecteur horizontal de véhicule sinistré (flottes)"""
    
    vehicle_selected = Signal(dict)
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._current_contract_id = None
        self._vehicules = []
        self._vehicules_filtres = []
        self._selected_vehicle = None
        
        self._setup_ui()
    
    # ============================================================
    # UI
    # ============================================================
    
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)
        
        # ---------- Carte principale ----------
        self.group = QGroupBox("🚛 Véhicule sinistré")
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
        self.input_search.setPlaceholderText("🔎 Rechercher...")
        self.input_search.setStyleSheet(STYLE_SEARCH)
        self.input_search.textChanged.connect(self._filtrer_vehicules)
        search_row.addWidget(self.input_search, 1)
        
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setToolTip("Recharger la liste des véhicules")
        self.btn_refresh.setFixedSize(38, 38)
        self.btn_refresh.setStyleSheet(STYLE_BTN_REFRESH)
        self.btn_refresh.clicked.connect(self._recharger_vehicules)
        search_row.addWidget(self.btn_refresh)
        
        left_col.addLayout(search_row)
        
        # Compteur
        self.lbl_count = QLabel("0 véhicule(s)")
        self.lbl_count.setStyleSheet(STYLE_COUNT)
        left_col.addWidget(self.lbl_count)
        
        # Liste
        self.list_vehicules = QListWidget()
        self.list_vehicules.setStyleSheet(STYLE_LIST)
        self.list_vehicules.setMinimumHeight(180)
        self.list_vehicules.currentItemChanged.connect(self._on_vehicle_clicked)
        left_col.addWidget(self.list_vehicules, 1)
        
        # État vide
        self.lbl_empty = QLabel("Aucun véhicule disponible")
        self.lbl_empty.setStyleSheet(STYLE_EMPTY)
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.lbl_empty.hide()
        left_col.addWidget(self.lbl_empty)
        
        # Ajout de la colonne gauche (2/3 de la largeur)
        body.addLayout(left_col, 2)
        
        # ==============================
        # COLONNE DROITE : Détails
        # ==============================
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        
        self.details_frame = QFrame()
        self.details_frame.setObjectName("VehicleDetails")
        self.details_frame.setStyleSheet(STYLE_DETAILS_FRAME)
        self.details_frame.setMinimumWidth(280)
        
        details_layout = QVBoxLayout(self.details_frame)
        details_layout.setContentsMargins(14, 12, 14, 12)
        details_layout.setSpacing(10)
        
        details_title = QLabel("📋 Détails du véhicule")
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
        self.lbl_no_selection = QLabel("👈 Sélectionnez un véhicule\ndans la liste")
        self.lbl_no_selection.setStyleSheet(STYLE_EMPTY)
        self.lbl_no_selection.setAlignment(Qt.AlignCenter)
        details_layout.addWidget(self.lbl_no_selection)
        
        right_col.addWidget(self.details_frame, 1)
        
        # Ajout de la colonne droite (1/3 de la largeur)
        body.addLayout(right_col, 1)
        
        group_layout.addLayout(body)
        
        # ---------- Bandeau de confirmation ----------
        self.banner = QFrame()
        self.banner.setStyleSheet(STYLE_BANNER_EMPTY)
        banner_layout = QHBoxLayout(self.banner)
        banner_layout.setContentsMargins(10, 6, 10, 6)
        
        self.lbl_banner = QLabel("⚠️ Aucun véhicule sélectionné")
        banner_layout.addWidget(self.lbl_banner)
        
        group_layout.addWidget(self.banner)
        
        root.addWidget(self.group)
    
    # ============================================================
    # API PUBLIQUE
    # ============================================================
    
    def set_contract(self, contract_id: int):
        """Définit le contrat et charge ses véhicules"""
        self._current_contract_id = contract_id
        self._recharger_vehicules()
    
    def clear(self):
        """Réinitialise le widget"""
        self._current_contract_id = None
        self._vehicules = []
        self._vehicules_filtres = []
        self._selected_vehicle = None
        self.list_vehicules.clear()
        self.input_search.clear()
        self._clear_details()
        self.lbl_count.setText("0 véhicule(s)")
        self.lbl_empty.hide()
        self._update_banner(None)
    
    def get_selected_vehicle(self) -> Optional[dict]:
        return self._selected_vehicle
    
    def get_selected_vehicle_id(self) -> Optional[int]:
        return self._selected_vehicle.get('id') if self._selected_vehicle else None
    
    def has_selection(self) -> bool:
        return self._selected_vehicle is not None
    
    # ============================================================
    # CHARGEMENT
    # ============================================================
    
    def _recharger_vehicules(self):
        """Recharge la liste des véhicules depuis le backend"""
        if not self._current_contract_id:
            self._vehicules = []
            self._vehicules_filtres = []
            self._refresh_list()
            return
        
        try:
            self._vehicules = self.controller.get_vehicules_by_contrat(self._current_contract_id) or []
            self._vehicules_filtres = list(self._vehicules)
            self.input_search.clear()
            self._refresh_list()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement véhicules: {str(e)}")
            self._vehicules = []
            self._vehicules_filtres = []
            self._refresh_list()
    
    def _filtrer_vehicules(self):
        """Filtre la liste selon la recherche"""
        text = self.input_search.text().strip().lower()
        
        if not text:
            self._vehicules_filtres = list(self._vehicules)
        else:
            self._vehicules_filtres = [
                v for v in self._vehicules
                if (text in (v.get('immatriculation') or '').lower()
                    or text in (v.get('marque') or '').lower()
                    or text in (v.get('modele') or '').lower()
                    or text in (v.get('chassis') or '').lower())
            ]
        
        self._refresh_list()
    
    def _refresh_list(self):
        """Reconstruit la liste affichée"""
        self.list_vehicules.blockSignals(True)
        self.list_vehicules.clear()
        
        if not self._vehicules_filtres:
            self.list_vehicules.hide()
            self.lbl_empty.show()
            if not self._vehicules:
                self.lbl_empty.setText("Aucun véhicule dans cette flotte")
            else:
                self.lbl_empty.setText("Aucun véhicule ne correspond à la recherche")
        else:
            self.lbl_empty.hide()
            self.list_vehicules.show()
            
            for v in self._vehicules_filtres:
                item = QListWidgetItem(self._format_vehicle_line(v))
                item.setData(Qt.UserRole, v)
                self.list_vehicules.addItem(item)
            
            # Resélectionner si déjà choisi
            if self._selected_vehicle:
                for i in range(self.list_vehicules.count()):
                    item = self.list_vehicules.item(i)
                    data = item.data(Qt.UserRole)
                    if data and data.get('id') == self._selected_vehicle.get('id'):
                        self.list_vehicules.setCurrentItem(item)
                        break
        
        self.lbl_count.setText(f"{len(self._vehicules_filtres)} véhicule(s)")
        self.list_vehicules.blockSignals(False)
    
    def _format_vehicle_line(self, v: dict) -> str:
        """Formate une ligne de la liste"""
        immat = v.get('immatriculation', 'N/A')
        marque = v.get('marque', '') or ''
        modele = v.get('modele', '') or ''
        annee = v.get('annee', '')
        
        parts = [f"🚗 {immat}"]
        mm = f"{marque} {modele}".strip()
        if mm:
            parts.append(mm)
        if annee:
            parts.append(f"({annee})")
        
        return "  |  ".join(parts)
    
    # ============================================================
    # SÉLECTION / DÉTAILS
    # ============================================================
    
    def _on_vehicle_clicked(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Gère la sélection d'un véhicule"""
        if not current:
            self._selected_vehicle = None
            self._clear_details()
            self._update_banner(None)
            return
        
        v = current.data(Qt.UserRole)
        if not v:
            return
        
        self._selected_vehicle = v
        self._afficher_details(v)
        self._update_banner(v)
        self.vehicle_selected.emit(v)
    
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
    
    def _afficher_details(self, v: dict):
        """Affiche les détails en disposition verticale (clé/valeur)"""
        self._clear_details()
        self.lbl_no_selection.hide()
        
        # Champs à afficher
        champs = [
            ("Immatriculation", v.get('immatriculation')),
            ("Châssis", v.get('chassis')),
            ("Marque", v.get('marque')),
            ("Modèle", v.get('modele')),
            ("Année", v.get('annee')),
            ("Puissance", f"{v.get('puissance_fiscale')} CV" if v.get('puissance_fiscale') else None),
            ("Places", v.get('places')),
            ("Valeur neuve", self._format_montant(v.get('valeur_neuf'))),
            ("Valeur vénale", self._format_montant(v.get('valeur_venale'))),
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
    
    def _format_montant(self, montant) -> Optional[str]:
        """Formate un montant en FCFA"""
        if montant is None:
            return None
        try:
            return f"{float(montant):,.0f} FCFA".replace(",", " ")
        except (ValueError, TypeError):
            return str(montant)
    
    def _update_banner(self, v: Optional[dict]):
        """Met à jour le bandeau de confirmation"""
        if v:
            immat = v.get('immatriculation', 'N/A')
            marque = v.get('marque', '') or ''
            modele = v.get('modele', '') or ''
            mm = f"{marque} {modele}".strip()
            texte = f"✅ Véhicule sélectionné : {immat}"
            if mm:
                texte += f" - {mm}"
            self.lbl_banner.setText(texte)
            self.banner.setStyleSheet(STYLE_BANNER_OK)
        else:
            self.lbl_banner.setText("⚠️ Aucun véhicule sélectionné")
            self.banner.setStyleSheet(STYLE_BANNER_EMPTY)