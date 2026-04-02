from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QScrollArea, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
                             QTabWidget, QMessageBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor, QPixmap
import qrcode
from io import BytesIO

MODERN_STYLE = """
    /* Global */
    QWidget {
        background-color: #f8fafc;
        font-family: 'Segoe UI', sans-serif;
        color: #1e293b;
    }
    
    /* Scroll Area */
    QScrollArea {
        border: none;
        background: transparent;
    }
    
    QScrollBar:vertical {
        background: #e2e8f0;
        width: 6px;
        border-radius: 3px;
    }
    
    QScrollBar::handle:vertical {
        background: #94a3b8;
        border-radius: 3px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #64748b;
    }
    
    /* Header Section */
    .HeaderCard {
        background: white;
        border-radius: 24px;
        padding: 24px;
        border: none;
    }
    
    /* Info Cards */
    .InfoCard {
        background: white;
        border-radius: 20px;
        padding: 24px;
        border: none;
    }
    
    /* Section Titles */
    .SectionTitle {
        font-size: 18px;
        font-weight: 700;
        color: #0f172a;
        padding-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* Labels */
    .LabelPrimary {
        color: #64748b;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .LabelSecondary {
        color: #1e293b;
        font-size: 15px;
        font-weight: 600;
        margin-top: 6px;
    }
    
    .ValueLarge {
        font-size: 32px;
        font-weight: 800;
        color: #0f172a;
    }
    
    .ValueMedium {
        font-size: 18px;
        font-weight: 600;
        color: #1e293b;
    }
    
    /* Table */
    QTableWidget {
        background: white;
        border: none;
        border-radius: 16px;
        gridline-color: #f1f5f9;
    }
    
    QTableWidget::item {
        padding: 14px 12px;
        border: none;
    }
    
    QHeaderView::section {
        background-color: #f8fafc;
        border: none;
        border-bottom: 2px solid #e2e8f0;
        padding: 14px 12px;
        font-weight: 600;
        color: #475569;
        font-size: 13px;
    }
    
    /* Recap Card */
    #RecapCard {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #667eea, stop:1 #764ba2);
        border-radius: 20px;
        padding: 28px 32px;
    }
    
    /* Print Buttons */
    .PrintBtn {
        background: white;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px 20px;
        font-weight: 600;
        font-size: 14px;
        text-align: left;
    }
    
    .PrintBtn:hover {
        background: #f8fafc;
        border-color: #cbd5e1;
    }
    
    .PrintBtn:pressed {
        background: #f1f5f9;
    }
    
    /* Action Buttons */
    .ActionBtn {
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        cursor: pointer;
    }
    
    /* Badge */
    .Badge {
        background: #eef2ff;
        color: #4f46e5;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Stats Card */
    .StatsCard {
        background: #f8fafc;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #e2e8f0;
    }
    
    /* Event timeline */
    .EventWidget {
        border-left: 3px solid #3b82f6;
        padding: 10px;
        margin: 5px 0;
    }
    
    /* Contact widget */
    .ContactWidget {
        background: #f8fafc;
        border-radius: 12px;
        padding: 12px;
    }
    
    /* Notification widget */
    .NotificationWidget {
        border-radius: 8px;
        padding: 8px;
        margin: 4px 0;
    }
"""

