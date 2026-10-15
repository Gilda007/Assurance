from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QScrollArea, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
                             QComboBox, QMessageBox)
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
        """Crée la carte récapitulative avec validation de paiement"""
        recap_frame = QFrame()
        recap_frame.setObjectName("RecapCard")
        recap_frame.setStyleSheet("""
            QFrame#RecapCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 20px;
            }
        """)
        
        main_layout = QVBoxLayout(recap_frame)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(20)
        
        # ========== LIGNE 1: TITRE ==========
        title_layout = QHBoxLayout()
        title_icon = QLabel("💰")
        title_icon.setStyleSheet("font-size: 20px; background: transparent;")
        title_text = QLabel("RÉCAPITULATIF FINANCIER")
        title_text.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 1px;
            background: transparent;
        """)
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        # ========== LIGNE 2: MONTANT PRINCIPAL ==========
        prime_nette = float(self.data.get('prime_nette', 0))
        prime_brute = float(self.data.get('prime_brute', 0))
        reduction = prime_brute - prime_nette
        reduction_percent = (reduction / prime_brute * 100) if prime_brute > 0 else 0
        
        amount_layout = QHBoxLayout()
        amount_layout.setSpacing(30)
        
        # Montant à payer
        left_amount = QVBoxLayout()
        left_amount.setSpacing(8)
        total_lbl = QLabel("MONTANT TOTAL À PAYER")
        total_lbl.setStyleSheet("""
            color: rgba(255,255,255,0.7);
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1px;
            background: transparent;
        """)
        amount_lbl = QLabel(f"{prime_nette:,.0f}".replace(",", " "))
        amount_lbl.setStyleSheet("""
            color: white;
            font-size: 42px;
            font-weight: 800;
            background: transparent;
        """)
        currency_lbl = QLabel("FCFA")
        currency_lbl.setStyleSheet("""
            color: rgba(255,255,255,0.6);
            font-size: 14px;
            background: transparent;
        """)
        left_amount.addWidget(total_lbl)
        left_amount.addWidget(amount_lbl)
        left_amount.addWidget(currency_lbl)
        
        # Détails
        right_details = QVBoxLayout()
        right_details.setSpacing(10)
        
        # Prime brute
        brut_widget = self.create_detail_row("Prime brute", f"{prime_brute:,.0f}".replace(",", " "), "#ffffff")
        right_details.addLayout(brut_widget)
        
        # Réduction
        reduction_color = "#fbbf24" if reduction > 0 else "#94a3b8"
        reduction_text = f"- {reduction:,.0f}".replace(",", " ") if reduction > 0 else "0"
        reduction_percent_text = f"({reduction_percent:.1f}%)" if reduction > 0 else ""
        red_widget = self.create_detail_row("Réduction", reduction_text, reduction_color, reduction_percent_text)
        right_details.addLayout(red_widget)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: rgba(255,255,255,0.2); max-height: 1px; margin: 5px 0;")
        right_details.addWidget(sep)
        
        # Net à payer
        net_widget = self.create_detail_row("Net à payer", f"{prime_nette:,.0f}".replace(",", " "), "#fbbf24", bold=True)
        right_details.addLayout(net_widget)
        
        amount_layout.addLayout(left_amount, 1)
        amount_layout.addLayout(right_details, 1)
        main_layout.addLayout(amount_layout)
        
        # ========== LIGNE 3: FRAIS SUPPLÉMENTAIRES ==========
        frais_title = QLabel("📋 DÉTAIL DES FRAIS")
        frais_title.setStyleSheet("""
            color: rgba(255,255,255,0.6);
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1px;
            margin-top: 10px;
            background: transparent;
        """)
        main_layout.addWidget(frais_title)
        
        frais_grid = QGridLayout()
        frais_grid.setSpacing(10)
        frais_grid.setContentsMargins(0, 5, 0, 5)
        
        # Récupération des frais
        carte_rose = float(self.data.get('carte_rose', 0))
        accessoires = float(self.data.get('accessoires', 0))
        tva = float(self.data.get('tva', 0))
        asac = float(self.data.get('fichier_asac', 0))
        vignette = float(self.data.get('vignette', 0))
        
        frais_items = [
            ("📄 Carte Rose", carte_rose),
            ("🔧 Accessoires", accessoires),
            ("📊 TVA (19.25%)", tva),
            ("📁 Fichier ASAC", asac),
            ("🎫 Vignette", vignette),
        ]
        
        for i, (label, value) in enumerate(frais_items):
            item_layout = self.create_frais_row(label, value)
            frais_grid.addLayout(item_layout, i // 3, i % 3)
        
        main_layout.addLayout(frais_grid)
        
        # ========== LIGNE 4: PTTC (Total TTC) ==========
        pttc = float(self.data.get('pttc', prime_nette + carte_rose + accessoires + tva + asac + vignette))
        
        pttc_layout = QHBoxLayout()
        pttc_layout.setContentsMargins(0, 15, 0, 0)
        
        pttc_label = QLabel("TOTAL TOUTES TAXES COMPRISES (PTTC)")
        pttc_label.setStyleSheet("""
            color: rgba(255,255,255,0.8);
            font-size: 13px;
            font-weight: 600;
            background: transparent;
        """)
        
        pttc_value = QLabel(f"{pttc:,.0f}".replace(",", " "))
        pttc_value.setStyleSheet("""
            color: #fbbf24;
            font-size: 28px;
            font-weight: 800;
            background: transparent;
        """)
        
        pttc_currency = QLabel("FCFA")
        pttc_currency.setStyleSheet("""
            color: rgba(255,255,255,0.6);
            font-size: 14px;
            background: transparent;
        """)
        
        pttc_layout.addWidget(pttc_label)
        pttc_layout.addStretch()
        pttc_layout.addWidget(pttc_value)
        pttc_layout.addWidget(pttc_currency)
        
        main_layout.addLayout(pttc_layout)
        
        # ========== LIGNE 5: SECTION VALIDATION PAIEMENT ==========
        validation_frame = QFrame()
        validation_frame.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.1);
                border-radius: 16px;
                margin-top: 15px;
            }
        """)
        validation_layout = QVBoxLayout(validation_frame)
        validation_layout.setContentsMargins(20, 15, 20, 15)
        validation_layout.setSpacing(12)
        
        # Titre validation
        validation_title = QLabel("✅ VALIDATION DU PAIEMENT")
        validation_title.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 1px;
            background: transparent;
        """)
        validation_layout.addWidget(validation_title)
        
        # Mode de paiement
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(15)
        
        mode_label = QLabel("Mode de paiement :")
        mode_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px; background: transparent;")
        
        self.payment_mode = QComboBox()
        self.payment_mode.addItems([
            "Espèces",
            "Carte bancaire", 
            "Virement",
            "Chèque",
            "Orange Money",
            "MTN Mobile Money",
            "Wave",
            "Dépôt bancaire"
        ])
        self.payment_mode.setStyleSheet("""
            QComboBox {
                background: white;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 140px;
            }
        """)
        
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.payment_mode)
        mode_layout.addStretch()
        validation_layout.addLayout(mode_layout)
        
        # Montant versé
        montant_layout = QHBoxLayout()
        montant_layout.setSpacing(15)
        
        montant_label = QLabel("Montant versé :")
        montant_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px; background: transparent;")
        
        self.montant_verse = QLineEdit()
        self.montant_verse.setPlaceholderText("0")
        self.montant_verse.setStyleSheet("""
            QLineEdit {
                background: white;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 150px;
            }
        """)
        self.montant_verse.textChanged.connect(self.update_balance)
        
        montant_layout.addWidget(montant_label)
        montant_layout.addWidget(self.montant_verse)
        montant_layout.addStretch()
        validation_layout.addLayout(montant_layout)
        
        # Solde restant
        solde_layout = QHBoxLayout()
        solde_layout.setSpacing(15)
        
        solde_label = QLabel("Solde restant :")
        solde_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px; background: transparent;")
        
        self.solde_restant = QLineEdit()
        self.solde_restant.setReadOnly(True)
        self.solde_restant.setPlaceholderText("0")
        self.solde_restant.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.2);
                color: #fbbf24;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-width: 150px;
            }
        """)
        
        solde_layout.addWidget(solde_label)
        solde_layout.addWidget(self.solde_restant)
        solde_layout.addStretch()
        validation_layout.addLayout(solde_layout)
        
        # Statut du paiement
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        
        self.payment_status = QLabel("⏳ En attente de paiement")
        self.payment_status.setStyleSheet("""
            QLabel {
                color: #fbbf24;
                font-size: 12px;
                font-weight: 600;
                background: rgba(0,0,0,0.2);
                padding: 5px 12px;
                border-radius: 20px;
            }
        """)
        
        status_layout.addWidget(self.payment_status)
        status_layout.addStretch()
        validation_layout.addLayout(status_layout)
        
        # Bouton de validation
        btn_validate = QPushButton("✓ VALIDER LE PAIEMENT")
        btn_validate.setCursor(Qt.PointingHandCursor)
        btn_validate.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                font-weight: 700;
                margin-top: 5px;
            }
            QPushButton:hover {
                background: #059669;
            }
            QPushButton:pressed {
                padding-top: 13px;
                padding-bottom: 11px;
            }
        """)
        btn_validate.clicked.connect(self.validate_payment)
        validation_layout.addWidget(btn_validate)
        
        main_layout.addWidget(validation_frame)
        
        return recap_frame

    def create_detail_row(self, label, value, color="#ffffff", suffix="", bold=False):
        """Crée une ligne de détail pour le récapitulatif"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet(f"""
            color: rgba(255,255,255,0.7);
            font-size: 12px;
            background: transparent;
        """)
        
        value_lbl = QLabel(f"{value} FCFA {suffix}")
        font_weight = "bold" if bold else "normal"
        value_lbl.setStyleSheet(f"""
            color: {color};
            font-size: 13px;
            font-weight: {font_weight};
            background: transparent;
        """)
        
        layout.addWidget(label_lbl)
        layout.addStretch()
        layout.addWidget(value_lbl)
        
        return layout

    def create_frais_row(self, label, value):
        """Crée une ligne de frais pour la grille"""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet("""
            color: rgba(255,255,255,0.6);
            font-size: 11px;
            background: transparent;
        """)
        
        value_lbl = QLabel(f"{value:,.0f}".replace(",", " "))
        value_lbl.setStyleSheet("""
            color: rgba(255,255,255,0.9);
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)
        
        layout.addWidget(label_lbl)
        layout.addStretch()
        layout.addWidget(value_lbl)
        
        return layout

    def update_balance(self):
        """Met à jour le solde restant en fonction du montant versé"""
        try:
            prime_nette = float(self.data.get('prime_nette', 0))
            montant_verse = float(self.montant_verse.text().replace(" ", "").replace(",", ".") or 0)
            
            solde = prime_nette - montant_verse
            
            if solde <= 0:
                self.solde_restant.setText("0")
                self.payment_status.setText("✅ Paiement complété")
                self.payment_status.setStyleSheet("""
                    QLabel {
                        color: #10b981;
                        font-size: 12px;
                        font-weight: 600;
                        background: rgba(0,0,0,0.2);
                        padding: 5px 12px;
                        border-radius: 20px;
                    }
                """)
            else:
                self.solde_restant.setText(f"{solde:,.0f}".replace(",", " "))
                self.payment_status.setText("⏳ Paiement partiel")
                self.payment_status.setStyleSheet("""
                    QLabel {
                        color: #fbbf24;
                        font-size: 12px;
                        font-weight: 600;
                        background: rgba(0,0,0,0.2);
                        padding: 5px 12px;
                        border-radius: 20px;
                    }
                """)
                
        except ValueError:
            self.solde_restant.setText("0")

    def validate_payment(self):
        """Valide le paiement et enregistre la transaction"""
        montant_verse = float(self.montant_verse.text().replace(" ", "").replace(",", ".") or 0)
        prime_nette = float(self.data.get('prime_nette', 0))
        mode = self.payment_mode.currentText()
        
        if montant_verse <= 0:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir un montant valide")
            return
        
        if montant_verse < prime_nette:
            reply = QMessageBox.question(
                self,
                "Paiement partiel",
                f"Le montant versé ({montant_verse:,.0f} FCFA) est inférieur à la prime nette ({prime_nette:,.0f} FCFA).\n\nSouhaitez-vous continuer ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Ici, vous pouvez ajouter la logique d'enregistrement du paiement
        QMessageBox.information(
            self,
            "Paiement validé",
            f"Paiement de {montant_verse:,.0f} FCFA effectué par {mode}\n\nSolde restant : {max(0, prime_nette - montant_verse):,.0f} FCFA"
        )

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
        """Crée une section de statistiques professionnelle de type tableau de bord"""
        
        # Conteneur principal avec ombre portée
        stats_card = QFrame()
        stats_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid #e9eef3;
            }
        """)
        
        # Ajouter une ombre (simulée avec un padding)
        main_layout = QVBoxLayout(stats_card)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # ========== EN-TÊTE PROFESSIONNEL ==========
        header = self.create_professional_header()
        main_layout.addWidget(header)
        
        # ========== KPI CARDS (4 cartes clés) ==========
        kpi_layout = self.create_kpi_cards()
        main_layout.addLayout(kpi_layout)
        
        # ========== SECTION ANALYSE DOUBLE ==========
        analytics_row = QHBoxLayout()
        analytics_row.setSpacing(20)
        
        # Graphique d'évolution
        chart_widget = self.create_professional_chart()
        analytics_row.addWidget(chart_widget, 2)
        
        # Indicateurs de risque
        risk_widget = self.create_professional_risk_panel()
        analytics_row.addWidget(risk_widget, 1)
        
        main_layout.addLayout(analytics_row)
        
        # ========== TABLEAU DES PERFORMANCES ==========
        performance_table = self.create_performance_table()
        main_layout.addWidget(performance_table)
        
        return stats_card

    def create_professional_header(self):
        """Crée un en-tête professionnel avec métriques clés"""
        
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
                padding: 16px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Titre section
        title_section = QVBoxLayout()
        title = QLabel("ANALYSE DE PERFORMANCE")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: 0.5px;
        """)
        
        subtitle = QLabel("Indicateurs clés et tendances du contrat")
        subtitle.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
        """)
        
        title_section.addWidget(title)
        title_section.addWidget(subtitle)
        
        # Métriques rapides
        metrics = QHBoxLayout()
        metrics.setSpacing(24)
        
        prime = float(self.data.get('prime_nette', 0))
        metrics.addWidget(self.create_metric_pill("Prime mensuelle", f"{prime/12:,.0f}".replace(",", " "), "FCFA"))
        
        sinistres = int(self.data.get('sinistres', 0))
        metrics.addWidget(self.create_metric_pill("Sinistres/An", f"{sinistres/max(1, self.get_years_count()):.1f}", "ratio"))
        
        bonus = self.calculate_bonus_malus()
        metrics.addWidget(self.create_metric_pill("Bonus/Malus", f"{bonus}%", "niveau"))
        
        layout.addLayout(title_section)
        layout.addStretch()
        layout.addLayout(metrics)
        
        return header

    def create_metric_pill(self, label, value, unit):
        """Crée une pastille métrique compacte"""
        
        pill = QFrame()
        pill.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 8px 16px;
            }
        """)
        
        layout = QVBoxLayout(pill)
        layout.setSpacing(4)
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet("""
            font-size: 10px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
        """)
        
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("""
            font-size: 18px;
            font-weight: 800;
            color: #0f172a;
        """)
        
        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet("""
            font-size: 9px;
            color: #94a3b8;
        """)
        
        layout.addWidget(label_lbl)
        value_layout = QHBoxLayout()
        value_layout.addWidget(value_lbl)
        value_layout.addWidget(unit_lbl)
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        return pill

    def create_kpi_cards(self):
        """Crée 4 cartes KPI principales"""
        
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        
        # KPI 1 : Prime nette
        prime = float(self.data.get('prime_nette', 0))
        kpi1 = self.create_kpi_card(
            title="PRIME NETTE",
            value=f"{prime:,.0f}".replace(",", " "),
            subtitle="FCFA / an",
            icon="💰",
            trend=self.calculate_trend(),
            color="#3b82f6"
        )
        kpi_layout.addWidget(kpi1)
        
        # KPI 2 : Sinistralité
        sinistres = int(self.data.get('sinistres', 0))
        years = max(1, self.get_years_count())
        frequency = sinistres / years
        kpi2 = self.create_kpi_card(
            title="SINISTRALITÉ",
            value=f"{frequency:.2f}",
            subtitle="sinistres / an",
            icon="⚠️",
            trend=self.get_claim_trend_text(),
            color="#ef4444" if frequency > 0.5 else "#10b981"
        )
        kpi_layout.addWidget(kpi2)
        
        # KPI 3 : Bonus/Malus
        bonus = self.calculate_bonus_malus()
        kpi3 = self.create_kpi_card(
            title="BONUS / MALUS",
            value=f"{bonus}%",
            subtitle="coefficient",
            icon="🎯",
            trend=self.get_bonus_trend_text(),
            color="#10b981" if bonus < 100 else "#ef4444" if bonus > 100 else "#f59e0b"
        )
        kpi_layout.addWidget(kpi3)
        
        # KPI 4 : Ancienneté
        anciennete = self.get_years_count()
        kpi4 = self.create_kpi_card(
            title="ANCIENNETÉ",
            value=f"{anciennete}",
            subtitle="années",
            icon="📅",
            trend=f"+{anciennete * 12} mois",
            color="#8b5cf6"
        )
        kpi_layout.addWidget(kpi4)
        
        return kpi_layout

    def create_kpi_card(self, title, value, subtitle, icon, trend, color):
        """Crée une carte KPI professionnelle"""
        
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }}
            QFrame:hover {{
                border-color: {color};
                background: #fafcff;
            }}
        """)
        card.setMinimumHeight(130)
        card.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # Ligne 1 : Icône + Titre + Tendance
        header_layout = QHBoxLayout()
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 20px;")
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            font-size: 11px;
            font-weight: 700;
            color: #64748b;
            letter-spacing: 0.5px;
        """)
        
        trend_lbl = QLabel(trend)
        trend_color = "#10b981" if "▲" in trend else "#ef4444" if "▼" in trend else "#64748b"
        trend_lbl.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {trend_color};
        """)
        
        header_layout.addWidget(icon_lbl)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(trend_lbl)
        
        # Ligne 2 : Valeur principale
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 800;
            color: {color};
        """)
        
        # Ligne 3 : Subtitle
        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setStyleSheet("""
            font-size: 10px;
            color: #94a3b8;
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(value_lbl)
        layout.addWidget(subtitle_lbl)
        
        return card

    def create_professional_chart(self):
        """Crée un graphique professionnel avec zone et tendance"""
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # En-tête
        header_layout = QHBoxLayout()
        chart_title = QLabel("ÉVOLUTION DES PRIMES")
        chart_title.setStyleSheet("""
            font-size: 12px;
            font-weight: 700;
            color: #1e293b;
            letter-spacing: 0.5px;
        """)
        
        # Légende
        legend = QHBoxLayout()
        legend.setSpacing(16)
        legend.addWidget(self.create_legend_item("Année en cours", "#3b82f6"))
        legend.addWidget(self.create_legend_item("Projection", "#94a3b8"))
        
        header_layout.addWidget(chart_title)
        header_layout.addStretch()
        header_layout.addLayout(legend)
        layout.addLayout(header_layout)
        
        # Graphique
        chart_widget = self.create_professional_bars()
        layout.addWidget(chart_widget)
        
        # Statistiques
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        prime_actuelle = float(self.data.get('prime_nette', 0))
        prime_2024 = 138000
        
        evolution = ((prime_actuelle - prime_2024) / prime_2024) * 100
        evolution_text = f"{evolution:+.1f}% vs N-1"
        evolution_color = "#10b981" if evolution > 0 else "#ef4444"
        
        stats_layout.addWidget(self.create_stat_badge("Évolution", evolution_text, evolution_color))
        stats_layout.addWidget(self.create_stat_badge("Moyenne 3 ans", f"{self.calculate_3year_average():,.0f}".replace(",", " "), "#8b5cf6"))
        stats_layout.addWidget(self.create_stat_badge("Projection N+1", f"{int(prime_actuelle * 1.08):,.0f}".replace(",", " "), "#f59e0b"))
        
        layout.addLayout(stats_layout)
        
        return card

    def create_professional_bars(self):
        """Crée les barres du graphique professionnel"""
        
        widget = QFrame()
        widget.setFixedHeight(180)
        
        layout = QHBoxLayout(widget)
        layout.setSpacing(24)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Données
        years = [2021, 2022, 2023, 2024, 2025]
        historical = [95000, 112000, 125000, 138000]
        current = int(self.data.get('prime_nette', 150000))
        projection = int(current * 1.08)
        
        values = [95000, 112000, 125000, 138000, current]
        max_value = max(values + [projection])
        
        for i, (year, value) in enumerate(zip(years, values)):
            is_projection = (year == 2025)
            
            bar_container = QWidget()
            bar_layout = QVBoxLayout(bar_container)
            bar_layout.setSpacing(8)
            bar_layout.setAlignment(Qt.AlignBottom)
            
            # Hauteur de la barre
            height = max(50, int((value / max_value) * 120))
            
            # Barre
            bar = QFrame()
            bar.setFixedSize(48, height)
            
            if is_projection:
                bar.setStyleSheet("""
                    QFrame {
                        background: #e2e8f0;
                        border-radius: 8px;
                        border: 1px dashed #94a3b8;
                    }
                """)
            else:
                bar.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                            stop:0 #3b82f6, stop:1 #60a5fa);
                        border-radius: 8px;
                    }
                """)
            
            # Valeur
            value_lbl = QLabel(f"{value/1000:.0f}k")
            value_lbl.setStyleSheet("""
                font-size: 11px;
                font-weight: 600;
                color: #475569;
            """)
            value_lbl.setAlignment(Qt.AlignCenter)
            
            # Année
            year_lbl = QLabel(str(year))
            year_lbl.setStyleSheet("""
                font-size: 11px;
                font-weight: 600;
                color: #64748b;
            """)
            year_lbl.setAlignment(Qt.AlignCenter)
            
            bar_layout.addStretch()
            bar_layout.addWidget(bar)
            bar_layout.addWidget(value_lbl)
            bar_layout.addWidget(year_lbl)
            
            layout.addWidget(bar_container)
            
            if i < len(years) - 1:
                layout.addStretch()
        
        return widget

    def create_professional_risk_panel(self):
        """Crée un panneau d'analyse de risque professionnel"""
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Titre
        title = QLabel("ANALYSE DE RISQUE")
        title.setStyleSheet("""
            font-size: 12px;
            font-weight: 700;
            color: #1e293b;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(title)
        
        # Score de risque global
        sinistres = int(self.data.get('sinistres', 0))
        risk_score = min(100, sinistres * 25)
        risk_level = "Faible" if risk_score < 30 else "Modéré" if risk_score < 70 else "Élevé"
        risk_color = "#10b981" if risk_score < 30 else "#f59e0b" if risk_score < 70 else "#ef4444"
        
        score_container = QFrame()
        score_container.setStyleSheet(f"""
            QFrame {{
                background: {risk_color}10;
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        score_layout = QHBoxLayout(score_container)
        
        score_value = QLabel(f"{risk_score}%")
        score_value.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 800;
            color: {risk_color};
        """)
        
        score_text = QLabel(f"Niveau de risque {risk_level}")
        score_text.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {risk_color};
        """)
        
        score_layout.addWidget(score_value)
        score_layout.addSpacing(12)
        score_layout.addWidget(score_text)
        score_layout.addStretch()
        layout.addWidget(score_container)
        
        # Facteurs de risque
        factors = self.get_risk_factors()
        for factor in factors:
            factor_widget = self.create_risk_factor_row(factor)
            layout.addWidget(factor_widget)
        
        # Bouton d'analyse
        analyze_btn = QPushButton("ANALYSE DÉTAILLÉE →")
        analyze_btn.setCursor(Qt.PointingHandCursor)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background: #1e293b;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 11px;
                font-weight: 600;
                margin-top: 8px;
            }
            QPushButton:hover {
                background: #334155;
            }
        """)
        layout.addWidget(analyze_btn)
        
        return card

    def create_risk_factor_row(self, factor):
        """Crée une ligne de facteur de risque"""
        
        row = QFrame()
        row.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 8, 12, 8)
        
        icon = QLabel(factor['icon'])
        icon.setStyleSheet("font-size: 14px;")
        
        label = QLabel(factor['label'])
        label.setStyleSheet("""
            font-size: 11px;
            font-weight: 500;
            color: #475569;
        """)
        
        value = QLabel(factor['value'])
        value.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {factor['color']};
        """)
        
        layout.addWidget(icon)
        layout.addSpacing(8)
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(value)
        
        return row

    def create_performance_table(self):
        """Crée un tableau de performance détaillé"""
        
        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(table_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Titre
        title = QLabel("INDICATEURS DE PERFORMANCE")
        title.setStyleSheet("""
            font-size: 12px;
            font-weight: 700;
            color: #1e293b;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(title)
        
        # Tableau
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Indicateur", "Valeur", "Statut"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                border: none;
                background: transparent;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border: none;
            }
            QHeaderView::section {
                background: #f8fafc;
                color: #64748b;
                font-size: 11px;
                font-weight: 600;
                padding: 12px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        
        # Données du tableau
        prime = float(self.data.get('prime_nette', 0))
        prime_brute = float(self.data.get('prime_brute', 0))
        reduction = prime_brute - prime
        reduction_percent = (reduction / prime_brute * 100) if prime_brute > 0 else 0
        
        performances = [
            ("Taux de réduction", f"{reduction_percent:.1f}%", "Excellent" if reduction_percent > 15 else "Bon" if reduction_percent > 5 else "Standard"),
            ("Ratio sinistre/prime", self.calculate_loss_ratio(), self.get_loss_ratio_status()),
            ("Efficacité couverture", f"{self.calculate_coverage_rate()}%", "Optimal" if self.calculate_coverage_rate() > 80 else "Correct" if self.calculate_coverage_rate() > 60 else "À améliorer"),
            ("Rentabilité client", self.calculate_client_profitability(), self.get_profitability_status()),
        ]
        
        for row, (indicator, value, status) in enumerate(performances):
            table.insertRow(row)
            
            # Indicateur
            item_indicator = QTableWidgetItem(indicator)
            item_indicator.setFont(QFont("Segoe UI", 10))
            table.setItem(row, 0, item_indicator)
            
            # Valeur
            item_value = QTableWidgetItem(str(value))
            item_value.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
            table.setItem(row, 1, item_value)
            
            # Statut avec badge
            status_color = "#10b981" if "Excellent" in status or "Optimal" in status else "#f59e0b" if "Bon" in status or "Correct" in status else "#ef4444"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(status_color))
            status_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            table.setItem(row, 2, status_item)
        
        table.setFixedHeight(200)
        layout.addWidget(table)
        
        return table_card

    # ========== MÉTHODES UTILITAIRES ==========

    def get_claim_trend_text(self):
        """Retourne le texte de tendance des sinistres"""
        sinistres = int(self.data.get('sinistres', 0))
        if sinistres == 0:
            return "▼ En baisse"
        elif sinistres == 1:
            return "► Stable"
        else:
            return "▲ En hausse"

    def get_bonus_trend_text(self):
        """Retourne le texte de tendance du bonus"""
        bonus = self.calculate_bonus_malus()
        if bonus < 100:
            return "▼ Bonus"
        elif bonus > 100:
            return "▲ Malus"
        else:
            return "► Neutre"

    def calculate_3year_average(self):
        """Calcule la moyenne sur 3 ans"""
        values = [95000, 112000, 125000, 138000]
        return sum(values[-3:]) / 3

    def calculate_loss_ratio(self):
        """Calcule le ratio sinistre/prime"""
        sinistres = int(self.data.get('sinistres', 0))
        prime = float(self.data.get('prime_nette', 1))
        # Simulation de montant moyen de sinistre
        avg_claim = 50000 * sinistres
        ratio = (avg_claim / prime) * 100
        return f"{ratio:.1f}%"

    def get_loss_ratio_status(self):
        """Statut du ratio sinistre/prime"""
        sinistres = int(self.data.get('sinistres', 0))
        if sinistres == 0:
            return "Excellent"
        elif sinistres == 1:
            return "Bon"
        else:
            return "À surveiller"

    def calculate_client_profitability(self):
        """Calcule la rentabilité client"""
        sinistres = int(self.data.get('sinistres', 0))
        if sinistres == 0:
            return "Très bonne"
        elif sinistres == 1:
            return "Moyenne"
        else:
            return "Faible"

    def get_profitability_status(self):
        """Statut de rentabilité"""
        sinistres = int(self.data.get('sinistres', 0))
        if sinistres == 0:
            return "Optimal"
        elif sinistres == 1:
            return "Correct"
        else:
            return "Critique"

    def create_legend_item(self, text, color):
        """Crée un élément de légende"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 4px;
            }}
        """)
        
        label = QLabel(text)
        label.setStyleSheet("font-size: 10px; color: #64748b;")
        
        layout.addWidget(dot)
        layout.addWidget(label)
        
        return widget

    def create_stat_badge(self, label, value, color):
        """Crée un badge statistique"""
        badge = QFrame()
        badge.setStyleSheet(f"""
            QFrame {{
                background: {color}10;
                border-radius: 8px;
                padding: 6px 12px;
            }}
        """)
        
        layout = QHBoxLayout(badge)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet("font-size: 9px; color: #64748b;")
        
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {color};")
        
        layout.addWidget(label_lbl)
        layout.addWidget(value_lbl)
        
        return badge

    def get_risk_factors(self):
        """Retourne les facteurs de risque analysés"""
        factors = []
        sinistres = int(self.data.get('sinistres', 0))
        years = self.get_years_count()
        
        if sinistres > 0:
            factors.append({
                "icon": "⚠️",
                "label": "Antécédent sinistre",
                "value": f"{sinistres} déclaration(s)",
                "color": "#ef4444"
            })
        
        if years < 2:
            factors.append({
                "icon": "🆕",
                "label": "Ancienneté faible",
                "value": "Période probatoire",
                "color": "#f59e0b"
            })
        
        coverage = self.calculate_coverage_rate()
        if coverage < 70:
            factors.append({
                "icon": "🛡️",
                "label": "Couverture partielle",
                "value": f"{coverage}% des risques",
                "color": "#f59e0b"
            })
        
        if len(factors) == 0:
            factors.append({
                "icon": "✅",
                "label": "Profil à risque faible",
                "value": "Excellent dossier",
                "color": "#10b981"
            })
        
        return factors

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
    
    def calculate_coverage_rate(self):
        """Calcule le taux de couverture des garanties"""
        garanties = ['amt_rc', 'amt_dr', 'amt_vol', 'amt_in', 'amt_bris', 'amt_ar', 'amt_dta']
        total_garanties = 0
        for g in garanties:
            try:
                if float(self.data.get(g, 0)) > 0:
                    total_garanties += 1
            except (ValueError, TypeError):
                pass
        return int((total_garanties / len(garanties)) * 100) if garanties else 0

    def calculate_protection_index(self):
        """Calcule l'indice de protection"""
        base_score = 50
        try:
            bonus = self.calculate_bonus_malus()
            coverage = self.calculate_coverage_rate()
            # Bonus favorable réduit le risque
            bonus_factor = (100 - bonus) * 0.3 if bonus < 100 else 0
            # Meilleure couverture = meilleure protection
            coverage_factor = coverage * 0.2
            score = base_score + bonus_factor + coverage_factor
            return min(100, max(0, int(score)))
        except:
            return base_score

    def calculate_trend(self):
        """Calcule la tendance d'évolution"""
        try:
            prime_actuelle = float(self.data.get('prime_nette', 0))
            prime_2024 = 138000  # Valeur historique
            
            if prime_actuelle > prime_2024:
                variation = ((prime_actuelle - prime_2024) / prime_2024) * 100
                return f"▲ +{variation:.1f}%"
            elif prime_actuelle < prime_2024:
                variation = ((prime_2024 - prime_actuelle) / prime_2024) * 100
                return f"▼ -{variation:.1f}%"
            else:
                return "► Stable"
        except:
            return "► Stable"

    def get_claim_trend_text(self):
        """Retourne le texte de tendance des sinistres"""
        try:
            sinistres = int(self.data.get('sinistres', 0))
            if sinistres == 0:
                return "▼ En baisse"
            elif sinistres == 1:
                return "► Stable"
            else:
                return "▲ En hausse"
        except:
            return "► Stable"

    def get_bonus_trend_text(self):
        """Retourne le texte de tendance du bonus"""
        try:
            bonus = self.calculate_bonus_malus()
            if bonus < 100:
                return "▼ Bonus"
            elif bonus > 100:
                return "▲ Malus"
            else:
                return "► Neutre"
        except:
            return "► Neutre"

    def calculate_3year_average(self):
        """Calcule la moyenne sur 3 ans"""
        try:
            # Valeurs historiques (à adapter selon vos données réelles)
            values = [95000, 112000, 125000, 138000]
            return sum(values[-3:]) / 3
        except:
            prime = float(self.data.get('prime_nette', 0))
            return prime

    def calculate_loss_ratio(self):
        """Calcule le ratio sinistre/prime"""
        try:
            sinistres = int(self.data.get('sinistres', 0))
            prime = float(self.data.get('prime_nette', 1))
            # Simulation de montant moyen de sinistre (à adapter)
            avg_claim = 50000 * sinistres
            ratio = (avg_claim / prime) * 100 if prime > 0 else 0
            return f"{ratio:.1f}%"
        except:
            return "0%"

    def get_loss_ratio_status(self):
        """Statut du ratio sinistre/prime"""
        try:
            sinistres = int(self.data.get('sinistres', 0))
            if sinistres == 0:
                return "Excellent"
            elif sinistres == 1:
                return "Bon"
            else:
                return "À surveiller"
        except:
            return "Standard"

    def calculate_client_profitability(self):
        """Calcule la rentabilité client"""
        try:
            sinistres = int(self.data.get('sinistres', 0))
            if sinistres == 0:
                return "Très bonne"
            elif sinistres == 1:
                return "Moyenne"
            else:
                return "Faible"
        except:
            return "Standard"

    def get_profitability_status(self):
        """Statut de rentabilité"""
        try:
            sinistres = int(self.data.get('sinistres', 0))
            if sinistres == 0:
                return "Optimal"
            elif sinistres == 1:
                return "Correct"
            else:
                return "Critique"
        except:
            return "Standard"

    def get_risk_factors(self):
        """Retourne les facteurs de risque analysés"""
        factors = []
        try:
            sinistres = int(self.data.get('sinistres', 0))
            years = self.get_years_count()
            
            if sinistres > 0:
                factors.append({
                    "icon": "⚠️",
                    "label": "Antécédent sinistre",
                    "value": f"{sinistres} déclaration(s)",
                    "color": "#ef4444"
                })
            
            if years < 2:
                factors.append({
                    "icon": "🆕",
                    "label": "Ancienneté faible",
                    "value": "Période probatoire",
                    "color": "#f59e0b"
                })
            
            coverage = self.calculate_coverage_rate()
            if coverage < 70:
                factors.append({
                    "icon": "🛡️",
                    "label": "Couverture partielle",
                    "value": f"{coverage}% des risques",
                    "color": "#f59e0b"
                })
            
            if len(factors) == 0:
                factors.append({
                    "icon": "✅",
                    "label": "Profil à risque faible",
                    "value": "Excellent dossier",
                    "color": "#10b981"
                })
        except:
            factors.append({
                "icon": "ℹ️",
                "label": "Analyse non disponible",
                "value": "Données insuffisantes",
                "color": "#64748b"
            })
        
        return factors

    def create_legend_item(self, text, color):
        """Crée un élément de légende"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 4px;
            }}
        """)
        
        label = QLabel(text)
        label.setStyleSheet("font-size: 10px; color: #64748b;")
        
        layout.addWidget(dot)
        layout.addWidget(label)
        
        return widget

    def create_stat_badge(self, label, value, color):
        """Crée un badge statistique"""
        badge = QFrame()
        badge.setStyleSheet(f"""
            QFrame {{
                background: {color}10;
                border-radius: 8px;
                padding: 6px 12px;
            }}
        """)
        
        layout = QHBoxLayout(badge)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet("font-size: 9px; color: #64748b;")
        
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {color};")
        
        layout.addWidget(label_lbl)
        layout.addWidget(value_lbl)
        
        return badge