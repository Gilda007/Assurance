# addons/Automobiles/views/sinistre/sinistre_list_view.py
"""
Vue de la liste des sinistres
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QLineEdit, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.views.widgets.modern_card import ModernCard
from addons.Automobiles.models.sinistre_models import StatutSinistre, TypeSinistre


class SinistreListView(QWidget):
    """Vue de la liste des sinistres"""
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
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
        
        # Statistiques
        stats = self.setup_stats()
        layout.addWidget(stats)
        
        # Tableau
        self.table = self.setup_table()
        layout.addWidget(self.table)
    
    def setup_header(self):
        """En-tête de la page"""
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Gestion des Sinistres")
        title.setStyleSheet(f"""
            font-size: {Fonts.H2}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
        """)
        
        btn_new = QPushButton("+ Nouveau Sinistre")
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
        btn_new.clicked.connect(self.open_new_sinistre)
        
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
        self.search_input.setPlaceholderText("🔍 Rechercher un sinistre...")
        self.search_input.textChanged.connect(self.filter_data)
        layout.addWidget(self.search_input, 2)
        
        # Filtre statut
        self.statut_filter = QComboBox()
        self.statut_filter.addItem("Tous les statuts")
        for statut in StatutSinistre:
            self.statut_filter.addItem(statut.value)
        self.statut_filter.currentTextChanged.connect(self.filter_data)
        layout.addWidget(self.statut_filter)
        
        # Filtre type
        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous les types")
        for type_ in TypeSinistre:
            self.type_filter.addItem(type_.value)
        self.type_filter.currentTextChanged.connect(self.filter_data)
        layout.addWidget(self.type_filter)
        
        return filters
    
    def setup_stats(self):
        """Cartes de statistiques"""
        stats = QFrame()
        layout = QHBoxLayout(stats)
        layout.setSpacing(Spacing.MD)
        
        self.stats_cards = {}
        stat_items = [
            ("total", "Total", "0", "#2563eb"),
            ("en_cours", "En cours", "0", "#f59e0b"),
            ("clos", "Clos", "0", "#16a34a"),
            ("urgent", "Urgents", "0", "#dc2626"),
        ]
        
        for key, title, value, color in stat_items:
            card = ModernCard(title=title)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {Colors.WHITE};
                    border: 1px solid {Colors.BORDER};
                    border-radius: 12px;
                    padding: 16px;
                    min-width: 120px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            
            label_value = QLabel(value)
            label_value.setStyleSheet(f"""
                font-size: {Fonts.H1}px;
                font-weight: {Fonts.BOLD};
                color: {color};
            """)
            label_value.setAlignment(Qt.AlignCenter)
            
            label_title = QLabel(title)
            label_title.setStyleSheet(f"""
                font-size: {Fonts.SMALL}px;
                color: {Colors.TEXT_SECONDARY};
            """)
            label_title.setAlignment(Qt.AlignCenter)
            
            card_layout.addWidget(label_value)
            card_layout.addWidget(label_title)
            
            layout.addWidget(card)
            self.stats_cards[key] = label_value
        
        return stats
    
    def setup_table(self):
        """Tableau des sinistres"""
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "N° Dossier", "Type", "Véhicule", "Date", "Statut", "Montant", "Jours", "Actions"
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
        self.sinistres = self.controller.sinistre.get_all() or []
        self.display_data()
        self.update_stats()
    
    def display_data(self):
        """Affiche les données dans le tableau"""
        self.table.setRowCount(len(self.sinistres))
        
        for i, sinistre in enumerate(self.sinistres):
            # Numéro dossier
            self.table.setItem(i, 0, QTableWidgetItem(sinistre.numero_dossier))
            
            # Type
            type_item = QTableWidgetItem(sinistre.get_type_label())
            self.table.setItem(i, 1, type_item)
            
            # Véhicule
            immat = sinistre.vehicule.immatriculation if sinistre.vehicule else "N/A"
            self.table.setItem(i, 2, QTableWidgetItem(immat))
            
            # Date
            date_str = sinistre.date_survenue.strftime("%d/%m/%Y") if sinistre.date_survenue else ""
            self.table.setItem(i, 3, QTableWidgetItem(date_str))
            
            # Statut avec couleur
            statut_item = QTableWidgetItem(sinistre.statut.value)
            statut_item.setForeground(self.get_statut_color(sinistre.statut))
            self.table.setItem(i, 4, statut_item)
            
            # Montant
            montant = f"{sinistre.estimation_preliminaire:,.0f} FCFA"
            self.table.setItem(i, 5, QTableWidgetItem(montant))
            
            # Jours
            self.table.setItem(i, 6, QTableWidgetItem(str(sinistre.jours_ecoules)))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            btn_view = QPushButton("👁️")
            btn_view.setFixedSize(30, 30)
            btn_view.setStyleSheet("border: none; background: transparent;")
            btn_view.clicked.connect(lambda checked, s=sinistre: self.view_sinistre(s))
            
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(30, 30)
            btn_edit.setStyleSheet("border: none; background: transparent;")
            btn_edit.clicked.connect(lambda checked, s=sinistre: self.edit_sinistre(s))
            
            actions_layout.addWidget(btn_view)
            actions_layout.addWidget(btn_edit)
            
            self.table.setCellWidget(i, 7, actions_widget)
    
    def get_statut_color(self, statut):
        """Retourne la couleur selon le statut"""
        colors = {
            StatutSinistre.DECLARE: QColor("#2563eb"),
            StatutSinistre.EN_INSTRUCTION: QColor("#f59e0b"),
            StatutSinistre.EN_ATTENTE: QColor("#f59e0b"),
            StatutSinistre.EXPERTISE: QColor("#8b5cf6"),
            StatutSinistre.VALIDE: QColor("#16a34a"),
            StatutSinistre.REJETE: QColor("#dc2626"),
            StatutSinistre.INDEMNISE: QColor("#16a34a"),
            StatutSinistre.CLOS: QColor("#64748b"),
        }
        return colors.get(statut, QColor("#64748b"))
    
    def update_stats(self):
        """Met à jour les statistiques"""
        stats = self.controller.sinistre.get_stats() or {}
        
        self.stats_cards["total"].setText(str(stats.get('total', 0)))
        self.stats_cards["en_cours"].setText(str(stats.get('en_cours', 0)))
        self.stats_cards["clos"].setText(str(stats.get('clos', 0)))
        
        # Urgents : sinistres en cours depuis > 15 jours
        urgents = sum(1 for s in self.sinistres if s.est_urgent)
        self.stats_cards["urgent"].setText(str(urgents))
    
    def filter_data(self):
        """Filtre les données affichées"""
        search = self.search_input.text().lower()
        statut = self.statut_filter.currentText()
        type_ = self.type_filter.currentText()
        
        filtered = []
        for s in self.sinistres:
            if search and search not in s.numero_dossier.lower():
                continue
            if statut != "Tous les statuts" and s.statut.value != statut:
                continue
            if type_ != "Tous les types" and s.type.value != type_:
                continue
            filtered.append(s)
        
        self.sinistres = filtered
        self.display_data()
    
    def open_new_sinistre(self):
        """Ouvre le formulaire de création"""
        from addons.Automobiles.views.sinistre.sinistre_form_view import SinistreFormView
    
        form = SinistreFormView(
            controller=self.controller,
            user=self.user,
            parent=self
        )
        form.sinistre_saved.connect(self.on_sinistre_saved)
        
        # ✅ exec() fonctionne maintenant car c'est un QDialog
        if form.exec() == QDialog.Accepted:
            self.load_data()
            self.update_stats()
    
    def view_sinistre(self, sinistre):
        """Affiche les détails d'un sinistre"""
        from addons.Automobiles.views.sinistre.sinistre_detail_view import SinistreDetailView
        detail = SinistreDetailView(self.controller, sinistre, self.user)
        detail.exec()
    
    def on_sinistre_saved(self, sinistre):
        """
        Appelé quand un sinistre est sauvegardé (création ou modification)
        
        Args:
            sinistre: L'objet Sinistre sauvegardé
        """
        try:
            # Rafraîchir les données
            self.load_data()
            self.update_stats()
            
            # Afficher un message de confirmation
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Succès",
                f"Sinistre {sinistre.numero_dossier} enregistré avec succès"
            )
            
            # Optionnel : sélectionner le sinistre dans la liste
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)  # Colonne du numéro de dossier
                if item and item.text() == sinistre.numero_dossier:
                    self.table.selectRow(row)
                    break
                    
        except Exception as e:
            print(f"Erreur dans on_sinistre_saved: {e}")

    def edit_sinistre(self, sinistre):
        """Édite un sinistre"""
        from addons.Automobiles.views.sinistre.sinistre_form_view import SinistreFormView
    
        form = SinistreFormView(
            controller=self.controller,
            user=self.user,
            sinistre=sinistre,
            parent=self
        )
        form.sinistre_saved.connect(self.on_sinistre_saved)
        
        # ✅ exec() fonctionne maintenant
        if form.exec() == QDialog.Accepted:
            self.load_data()
            self.update_stats()