from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, 
                             QLineEdit, QComboBox, QLabel, QFileDialog, QProgressDialog)
from PySide6.QtCore import Qt
from core. import AlertManager

class TarifMainView(QWidget):
    def __init__(self, controller, current_user):
        super().__init__()
        self.controller = controller
        self.user = current_user
        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- BARRE D'OUTILS (Header) ---
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Gestion des Tarifs Automobiles")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        
        self.btn_import = QPushButton("📥 Importer CSV/Excel")
        self.btn_import.setStyleSheet("""
            QPushButton { background-color: #2563eb; color: white; padding: 8px 15px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_import.clicked.connect(self.on_import_click)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_import)
        layout.addLayout(header_layout)

        # --- BARRE DE FILTRES ---
        filter_layout = QHBoxLayout()
        
        # Filtre par Compagnie
        self.combo_cie = QComboBox()
        self.combo_cie.setFixedWidth(250)
        self.combo_cie.addItem("Toutes les compagnies", None)
        self.combo_cie.currentIndexChanged.connect(self.filter_data)
        
        # Barre de recherche
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Rechercher un tarif, une catégorie...")
        self.search_bar.textChanged.connect(self.filter_data)
        
        filter_layout.addWidget(QLabel("Compagnie :"))
        filter_layout.addWidget(self.combo_cie)
        filter_layout.addWidget(self.search_bar)
        layout.addLayout(filter_layout)

        # --- TABLEAU DES TARIFS ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Code", "Libellé Tarif", "Cat.", "Zone", "Prime 1", "Max Corpo", "Max Matériel", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #e2e8f0; border-radius: 8px; background-color: white; }
            QHeaderView::section { background-color: #f8fafc; padding: 10px; font-weight: bold; border: none; }
        """)
        layout.addWidget(self.table)

    def load_initial_data(self):
        """Charge les compagnies dans le filtre et les premiers tarifs."""
        # 1. Remplir la combo des compagnies
        compagnies = self.controller.compagnies.get_all_active_compagnies()
        for cie in compagnies:
            self.combo_cie.addItem(cie.nom, cie.id)
            
        # 2. Charger les tarifs
        self.refresh_table()

    def refresh_table(self, filtered_data=None):
        """Remplit le tableau avec les données."""
        tarifs = filtered_data if filtered_data is not None else self.controller.tarifs.get_all_tarifs()
        
        self.table.setRowCount(0)
        for t in tarifs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(t.tarif_code)))
            self.table.setItem(row, 1, QTableWidgetItem(str(t.lib_tarif)))
            self.table.setItem(row, 2, QTableWidgetItem(str(t.categorie)))
            self.table.setItem(row, 3, QTableWidgetItem(str(t.zone)))
            self.table.setItem(row, 4, QTableWidgetItem(f"{t.prime1:,.0f} FCFA"))
            self.table.setItem(row, 5, QTableWidgetItem(str(t.max_corpo)))
            self.table.setItem(row, 6, QTableWidgetItem(f"{t.max_materiel:,.0f}"))
            
            # Bouton supprimer (exemple)
            btn_del = QPushButton("🗑️")
            btn_del.setFixedWidth(40)
            btn_del.clicked.connect(lambda chk=False, t_id=t.id: self.on_delete_tarif(t_id))
            self.table.setCellWidget(row, 7, btn_del)

    def filter_data(self):
        """Logique de filtrage combinée."""
        cie_id = self.combo_cie.currentData()
        search_text = self.search_bar.text().lower()
        
        # On récupère soit tout, soit par compagnie
        if cie_id:
            data = self.controller.tarifs.get_tarifs_by_compagnie(cie_id)
        else:
            data = self.controller.tarifs.get_all_tarifs()
            
        # Filtrage texte
        if search_text:
            data = [t for t in data if search_text in t.lib_tarif.lower() or search_text in t.categorie.lower()]
            
        self.refresh_table(data)

    def on_import_click(self):
        """Gère l'importation avec une fenêtre de sélection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importer les Tarifs", "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            # Création d'une barre de progression pour l'utilisateur
            progress = QProgressDialog("Importation des tarifs en cours...", "Annuler", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            u_id = self.user.id if hasattr(self.user, 'id') else 1
            success, message = self.controller.tarifs.import_tarifs_from_file(file_path, u_id)
            
            progress.close()
            
            if success:
                AlertManager.show_success(self, "Importation", message)
                self.refresh_table()
            else:
                AlertManager.show_error(self, "Erreur", message)

    def on_delete_tarif(self, t_id):
        if AlertManager.ask_confirmation(self, "Supprimer", "Voulez-vous supprimer ce tarif ?"):
            self.controller.tarifs.delete_tarif(t_id)
            self.refresh_table()