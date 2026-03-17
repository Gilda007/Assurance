from PySide6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from sqlalchemy import table

class AuditLogDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("📜 Journal d'Audit Système")
        self.resize(1000, 600)
        
        layout = QVBoxLayout(self)
        main_layout = QVBoxLayout(self)

        # --- BARRE DE FILTRAGE ---
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par ID, Utilisateur ou Contenu...")
        self.search_input.textChanged.connect(self.apply_filters)
        
        self.action_filter = QComboBox()
        self.action_filter.addItems(["Toutes les actions", "INSERT", "UPDATE", "DELETE"])
        self.action_filter.currentTextChanged.connect(self.apply_filters)

        filter_layout.addWidget(self.search_input, 4)
        filter_layout.addWidget(self.action_filter, 1)
        main_layout.addLayout(filter_layout)
        self.tabs = QTabWidget()
        
        # Configuration des onglets
        self.tab_fleets = self.create_audit_table()
        self.tab_vehicles = self.create_audit_table()
        self.tab_contracts = self.create_audit_table()
        
        self.tabs.addTab(self.tab_fleets, "🏢 Audit Flottes")
        self.tabs.addTab(self.tab_vehicles, "🚗 Audit Véhicules")
        self.tabs.addTab(self.tab_contracts, "📄 Audit Contrats")
        STYLE_MODERN = """
            QDialog { background-color: #f8f9fa; }
            QTabWidget::pane { border: 1px solid #dee2e6; background: white; border-radius: 8px; }
            QTabBar::tab { background: #e9ecef; padding: 10px 20px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px; }
            QTabBar::tab:selected { background: white; border-bottom: 2px solid #0d6efd; font-weight: bold; }
            QTableWidget { border: none; gridline-color: #f1f3f5; }
            QHeaderView::section { background-color: #f8f9fa; padding: 8px; border: none; border-bottom: 2px solid #dee2e6; font-weight: bold; }
            QLineEdit { padding: 8px; border: 1px solid #ced4da; border-radius: 4px; }
        """
        self.setStyleSheet(STYLE_MODERN)
        
        layout.addWidget(self.tabs)
        self.load_all_audits()

    def create_audit_table(self):
        table = QTableWidget()
        # On passe à 7 colonnes pour inclure IP Locale et IP Publique
        table.setColumnCount(7) 
        table.setHorizontalHeaderLabels([
            "HEURE", "UTILISATEUR", "ACTION", "ITEM ID", "IP LOCALE", "IP PUBLIQUE", "MODIFS"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table
    
    def create_action_badge(self, action):
        badge = QLabel(action.upper())
        colors = {
            "INSERT": ("#61eeaf", "#12de7ff1"), # Vert
            "UPDATE": ("#2ac4f7", "#10A0E9"), # Jaune/Orange
            "DELETE": ("#ed3c4a", "#F44453"), # Rouge
        }
        bg, fg = colors.get(action.upper(), ("#e2e3e5", "#41464b"))
        badge.setStyleSheet(f"""
            background-color: {bg}; color: {fg}; 
            border-radius: 10px; padding: 2px 8px; 
            font-weight: bold; font-size: 10px;
        """)
        badge.setFixedSize(80, 22)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return badge

    def load_all_audits(self):
        # On charge les données pour chaque module
        self.fill_table(self.tab_fleets, self.controller.get_audit_logs("FLEETS"))
        self.fill_table(self.tab_vehicles, self.controller.get_audit_logs("VEHICLES"))
        self.fill_table(self.tab_contracts, self.controller.get_audit_logs("CONTRACTS"))

    def fill_table(self, table, logs):
        table.setRowCount(0)
        for log in logs:
            row = table.rowCount()
            table.insertRow(row)
            
            # Colonnes standards
            table.setItem(row, 0, QTableWidgetItem(log.timestamp.strftime("%d/%m %H:%M")))
            table.setItem(row, 1, QTableWidgetItem(f"ID: {log.user_id}"))
            table.setCellWidget(row, 2, self.create_action_badge(log.action))
            table.setItem(row, 3, QTableWidgetItem(str(log.item_id)))
            
            # --- AFFICHAGE DES ADRESSES IP ---
            # On utilise 'getattr' ou une valeur par défaut au cas où le champ est vide
            table.setItem(row, 4, QTableWidgetItem(log.ip_local or "127.0.0.1"))
            table.setItem(row, 5, QTableWidgetItem(log.ip_public or "Inconnue"))
            
            # Détails (JSON)
            table.setItem(row, 6, QTableWidgetItem(str(log.new_values)[:40] + "..."))

    def apply_filters(self):
        """Masque les lignes qui ne correspondent pas aux critères de recherche."""
        search_text = self.search_input.text().lower()
        action_text = self.action_filter.currentText()
        current_table = self.tabs.currentWidget()

        for i in range(current_table.rowCount()):
            match_search = False
            match_action = (action_text == "Toutes les actions")

            for j in range(current_table.columnCount()):
                item = current_table.item(i, j)
                # On vérifie le texte de la cellule ou de l'action badge
                content = item.text().lower() if item else ""
                if search_text in content:
                    match_search = True
                
                # Vérifier l'action badge (index 2)
                if j == 2:
                    badge = current_table.cellWidget(i, j)
                    if badge and (action_text == badge.text()):
                        match_action = True

            current_table.setRowHidden(i, not (match_search and match_action))

    def load_data(self):
        self.fill_table(self.tab_fleets, self.controller.get_audit_logs("FLEETS"))
        self.fill_table(self.tab_vehicles, self.controller.get_audit_logs("VEHICLES"))
        self.fill_table(self.tab_contracts, self.controller.get_audit_logs("CONTRACTS"))