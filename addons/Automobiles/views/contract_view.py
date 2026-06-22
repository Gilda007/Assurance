# addons/Automobiles/views/contract_view.py
"""
Vue de gestion des contrats d'assurance
Design professionnel avec tableau de bord des contrats
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QComboBox,
    QFrame, QTabWidget, QGroupBox, QFormLayout, QDateEdit,
    QDoubleSpinBox, QTextEdit, QMessageBox, QMenu, QDialog,
    QDialogButtonBox, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QDate, QDateTime
from PySide6.QtGui import QColor, QFont

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.views.widgets.modern_card import ModernCard


class ContractDialog(QDialog):
    """Dialogue de création/édition de contrat"""
    
    def __init__(self, controller, contract_id: int = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.contract_id = contract_id
        self.setup_ui()
        
        if contract_id:
            self.load_contract()
            self.setWindowTitle("Modifier le contrat")
        else:
            self.setWindowTitle("Nouveau contrat")
    
    def setup_ui(self):
        self.setMinimumSize(700, 600)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.WHITE};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.LG)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        
        # Scroll area pour le formulaire
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(Spacing.LG)
        
        # Section 1: Informations générales
        general_group = QGroupBox("Informations générales")
        general_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: {Fonts.SEMIBOLD};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }}
        """)
        
        general_layout = QGridLayout(general_group)
        general_layout.setSpacing(Spacing.MD)
        
        # Numéro police
        general_layout.addWidget(QLabel("Numéro police:"), 0, 0)
        self.police_input = QLineEdit()
        self.police_input.setPlaceholderText("Auto-généré si vide")
        general_layout.addWidget(self.police_input, 0, 1)
        
        # Souscripteur
        general_layout.addWidget(QLabel("Souscripteur:"), 1, 0)
        self.owner_combo = QComboBox()
        self.owner_combo.setEditable(True)
        self.load_contacts()
        general_layout.addWidget(self.owner_combo, 1, 1)
        
        # Compagnie
        general_layout.addWidget(QLabel("Compagnie:"), 2, 0)
        self.company_combo = QComboBox()
        self.load_companies()
        general_layout.addWidget(self.company_combo, 2, 1)
        
        # Véhicule
        general_layout.addWidget(QLabel("Véhicule:"), 3, 0)
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.setEditable(True)
        self.load_vehicles()
        general_layout.addWidget(self.vehicle_combo, 3, 1)
        
        # Type contrat
        general_layout.addWidget(QLabel("Type contrat:"), 4, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["VEHICULE", "FLOTTE"])
        general_layout.addWidget(self.type_combo, 4, 1)
        
        # Statut
        general_layout.addWidget(QLabel("Statut:"), 5, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["proformat", "actif", "resilie", "expire", "annule"])
        general_layout.addWidget(self.status_combo, 5, 1)
        
        form_layout.addWidget(general_group)
        
        # Section 2: Dates
        dates_group = QGroupBox("Période d'assurance")
        dates_group.setStyleSheet(general_group.styleSheet())
        
        dates_layout = QGridLayout(dates_group)
        dates_layout.setSpacing(Spacing.MD)
        
        dates_layout.addWidget(QLabel("Date début:"), 0, 0)
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        dates_layout.addWidget(self.start_date, 0, 1)
        
        dates_layout.addWidget(QLabel("Date fin:"), 1, 0)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addDays(365))
        dates_layout.addWidget(self.end_date, 1, 1)
        
        dates_layout.addWidget(QLabel("Date proformat:"), 2, 0)
        self.proformat_date = QDateEdit()
        self.proformat_date.setCalendarPopup(True)
        self.proformat_date.setDate(QDate.currentDate())
        dates_layout.addWidget(self.proformat_date, 2, 1)
        
        form_layout.addWidget(dates_group)
        
        # Section 3: Finances
        finance_group = QGroupBox("Informations financières")
        finance_group.setStyleSheet(general_group.styleSheet())
        
        finance_layout = QGridLayout(finance_group)
        finance_layout.setSpacing(Spacing.MD)
        
        finance_layout.addWidget(QLabel("Prime pure (XAF):"), 0, 0)
        self.prime_pure = QDoubleSpinBox()
        self.prime_pure.setRange(0, 100000000)
        self.prime_pure.setPrefix("XAF ")
        finance_layout.addWidget(self.prime_pure, 0, 1)
        
        finance_layout.addWidget(QLabel("Accessoires (XAF):"), 1, 0)
        self.accessoires = QDoubleSpinBox()
        self.accessoires.setRange(0, 10000000)
        self.accessoires.setPrefix("XAF ")
        finance_layout.addWidget(self.accessoires, 1, 1)
        
        finance_layout.addWidget(QLabel("Taxes (XAF):"), 2, 0)
        self.taxes = QDoubleSpinBox()
        self.taxes.setRange(0, 10000000)
        self.taxes.setPrefix("XAF ")
        finance_layout.addWidget(self.taxes, 2, 1)
        
        finance_layout.addWidget(QLabel("Réduction flotte (%):"), 3, 0)
        self.discount = QDoubleSpinBox()
        self.discount.setRange(0, 50)
        self.discount.setSuffix(" %")
        finance_layout.addWidget(self.discount, 3, 1)
        
        # Total calculé
        self.total_label = QLabel("Total TTC: XAF 0")
        self.total_label.setStyleSheet(f"""
            font-weight: {Fonts.BOLD};
            color: {Colors.PRIMARY};
            font-size: 14px;
        """)
        finance_layout.addWidget(self.total_label, 4, 0, 1, 2)
        
        # Connecter les signaux pour recalcul
        self.prime_pure.valueChanged.connect(self.update_total)
        self.accessoires.valueChanged.connect(self.update_total)
        self.taxes.valueChanged.connect(self.update_total)
        self.discount.valueChanged.connect(self.update_total)
        
        form_layout.addWidget(finance_group)
        
        # Section 4: Notes
        notes_group = QGroupBox("Notes")
        notes_group.setStyleSheet(general_group.styleSheet())
        
        notes_layout = QVBoxLayout(notes_group)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_input)
        
        form_layout.addWidget(notes_group)
        
        form_layout.addStretch()
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_contacts(self):
        """Charge la liste des contacts"""
        try:
            if hasattr(self.controller, 'get_all_contacts'):
                contacts = self.controller.get_all_contacts(limit=100)
                for contact in contacts:
                    name = getattr(contact, 'customer_name', getattr(contact, 'name', f"Contact {contact.id}"))
                    self.owner_combo.addItem(f"{name} (ID: {contact.id})", contact.id)
        except Exception as e:
            print(f"Erreur chargement contacts: {e}")
    
    def load_companies(self):
        """Charge la liste des compagnies"""
        # TODO: Implémenter selon votre modèle Compagnie
        self.company_combo.addItem("Sélectionner une compagnie", None)
        self.company_combo.addItem("AXA Assurance", 1)
        self.company_combo.addItem("Allianz", 2)
        self.company_combo.addItem("SAHAM", 3)
    
    def load_vehicles(self):
        """Charge la liste des véhicules"""
        try:
            if hasattr(self.controller, 'get_all_vehicles'):
                vehicles = self.controller.get_all_vehicles(limit=100)
                for vehicle in vehicles:
                    plate = getattr(vehicle, 'licence_plate', f"Véhicule {vehicle.id}")
                    self.vehicle_combo.addItem(f"{plate}", vehicle.id)
        except Exception as e:
            print(f"Erreur chargement véhicules: {e}")
    
    def update_total(self):
        """Met à jour le total calculé"""
        prime = self.prime_pure.value()
        access = self.accessoires.value()
        taxes = self.taxes.value()
        discount = self.discount.value()
        
        total = prime + access + taxes
        if discount > 0:
            total = total * (1 - discount / 100)
        
        self.total_label.setText(f"Total TTC: XAF {total:,.0f}".replace(",", " "))
    
    def load_contract(self):
        """Charge les données du contrat pour modification"""
        try:
            contract = self.controller.get_contract(self.contract_id)
            if contract:
                self.police_input.setText(getattr(contract, 'numero_police', ''))
                self.start_date.setDate(QDateTime.fromPython(getattr(contract, 'date_debut', datetime.now())).date() if getattr(contract, 'date_debut', None) else QDate.currentDate())
                self.end_date.setDate(QDateTime.fromPython(getattr(contract, 'date_fin', datetime.now())).date() if getattr(contract, 'date_fin', None) else QDate.currentDate().addDays(365))
                self.prime_pure.setValue(getattr(contract, 'prime_pure', 0))
                self.accessoires.setValue(getattr(contract, 'accessoires', 0))
                self.taxes.setValue(getattr(contract, 'taxes_totales', 0))
                self.discount.setValue(getattr(contract, 'fleet_discount', 0))
                self.update_total()
        except Exception as e:
            print(f"Erreur chargement contrat: {e}")
    
    def get_contract_data(self) -> Dict[str, Any]:
        """Récupère les données du formulaire"""
        return {
            'numero_police': self.police_input.text() or None,
            'owner_id': self.owner_combo.currentData(),
            'company_id': self.company_combo.currentData(),
            'vehicle_id': self.vehicle_combo.currentData(),
            'type_contrat': self.type_combo.currentText(),
            'statut': self.status_combo.currentText(),
            'date_debut': self.start_date.date().toPython(),
            'date_fin': self.end_date.date().toPython(),
            'date_proformat': self.proformat_date.date().toPython(),
            'prime_pure': self.prime_pure.value(),
            'accessoires': self.accessoires.value(),
            'taxes_totales': self.taxes.value(),
            'fleet_discount': self.discount.value(),
            'notes': self.notes_input.toPlainText()
        }


