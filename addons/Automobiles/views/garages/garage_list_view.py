# addons/Automobiles/views/garages/garage_list_view.py
"""
Vue de la liste des garages agréés
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QLineEdit, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.views.widgets.modern_card import ModernCard


class GarageListView(QWidget):
    """Vue de la liste des garages agréés"""
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.garages = []
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.LG)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # En-tête
        header = self.setup_header()
        layout.addWidget(header)
        
        # Filtres
        filters = self.setup_filters()
        layout.addWidget(filters)
        
        # Tableau
        self.table = self.setup_table()
        layout.addWidget(self.table)
    
    def setup_header(self):
        """En-tête de la page"""
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Garages Agréés")
        title.setStyleSheet(f"""
            font-size: {Fonts.H2}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
        """)
        
        btn_new = QPushButton("+ Nouveau Garage")
        btn_new.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: {Fonts.MEDIUM};
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_DARK};
            }}
        """)
        btn_new.clicked.connect(self.open_new_garage)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(btn_new)
        
        return header
    
    def setup_filters(self):
        """Barre de filtres"""
        filters = QFrame()
        filters.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout(filters)
        layout.setSpacing(Spacing.MD)
        
        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un garage...")
        self.search_input.textChanged.connect(self.filter_data)
        layout.addWidget(self.search_input, 2)
        
        # Filtre statut
        self.statut_filter = QComboBox()
        self.statut_filter.addItem("Tous les statuts")
        self.statut_filter.addItems(["actif", "suspendu", "expire", "revogue", "en_attente"])
        self.statut_filter.currentTextChanged.connect(self.filter_data)
        layout.addWidget(self.statut_filter)
        
        # Filtre ville
        self.ville_filter = QComboBox()
        self.ville_filter.addItem("Toutes les villes")
        self.ville_filter.addItems(["Yaoundé", "Douala", "Bafoussam", "Garoua", "Maroua"])
        self.ville_filter.currentTextChanged.connect(self.filter_data)
        layout.addWidget(self.ville_filter)
        
        return filters
    
    def setup_table(self):
        """Tableau des garages"""
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Code", "Nom", "Type", "Ville", "Téléphone", "Statut", "Note", "Actions"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                gridline-color: {Colors.BORDER};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
        """)
        
        return table
    
    def load_data(self):
        """Charge les données"""
        try:
            self.garages = self.controller.garage.get_all() or []
            self.display_data()
        except Exception as e:
            print(f"Erreur chargement garages: {e}")
            self.garages = []
            self.display_data()
    
    def display_data(self):
        """Affiche les données dans le tableau"""
        self.table.setRowCount(len(self.garages))
        
        for i, garage in enumerate(self.garages):
            # Code
            self.table.setItem(i, 0, QTableWidgetItem(garage.code or "N/A"))
            
            # Nom
            self.table.setItem(i, 1, QTableWidgetItem(garage.nom or "N/A"))
            
            # Type
            type_label = garage.type.value if garage.type else "N/A"
            self.table.setItem(i, 2, QTableWidgetItem(type_label))
            
            # Ville
            self.table.setItem(i, 3, QTableWidgetItem(garage.ville or "N/A"))
            
            # Téléphone
            self.table.setItem(i, 4, QTableWidgetItem(garage.telephone or "N/A"))
            
            # Statut
            statut_item = QTableWidgetItem(garage.agrement_statut.value if garage.agrement_statut else "N/A")
            statut_item.setForeground(self.get_statut_color(garage.agrement_statut))
            self.table.setItem(i, 5, statut_item)
            
            # Note
            note = f"{garage.note_moyenne:.1f} ⭐" if garage.note_moyenne > 0 else "N/A"
            self.table.setItem(i, 6, QTableWidgetItem(note))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            btn_view = QPushButton("👁️")
            btn_view.setFixedSize(30, 30)
            btn_view.setStyleSheet("border: none; background: transparent;")
            btn_view.clicked.connect(lambda checked, g=garage: self.view_garage(g))
            
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(30, 30)
            btn_edit.setStyleSheet("border: none; background: transparent;")
            btn_edit.clicked.connect(lambda checked, g=garage: self.edit_garage(g))
            
            actions_layout.addWidget(btn_view)
            actions_layout.addWidget(btn_edit)
            
            self.table.setCellWidget(i, 7, actions_widget)
    
    def get_statut_color(self, statut):
        """Retourne la couleur selon le statut"""
        from addons.Automobiles.models.garage_models import StatutAgrement
        colors = {
            StatutAgrement.ACTIF: QColor("#16a34a"),
            StatutAgrement.SUSPENDU: QColor("#f59e0b"),
            StatutAgrement.EXPIRE: QColor("#dc2626"),
            StatutAgrement.REVOQUE: QColor("#dc2626"),
            StatutAgrement.EN_ATTENTE: QColor("#2563eb"),
        }
        return colors.get(statut, QColor("#64748b"))
    
    def filter_data(self):
        """Filtre les données affichées"""
        search = self.search_input.text().lower()
        statut = self.statut_filter.currentText()
        ville = self.ville_filter.currentText()
        
        filtered = []
        for g in self.garages:
            if search:
                if search not in (g.nom or "").lower() and search not in (g.code or "").lower():
                    continue
            if statut != "Tous les statuts" and (not g.agrement_statut or g.agrement_statut.value != statut):
                continue
            if ville != "Toutes les villes" and (g.ville or "") != ville:
                continue
            filtered.append(g)
        
        self.garages = filtered
        self.display_data()
    
    def open_new_garage(self):
        """Ouvre le formulaire de création"""
        QMessageBox.information(self, "Information", "Formulaire de création de garage en développement")
    
    def view_garage(self, garage):
        """Affiche les détails d'un garage"""
        QMessageBox.information(self, "Détails", f"Garage {garage.nom} - {garage.code}")
    
    def edit_garage(self, garage):
        """Édite un garage"""
        QMessageBox.information(self, "Édition", f"Modification du garage {garage.nom}")