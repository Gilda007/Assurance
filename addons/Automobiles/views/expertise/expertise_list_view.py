# addons/Automobiles/views/expertise/expertise_list_view.py
"""
Vue de la liste des expertises automobiles
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


class ExpertiseListView(QWidget):
    """Vue de la liste des expertises"""
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.expertises = []
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
        
        title = QLabel("Expertises Automobiles")
        title.setStyleSheet(f"""
            font-size: {Fonts.H2}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
        """)
        
        btn_new = QPushButton("+ Nouvelle Expertise")
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
        btn_new.clicked.connect(self.open_new_expertise)
        
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
        self.search_input.setPlaceholderText("🔍 Rechercher une expertise...")
        self.search_input.textChanged.connect(self.filter_data)
        layout.addWidget(self.search_input, 2)
        
        # Filtre statut
        self.statut_filter = QComboBox()
        self.statut_filter.addItem("Tous les statuts")
        self.statut_filter.addItems(["planifiee", "en_cours", "terminee", "validee", "rejetee"])
        self.statut_filter.currentTextChanged.connect(self.filter_data)
        layout.addWidget(self.statut_filter)
        
        return filters
    
    def setup_table(self):
        """Tableau des expertises"""
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "ID", "Sinistre", "Type", "Expert", "Date", "Statut", "Actions"
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
            self.expertises = self.controller.expertise.get_all() or []
            self.display_data()
        except Exception as e:
            print(f"Erreur chargement expertises: {e}")
            self.expertises = []
            self.display_data()
    
    def display_data(self):
        """Affiche les données dans le tableau"""
        self.table.setRowCount(len(self.expertises))
        
        for i, expertise in enumerate(self.expertises):
            # ID
            self.table.setItem(i, 0, QTableWidgetItem(str(expertise.id)))
            
            # Sinistre
            sinistre_num = expertise.sinistre.numero_dossier if expertise.sinistre else "N/A"
            self.table.setItem(i, 1, QTableWidgetItem(sinistre_num))
            
            # Type
            type_label = expertise.type.value if expertise.type else "N/A"
            self.table.setItem(i, 2, QTableWidgetItem(type_label))
            
            # Expert
            expert_name = expertise.expert_nom or "Non assigné"
            self.table.setItem(i, 3, QTableWidgetItem(expert_name))
            
            # Date
            date_str = expertise.date_planifiee.strftime("%d/%m/%Y") if expertise.date_planifiee else ""
            self.table.setItem(i, 4, QTableWidgetItem(date_str))
            
            # Statut
            statut_item = QTableWidgetItem(expertise.statut.value if expertise.statut else "N/A")
            statut_item.setForeground(self.get_statut_color(expertise.statut))
            self.table.setItem(i, 5, statut_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            btn_view = QPushButton("👁️")
            btn_view.setFixedSize(30, 30)
            btn_view.setStyleSheet("border: none; background: transparent;")
            btn_view.clicked.connect(lambda checked, e=expertise: self.view_expertise(e))
            
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(30, 30)
            btn_edit.setStyleSheet("border: none; background: transparent;")
            btn_edit.clicked.connect(lambda checked, e=expertise: self.edit_expertise(e))
            
            actions_layout.addWidget(btn_view)
            actions_layout.addWidget(btn_edit)
            
            self.table.setCellWidget(i, 6, actions_widget)
    
    def get_statut_color(self, statut):
        """Retourne la couleur selon le statut"""
        colors = {
            "planifiee": QColor("#2563eb"),
            "en_cours": QColor("#f59e0b"),
            "terminee": QColor("#16a34a"),
            "validee": QColor("#16a34a"),
            "rejetee": QColor("#dc2626"),
        }
        return colors.get(statut.value if statut else "", QColor("#64748b"))
    
    def filter_data(self):
        """Filtre les données affichées"""
        search = self.search_input.text().lower()
        statut = self.statut_filter.currentText()
        
        filtered = []
        for e in self.expertises:
            if search:
                sinistre_num = e.sinistre.numero_dossier if e.sinistre else ""
                if search not in str(e.id).lower() and search not in sinistre_num.lower():
                    continue
            if statut != "Tous les statuts" and (not e.statut or e.statut.value != statut):
                continue
            filtered.append(e)
        
        self.expertises = filtered
        self.display_data()
    
    def open_new_expertise(self):
        """Ouvre le formulaire de création"""
        QMessageBox.information(self, "Information", "Formulaire de création d'expertise en développement")
    
    def view_expertise(self, expertise):
        """Affiche les détails d'une expertise"""
        QMessageBox.information(self, "Détails", f"Expertise #{expertise.id} - {expertise.type.value if expertise.type else 'N/A'}")
    
    def edit_expertise(self, expertise):
        """Édite une expertise"""
        QMessageBox.information(self, "Édition", f"Modification de l'expertise #{expertise.id}")