class ContractView(QWidget):
    """Vue principale de gestion des contrats"""
    
    contract_selected = Signal(dict)
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.contracts = []
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)
        
        # En-tête avec stats
        self.setup_stats_header()
        layout.addWidget(self.stats_card)
        
        # Barre d'outils
        self.setup_toolbar()
        layout.addWidget(self.toolbar)
        
        # Tableau des contrats
        self.setup_table()
        layout.addWidget(self.table_card)
        
        # Onglets supplémentaires
        self.setup_tabs()
        layout.addWidget(self.tabs_widget)
        
        # Barre de statut
        self.setup_status_bar()
        layout.addWidget(self.status_bar)
    
    def setup_stats_header(self):
        """Configure l'en-tête avec statistiques"""
        self.stats_card = ModernCard(title="Aperçu des contrats", icon="📊")
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(Spacing.XL)
        
        # Statistiques
        self.stats_labels = {}
        stats_items = [
            ("total", "Total contrats", "0"),
            ("active", "Actifs", "0"),
            ("expiring", "Échéance < 30j", "0"),
            ("revenue", "CA mensuel", "0 XAF")
        ]
        
        for key, title, default in stats_items:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setSpacing(Spacing.XS)
            
            value_label = QLabel(default)
            value_label.setStyleSheet(f"""
                font-size: {Fonts.H3}px;
                font-weight: {Fonts.BOLD};
                color: {Colors.PRIMARY};
            """)
            
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                font-size: {Fonts.SMALL}px;
                color: {Colors.TEXT_SECONDARY};
            """)
            
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(title_label)
            
            stats_layout.addWidget(stat_widget)
            self.stats_labels[key] = value_label
        
        stats_layout.addStretch()
        self.stats_card.add_layout(stats_layout)
    
    def setup_toolbar(self):
        """Configure la barre d'outils"""
        self.toolbar = QFrame()
        self.toolbar.setStyleSheet("background: transparent;")
        
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(Spacing.MD)
        
        # Bouton nouveau contrat
        self.new_btn = QPushButton("+ Nouveau contrat")
        self.new_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: {Colors.WHITE};
                border-radius: 10px;
                padding: 10px 20px;
            }}
        """)
        self.new_btn.clicked.connect(self.on_new_contract)
        
        # Filtres
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par police...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.on_search)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "actif", "proformat", "expire", "resilie"])
        self.status_filter.setFixedWidth(120)
        self.status_filter.currentTextChanged.connect(self.on_filter_change)
        
        # Bouton export
        self.export_btn = QPushButton("📎 Exporter")
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SUCCESS};
                color: {Colors.WHITE};
                border-radius: 8px;
                padding: 8px 16px;
            }}
        """)
        self.export_btn.clicked.connect(self.on_export)
        
        toolbar_layout.addWidget(self.new_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addWidget(self.export_btn)
    
    def setup_table(self):
        """Configure le tableau des contrats"""
        self.table_card = ModernCard(title="Liste des contrats", icon="📄")
        
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Police", "Souscripteur", "Véhicule", "Début", "Fin",
            "Prime TTC", "Statut", "Paiement", "Actions"
        ])
        
        # Configuration des colonnes
        header = self.table.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(8, 100)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_contract_double_clicked)
        
        self.table_card.add_widget(self.table)
    
    def setup_tabs(self):
        """Configure les onglets supplémentaires"""
        self.tabs_widget = QTabWidget()
        self.tabs_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
            QTabBar::tab {{
                padding: 10px 20px;
                margin-right: 4px;
            }}
        """)
        
        # Onglet Échéances
        expiring_tab = self.create_expiring_tab()
        self.tabs_widget.addTab(expiring_tab, "📅 Échéances")
        
        # Onglet Statistiques
        stats_tab = self.create_stats_tab()
        self.tabs_widget.addTab(stats_tab, "📊 Statistiques")
    
    def create_expiring_tab(self):
        """Crée l'onglet des échéances"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.expiring_table = QTableWidget()
        self.expiring_table.setColumnCount(5)
        self.expiring_table.setHorizontalHeaderLabels(["Police", "Souscripteur", "Date fin", "Jours restants", "Action"])
        self.expiring_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.expiring_table)
        
        return tab
    
    def create_stats_tab(self):
        """Crée l'onglet des statistiques"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        stats_text = QLabel("Statistiques détaillées des contrats")
        stats_text.setStyleSheet(f"font-size: {Fonts.H5}px; font-weight: {Fonts.MEDIUM};")
        layout.addWidget(stats_text)
        
        # TODO: Ajouter des graphiques
        
        return tab
    
    def setup_status_bar(self):
        """Configure la barre de statut"""
        self.status_bar = QFrame()
        self.status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.GRAY_50};
                border-radius: 10px;
            }}
        """)
        
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
    
    def load_data(self):
        """Charge les données des contrats"""
        if not self.controller:
            return
        
        try:
            if hasattr(self.controller, 'get_all_contracts'):
                self.contracts = self.controller.get_all_contracts(limit=100)
            elif hasattr(self.controller, 'get_contracts'):
                self.contracts = self.controller.get_contracts()
            else:
                self.contracts = []
            
            self.refresh_table()
            self.update_stats()
            self.update_expiring_table()
            
            self.status_label.setText(f"{len(self.contracts)} contrats chargés")
            
        except Exception as e:
            self.status_label.setText(f"Erreur: {str(e)}")
            print(f"Erreur chargement contrats: {e}")
    
    def refresh_table(self):
        """Rafraîchit le tableau"""
        self.table.setRowCount(len(self.contracts))
        
        for row, contract in enumerate(self.contracts):
            # Numéro police
            police = getattr(contract, 'numero_police', '-')
            self.table.setItem(row, 0, QTableWidgetItem(police))
            
            # Souscripteur
            owner = getattr(contract, 'owner', None)
            owner_name = getattr(owner, 'customer_name', getattr(owner, 'name', '-')) if owner else '-'
            self.table.setItem(row, 1, QTableWidgetItem(owner_name))
            
            # Véhicule
            vehicle = getattr(contract, 'vehicle', None)
            vehicle_plate = getattr(vehicle, 'licence_plate', '-') if vehicle else '-'
            self.table.setItem(row, 2, QTableWidgetItem(vehicle_plate))
            
            # Dates
            start = getattr(contract, 'date_debut', None)
            start_str = start.strftime("%d/%m/%Y") if start else '-'
            self.table.setItem(row, 3, QTableWidgetItem(start_str))
            
            end = getattr(contract, 'date_fin', None)
            end_str = end.strftime("%d/%m/%Y") if end else '-'
            self.table.setItem(row, 4, QTableWidgetItem(end_str))
            
            # Prime
            prime = getattr(contract, 'prime_totale_ttc', getattr(contract, 'prime_pure', 0))
            prime_str = f"XAF {prime:,.0f}".replace(",", " ")
            self.table.setItem(row, 5, QTableWidgetItem(prime_str))
            
            # Statut
            status = getattr(contract, 'statut', 'inconnu')
            status_item = QTableWidgetItem(status)
            status_colors = {
                'actif': Colors.SUCCESS,
                'proformat': Colors.WARNING,
                'expire': Colors.DANGER,
                'resilie': Colors.DANGER,
                'annule': Colors.TEXT_MUTED
            }
            status_item.setForeground(QColor(status_colors.get(status, Colors.TEXT_SECONDARY)))
            self.table.setItem(row, 6, status_item)
            
            # Paiement
            payment = getattr(contract, 'statut_paiement', 'NON_PAYE')
            payment_item = QTableWidgetItem("✓ Payé" if payment == "PAYE" else "⏳ En attente")
            payment_color = Colors.SUCCESS if payment == "PAYE" else Colors.WARNING
            payment_item.setForeground(QColor(payment_color))
            self.table.setItem(row, 7, payment_item)
            
            # Actions
            actions_widget = self.create_actions_widget(contract)
            self.table.setCellWidget(row, 8, actions_widget)
    
    def create_actions_widget(self, contract):
        """Crée les boutons d'action"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(Spacing.XS, Spacing.XS, Spacing.XS, Spacing.XS)
        layout.setSpacing(Spacing.XS)
        
        view_btn = QPushButton("👁️")
        view_btn.setFixedSize(28, 28)
        view_btn.setToolTip("Voir détails")
        view_btn.clicked.connect(lambda: self.on_view_contract(contract))
        
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(28, 28)
        edit_btn.setToolTip("Modifier")
        edit_btn.clicked.connect(lambda: self.on_edit_contract(contract))
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setToolTip("Supprimer")
        delete_btn.clicked.connect(lambda: self.on_delete_contract(contract))
        
        layout.addWidget(view_btn)
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        
        return widget
    
    def update_stats(self):
        """Met à jour les statistiques"""
        total = len(self.contracts)
        active = sum(1 for c in self.contracts if getattr(c, 'statut', '') == 'actif')
        
        # Contrats expirant dans 30 jours
        today = datetime.now().date()
        expiring = sum(1 for c in self.contracts 
                      if getattr(c, 'date_fin', None) and 
                      (getattr(c, 'date_fin').date() - today).days <= 30 and
                      (getattr(c, 'date_fin').date() - today).days > 0)
        
        # CA mensuel (simulé)
        monthly_revenue = sum(getattr(c, 'prime_totale_ttc', getattr(c, 'prime_pure', 0)) 
                             for c in self.contracts if getattr(c, 'statut', '') == 'actif') / 12
        
        self.stats_labels["total"].setText(str(total))
        self.stats_labels["active"].setText(str(active))
        self.stats_labels["expiring"].setText(str(expiring))
        self.stats_labels["revenue"].setText(f"XAF {monthly_revenue:,.0f}".replace(",", " "))
    
    def update_expiring_table(self):
        """Met à jour le tableau des échéances"""
        today = datetime.now().date()
        expiring_contracts = []
        
        for contract in self.contracts:
            end_date = getattr(contract, 'date_fin', None)
            if end_date:
                days_left = (end_date.date() - today).days
                if 0 <= days_left <= 30:
                    expiring_contracts.append((contract, days_left))
        
        expiring_contracts.sort(key=lambda x: x[1])
        
        self.expiring_table.setRowCount(len(expiring_contracts))
        
        for row, (contract, days_left) in enumerate(expiring_contracts):
            police = getattr(contract, 'numero_police', '-')
            self.expiring_table.setItem(row, 0, QTableWidgetItem(police))
            
            owner = getattr(contract, 'owner', None)
            owner_name = getattr(owner, 'customer_name', '-') if owner else '-'
            self.expiring_table.setItem(row, 1, QTableWidgetItem(owner_name))
            
            end = getattr(contract, 'date_fin', None)
            end_str = end.strftime("%d/%m/%Y") if end else '-'
            self.expiring_table.setItem(row, 2, QTableWidgetItem(end_str))
            
            days_item = QTableWidgetItem(f"{days_left} jours")
            if days_left <= 7:
                days_item.setForeground(QColor(Colors.DANGER))
            elif days_left <= 15:
                days_item.setForeground(QColor(Colors.WARNING))
            self.expiring_table.setItem(row, 3, days_item)
            
            renew_btn = QPushButton("Renouveler")
            renew_btn.setFixedWidth(100)
            renew_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.PRIMARY};
                    border-radius: 6px;
                    padding: 4px 8px;
                }}
            """)
            renew_btn.clicked.connect(lambda checked, c=contract: self.on_renew_contract(c))
            self.expiring_table.setCellWidget(row, 4, renew_btn)
    
    def on_new_contract(self):
        """Crée un nouveau contrat"""
        dialog = ContractDialog(self.controller, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_contract_data()
            try:
                if hasattr(self.controller, 'create_contract'):
                    self.controller.create_contract(data)
                self.load_data()
                QMessageBox.information(self, "Succès", "Contrat créé avec succès")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {e}")
    
    def on_edit_contract(self, contract):
        """Modifie un contrat"""
        contract_id = getattr(contract, 'id', None)
        if contract_id:
            dialog = ContractDialog(self.controller, contract_id, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                QMessageBox.information(self, "Succès", "Contrat modifié avec succès")
    
    def on_view_contract(self, contract):
        """Affiche les détails d'un contrat"""
        # TODO: Afficher une vue détaillée
        police = getattr(contract, 'numero_police', '-')
        QMessageBox.information(self, "Détails", f"Contrat: {police}")
    
    def on_delete_contract(self, contract):
        """Supprime un contrat"""
        reply = QMessageBox.question(self, "Confirmation", 
                                     "Êtes-vous sûr de vouloir supprimer ce contrat ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            contract_id = getattr(contract, 'id', None)
            if contract_id and hasattr(self.controller, 'delete_contract'):
                self.controller.delete_contract(contract_id)
                self.load_data()
                QMessageBox.information(self, "Succès", "Contrat supprimé")
    
    def on_renew_contract(self, contract):
        """Renouvelle un contrat"""
        reply = QMessageBox.question(self, "Renouvellement", 
                                     "Voulez-vous renouveler ce contrat pour un an ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Implémenter le renouvellement
            QMessageBox.information(self, "Renouvellement", "Contrat renouvelé avec succès")
    
    def on_search(self, text):
        """Recherche de contrats"""
        if not text:
            self.refresh_table()
        else:
            filtered = [c for c in self.contracts 
                       if text.lower() in getattr(c, 'numero_police', '').lower()]
            self.table.setRowCount(len(filtered))
            # TODO: Afficher les résultats filtrés
    
    def on_filter_change(self):
        """Filtre par statut"""
        self.refresh_table()
    
    def on_export(self):
        """Exporte les données"""
        QMessageBox.information(self, "Export", "Fonction d'export à implémenter")
    
    def on_contract_double_clicked(self, index):
        """Double-clic sur un contrat"""
        row = index.row()
        if row < len(self.contracts):
            contract = self.contracts[row]
            self.on_view_contract(contract)
    
    def refresh_data(self):
        """Rafraîchit les données"""
        self.load_data()