class VehicleDetailView(QWidget):
    def __init__(self, vehicle_data, controller=None):
        super().__init__()
        self.data = vehicle_data
        self.controller = controller
        self.setStyleSheet(MODERN_STYLE)
        self.setMinimumSize(1100, 800)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 32)
        main_layout.setSpacing(24)

        # --- HEADER SECTION ---
        main_layout.addWidget(self.create_header())

        # --- CONTENU SCROLLABLE ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(28)

        # 1. Informations Véhicule & Propriétaire
        container_layout.addWidget(self.create_info_card())
        
        # 2. Statistiques
        container_layout.addWidget(self.create_stats_section())
        
        # 3. Tableau des Garanties
        container_layout.addWidget(self.create_garanties_table())
        
        # 4. Récapitulatif Final
        container_layout.addWidget(self.create_recap_card())
        
        # 5. Calendrier des échéances
        container_layout.addWidget(self.create_calendar_section())
        
        # 6. Historique
        container_layout.addWidget(self.create_history_section())
        
        # 7. Documents annexes
        container_layout.addWidget(self.create_documents_section())
        
        # 8. Contacts utiles
        container_layout.addWidget(self.create_contacts_section())
        
        # 9. Notifications
        container_layout.addWidget(self.create_notifications_section())
        
        # 10. QR Code
        container_layout.addWidget(self.create_qrcode_section())
        
        # 11. Actions d'impression
        container_layout.addLayout(self.create_print_section())
        
        # Add spacer at bottom
        container_layout.addSpacing(20)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def create_header(self):
        """Crée l'en-tête avec les informations principales"""
        header_card = QFrame()
        header_card.setProperty("class", "HeaderCard")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(24, 20, 24, 20)
        
        # Left side - Vehicle info
        left_info = QVBoxLayout()
        left_info.setSpacing(8)
        
        immat_lbl = QLabel(self.data.get('immatriculation', 'N/A'))
        immat_lbl.setStyleSheet("font-size: 32px; font-weight: 800; color: #0f172a;")
        
        model_text = f"{self.data.get('marque', '')} {self.data.get('modele', '')}"
        model_lbl = QLabel(model_text)
        model_lbl.setStyleSheet("font-size: 16px; color: #64748b;")
        
        # Badge for status
        status = self.data.get('statut', 'En circulation')
        status_badge = QLabel(status)
        status_badge.setProperty("class", "Badge")
        
        left_info.addWidget(immat_lbl)
        left_info.addWidget(model_lbl)
        left_info.addWidget(status_badge)
        
        # Middle - Period info
        middle_info = QVBoxLayout()
        middle_info.setAlignment(Qt.AlignCenter)
        middle_info.setSpacing(8)
        
        date_debut = self.format_date(self.data.get('date_debut', ''))
        date_fin = self.format_date(self.data.get('date_fin', ''))
        
        period_lbl = QLabel("PÉRIODE D'ASSURANCE")
        period_lbl.setProperty("class", "LabelPrimary")
        
        dates_lbl = QLabel(f"{date_debut} → {date_fin}")
        dates_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #1e293b;")
        
        validity = self.calculate_validity()
        validity_lbl = QLabel(validity)
        validity_lbl.setStyleSheet("font-size: 12px; color: #10b981;")
        
        middle_info.addWidget(period_lbl)
        middle_info.addWidget(dates_lbl)
        middle_info.addWidget(validity_lbl)
        
        # Right side - Company info and actions
        right_info = QVBoxLayout()
        right_info.setAlignment(Qt.AlignRight)
        right_info.setSpacing(8)
        
        company_lbl = QLabel("COMPAGNIE D'ASSURANCE")
        company_lbl.setProperty("class", "LabelPrimary")
        
        company_name = QLabel(self.data.get('compagny', 'N/A'))
        company_name.setProperty("class", "ValueMedium")
        
        # Action buttons
        action_buttons = QHBoxLayout()
        action_buttons.setSpacing(8)
        
        actions = [
            ("✏️ Modifier", "edit", "#3b82f6"),
            ("🔄 Renouveler", "renew", "#10b981"),
            ("📧 Email", "email", "#8b5cf6"),
            ("📥 PDF", "export", "#f59e0b")
        ]
        
        self.action_buttons = {}
        for label, action, color in actions:
            btn = QPushButton(label)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-weight: 600;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {color}dd;
                }}
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("action", action)
            self.action_buttons[action] = btn
            action_buttons.addWidget(btn)
        
        right_info.addWidget(company_lbl)
        right_info.addWidget(company_name)
        right_info.addSpacing(8)
        right_info.addLayout(action_buttons)
        
        header_layout.addLayout(left_info)
        header_layout.addLayout(middle_info)
        header_layout.addStretch()
        header_layout.addLayout(right_info)
        
        return header_card

    def create_info_card(self):
        """Crée la carte d'informations détaillées"""
        info_card = QFrame()
        info_card.setProperty("class", "InfoCard")
        info_layout = QGridLayout(info_card)
        info_layout.setContentsMargins(24, 20, 24, 20)
        info_layout.setVerticalSpacing(24)
        info_layout.setHorizontalSpacing(48)
        
        # Section 1: Caractéristiques Techniques
        tech_title = QLabel("Caractéristiques techniques")
        tech_title.setStyleSheet("font-weight: 700; font-size: 14px; color: #0f172a;")
        info_layout.addWidget(tech_title, 0, 0, 1, 2)
        print(self.data)
        
        tech_info = [
            ("Châssis (VIN)", self.data.get('chassis', ''), 1, 0),
            ("Puissance fiscale", f"{self.data.get('usage', '')}", 1, 1),
            ("Énergie", self.data.get('energy', self.data.get('energie', '')), 2, 0),
            ("Places", (self.data.get('places', '')), 2, 1),
            ("Année", (self.data.get('annee', '')), 3, 0),
            ("Catégorie", self.data.get('categorie', ''), 3, 1),
            ("Zone", self.data.get('zone', ''), 4, 0),
            ("Code tarif", self.data.get('code_tarif', ''), 4, 1),
        ]
        
        for label, value, row, col in tech_info:
            vbox = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setProperty("class", "LabelPrimary")
            val = QLabel(str(value))
            val.setProperty("class", "LabelSecondary")
            vbox.addWidget(lbl)
            vbox.addWidget(val)
            info_layout.addLayout(vbox, row, col)
        
        # Section 2: Propriétaire
        owner_title = QLabel("Propriétaire du véhicule")
        owner_title.setStyleSheet("font-weight: 700; font-size: 14px; color: #0f172a; margin-top: 8px;")
        info_layout.addWidget(owner_title, 5, 0, 1, 2)
        # print(self.data)
        
        owner_info = [
            ("Nom complet", self.data.get('owner', ''), 6, 0),
            ("Téléphone", self.data.get('phone', ''), 6, 1),
            ("Email", self.data.get('email', ''), 7, 0),
            ("Adresse", self.data.get('city', ''), 7, 1),
        ]
        
        for label, value, row, col in owner_info:
            vbox = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setProperty("class", "LabelPrimary")
            val = QLabel(str(value))
            val.setProperty("class", "LabelSecondary")
            val.setWordWrap(True)
            vbox.addWidget(lbl)
            vbox.addWidget(val)
            info_layout.addLayout(vbox, row, col)
        
        return info_card

    def create_garanties_table(self):
        """Crée le tableau des garanties"""
        title_tab = QLabel("DÉTAIL DES PRIMES ET GARANTIES")
        title_tab.setProperty("class", "SectionTitle")
        
        # Container pour le tableau
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(16)
        container_layout.addWidget(title_tab)

        self.table = QTableWidget(9, 3)
        self.table.setHorizontalHeaderLabels(["Garantie", "Montant Brut (FCFA)", "Montant Net (FCFA)"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border-radius: 16px;
            }
            QTableWidget::item:selected {
                background-color: #eef2ff;
            }
            QTableWidget::item:alternate {
                background-color: #fafbff;
            }
        """)
        
        # Définition des garanties avec leurs clés
        garanties = [
            ("Responsabilité Civile", 'amt_rc', 'amt_red_rc'),
            ("Défense et Recours", 'amt_dr', 'amt_red_dr'),
            ("Vol du véhicule", 'amt_vol', 'amt_red_vol'),
            ("Vol à Main Armée", 'amt_vb', 'amt_red_vb'),
            ("Incendie", 'amt_in', 'amt_red_in'),
            ("Bris de Glaces", 'amt_bris', 'amt_red_bris'),
            ("Assistance Panne", 'amt_ar', 'amt_red_ar'),
            ("Dommages Tous Accidents", 'amt_dta', 'amt_red_dta'),
            ("Individuelle Chauffeur", 'amt_ipt', 'amt_red_ipt')
        ]

        total_brut = 0
        total_net = 0
        
        for row, (name, k_brut, k_net) in enumerate(garanties):
            # 1. Récupération sécurisée des valeurs avec conversion en float
            try:
                val_brut_raw = self.data.get(k_brut, 0)
                # Conversion en float, gestion des chaînes vides ou None
                if val_brut_raw is None or val_brut_raw == '':
                    val_brut = 0.0
                else:
                    val_brut = float(val_brut_raw)
            except (ValueError, TypeError):
                val_brut = 0.0
            
            try:
                val_net_raw = self.data.get(k_net, 0)
                if val_net_raw is None or val_net_raw == '':
                    val_net = 0.0
                else:
                    val_net = float(val_net_raw)
            except (ValueError, TypeError):
                # Si la clé net n'existe pas, utiliser le montant brut
                val_net = val_brut
            
            # 2. Accumulation des totaux
            total_brut += val_brut
            total_net += val_net
            
            # --- Remplissage du tableau ---
            # Nom de la garantie
            item_name = QTableWidgetItem(name)
            item_name.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 0, item_name)
            
            # Montant brut
            txt_brut = f"{val_brut:,.0f}".replace(",", " ") if val_brut > 0 else "0"
            item_brut = QTableWidgetItem(txt_brut)
            item_brut.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_brut.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 1, item_brut)
            
            # Montant net
            txt_net = f"{val_net:,.0f}".replace(",", " ") if val_net > 0 else "0"
            item_net = QTableWidgetItem(txt_net)
            item_net.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_net.setFont(QFont("Segoe UI", 10))
            
            # Appliquer une couleur selon la situation
            if val_net < val_brut and val_net > 0:
                # Réduction appliquée
                item_net.setForeground(QColor("#10b981"))
            elif val_net == 0 and val_brut > 0:
                # Garantie offerte ou totalement réduite
                item_net.setForeground(QColor("#ef4444"))
            elif val_net > 0:
                # Montant normal
                item_net.setForeground(QColor("#1e293b"))
            
            self.table.setItem(row, 2, item_net)

        self.table.setFixedHeight(340)
        container_layout.addWidget(self.table)
        
        # Ajouter un résumé rapide sous le tableau
        summary_widget = QFrame()
        summary_widget.setStyleSheet("background: #f8fafc; border-radius: 12px; padding: 12px;")
        summary_layout = QHBoxLayout(summary_widget)
        
        total_brut_lbl = QLabel(f"Total brut: {total_brut:,.0f} FCFA".replace(",", " "))
        total_brut_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        
        total_net_lbl = QLabel(f"Total net: {total_net:,.0f} FCFA".replace(",", " "))
        total_net_lbl.setStyleSheet("font-weight: 700; color: #3b82f6;")
        
        # Calcul de la réduction totale
        reduction_total = total_brut - total_net
        if reduction_total > 0:
            reduction_lbl = QLabel(f"Réduction: {reduction_total:,.0f} FCFA".replace(",", " "))
            reduction_lbl.setStyleSheet("font-weight: 600; color: #f59e0b;")
            summary_layout.addWidget(reduction_lbl)
            summary_layout.addStretch()
        
        summary_layout.addWidget(total_brut_lbl)
        summary_layout.addStretch()
        summary_layout.addWidget(total_net_lbl)
        
        container_layout.addWidget(summary_widget)
        
        return container

    def create_recap_card(self):
        """Crée la carte récapitulative"""
        recap_frame = QFrame()
        recap_frame.setObjectName("RecapCard")
        recap_layout = QHBoxLayout(recap_frame)
        recap_layout.setContentsMargins(32, 28, 32, 28)
        
        prime_nette = float(self.data.get('prime_nette', 0))
        prime_brute = float(self.data.get('prime_brute', 0))
        reduction = prime_brute - prime_nette
        reduction_percent = (reduction / prime_brute * 100) if prime_brute > 0 else 0
        
        # Left side - Stats
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(8)
        
        total_lbl = QLabel("PRIME NETTE À PAYER")
        total_lbl.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 13px; font-weight: 500;")
        
        amount_lbl = QLabel(f"{prime_nette:,.0f} FCFA".replace(",", " "))
        amount_lbl.setStyleSheet("color: white; font-size: 36px; font-weight: 800;")
        
        stats_layout.addWidget(total_lbl)
        stats_layout.addWidget(amount_lbl)
        
        # Middle - Stats card
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(24)
        
        # Prime brute
        brut_card = QFrame()
        brut_card.setStyleSheet("background: rgba(255,255,255,0.15); border-radius: 12px; padding: 12px 20px;")
        brut_layout = QVBoxLayout(brut_card)
        brut_layout.setSpacing(4)
        
        brut_title = QLabel("Prime brute")
        brut_title.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 11px;")
        brut_value = QLabel(f"{prime_brute:,.0f} FCFA".replace(",", " "))
        brut_value.setStyleSheet("color: white; font-size: 16px; font-weight: 600;")
        
        brut_layout.addWidget(brut_title)
        brut_layout.addWidget(brut_value)
        
        # Réduction
        red_card = QFrame()
        red_card.setStyleSheet("background: rgba(255,255,255,0.15); border-radius: 12px; padding: 12px 20px;")
        red_layout = QVBoxLayout(red_card)
        red_layout.setSpacing(4)
        
        red_title = QLabel("Réduction")
        red_title.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 11px;")
        red_value = QLabel(f"- {reduction:,.0f} FCFA".replace(",", " "))
        red_value.setStyleSheet("color: #fbbf24; font-size: 16px; font-weight: 600;")
        red_percent = QLabel(f"({reduction_percent:.1f}%)")
        red_percent.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 11px;")
        
        red_layout.addWidget(red_title)
        red_layout.addWidget(red_value)
        red_layout.addWidget(red_percent)
        
        middle_layout.addWidget(brut_card)
        middle_layout.addWidget(red_card)
        
        recap_layout.addLayout(stats_layout, 2)
        recap_layout.addLayout(middle_layout, 2)
        recap_layout.addStretch()
        
        return recap_frame

    def create_calendar_section(self):
        """Crée la section des prochaines échéances"""
        calendar_card = QFrame()
        calendar_card.setProperty("class", "InfoCard")
        layout = QVBoxLayout(calendar_card)
        
        title = QLabel("📅 PROCHAINES ÉCHÉANCES")
        title.setProperty("class", "SectionTitle")
        layout.addWidget(title)
        
        # Calculer les échéances à partir des données
        date_fin = self.data.get('date_fin')
        days_left = 0
        if date_fin:
            from datetime import date
            if isinstance(date_fin, date):
                days_left = (date_fin - date.today()).days
        
        echeances = [
            ("Renouvellement contrat", self.format_date(date_fin), f"{days_left} jours restants" if days_left > 0 else "Expiré"),
            ("Paiement mensuel", self.format_date(self.data.get('prochain_paiement', 'N/A')), "À venir"),
            ("Visite technique", self.format_date(self.data.get('visite_technique', 'N/A')), "À programmer"),
            ("Révision périodique", self.format_date(self.data.get('revision', 'N/A')), "À programmer")
        ]
        
        for event, date, delay in echeances:
            widget = QFrame()
            widget_layout = QHBoxLayout(widget)
            
            date_lbl = QLabel(date)
            date_lbl.setStyleSheet("background: #eef2ff; padding: 4px 12px; border-radius: 20px; font-size: 12px; min-width: 120px;")
            
            event_lbl = QLabel(event)
            event_lbl.setStyleSheet("font-weight: 500;")
            
            delay_lbl = QLabel(delay)
            delay_color = "#f97316" if "jours restants" in delay else "#ef4444" if "Expiré" in delay else "#64748b"
            delay_lbl.setStyleSheet(f"color: {delay_color}; font-size: 12px;")
            
            widget_layout.addWidget(date_lbl)
            widget_layout.addWidget(event_lbl)
            widget_layout.addStretch()
            widget_layout.addWidget(delay_lbl)
            
            layout.addWidget(widget)
        
        return calendar_card

    def create_history_section(self):
        """Crée la section historique des événements"""
        history_card = QFrame()
        history_card.setProperty("class", "InfoCard")
        layout = QVBoxLayout(history_card)
        
        title = QLabel("📋 HISTORIQUE DU VÉHICULE")
        title.setProperty("class", "SectionTitle")
        layout.addWidget(title)
        
        # Récupérer l'historique réel ou utiliser des données simulées
        events = self.data.get('historique', [
            ("📄 Contrat souscrit", self.format_date(self.data.get('date_debut', '')), f"Prime: {self.format_amount(self.data.get('prime_nette', 0))} FCFA"),
            ("🔄 Renouvellement", self.format_date(self.data.get('date_fin', '')), f"Prime: {self.format_amount(self.data.get('prime_nette', 0))} FCFA"),
            ("📝 Modification garantie", self.format_date(self.data.get('date_fin', '')), "Ajout vol + incendie"),
            ("💰 Paiement effectué", self.format_date(self.data.get('date_fin', '')), f"Montant: {self.format_amount(self.data.get('prime_nette', 0))} FCFA")
        ])
        
        for event, date, detail in events:
            event_widget = QFrame()
            event_widget.setProperty("class", "EventWidget")
            event_layout = QHBoxLayout(event_widget)
            
            date_lbl = QLabel(date)
            date_lbl.setStyleSheet("font-size: 11px; color: #64748b; min-width: 100px;")
            
            event_lbl = QLabel(event)
            event_lbl.setStyleSheet("font-weight: 600;")
            
            detail_lbl = QLabel(detail)
            detail_lbl.setStyleSheet("color: #475569; font-size: 12px;")
            
            event_layout.addWidget(date_lbl)
            event_layout.addWidget(event_lbl)
            event_layout.addStretch()
            event_layout.addWidget(detail_lbl)
            
            layout.addWidget(event_widget)
        
        return history_card

    def create_documents_section(self):
        """Crée la section des documents téléchargeables"""
        docs_card = QFrame()
        docs_card.setProperty("class", "InfoCard")
        layout = QVBoxLayout(docs_card)
        
        title = QLabel("📁 DOCUMENTS ANNEXES")
        title.setProperty("class", "SectionTitle")
        layout.addWidget(title)
        
        docs_grid = QGridLayout()
        docs_grid.setSpacing(12)
        
        documents = [
            ("📄 Contrat d'assurance", "contrat.pdf", "1.2 MB"),
            ("📋 Conditions générales", "conditions.pdf", "2.5 MB"),
            ("📝 Avenant n°1", "avenant.pdf", "0.8 MB"),
            ("💳 Relevé de paiement", "paiement.pdf", "0.5 MB"),
            ("🛡️ Attestation", "attestation.pdf", "0.3 MB"),
            ("📊 Devis initial", "devis.pdf", "0.4 MB")
        ]
        
        self.doc_buttons = {}
        for i, (name, file, size) in enumerate(documents):
            doc_btn = QPushButton(f"{name} ({size})")
            doc_btn.setStyleSheet("""
                QPushButton {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background: #f1f5f9;
                }
            """)
            doc_btn.setCursor(Qt.PointingHandCursor)
            doc_btn.setProperty("file", file)
            self.doc_buttons[file] = doc_btn
            docs_grid.addWidget(doc_btn, i // 2, i % 2)
        
        layout.addLayout(docs_grid)
        return docs_card

    def create_contacts_section(self):
        """Crée la section des contacts utiles"""
        contacts_card = QFrame()
        contacts_card.setProperty("class", "InfoCard")
        layout = QVBoxLayout(contacts_card)
        
        title = QLabel("📞 CONTACTS UTILES")
        title.setProperty("class", "SectionTitle")
        layout.addWidget(title)
        
        contacts_grid = QGridLayout()
        contacts_grid.setSpacing(15)
        
        contacts = [
            ("👤 Agent commercial", "Mme TAMAR HAMBEN", "+237 6XX XX XX XX", "jean.dupont@assurance.com"),
            ("🛡️ Assistance 24/7", "Service client", "+237 800 00 00 00", "assistance@amsassurance.com"),
            ("🚗 Dépannage", "Auto Assistance", "+237 699 99 99 99", None),
            ("⚖️ Sinistres", "Déclaration sinistre", "+237 6XX XX XX XX", "sinistres@amsassurance.com")
        ]
        
        for i, (role, name, phone, email) in enumerate(contacts):
            contact_widget = QFrame()
            contact_widget.setProperty("class", "ContactWidget")
            contact_layout = QVBoxLayout(contact_widget)
            
            role_lbl = QLabel(role)
            role_lbl.setStyleSheet("font-weight: 700; font-size: 13px;")
            
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-size: 12px; color: #1e293b;")
            
            phone_lbl = QLabel(phone)
            phone_lbl.setStyleSheet("font-size: 12px; color: #3b82f6;")
            
            contact_layout.addWidget(role_lbl)
            contact_layout.addWidget(name_lbl)
            contact_layout.addWidget(phone_lbl)
            
            if email:
                email_lbl = QLabel(email)
                email_lbl.setStyleSheet("font-size: 11px; color: #64748b;")
                contact_layout.addWidget(email_lbl)
            
            contacts_grid.addWidget(contact_widget, i // 2, i % 2)
        
        layout.addLayout(contacts_grid)
        return contacts_card

    def create_notifications_section(self):
        """Crée la section des notifications"""
        notif_card = QFrame()
        notif_card.setProperty("class", "InfoCard")
        layout = QVBoxLayout(notif_card)
        
        title = QLabel("🔔 NOTIFICATIONS")
        title.setProperty("class", "SectionTitle")
        layout.addWidget(title)
        
        # Générer des notifications dynamiques
        notifications = []
        
        # Vérifier l'expiration
        date_fin = self.data.get('date_fin')
        if date_fin:
            from datetime import date
            if isinstance(date_fin, date):
                days_left = (date_fin - date.today()).days
                if days_left <= 30:
                    notifications.append((f"⚠️ Votre contrat arrive à échéance dans {days_left} jours", "warning"))
        
        notifications.extend([
            ("✅ Paiement du mois confirmé", "success"),
            ("📄 Nouveau document disponible", "info"),
            ("💡 Astuce: Activez le prélèvement automatique", "tip")
        ])
        
        colors = {
            "warning": "#fef3c7",
            "success": "#dcfce7",
            "info": "#eef2ff",
            "tip": "#fce7f3"
        }
        
        for msg, type_ in notifications:
            notif_widget = QFrame()
            notif_widget.setProperty("class", "NotificationWidget")
            notif_widget.setStyleSheet(f"""
                background: {colors.get(type_, '#f1f5f9')};
                border-radius: 8px;
                padding: 8px;
                margin: 4px 0;
            """)
            notif_layout = QHBoxLayout(notif_widget)
            
            msg_lbl = QLabel(msg)
            msg_lbl.setStyleSheet("font-size: 12px;")
            
            notif_layout.addWidget(msg_lbl)
            notif_layout.addStretch()
            
            layout.addWidget(notif_widget)
        
        return notif_card

    def create_qrcode_section(self):
        """Crée un QR code pour accès rapide"""
        qr_card = QFrame()
        qr_card.setProperty("class", "InfoCard")
        layout = QHBoxLayout(qr_card)
        layout.setContentsMargins(24, 20, 24, 20)
        
        # Générer QR code avec les infos du véhicule
        vehicle_id = self.data.get('id', '')
        data_str = f"https://amsassurance.com/vehicle/{vehicle_id}"
        
        try:
            qr = qrcode.QRCode(box_size=4, border=1)
            qr.add_data(data_str)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#3b82f6", back_color="white")
            
            # Convertir en QPixmap
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            qr_label = QLabel()
            qr_label.setPixmap(pixmap)
        except:
            qr_label = QLabel("🔲 QR Code")
            qr_label.setStyleSheet("font-size: 48px;")
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        title_lbl = QLabel("🔗 ACCÈS RAPIDE")
        title_lbl.setStyleSheet("font-weight: 700; font-size: 14px;")
        
        desc_lbl = QLabel("Scannez ce QR code pour accéder")
        desc_lbl.setStyleSheet("font-size: 12px; color: #64748b;")
        
        link_lbl = QLabel("à la fiche véhicule en ligne")
        link_lbl.setStyleSheet("font-size: 12px; color: #64748b;")
        
        info_layout.addWidget(title_lbl)
        info_layout.addWidget(desc_lbl)
        info_layout.addWidget(link_lbl)
        
        layout.addWidget(qr_label)
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return qr_card

    def create_print_section(self):
        """Crée la section des actions d'impression"""
        print_section = QVBoxLayout()
        print_section.setSpacing(16)
        
        title_print = QLabel("ACTIONS D'IMPRESSION")
        title_print.setProperty("class", "SectionTitle")
        print_section.addWidget(title_print)
        
        btn_grid = QGridLayout()
        btn_grid.setSpacing(16)
        
        actions = [
            ("📄 CARTE ROSE", "carte_rose", "Document officiel d'assurance"),
            ("🎫 VIGNETTE", "vignette", "Vignette à apposer sur le pare-brise"),
            ("🧾 QUITTANCE", "quittance", "Preuve de paiement"),
            ("🛡️ ATTESTATION", "attestation", "Attestation d'assurance"),
            ("📊 DEVIS", "devis", "Devis détaillé"),
            ("📑 RAPPORT COMPLET", "rapport", "Rapport complet du véhicule")
        ]
        
        self.print_buttons = {}
        
        for i, (label, key, tooltip) in enumerate(actions):
            btn = QPushButton(label)
            btn.setProperty("class", "PrintBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tooltip)
            btn.setMinimumHeight(60)
            
            self.print_buttons[key] = btn
            btn_grid.addWidget(btn, i // 3, i % 3)
        
        print_section.addLayout(btn_grid)
        return print_section

    def format_amount(self, amount):
        """Formate un montant avec séparateurs de milliers"""
        try:
            return f"{int(amount):,}".replace(",", " ")
        except:
            return "0"
    
    def format_date(self, date):
        """Formate une date"""
        if date and date != 'N/A' and date != '':
            try:
                if hasattr(date, 'strftime'):
                    return date.strftime("%d/%m/%Y")
                return str(date)
            except:
                return str(date)
        return "Non définie"
    
    def calculate_validity(self):
        """Calcule la validité du contrat"""
        try:
            date_fin = self.data.get('date_fin')
            if date_fin:
                from datetime import date
                if isinstance(date_fin, date):
                    if date_fin < date.today():
                        return "Contrat expiré"
                    else:
                        days_left = (date_fin - date.today()).days
                        return f"Valide (encore {days_left} jours)"
        except:
            pass
        return "Statut inconnu"
    
    def calculate_years_insured(self):
        """Calcule le nombre d'années d'assurance"""
        try:
            date_debut = self.data.get('date_debut')
            if date_debut:
                from datetime import date
                if isinstance(date_debut, date):
                    years = date.today().year - date_debut.year
                    return f"{years} ans"
        except:
            pass
        return "Nouveau"
    
    def calculate_total_premiums_paid(self):
        """Calcule le total des primes versées"""
        try:
            prime_nette = float(self.data.get('prime_nette', 0))
            years = self.calculate_years_insured()
            if years != "Nouveau":
                years_num = int(years.split()[0])
                total = prime_nette * years_num
                return f"{self.format_amount(total)} FCFA"
        except:
            pass
        return "Non disponible"
    
    def connect_signals(self):
        """Connecte les boutons aux fonctions du contrôleur"""
        # Connexion des boutons d'action
        for action, btn in self.action_buttons.items():
            btn.clicked.connect(lambda checked, a=action: self.handle_action(a))
        
        # Connexion des boutons d'impression
        if self.controller:
            for key, btn in self.print_buttons.items():
                btn.clicked.connect(lambda checked, k=key: self.print_document(k))
        
        # Connexion des boutons de documents
        for file, btn in self.doc_buttons.items():
            btn.clicked.connect(lambda checked, f=file: self.download_document(f))
    
    def handle_action(self, action):
        """Gère les actions du header"""
        if action == "edit":
            QMessageBox.information(self, "Modification", "Fonction de modification à implémenter")
        elif action == "renew":
            QMessageBox.information(self, "Renouvellement", "Fonction de renouvellement à implémenter")
        elif action == "email":
            QMessageBox.information(self, "Envoi email", "Fonction d'envoi par email à implémenter")
        elif action == "export":
            QMessageBox.information(self, "Export PDF", "Fonction d'export PDF à implémenter")
    
    def print_document(self, doc_type):
        """Gère l'impression des documents"""
        if self.controller:
            methods = {
                "carte_rose": getattr(self.controller.vehicles, 'print_carte_rose', None),
                "vignette": getattr(self.controller.vehicles, 'print_vignette', None),
                "quittance": getattr(self.controller.vehicles, 'print_quittance', None),
                "attestation": getattr(self.controller.vehicles, 'print_attestation', None),
                "devis": getattr(self.controller.vehicles, 'print_devis', None),
                "rapport": getattr(self.controller.vehicles, 'print_rapport', None)
            }
            if doc_type in methods and methods[doc_type]:
                methods[doc_type](self.data)
            else:
                QMessageBox.information(self, "Impression", f"Impression du document {doc_type}")
    
    def download_document(self, file):
        """Gère le téléchargement des documents"""
        QMessageBox.information(self, "Téléchargement", f"Téléchargement du document {file}")

    def close_window(self):
        """Ferme la fenêtre"""
        self.close()

    # gestion de la statistque de chaque contrat

    def create_stats_section(self):
        """Crée une section de statistiques premium avec design moderne"""
        stats_card = QFrame()
        stats_card.setProperty("class", "InfoCard")
        stats_card.setStyleSheet("""
            QFrame#InfoCard {
                background: white;
                border-radius: 24px;
                padding: 0px;
            }
        """)
        
        # Layout principal avec padding interne
        main_layout = QVBoxLayout(stats_card)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # === EN-TÊTE DE SECTION AVEC DÉCORATION ===
        header_widget = QFrame()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Titre avec effet
        title_container = QFrame()
        title_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #f0f9ff, stop:1 #ffffff);
            border-radius: 40px;
            padding: 8px 20px;
        """)
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)
        
        title_icon = QLabel("⚡")
        title_icon.setStyleSheet("font-size: 22px;")
        title_text = QLabel("TABLEAU DE BORD")
        title_text.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b; letter-spacing: 1px;")
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        
        # Date du jour
        from datetime import datetime
        date_lbl = QLabel(datetime.now().strftime("%d/%m/%Y"))
        date_lbl.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 500;")
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        header_layout.addWidget(date_lbl)
        
        main_layout.addWidget(header_widget)
        
        # === CARTE PRINCIPALE DE PRIME ===
        prime_card = self.create_premium_prime_card()
        main_layout.addWidget(prime_card)
        
        # === GRILLE DES STATS ===
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        stats_grid.setContentsMargins(0, 0, 0, 0)
        
        # Calcul des données
        prime_nette = float(self.data.get('prime_nette', 0))
        prime_brute = float(self.data.get('prime_brute', 0))
        reduction = prime_brute - prime_nette
        reduction_percent = (reduction / prime_brute * 100) if prime_brute > 0 else 0
        
        stats_data = [
            {
                "icon": "📅",
                "icon_color": "#3b82f6",
                "label": "Ancienneté",
                "value": self.calculate_years_insured(),
                "unit": "",
                "bg_color": "#eff6ff",
                "border_color": "#3b82f6"
            },
            {
                "icon": "🛡️",
                "icon_color": "#10b981",
                "label": "Sinistres",
                "value": str(self.data.get('sinistres', 0)),
                "unit": "déclaré(s)",
                "bg_color": "#ecfdf5",
                "border_color": "#10b981"
            },
            {
                "icon": "💰",
                "icon_color": "#f59e0b",
                "label": "Total versé",
                "value": self.calculate_total_premiums_paid(),
                "unit": "FCFA",
                "bg_color": "#fffbeb",
                "border_color": "#f59e0b"
            },
            {
                "icon": "🎯",
                "icon_color": "#8b5cf6",
                "label": "Bonus",
                "value": f"{self.calculate_bonus_malus()}",
                "unit": "%",
                "bg_color": "#f5f3ff",
                "border_color": "#8b5cf6"
            }
        ]
        
        for i, stat in enumerate(stats_data):
            stat_widget = self.create_modern_stat_card(stat)
            stats_grid.addWidget(stat_widget, i // 2, i % 2)
        
        main_layout.addLayout(stats_grid)
        
        # === SECTION ÉVOLUTION ET RISQUE ===
        bottom_grid = QGridLayout()
        bottom_grid.setSpacing(16)
        bottom_grid.setContentsMargins(0, 0, 0, 0)
        
        # Graphique d'évolution
        evolution_widget = self.create_modern_evolution_chart()
        bottom_grid.addWidget(evolution_widget, 0, 0)
        
        # Indicateurs de risque
        risk_widget = self.create_modern_risk_indicator()
        bottom_grid.addWidget(risk_widget, 0, 1)
        
        main_layout.addLayout(bottom_grid)
        
        return stats_card

    def create_premium_prime_card(self):
        """Crée une carte premium pour la prime principale"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
                border-radius: 20px;
            }
        """)
        card.setFixedHeight(140)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        
        # Partie gauche - Prime
        left_widget = QFrame()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(8)
        
        prime_label = QLabel("PRIME NETTE ANNUELLE")
        prime_label.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600; letter-spacing: 1px;")
        
        prime_nette = float(self.data.get('prime_nette', 0))
        prime_value = QLabel(f"{prime_nette:,.0f}".replace(",", " "))
        prime_value.setStyleSheet("color: white; font-size: 36px; font-weight: 800;")
        
        prime_sub = QLabel("FCFA TTC")
        prime_sub.setStyleSheet("color: #64748b; font-size: 11px;")
        
        left_layout.addWidget(prime_label)
        left_layout.addWidget(prime_value)
        left_layout.addWidget(prime_sub)
        
        # Partie droite - Badge de réduction
        prime_brute = float(self.data.get('prime_brute', 0))
        reduction = prime_brute - prime_nette
        reduction_percent = (reduction / prime_brute * 100) if prime_brute > 0 else 0
        
        right_widget = QFrame()
        right_widget.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.1);
                border-radius: 16px;
            }
        """)
        right_widget.setFixedWidth(120)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setSpacing(4)
        
        if reduction > 0:
            reduction_badge = QLabel("ÉCONOMIE")
            reduction_badge.setStyleSheet("color: #fbbf24; font-size: 10px; font-weight: 600;")
            
            reduction_value = QLabel(f"{reduction:,.0f}".replace(",", " "))
            reduction_value.setStyleSheet("color: white; font-size: 18px; font-weight: 700;")
            
            reduction_percent_label = QLabel(f"-{reduction_percent:.0f}%")
            reduction_percent_label.setStyleSheet("color: #fbbf24; font-size: 20px; font-weight: 800;")
            
            right_layout.addWidget(reduction_badge)
            right_layout.addWidget(reduction_percent_label)
            right_layout.addWidget(reduction_value)
        else:
            no_reduction = QLabel("AUCUNE\nRÉDUCTION")
            no_reduction.setAlignment(Qt.AlignCenter)
            no_reduction.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600;")
            right_layout.addWidget(no_reduction)
        
        layout.addWidget(left_widget)
        layout.addStretch()
        layout.addWidget(right_widget)
        
        return card

    def create_modern_stat_card(self, stat):
        """Crée une carte statistique moderne"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {stat['bg_color']};
                border-radius: 16px;
                border-left: 4px solid {stat['border_color']};
            }}
        """)
        card.setMinimumHeight(100)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Icône
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {stat['icon_color']}20;
                border-radius: 24px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel(stat['icon'])
        icon_lbl.setStyleSheet(f"font-size: 24px; background: transparent;")
        icon_layout.addWidget(icon_lbl)
        
        # Contenu
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(4)
        
        label_lbl = QLabel(stat['label'])
        label_lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 500; text-transform: uppercase;")
        
        value_lbl = QLabel(stat['value'])
        value_lbl.setStyleSheet(f"color: {stat['icon_color']}; font-size: 24px; font-weight: 800;")
        
        unit_lbl = QLabel(stat['unit'])
        unit_lbl.setStyleSheet("color: #94a3b8; font-size: 10px;")
        
        content_layout.addWidget(label_lbl)
        content_layout.addWidget(value_lbl)
        content_layout.addWidget(unit_lbl)
        
        layout.addWidget(icon_container)
        layout.addSpacing(12)
        layout.addWidget(content_widget)
        layout.addStretch()
        
        return card

    def create_modern_evolution_chart(self):
        """Crée un graphique d'évolution moderne"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        
        # En-tête
        header_layout = QHBoxLayout()
        title_lbl = QLabel("📈 Évolution des primes")
        title_lbl.setStyleSheet("font-weight: 700; font-size: 13px; color: #1e293b;")
        
        trend_value = self.calculate_trend()
        trend_lbl = QLabel(f"{trend_value}")
        trend_lbl.setStyleSheet("color: #10b981; font-size: 12px; font-weight: 600;")
        
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(trend_lbl)
        layout.addLayout(header_layout)
        
        # Graphique
        chart_widget = self.create_animated_chart()
        layout.addWidget(chart_widget)
        
        return card

    def create_animated_chart(self):
        """Crée un graphique à barres animé"""
        widget = QFrame()
        widget.setFixedHeight(120)
        
        layout = QHBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Données
        years = [2023, 2024, 2025]
        premiums = [125000, 138000, int(self.data.get('prime_nette', 150000))]
        max_premium = max(premiums) if premiums else 100000
        
        for year, premium in zip(years, premiums):
            bar_container = QWidget()
            bar_layout = QVBoxLayout(bar_container)
            bar_layout.setSpacing(6)
            bar_layout.setAlignment(Qt.AlignBottom)
            
            # Barre
            height = max(30, int((premium / max_premium) * 70))
            bar = QFrame()
            bar.setFixedSize(36, height)
            
            # Couleur dégradée
            if premium >= max_premium:
                bar.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                            stop:0 #3b82f6, stop:1 #60a5fa);
                        border-radius: 6px;
                    }
                """)
            else:
                bar.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                            stop:0 #94a3b8, stop:1 #cbd5e1);
                        border-radius: 6px;
                    }
                """)
            
            # Valeur
            value_lbl = QLabel(f"{premium/1000:.0f}k")
            value_lbl.setStyleSheet("font-size: 9px; font-weight: 600; color: #475569;")
            value_lbl.setAlignment(Qt.AlignCenter)
            
            # Année
            year_lbl = QLabel(str(year))
            year_lbl.setStyleSheet("font-size: 10px; font-weight: 500; color: #64748b;")
            year_lbl.setAlignment(Qt.AlignCenter)
            
            bar_layout.addStretch()
            bar_layout.addWidget(bar)
            bar_layout.addWidget(value_lbl)
            bar_layout.addWidget(year_lbl)
            
            layout.addWidget(bar_container)
            layout.addStretch()
        
        return widget

    def create_modern_risk_indicator(self):
        """Crée un indicateur de risque moderne"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        
        # Titre
        title_lbl = QLabel("🎯 Niveau de risque")
        title_lbl.setStyleSheet("font-weight: 700; font-size: 13px; color: #1e293b;")
        layout.addWidget(title_lbl)
        
        # Jauge de risque
        sinistres = int(self.data.get('sinistres', 0))
        risk_score = min(100, sinistres * 25)
        risk_color = "#10b981" if risk_score <= 25 else "#f59e0b" if risk_score <= 50 else "#ef4444"
        
        gauge_widget = self.create_risk_gauge(risk_score, risk_color)
        layout.addWidget(gauge_widget)
        
        # Indicateurs
        indicators_layout = QHBoxLayout()
        indicators_layout.setSpacing(8)
        
        indicators = [
            ("Profil", "Bon conducteur" if sinistres == 0 else "Standard", "#3b82f6"),
            ("Classe", f"{self.calculate_bonus_malus()}%", "#8b5cf6")
        ]
        
        for label, value, color in indicators:
            indicator = QFrame()
            indicator.setStyleSheet(f"""
                QFrame {{
                    background: {color}10;
                    border-radius: 12px;
                    padding: 8px;
                }}
            """)
            indicator_layout = QVBoxLayout(indicator)
            
            label_lbl = QLabel(label)
            label_lbl.setStyleSheet("color: #64748b; font-size: 10px;")
            
            value_lbl = QLabel(value)
            value_lbl.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 700;")
            
            indicator_layout.addWidget(label_lbl)
            indicator_layout.addWidget(value_lbl)
            
            indicators_layout.addWidget(indicator)
        
        layout.addLayout(indicators_layout)
        
        return card

    def create_risk_gauge(self, score, color):
        """Crée une jauge de risque circulaire"""
        widget = QFrame()
        widget.setFixedHeight(60)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre de progression horizontale
        bar_container = QFrame()
        bar_container.setStyleSheet("""
            QFrame {
                background: #e2e8f0;
                border-radius: 10px;
            }
        """)
        bar_container.setFixedHeight(20)
        
        bar = QFrame()
        bar.setFixedWidth(int(score * 3))
        bar.setFixedHeight(20)
        bar.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 10px;
            }}
        """)
        
        bar_layout = QHBoxLayout(bar_container)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.addWidget(bar)
        bar_layout.addStretch()
        
        # Score
        score_lbl = QLabel(f"{score}%")
        score_lbl.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 800;")
        score_lbl.setMinimumWidth(50)
        
        layout.addWidget(bar_container)
        layout.addWidget(score_lbl)
        
        return widget

    def calculate_trend(self):
        """Calcule la tendance d'évolution"""
        prime_actuelle = float(self.data.get('prime_nette', 0))
        prime_2024 = 138000  # À remplacer par donnée réelle
        
        if prime_actuelle > prime_2024:
            variation = ((prime_actuelle - prime_2024) / prime_2024) * 100
            return f"▲ +{variation:.1f}%"
        elif prime_actuelle < prime_2024:
            variation = ((prime_2024 - prime_actuelle) / prime_2024) * 100
            return f"▼ -{variation:.1f}%"
        else:
            return "► Stable"

    def get_years_count(self):
        """Retourne le nombre d'années d'assurance"""
        try:
            date_debut = self.data.get('date_debut')
            if date_debut:
                from datetime import date
                if isinstance(date_debut, date):
                    years = date.today().year - date_debut.year
                    return max(0, years)
        except:
            pass
        return 0

    def calculate_years_insured(self):
        """Calcule le nombre d'années d'assurance"""
        years = self.get_years_count()
        if years == 0:
            return "< 1 an"
        return f"{years} an{'s' if years > 1 else ''}"

    def calculate_total_premiums_paid(self):
        """Calcule le total des primes versées"""
        try:
            prime_nette = float(self.data.get('prime_nette', 0))
            years = max(1, self.get_years_count())
            total = prime_nette * years
            return f"{total/1000000:.1f}M" if total > 1000000 else f"{total/1000:.0f}k"
        except:
            return "0"

    def calculate_bonus_malus(self):
        """Calcule le bonus/malus"""
        sinistres = int(self.data.get('sinistres', 0))
        years = self.get_years_count()
        
        if years == 0:
            return 100
        
        bonus = min(50, years * 5) if sinistres == 0 else 0
        malus = min(50, sinistres * 25)
        result = max(50, min(150, 100 - bonus + malus))
        
        return result