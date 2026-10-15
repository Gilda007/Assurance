# addons/Automobiles/views/sinistre/sinistre_detail_view.py
"""
Vue des détails d'un sinistre
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QGroupBox, QScrollArea, QMessageBox,
    QWidget, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QApplication
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QColor, QFont, QClipboard

from datetime import datetime

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.models.sinistre_models import StatutSinistre, TypeSinistre


class SinistreDetailView(QDialog):
    """Vue des détails d'un sinistre"""
    
    def __init__(self, controller, sinistre, user=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.sinistre = sinistre
        self.user = user
        
        self.setWindowTitle(f"Détails du sinistre {sinistre.numero_dossier}")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        self.resize(950, 750)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BACKGROUND};
            }}
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(Spacing.LG)
        main_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        
        # --- En-tête ---
        header = self.create_header()
        main_layout.addWidget(header)
        
        # --- Onglets ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                background-color: {Colors.WHITE};
                padding: 8px;
            }}
            QTabBar::tab {{
                padding: 12px 24px;
                border-radius: 8px 8px 0 0;
                font-weight: {Fonts.MEDIUM};
            }}
            QTabBar::tab:selected {{
                background-color: {Colors.PRIMARY};
                color: white;
            }}
        """)
        
        # Onglet Informations
        info_tab = self.create_info_tab()
        self.tabs.addTab(info_tab, "📋 Informations")
        
        # Onglet Tiers et témoins
        tiers_tab = self.create_tiers_tab()
        self.tabs.addTab(tiers_tab, "👤 Tiers et témoins")
        
        # Onglet Finances
        finances_tab = self.create_finances_tab()
        self.tabs.addTab(finances_tab, "💰 Finances")
        
        # Onglet Historique
        history_tab = self.create_history_tab()
        self.tabs.addTab(history_tab, "📜 Historique")
        
        main_layout.addWidget(self.tabs)
        
        # --- Boutons d'action ---
        buttons = self.create_buttons()
        main_layout.addWidget(buttons)
    
    def create_header(self):
        """Crée l'en-tête avec les infos principales"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setSpacing(Spacing.LG)
        
        # Colonne gauche : N° dossier et type
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(Spacing.SM)
        
        # N° dossier
        dossier_label = QLabel(f"📄 {self.sinistre.numero_dossier}")
        dossier_label.setStyleSheet(f"""
            font-size: {Fonts.H2}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
        """)
        left_layout.addWidget(dossier_label)
        
        # Type
        type_label = QLabel(f"Type : {self._get_type_label(self.sinistre.type)}")
        type_label.setStyleSheet(f"""
            font-size: {Fonts.SMALL}px;
            color: {Colors.TEXT_SECONDARY};
        """)
        left_layout.addWidget(type_label)
        
        layout.addWidget(left, 2)
        
        # Colonne centrale : Statut et dates
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setSpacing(Spacing.SM)
        
        # Statut (avec badge)
        statut_widget = QFrame()
        statut_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {self._get_statut_color(self.sinistre.statut)};
                border-radius: 20px;
                padding: 4px 16px;
            }}
        """)
        statut_layout = QHBoxLayout(statut_widget)
        statut_layout.setContentsMargins(8, 4, 8, 4)
        
        statut_label = QLabel(f"📌 {self.sinistre.statut.value.upper()}")
        statut_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        statut_layout.addWidget(statut_label)
        
        center_layout.addWidget(statut_widget)
        
        # Dates
        date_declaration = self.sinistre.date_declaration.strftime("%d/%m/%Y %H:%M") if self.sinistre.date_declaration else "N/A"
        date_survenue = self.sinistre.date_survenue.strftime("%d/%m/%Y %H:%M") if self.sinistre.date_survenue else "N/A"
        
        dates_label = QLabel(f"Survenue : {date_survenue}  |  Déclaration : {date_declaration}")
        dates_label.setStyleSheet(f"""
            font-size: {Fonts.SMALL}px;
            color: {Colors.TEXT_SECONDARY};
        """)
        center_layout.addWidget(dates_label)
        
        # Jours écoulés
        jours_label = QLabel(f"⏱️ {self.sinistre.jours_ecoules} jours depuis la déclaration")
        jours_label.setStyleSheet(f"""
            font-size: {Fonts.SMALL}px;
            color: {Colors.TEXT_SECONDARY};
        """)
        center_layout.addWidget(jours_label)
        
        layout.addWidget(center, 2)
        
        # Colonne droite : Boutons d'action rapide
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setSpacing(Spacing.SM)
        
        btn_edit = QPushButton("✏️ Modifier")
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: {Fonts.MEDIUM};
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_DARK};
            }}
        """)
        btn_edit.clicked.connect(self.edit_sinistre)
        right_layout.addWidget(btn_edit)
        
        btn_refresh = QPushButton("🔄 Rafraîchir")
        btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GRAY_100};
                color: {Colors.TEXT_SECONDARY};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: {Fonts.MEDIUM};
            }}
            QPushButton:hover {{
                background-color: {Colors.GRAY_200};
            }}
        """)
        btn_refresh.clicked.connect(self.refresh_data)
        right_layout.addWidget(btn_refresh)
        
        layout.addWidget(right, 1)
        
        return header
    
    def create_info_tab(self):
        """Crée l'onglet des informations générales"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.MD)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        content_layout = QGridLayout(content)
        content_layout.setSpacing(Spacing.MD)
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 2)
        
        row = 0
        
        # --- Section : Identifiants ---
        title = QLabel("🏷️ Identifiants")
        title.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 4px;
            border-bottom: 2px solid {Colors.PRIMARY};
        """)
        content_layout.addWidget(title, row, 0, 1, 2)
        row += 1
        
        # Contrat
        contrat_num = self.sinistre.contrat.numero_police if self.sinistre.contrat else "N/A"
        content_layout.addWidget(QLabel("Contrat:"), row, 0)
        content_layout.addWidget(QLabel(contrat_num), row, 1)
        row += 1
        
        # Véhicule
        vehicule_immat = self.sinistre.vehicule.immatriculation if self.sinistre.vehicule else "N/A"
        vehicule_info = f"{vehicule_immat} - {self.sinistre.vehicule.marque} {self.sinistre.vehicule.modele}" if self.sinistre.vehicule else "N/A"
        content_layout.addWidget(QLabel("Véhicule:"), row, 0)
        content_layout.addWidget(QLabel(vehicule_info), row, 1)
        row += 1
        
        # Client
        client_nom = f"{self.sinistre.client.nom} {self.sinistre.client.prenom}" if self.sinistre.client else "N/A"
        content_layout.addWidget(QLabel("Client:"), row, 0)
        content_layout.addWidget(QLabel(client_nom), row, 1)
        row += 1
        
        # --- Section : Lieu ---
        title2 = QLabel("📍 Lieu")
        title2.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 4px;
            border-bottom: 2px solid {Colors.PRIMARY};
            margin-top: 16px;
        """)
        content_layout.addWidget(title2, row, 0, 1, 2)
        row += 1
        
        content_layout.addWidget(QLabel("Lieu:"), row, 0)
        content_layout.addWidget(QLabel(self.sinistre.lieu or "Non spécifié"), row, 1)
        row += 1
        
        content_layout.addWidget(QLabel("Ville:"), row, 0)
        content_layout.addWidget(QLabel(self.sinistre.ville or "Non spécifiée"), row, 1)
        row += 1
        
        content_layout.addWidget(QLabel("Pays:"), row, 0)
        content_layout.addWidget(QLabel(self.sinistre.pays or "Cameroun"), row, 1)
        row += 1
        
        # --- Section : Description ---
        title3 = QLabel("📝 Description")
        title3.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 4px;
            border-bottom: 2px solid {Colors.PRIMARY};
            margin-top: 16px;
        """)
        content_layout.addWidget(title3, row, 0, 1, 2)
        row += 1
        
        # Description
        desc_text = self.sinistre.description or "Aucune description"
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            background-color: {Colors.GRAY_50};
            border-radius: 8px;
            padding: 12px;
        """)
        content_layout.addWidget(desc_label, row, 0, 1, 2)
        row += 1
        
        # Circonstances
        if self.sinistre.circonstances:
            circ_label = QLabel("Circonstances:")
            content_layout.addWidget(circ_label, row, 0)
            
            circ_text = QLabel(self.sinistre.circonstances)
            circ_text.setWordWrap(True)
            circ_text.setStyleSheet(f"""
                background-color: {Colors.GRAY_50};
                border-radius: 8px;
                padding: 12px;
            """)
            content_layout.addWidget(circ_text, row, 1)
            row += 1
        
        # --- Section : Affectation ---
        title4 = QLabel("👤 Affectation")
        title4.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 4px;
            border-bottom: 2px solid {Colors.PRIMARY};
            margin-top: 16px;
        """)
        content_layout.addWidget(title4, row, 0, 1, 2)
        row += 1
        
        content_layout.addWidget(QLabel("Assigné à:"), row, 0)
        assignee = self.sinistre.assigned_to or "Non assigné"
        content_layout.addWidget(QLabel(str(assignee)), row, 1)
        row += 1
        
        content_layout.addWidget(QLabel("Conditions météo:"), row, 0)
        content_layout.addWidget(QLabel(self.sinistre.conditions_meteo or "Non spécifiées"), row, 1)
        row += 1
        
        # Notes
        if self.sinistre.notes:
            title5 = QLabel("📌 Notes internes")
            title5.setStyleSheet(f"""
                font-size: {Fonts.H4}px;
                font-weight: {Fonts.BOLD};
                color: {Colors.TEXT_PRIMARY};
                padding-bottom: 4px;
                border-bottom: 2px solid {Colors.PRIMARY};
                margin-top: 16px;
            """)
            content_layout.addWidget(title5, row, 0, 1, 2)
            row += 1
            
            notes_label = QLabel(self.sinistre.notes)
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet(f"""
                background-color: {Colors.GRAY_50};
                border-radius: 8px;
                padding: 12px;
                color: {Colors.TEXT_SECONDARY};
                font-style: italic;
            """)
            content_layout.addWidget(notes_label, row, 0, 1, 2)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def create_tiers_tab(self):
        """Crée l'onglet des tiers et témoins"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.MD)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        content_layout = QGridLayout(content)
        content_layout.setSpacing(Spacing.MD)
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 2)
        
        row = 0
        
        # --- Section : Tiers ---
        title = QLabel("👤 Tiers impliqué")
        title.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 4px;
            border-bottom: 2px solid {Colors.PRIMARY};
        """)
        content_layout.addWidget(title, row, 0, 1, 2)
        row += 1
        
        content_layout.addWidget(QLabel("Nom:"), row, 0)
        content_layout.addWidget(QLabel(self.sinistre.tiers_nom or "Non spécifié"), row, 1)
        row += 1
        
        content_layout.addWidget(QLabel("Prénom:"), row, 0)
        content_layout.addWidget(QLabel(self.sinistre.tiers_prenom or "Non spécifié"), row, 1)
        row += 1
        
        content_layout.addWidget(QLabel("Téléphone:"), row, 0)
        content_layout.addWidget(QLabel(self.sinistre.tiers_telephone or "Non spécifié"), row, 1)
        row += 1
        
        content_layout.addWidget(QLabel("Assurance:"), row, 0)
        content_layout.addWidget(QLabel(self.sinistre.tiers_assurance or "Non spécifiée"), row, 1)
        row += 1
        
        content_layout.addWidget(QLabel("N° Police:"), row, 0)
        content_layout.addWidget(QLabel(self.sinistre.tiers_police or "Non spécifié"), row, 1)
        row += 1
        
        content_layout.addWidget(QLabel("Véhicule:"), row, 0)
        content_layout.addWidget(QLabel(self.sinistre.tiers_vehicule or "Non spécifié"), row, 1)
        row += 1
        
        # --- Section : Témoins ---
        title2 = QLabel("👥 Témoins")
        title2.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 4px;
            border-bottom: 2px solid {Colors.PRIMARY};
            margin-top: 16px;
        """)
        content_layout.addWidget(title2, row, 0, 1, 2)
        row += 1
        
        content_layout.addWidget(QLabel("Nombre:"), row, 0)
        content_layout.addWidget(QLabel(str(self.sinistre.temoins_nombre or 0)), row, 1)
        row += 1
        
        if self.sinistre.temoins_noms:
            content_layout.addWidget(QLabel("Noms:"), row, 0)
            témoins_text = self.sinistre.temoins_noms
            témoins_label = QLabel(témoins_text)
            témoins_label.setWordWrap(True)
            témoins_label.setStyleSheet(f"""
                background-color: {Colors.GRAY_50};
                border-radius: 8px;
                padding: 12px;
            """)
            content_layout.addWidget(témoins_label, row, 1)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def create_finances_tab(self):
        """Crée l'onglet des finances"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.MD)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        content_layout = QGridLayout(content)
        content_layout.setSpacing(Spacing.MD)
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 2)
        
        row = 0
        
        # --- Section : Estimations ---
        title = QLabel("💰 Estimations")
        title.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 4px;
            border-bottom: 2px solid {Colors.PRIMARY};
        """)
        content_layout.addWidget(title, row, 0, 1, 2)
        row += 1
        
        content_layout.addWidget(QLabel("Estimation préliminaire:"), row, 0)
        content_layout.addWidget(QLabel(f"{self.sinistre.estimation_preliminaire:,.0f} FCFA"), row, 1)
        row += 1
        
        content_layout.addWidget(QLabel("Estimation finale:"), row, 0)
        content_layout.addWidget(QLabel(f"{self.sinistre.estimation_finale:,.0f} FCFA"), row, 1)
        row += 1
        
        # --- Section : Indemnisation ---
        title2 = QLabel("💳 Indemnisation")
        title2.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 4px;
            border-bottom: 2px solid {Colors.PRIMARY};
            margin-top: 16px;
        """)
        content_layout.addWidget(title2, row, 0, 1, 2)
        row += 1
        
        content_layout.addWidget(QLabel("Franchise:"), row, 0)
        content_layout.addWidget(QLabel(f"{self.sinistre.franchise:,.0f} FCFA"), row, 1)
        row += 1
        
        content_layout.addWidget(QLabel("Montant indemnisé:"), row, 0)
        content_layout.addWidget(QLabel(f"{self.sinistre.montant_indemnise:,.0f} FCFA"), row, 1)
        row += 1
        
        content_layout.addWidget(QLabel("Montant net:"), row, 0)
        net = (self.sinistre.montant_indemnise or 0) - (self.sinistre.franchise or 0)
        content_layout.addWidget(QLabel(f"{net:,.0f} FCFA"), row, 1)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def create_history_tab(self):
        """Crée l'onglet d'historique"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.MD)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        
        # --- Informations de création ---
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.GRAY_50};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        info_layout = QGridLayout(info_frame)
        info_layout.setSpacing(Spacing.MD)
        
        created_at = self.sinistre.created_at.strftime("%d/%m/%Y %H:%M") if self.sinistre.created_at else "N/A"
        updated_at = self.sinistre.updated_at.strftime("%d/%m/%Y %H:%M") if self.sinistre.updated_at else "N/A"
        
        info_layout.addWidget(QLabel("Créé le:"), 0, 0)
        info_layout.addWidget(QLabel(created_at), 0, 1)
        info_layout.addWidget(QLabel("Dernière mise à jour:"), 1, 0)
        info_layout.addWidget(QLabel(updated_at), 1, 1)
        
        layout.addWidget(info_frame)
        
        # --- Tableau d'historique des statuts ---
        history_label = QLabel("📜 Historique des statuts")
        history_label.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
        """)
        layout.addWidget(history_label)
        
        # Tableau (simulé pour l'instant)
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Date", "Statut", "Commentaire"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
            }}
        """)
        
        # Données simulées (à remplacer par des données réelles)
        history_data = [
            (self.sinistre.created_at, self.sinistre.statut.value, "Création du sinistre"),
        ]
        
        table.setRowCount(len(history_data))
        for i, (date, statut, comment) in enumerate(history_data):
            date_str = date.strftime("%d/%m/%Y %H:%M") if date else "N/A"
            table.setItem(i, 0, QTableWidgetItem(date_str))
            table.setItem(i, 1, QTableWidgetItem(statut))
            table.setItem(i, 2, QTableWidgetItem(comment))
        
        layout.addWidget(table)
        
        return tab
    
    def create_buttons(self):
        """Crée les boutons d'action"""
        buttons = QFrame()
        buttons.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(buttons)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MD)
        
        layout.addStretch()
        
        # Bouton Fermer
        btn_close = QPushButton("Fermer")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GRAY_100};
                color: {Colors.TEXT_SECONDARY};
                border: none;
                border-radius: 10px;
                padding: 10px 32px;
                font-weight: {Fonts.MEDIUM};
            }}
            QPushButton:hover {{
                background-color: {Colors.GRAY_200};
            }}
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        return buttons
    
    # ============================================================================
    # MÉTHODES UTILITAIRES
    # ============================================================================
    
    def _get_type_label(self, type_enum):
        """Retourne le libellé d'un type de sinistre"""
        labels = {
            TypeSinistre.ACCIDENT: "Accident",
            TypeSinistre.VOL: "Vol",
            TypeSinistre.INCENDIE: "Incendie",
            TypeSinistre.DEGAT_NATUREL: "Dégât naturel",
            TypeSinistre.BRIS_GLACE: "Bris de glace",
            TypeSinistre.VANDALISME: "Vandalisme",
            TypeSinistre.COLLISION: "Collision",
            TypeSinistre.AUTRE: "Autre"
        }
        return labels.get(type_enum, str(type_enum))
    
    def _get_statut_color(self, statut):
        """Retourne la couleur associée à un statut"""
        colors = {
            StatutSinistre.DECLARE: "#2563eb",
            StatutSinistre.EN_INSTRUCTION: "#f59e0b",
            StatutSinistre.EN_ATTENTE: "#f59e0b",
            StatutSinistre.EXPERTISE: "#8b5cf6",
            StatutSinistre.VALIDE: "#16a34a",
            StatutSinistre.REJETE: "#dc2626",
            StatutSinistre.INDEMNISE: "#16a34a",
            StatutSinistre.CLOS: "#64748b",
        }
        return colors.get(statut, "#64748b")
    
    # ============================================================================
    # MÉTHODES D'ACTION
    # ============================================================================
    
    def edit_sinistre(self):
        """Ouvre le formulaire d'édition du sinistre"""
        from addons.Automobiles.views.sinistre.sinistre_form_view import SinistreFormView
        
        form = SinistreFormView(
            controller=self.controller,
            user=self.user,
            sinistre=self.sinistre,
            parent=self
        )
        form.sinistre_saved.connect(self.refresh_data)
        form.exec()
    
    def refresh_data(self):
        """Rafraîchit les données du sinistre"""
        try:
            # Recharger le sinistre depuis la base
            refreshed = self.controller.get_by_id(self.sinistre.id)
            if refreshed:
                self.sinistre = refreshed
                # Réinitialiser l'interface
                self.setup_ui()
                QMessageBox.information(self, "✅ Succès", "Données rafraîchies avec succès")
            else:
                QMessageBox.warning(self, "⚠️ Attention", "Le sinistre n'a pas été trouvé dans la base de données")
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur", f"Erreur lors du rafraîchissement: {str(e)}")