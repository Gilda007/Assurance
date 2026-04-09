from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QScrollArea, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
                             QComboBox, QMessageBox)
from PySide6.QtCore import Qt
import qrcode
from io import BytesIO
from PySide6.QtGui import QFont, QColor, QPixmap


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
        font-weight: 900;
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
    
    /* Tab Widget */
    QTabWidget::pane {
        border: none;
        background: transparent;
    }
    
    QTabBar::tab {
        background: #f1f5f9;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        margin: 0 4px;
        font-weight: 600;
        font-size: 13px;
    }
    
    QTabBar::tab:selected {
        background: #3b82f6;
        color: white;
    }
    
    QTabBar::tab:hover {
        background: #e2e8f0;
    }
    
    /* ComboBox */
    QComboBox {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        min-width: 140px;
    }
    
    QComboBox:hover {
        border-color: #cbd5e1;
    }
    
    QComboBox:focus {
        border-color: #3b82f6;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    /* LineEdit */
    QLineEdit {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }
    
    QLineEdit:focus {
        border-color: #3b82f6;
    }
    
    QLineEdit:read-only {
        background: #f8fafc;
        color: #64748b;
    }
    
    /* PushButton général */
    QPushButton {
        background: #f1f5f9;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 13px;
    }
    
    QPushButton:hover {
        background: #e2e8f0;
    }
    
    QPushButton:pressed {
        background: #cbd5e1;
    }
    
    /* ScrollArea */
    QScrollArea {
        border: none;
        background: transparent;
    }
    
    /* Frame général */
    QFrame {
        background: transparent;
    }
    
    /* ToolTip */
    QToolTip {
        background: #1e293b;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
    }
"""

class VehicleDetailView(QWidget):
    def __init__(self, vehicle_data, controller=None, db_session=None):
        super().__init__()
        self.data = vehicle_data
        self.controller = controller
        self.db_session = db_session
        print(self.db_session)  # Debug: vérifier que la session est bien passée
        self.setStyleSheet(MODERN_STYLE)
        self.setMinimumSize(1100, 800)

        # === INITIALISATION DE TOUS LES ATTRIBUTS PAR DÉFAUT ===
        self.doc_buttons = {}  
        self.print_buttons = {}
        self.action_buttons = {}
        
        # Attributs pour les contrôleurs
        self.contract_ctrl = None
        self.payment_ctrl = None
        
        # Attributs pour les données financières (initialisés par défaut)
        self.contract_data = None
        self.payment_history = []      # ← IMPORTANT: initialisé à liste vide
        self.payment_schedule = []     # ← IMPORTANT: initialisé à liste vide
        
        # Attributs pour l'UI des paiements
        self.payment_mode = None
        self.montant_verse = None
        self.solde_restant = None
        self.payment_status = None
        
        # Initialiser les contrôleurs
        self._init_controllers()
        
        # Configurer l'interface
        self.setup_ui()

    def _init_controllers(self):
        """Initialise les contrôleurs pour la gestion des contrats et paiements"""
        try:
            # Vérifier si le contrôleur principal existe et a les attributs requis
            if self.controller:
                if hasattr(self.controller, 'contracts'):
                    self.contract_ctrl = self.controller.contracts
                    print("✓ Contract controller initialisé")
                else:
                    print("⚠️ Pas de contracts dans controller")
                
                if hasattr(self.controller, 'paiements'):
                    self.payment_ctrl = self.controller.paiements
                    print("✓ Payment controller initialisé")
                else:
                    print("⚠️ Pas de paiements dans controller")
            else:
                print("⚠️ Controller principal est None")
            
            # Charger les données du contrat pour ce véhicule
            self._load_contract_data()
            
        except Exception as e:
            print(f"Erreur initialisation contrôleurs: {e}")
            import traceback
            traceback.print_exc()
            self.contract_ctrl = None
            self.payment_ctrl = None
            self.contract_data = None
            self.payment_history = []
            self.payment_schedule = []

    def _load_contract_data(self):
        """Charge les données du contrat pour le véhicule actuel"""
        print(f"=== _load_contract_data ===")
        print(self.db_session)  # Debug: vérifier que la session est accessible
        
        # Initialiser par défaut
        self.contract_data = None
        self.payment_history = []
        self.payment_schedule = []
        
        if not self.data:
            print("self.data est None ou vide")
            return
        
        # Récupérer l'ID du véhicule
        vehicle_id = self.data.get('id')
        
        # Si l'ID n'est pas trouvé, chercher dans d'autres clés
        if not vehicle_id and isinstance(self.data, dict):
            for key in ['vehicle_id', 'vehicule_id', 'vehiculeId', 'id_vehicule']:
                if key in self.data:
                    vehicle_id = self.data[key]
                    print(f"ID trouvé via clé '{key}': {vehicle_id}")
                    break
        
        # Si toujours pas d'ID, essayer depuis l'objet
        if not vehicle_id and hasattr(self.data, 'id'):
            vehicle_id = self.data.id
            print(f"ID récupéré depuis l'attribut id: {vehicle_id}")
        
        print(f"vehicle_id final: {vehicle_id}")
        
        if not vehicle_id:
            print("❌ Impossible de trouver l'ID du véhicule")
            print(f"Clés disponibles: {list(self.data.keys()) if isinstance(self.data, dict) else 'non-dict'}")
            return
        
        if not self.contract_ctrl:
            print("❌ contract_ctrl est None")
            return
        
        try:
            # Nettoyer l'état de la session si possible
            if hasattr(self.contract_ctrl, 'session'):
                self.contract_ctrl.session.rollback()
            
            print(f"Recherche contrat pour vehicle_id: {vehicle_id}")
            
            # Chercher le contrat par véhicule
            contrat = self.contract_ctrl.get_contract_by_vehicle(vehicle_id)
            
            if contrat:
                print(f"✓ Contrat trouvé: {contrat.id}")
                
                # Construire contract_data
                self.contract_data = {
                    'amounts': {
                        'prime_totale_ttc': contrat.prime_totale_ttc,
                        'prime_pure': contrat.prime_pure,
                        'discount': 0,
                    },
                    'payment': {
                        'montant_paye': contrat.montant_paye,
                        'reste_a_payer': contrat.prime_totale_ttc - contrat.montant_paye,
                        'statut': contrat.statut_paiement,
                        'statut_label': self._get_payment_status_label(contrat.statut_paiement)
                    },
                    'contract': {
                        'id': contrat.id,
                        'numero_police': contrat.numero_police,
                        'statut': getattr(contrat, 'statut', 'ACTIF')
                    }
                }
                
                # Récupérer l'historique des paiements si disponible
                if self.payment_ctrl and hasattr(self.payment_ctrl, 'get_payments_by_contract'):
                    try:
                        payments = self.payment_ctrl.get_payments_by_contract(contrat.id)
                        self.payment_history = payments if payments else []
                        print(f"✓ {len(self.payment_history)} paiements trouvés")
                    except Exception as e:
                        print(f"Erreur récupération paiements: {e}")
                        self.payment_history = []
                
                # Récupérer l'échéancier si disponible
                if self.payment_ctrl and hasattr(self.payment_ctrl, 'get_payment_schedule'):
                    try:
                        schedule = self.payment_ctrl.get_payment_schedule(contrat.id)
                        self.payment_schedule = schedule if schedule else []
                        print(f"✓ {len(self.payment_schedule)} échéances trouvées")
                    except Exception as e:
                        print(f"Erreur récupération échéancier: {e}")
                        self.payment_schedule = []
                        
            else:
                print(f"❌ Aucun contrat trouvé pour le véhicule {vehicle_id}")
                self.contract_data = None
                
        except Exception as e:
            print(f"Erreur _load_contract_data: {e}")
            import traceback
            traceback.print_exc()
            self.contract_data = None
            self.payment_history = []
            self.payment_schedule = []

    def _get_payment_status_label(self, status):
        """Retourne le libellé du statut de paiement"""
        labels = {
            'NON_PAYE': 'Non payé',
            'PARTIEL': 'Paiement partiel',
            'PAYE': 'Entièrement payé'
        }
        return labels.get(status, 'Inconnu')

    def _get_payment_status_label(self, status):
        """Retourne le libellé du statut de paiement"""
        labels = {
            'NON_PAYE': 'Non payé',
            'PARTIEL': 'Paiement partiel',
            'PAYE': 'Entièrement payé'
        }
        return labels.get(status, 'Inconnu')

    def refresh_financial_data(self):
        """Rafraîchit les données financières et met à jour l'affichage"""
        self._load_contract_data()
        
        # Reconstruire l'onglet finances si nécessaire
        if hasattr(self, 'tab_widget'):
            # Mettre à jour l'onglet existant
            index = self.tab_widget.indexOf(self.finances_tab)
            if index >= 0:
                self.tab_widget.removeTab(index)
            
            self.finances_tab = self.create_finances_tab()
            self.tab_widget.insertTab(2, self.finances_tab, "💰 Finances")

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 32)
        main_layout.setSpacing(24)

        # En-tête (reste en haut, commun à tous les onglets)
        main_layout.addWidget(self.create_header())

        # Création du TabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #f1f5f9;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                margin: 0 4px;
                font-weight: 600;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: #3b82f6;
                color: white;
            }
            QTabBar::tab:hover {
                background: #e2e8f0;
            }
        """)

        # Onglet 1: Informations générales
        self.tab_widget.addTab(self.create_info_tab(), "📋 Informations")

        # Onglet 2: Garanties & Primes
        self.tab_widget.addTab(self.create_garanties_tab(), "🛡️ Garanties")

        # Onglet 3: Finances & Paiement
        self.tab_widget.addTab(self.create_finances_tab(), "💰 Finances")

        # Onglet 4: Statistiques & Performance
        self.tab_widget.addTab(self.create_stats_tab(), "📊 Statistiques")

        # Onglet 5: Documents & Contacts
        self.tab_widget.addTab(self.create_documents_tab(), "📁 Documents")

        # Onglet 6: Historique & Échéances
        self.tab_widget.addTab(self.create_history_tab(), "📅 Historique")

        main_layout.addWidget(self.tab_widget)

    def create_info_tab(self):
        """Onglet des informations générales"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(24)

        # Carte d'informations détaillées
        layout.addWidget(self.create_info_card())
        
        # QR Code
        layout.addWidget(self.create_qrcode_section())
        
        layout.addStretch()
        return tab

    def create_garanties_tab(self):
        """Onglet des garanties"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(24)

        # Tableau des garanties
        layout.addWidget(self.create_garanties_table())
        
        layout.addStretch()
        return tab

    def get_years_count(self):
        """Retourne le nombre d'années d'assurance"""
        try:
            date_debut = self.data.get('date_debut')
            if date_debut and date_debut != 'N/A' and date_debut != '':
                from datetime import date
                if isinstance(date_debut, date):
                    years = date.today().year - date_debut.year
                    # Ajuster si l'anniversaire n'est pas encore passé
                    if date.today().month < date_debut.month or \
                    (date.today().month == date_debut.month and date.today().day < date_debut.day):
                        years -= 1
                    return max(0, years)
                elif isinstance(date_debut, str):
                    # Tenter de parser la date string
                    from datetime import datetime
                    try:
                        parsed_date = datetime.strptime(date_debut, "%Y-%m-%d").date()
                        years = date.today().year - parsed_date.year
                        if date.today().month < parsed_date.month or \
                        (date.today().month == parsed_date.month and date.today().day < parsed_date.day):
                            years -= 1
                        return max(0, years)
                    except:
                        pass
        except Exception as e:
            print(f"Erreur get_years_count: {e}")
        return 0

    def calculate_years_insured(self):
        """Calcule le nombre d'années d'assurance (version texte)"""
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
            if total >= 1_000_000:
                return f"{total/1_000_000:.1f}M FCFA"
            elif total >= 1_000:
                return f"{total/1_000:.0f}k FCFA"
            else:
                return f"{total:,.0f} FCFA".replace(",", " ")
        except:
            return "0 FCFA"

    def calculate_bonus_malus(self):
        """Calcule le bonus/malus (50% minimum, 150% maximum)"""
        try:
            sinistres = int(self.data.get('sinistres', 0))
            years = self.get_years_count()
            
            if years == 0:
                return 100
            
            # Bonus: 5% par an sans sinistre, max 50%
            bonus = min(50, years * 5) if sinistres == 0 else 0
            # Malus: 25% par sinistre, max 50%
            malus = min(50, sinistres * 25)
            # Calcul final entre 50% et 150%
            result = max(50, min(150, 100 - bonus + malus))
            
            return result
        except:
            return 100

    def calculate_coverage_rate(self):
        """Calcule le taux de couverture des garanties"""
        garanties = ['amt_rc', 'amt_dr', 'amt_vol', 'amt_in', 'amt_bris', 'amt_ar', 'amt_dta']
        total_garanties = 0
        for g in garanties:
            try:
                value = self.data.get(g, 0)
                if value and float(value) > 0:
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
            # Bonus favorable réduit le risque (bonus < 100 = bon)
            bonus_factor = (100 - bonus) * 0.3 if bonus < 100 else 0
            # Meilleure couverture = meilleure protection
            coverage_factor = coverage * 0.2
            score = base_score + bonus_factor + coverage_factor
            return min(100, max(0, int(score)))
        except:
            return base_score

    def calculate_trend(self):
        """Calcule la tendance d'évolution des primes"""
        try:
            prime_actuelle = float(self.data.get('prime_nette', 0))
            # Récupérer prime N-1 depuis l'historique ou utiliser valeur par défaut
            prime_2024 = self.data.get('prime_n_1', 138000)
            try:
                prime_2024 = float(prime_2024)
            except (ValueError, TypeError):
                prime_2024 = 138000
            
            if prime_2024 == 0:
                return "► N/A"
            
            if prime_actuelle > prime_2024:
                variation = ((prime_actuelle - prime_2024) / prime_2024) * 100
                return f"▲ +{variation:.1f}%"
            elif prime_actuelle < prime_2024:
                variation = ((prime_2024 - prime_actuelle) / prime_2024) * 100
                return f"▼ -{variation:.1f}%"
            else:
                return "► Stable"
        except:
            return "► N/A"

    def get_claim_trend_text(self):
        """Retourne le texte de tendance des sinistres"""
        try:
            sinistres = int(self.data.get('sinistres', 0))
            sinistres_n_1 = int(self.data.get('sinistres_n_1', 0))
            
            if sinistres < sinistres_n_1:
                return "▼ En baisse"
            elif sinistres > sinistres_n_1:
                return "▲ En hausse"
            else:
                if sinistres == 0:
                    return "✓ Aucun sinistre"
                return "► Stable"
        except:
            return "► N/A"

    def get_bonus_trend_text(self):
        """Retourne le texte de tendance du bonus"""
        try:
            bonus = self.calculate_bonus_malus()
            bonus_n_1 = self.data.get('bonus_n_1', 100)
            try:
                bonus_n_1 = float(bonus_n_1)
            except (ValueError, TypeError):
                bonus_n_1 = 100
            
            if bonus < bonus_n_1:
                return "▼ Bonus amélioré"
            elif bonus > bonus_n_1:
                return "▲ Malus appliqué"
            else:
                if bonus < 100:
                    return "✓ Bonus maintenu"
                elif bonus > 100:
                    return "⚠️ Malus maintenu"
                return "► Neutre"
        except:
            return "► N/A"

    def calculate_3year_average(self):
        """Calcule la moyenne des primes sur 3 ans"""
        try:
            # Récupérer les primes historiques
            prime_n = float(self.data.get('prime_nette', 0))
            prime_n_1 = float(self.data.get('prime_n_1', 0))
            prime_n_2 = float(self.data.get('prime_n_2', 0))
            
            values = [p for p in [prime_n_2, prime_n_1, prime_n] if p > 0]
            if values:
                return sum(values) / len(values)
            
            # Fallback sur valeurs par défaut
            default_values = [95000, 112000, 125000]
            return sum(default_values) / len(default_values)
        except:
            prime = float(self.data.get('prime_nette', 0))
            return prime

    def calculate_loss_ratio(self):
        """Calcule le ratio sinistre/prime"""
        try:
            sinistres = int(self.data.get('sinistres', 0))
            prime = float(self.data.get('prime_nette', 1))
            
            if prime <= 0:
                return "0%"
            
            # Montant moyen estimé par sinistre (à adapter selon vos données)
            avg_claim_amount = self.data.get('avg_claim_amount', 50000)
            try:
                avg_claim_amount = float(avg_claim_amount)
            except (ValueError, TypeError):
                avg_claim_amount = 50000
            
            total_claims = sinistres * avg_claim_amount
            ratio = (total_claims / prime) * 100
            return f"{ratio:.1f}%"
        except:
            return "0%"

    def get_loss_ratio_status(self):
        """Statut du ratio sinistre/prime"""
        try:
            sinistres = int(self.data.get('sinistres', 0))
            prime = float(self.data.get('prime_nette', 1))
            
            if prime <= 0:
                return "Non évaluable"
            
            if sinistres == 0:
                return "Excellent"
            elif sinistres == 1:
                # Vérifier le montant si disponible
                sinistre_amount = float(self.data.get('dernier_sinistre_montant', 0))
                if sinistre_amount > prime * 0.5:
                    return "À surveiller"
                return "Bon"
            elif sinistres == 2:
                return "Préoccupant"
            else:
                return "Critique"
        except:
            return "Standard"

    def calculate_client_profitability(self):
        """Calcule la rentabilité client"""
        try:
            sinistres = int(self.data.get('sinistres', 0))
            prime = float(self.data.get('prime_nette', 0))
            years = max(1, self.get_years_count())
            
            total_premiums = prime * years
            
            # Estimation du coût des sinistres
            avg_claim = float(self.data.get('avg_claim_amount', 50000))
            total_claims = sinistres * avg_claim
            
            if total_premiums <= 0:
                return "Non calculable"
            
            profitability_ratio = (total_premiums - total_claims) / total_premiums * 100
            
            if profitability_ratio > 50:
                return "Très bonne"
            elif profitability_ratio > 20:
                return "Bonne"
            elif profitability_ratio > 0:
                return "Moyenne"
            elif profitability_ratio > -50:
                return "Faible"
            else:
                return "Déficitaire"
        except:
            return "Standard"

    def get_profitability_status(self):
        """Statut de rentabilité"""
        try:
            sinistres = int(self.data.get('sinistres', 0))
            prime = float(self.data.get('prime_nette', 0))
            years = max(1, self.get_years_count())
            
            total_premiums = prime * years
            avg_claim = float(self.data.get('avg_claim_amount', 50000))
            total_claims = sinistres * avg_claim
            
            if total_premiums <= 0:
                return "Standard"
            
            profitability_ratio = (total_premiums - total_claims) / total_premiums * 100
            
            if profitability_ratio > 40:
                return "Optimal"
            elif profitability_ratio > 15:
                return "Bon"
            elif profitability_ratio > 0:
                return "Correct"
            elif profitability_ratio > -30:
                return "À améliorer"
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
            else:
                factors.append({
                    "icon": "✅",
                    "label": "Aucun sinistre",
                    "value": "Profil exemplaire",
                    "color": "#10b981"
                })
            
            if years < 2:
                factors.append({
                    "icon": "🆕",
                    "label": "Ancienneté faible",
                    "value": "Période probatoire",
                    "color": "#f59e0b"
                })
            elif years >= 5:
                factors.append({
                    "icon": "⭐",
                    "label": "Ancienneté élevée",
                    "value": f"{years} ans de fidélité",
                    "color": "#10b981"
                })
            
            coverage = self.calculate_coverage_rate()
            if coverage < 70:
                factors.append({
                    "icon": "🛡️",
                    "label": "Couverture partielle",
                    "value": f"{coverage}% des risques",
                    "color": "#f59e0b"
                })
            elif coverage >= 90:
                factors.append({
                    "icon": "🛡️",
                    "label": "Couverture complète",
                    "value": f"{coverage}% des risques",
                    "color": "#10b981"
                })
            
            bonus = self.calculate_bonus_malus()
            if bonus > 100:
                factors.append({
                    "icon": "📈",
                    "label": "Coefficient malus",
                    "value": f"{bonus}%",
                    "color": "#ef4444"
                })
            elif bonus < 100:
                factors.append({
                    "icon": "📉",
                    "label": "Coefficient bonus",
                    "value": f"{bonus}%",
                    "color": "#10b981"
                })
            
            if len(factors) == 0:
                factors.append({
                    "icon": "ℹ️",
                    "label": "Profil standard",
                    "value": "Risque modéré",
                    "color": "#64748b"
                })
                
        except Exception as e:
            print(f"Erreur get_risk_factors: {e}")
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
        layout.addStretch()
        
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
        layout.addStretch()
        
        return badge
    
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
    
    def create_info_card(self):
        """Crée la carte d'informations détaillées"""
        info_card = QFrame()
        info_card.setProperty("class", "InfoCard")
        info_layout = QGridLayout(info_card)
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
        prime_nette = float(self.data.get('prime_nette', ''))
        prime_brute = float(self.data.get('prime_brute', ''))
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
        self.payment_mode.addItems(["Espèces", "Carte bancaire", "Virement", "Chèque", "Mobile Money"])
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
        
        for i, (name, file, size) in enumerate(documents):
            doc_btn = QPushButton(f"{name} ({size})")
            doc_btn.setStyleSheet("""
                QPushButton {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 28px 22px;
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
        # layout.setContentsMargins(20, 16, 20, 16)
        
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

    def format_amount(self, amount):
        """Formate un montant avec séparateurs de milliers"""
        try:
            return f"{int(amount):,}".replace(",", " ")
        except:
            return "0"
  
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



    # ------------------------------ GESTION DES STATISTIQUES ET ANALYSES PROFESSIONNELLES ------------------------------

    def create_stats_tab(self):
        """Onglet des statistiques et performances avec scroll area"""
        tab = QWidget()
        
        # Scroll Area principale
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        # Conteneur interne
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 16, 0, 16)
        container_layout.setSpacing(24)
        
        # Section statistiques complète
        container_layout.addWidget(self.create_stats_section())
        
        # Espacement final
        container_layout.addSpacing(20)
        
        scroll_area.setWidget(container)
        
        # Layout principal de l'onglet
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
        return tab

    def create_stats_section(self):
        """Crée une section de statistiques avec design moderne"""
        
        stats_card = QFrame()
        stats_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 24px;
            }
        """)
        
        main_layout = QVBoxLayout(stats_card)
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(28)
        
        # ========== EN-TÊTE ==========
        header = self.create_stats_header()
        main_layout.addWidget(header)
        
        # ========== LIGNE KPI CARDS ==========
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        
        prime = float(self.data.get('prime_nette', 0))
        sinistres = int(self.data.get('sinistres', 0))
        years = max(1, self.get_years_count())
        frequency = sinistres / years
        bonus = self.calculate_bonus_malus()
        anciennete = self.get_years_count()
        
        # KPI 1
        kpi1 = self.create_modern_kpi_card(
            title="PRIME NETTE",
            value=f"{int(prime):,}".replace(",", " "),
            subtitle="FCFA / an",
            icon="💰",
            trend=self.calculate_trend(),
            color="#3b82f6",
            bg_gradient="linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)"
        )
        kpi_layout.addWidget(kpi1)
        
        # KPI 2
        kpi2 = self.create_modern_kpi_card(
            title="SINISTRALITÉ",
            value=f"{frequency:.2f}",
            subtitle="sinistres / an",
            icon="⚠️",
            trend=self.get_claim_trend_text(),
            color="#ef4444" if frequency > 0.5 else "#10b981",
            bg_gradient="linear-gradient(135deg, #ef4444 0%, #dc2626 100%)" if frequency > 0.5 else "linear-gradient(135deg, #10b981 0%, #059669 100%)"
        )
        kpi_layout.addWidget(kpi2)
        
        # KPI 3
        kpi3 = self.create_modern_kpi_card(
            title="BONUS / MALUS",
            value=f"{bonus}%",
            subtitle="coefficient",
            icon="🎯",
            trend=self.get_bonus_trend_text(),
            color="#10b981" if bonus < 100 else "#ef4444" if bonus > 100 else "#f59e0b",
            bg_gradient="linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)"
        )
        kpi_layout.addWidget(kpi3)
        
        # KPI 4
        kpi4 = self.create_modern_kpi_card(
            title="ANCIENNETÉ",
            value=f"{anciennete}",
            subtitle="années",
            icon="📅",
            trend=f"+{anciennete * 12} mois" if anciennete > 0 else "Nouveau",
            color="#8b5cf6",
            bg_gradient="linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
        )
        kpi_layout.addWidget(kpi4)
        
        main_layout.addLayout(kpi_layout)
        
        # ========== SECTION ANALYSE DOUBLE ==========
        analytics_row = QHBoxLayout()
        analytics_row.setSpacing(24)
        
        # Graphique d'évolution
        chart_widget = self.create_modern_chart()
        analytics_row.addWidget(chart_widget, 2)
        
        # Indicateurs de risque
        risk_widget = self.create_modern_risk_panel()
        analytics_row.addWidget(risk_widget, 1)
        
        main_layout.addLayout(analytics_row)
        
        # ========== TABLEAU DES PERFORMANCES ==========
        performance_table = self.create_modern_performance_table()
        main_layout.addWidget(performance_table)
        
        return stats_card

    def create_stats_header(self):
        """Crée un en-tête stylisé pour la page statistique"""
        
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e293b, stop:1 #0f172a);
                border-radius: 20px;
            }
        """)
        header.setMinimumHeight(100)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 20, 28, 20)
        
        # Partie gauche - Titre
        title_section = QVBoxLayout()
        
        title = QLabel("📊 TABLEAU DE BORD PERFORMANCE")
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: 800;
            letter-spacing: 1px;
            border: none;
        """)
        
        subtitle = QLabel("Analyse détaillée des indicateurs clés et tendances du contrat")
        subtitle.setStyleSheet("""
            color: rgba(255,255,255,0.7);
            font-size: 12px;
            border: none;
        """)
        
        title_section.addWidget(title)
        title_section.addWidget(subtitle)
        
        # Partie droite - Date
        from datetime import datetime
        date_section = QVBoxLayout()
        date_section.setAlignment(Qt.AlignRight)
        
        date_lbl = QLabel(datetime.now().strftime("%d/%m/%Y"))
        date_lbl.setStyleSheet("""
            color: rgba(255,255,255,0.6);
            font-size: 12px;
            font-weight: 500;
            border: none;
        """)
        
        rapport_lbl = QLabel("Rapport périodique")
        rapport_lbl.setStyleSheet("""
            color: #fbbf24;
            font-size: 11px;
            font-weight: 600;
            border: none;
        """)
        
        date_section.addWidget(rapport_lbl)
        date_section.addWidget(date_lbl)
        
        layout.addLayout(title_section)
        layout.addStretch()
        layout.addLayout(date_section)
        
        return header

    def create_modern_kpi_card(self, title, value, subtitle, icon, trend, color, bg_gradient):
        """Crée une carte KPI moderne avec dégradé"""
        
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }}
            QFrame:hover {{
                border-color: {color};
            }}
        """)
        card.setMinimumHeight(140)
        card.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)
        
        # Ligne 1 : Icône + Titre
        header_layout = QHBoxLayout()
        
        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {color}15;
                border-radius: 12px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 22px; background: transparent;border: none;")
        icon_layout.addWidget(icon_lbl)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            font-size: 11px;
            font-weight: 700;
            color: #64748b;
            letter-spacing: 1px;
            border: none;
        """)
        
        header_layout.addWidget(icon_container)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        # Tendance
        trend_container = QFrame()
        trend_container.setStyleSheet(f"""
            QFrame {{
                background: {color}10;
                border-radius: 20px;
                padding: 4px 10px;
            }}
        """)
        trend_layout = QHBoxLayout(trend_container)
        trend_layout.setContentsMargins(8, 4, 8, 4)
        
        trend_lbl = QLabel(trend)
        trend_lbl.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {color};
            background: transparent;
            border: none;
        """)
        trend_layout.addWidget(trend_lbl)
        
        header_layout.addWidget(trend_container)
        
        # Ligne 2 : Valeur
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 800;
            color: {color};
            border: none;
        """)
        
        # Ligne 3 : Subtitle
        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setStyleSheet("""
            font-size: 11px;
            color: #94a3b8;
            border: none;
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(value_lbl)
        layout.addWidget(subtitle_lbl)
        
        return card

    def create_modern_chart(self):
        """Crée un graphique moderne avec barres stylisées"""
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QHBoxLayout()
        chart_title = QLabel("📈 ÉVOLUTION DES PRIMES")
        chart_title.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #1e293b;
            border: none;
        """)
        
        # Légende
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(16)
        
        legend1 = self.create_legend_dot("Année en cours", "#3b82f6")
        legend2 = self.create_legend_dot("Projection", "#cbd5e1")
        
        legend_layout.addWidget(legend1)
        legend_layout.addWidget(legend2)
        
        header_layout.addWidget(chart_title)
        header_layout.addStretch()
        header_layout.addLayout(legend_layout)
        layout.addLayout(header_layout)
        
        # Graphique
        chart_widget = self.create_modern_bars()
        layout.addWidget(chart_widget)
        
        # Stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        
        prime_actuelle = float(self.data.get('prime_nette', 0))
        prime_2024 = float(self.data.get('prime_n_1', 138000))
        
        if prime_2024 > 0:
            evolution = ((prime_actuelle - prime_2024) / prime_2024) * 100
            stats_layout.addWidget(self.create_stat_pill("📊 Évolution", f"{evolution:+.1f}%", "#10b981" if evolution > 0 else "#ef4444"))
        
        stats_layout.addWidget(self.create_stat_pill("📈 Moyenne 3 ans", f"{int(self.calculate_3year_average()):,}".replace(",", " "), "#8b5cf6"))
        stats_layout.addWidget(self.create_stat_pill("🎯 Projection 2026", f"{int(prime_actuelle * 1.08):,}".replace(",", " "), "#f59e0b"))
        
        layout.addLayout(stats_layout)
        
        return card

    def create_modern_bars(self):
        """Crée des barres de graphique modernes"""
        
        widget = QFrame()
        widget.setFixedHeight(180)
        
        layout = QHBoxLayout(widget)
        layout.setSpacing(16)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Données
        years = [2022, 2023, 2024, 2025]
        values = [
            float(self.data.get('prime_n_2', 112000)),
            float(self.data.get('prime_n_1', 125000)),
            float(self.data.get('prime_nette', 138000)),
            float(self.data.get('prime_nette', 138000)) * 1.08
        ]
        
        max_value = max(values) if values else 150000
        
        for year, value in zip(years, values):
            bar_container = QWidget()
            bar_layout = QVBoxLayout(bar_container)
            bar_layout.setSpacing(10)
            bar_layout.setAlignment(Qt.AlignBottom)
            
            # Hauteur de la barre
            height = max(50, int((value / max_value) * 110))
            
            # Barre avec animation hover
            bar = QFrame()
            bar.setFixedSize(55, height)
            
            if year == 2025:
                bar.setStyleSheet("""
                    QFrame {
                        background: #e2e8f0;
                        border-radius: 10px;
                        border: 1px dashed #94a3b8;
                    }
                    QFrame:hover {
                        background: #cbd5e1;
                    }
                """)
            else:
                bar.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                            stop:0 #3b82f6, stop:1 #60a5fa);
                        border-radius: 10px;
                    }
                    QFrame:hover {
                        background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                            stop:0 #2563eb, stop:1 #3b82f6);
                    }
                """)
            
            # Valeur
            value_lbl = QLabel(f"{int(value/1000)}k FCFA")
            value_lbl.setStyleSheet("""
                font-size: 11px;
                font-weight: 700;
                color: #475569;
                border: none;
            """)
            value_lbl.setAlignment(Qt.AlignCenter)
            
            # Année
            year_lbl = QLabel(str(year))
            year_lbl.setStyleSheet("""
                font-size: 12px;
                font-weight: 600;
                color: #64748b;
                border: none;
            """)
            year_lbl.setAlignment(Qt.AlignCenter)
            
            bar_layout.addStretch()
            bar_layout.addWidget(bar)
            bar_layout.addWidget(value_lbl)
            bar_layout.addWidget(year_lbl)
            
            layout.addWidget(bar_container)
            layout.addStretch()
        
        return widget

    def create_modern_risk_panel(self):
        """Crée un panneau de risque moderne avec jauge"""
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(18)
        
        # Titre
        title_layout = QHBoxLayout()
        title = QLabel("⚠️ NIVEAU DE RISQUE")
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #1e293b;
            border: none;
        """)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Score de risque
        sinistres = int(self.data.get('sinistres', 0))
        risk_score = min(100, sinistres * 25)
        
        if risk_score < 30:
            risk_level = "Faible"
            risk_color = "#10b981"
            risk_icon = "🟢"
        elif risk_score < 70:
            risk_level = "Modéré"
            risk_color = "#f59e0b"
            risk_icon = "🟡"
        else:
            risk_level = "Élevé"
            risk_color = "#ef4444"
            risk_icon = "🔴"
        
        # Jauge circulaire simplifiée
        gauge_container = QFrame()
        gauge_container.setStyleSheet(f"""
            QFrame {{
                background: {risk_color}10;
                border-radius: 16px;
            }}
        """)
        gauge_layout = QHBoxLayout(gauge_container)
        gauge_layout.setContentsMargins(20, 16, 20, 16)
        
        # Score
        score_lbl = QLabel(f"{risk_score}%")
        score_lbl.setStyleSheet(f"""
            font-size: 36px;
            font-weight: 800;
            color: {risk_color};
            border: none;
        """)
        
        # Infos
        info_layout = QVBoxLayout()
        level_lbl = QLabel(f"{risk_icon} Niveau {risk_level}")
        level_lbl.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: {risk_color};
            border: none;
        """)
        
        desc_lbl = QLabel("Basé sur l'historique des sinistres")
        desc_lbl.setStyleSheet("""
            font-size: 10px;
            color: #94a3b8;
            border: none;
        """)
        
        info_layout.addWidget(level_lbl)
        info_layout.addWidget(desc_lbl)
        
        gauge_layout.addWidget(score_lbl)
        gauge_layout.addSpacing(20)
        gauge_layout.addLayout(info_layout)
        gauge_layout.addStretch()
        
        layout.addWidget(gauge_container)
        
        # Facteurs de risque
        factors = self.get_risk_factors()
        for factor in factors[:3]:
            layout.addWidget(self.create_modern_risk_factor(factor))
        
        return card

    def create_modern_risk_factor(self, factor):
        """Crée une ligne de facteur de risque moderne"""
        
        row = QFrame()
        row.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 12px;
            }
        """)
        
        layout = QHBoxLayout(row)
        layout.setContentsMargins(16, 12, 16, 12)
        
        icon = QLabel(factor['icon'])
        icon.setStyleSheet("font-size: 18px;border: none;")
        
        label = QLabel(factor['label'])
        label.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: #475569;
            border: none;
        """)
        
        value = QLabel(factor['value'])
        value.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {factor['color']};
            border: none;
        """)
        
        layout.addWidget(icon)
        layout.addSpacing(12)
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(value)
        
        return row

    def create_modern_performance_table(self):
        """Crée un tableau de performance moderne"""
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Titre
        title = QLabel("📋 INDICATEURS DE PERFORMANCE")
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #1e293b;
            border: none;
        """)
        layout.addWidget(title)
        
        # Tableau stylisé
        prime = float(self.data.get('prime_nette', 0))
        prime_brute = float(self.data.get('prime_brute', 0))
        reduction = prime_brute - prime
        reduction_percent = (reduction / prime_brute * 100) if prime_brute > 0 else 0
        
        performances = [
            ("🎯 Taux de réduction", f"{reduction_percent:.1f}%", 
            "Excellent" if reduction_percent > 15 else "Bon" if reduction_percent > 5 else "Standard"),
            ("⚠️ Ratio sinistre/prime", self.calculate_loss_ratio(), 
            self.get_loss_ratio_status()),
            ("🛡️ Efficacité couverture", f"{self.calculate_coverage_rate()}%", 
            "Optimal" if self.calculate_coverage_rate() > 80 else "Correct" if self.calculate_coverage_rate() > 60 else "À améliorer"),
            ("💰 Rentabilité client", self.calculate_client_profitability(), 
            self.get_profitability_status()),
        ]
        
        for i, (indicator, value, status) in enumerate(performances):
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: #f8fafc;
                    border-radius: 12px;
                    margin-bottom: 8px;
                }}
            """)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(20, 14, 20, 14)
            
            # Indicateur
            indicator_lbl = QLabel(indicator)
            indicator_lbl.setStyleSheet("font-size: 13px; font-weight: 500; color: #1e293b;border: none;")
            row_layout.addWidget(indicator_lbl)
            row_layout.addStretch()
            
            # Valeur
            value_lbl = QLabel(str(value))
            value_lbl.setStyleSheet("""
                font-size: 14px;
                font-weight: 700;
                color: #475569;
                border: none;
            """)
            row_layout.addWidget(value_lbl)
            row_layout.addSpacing(20)
            
            # Statut
            if "Excellent" in status or "Optimal" in status:
                status_color = "#10b981"
                status_bg = "#10b98115"
            elif "Bon" in status or "Correct" in status:
                status_color = "#f59e0b"
                status_bg = "#f59e0b15"
            else:
                status_color = "#ef4444"
                status_bg = "#ef444415"
            
            status_container = QFrame()
            status_container.setStyleSheet(f"""
                QFrame {{
                    background: {status_bg};
                    border-radius: 20px;
                    padding: 4px 12px;
                    border: none;
                }}
            """)
            status_layout = QHBoxLayout(status_container)
            status_layout.setContentsMargins(10, 4, 10, 4)
            
            status_lbl = QLabel(status)
            status_lbl.setStyleSheet(f"""
                font-size: 11px;
                font-weight: 700;
                color: {status_color};
                border: none;
            """)
            status_layout.addWidget(status_lbl)
            
            row_layout.addWidget(status_container)
            
            layout.addWidget(row)
        
        return card

    def create_legend_dot(self, text, color):
        """Crée une légende avec un point coloré"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        dot = QFrame()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 5px;
            }}
        """)
        
        label = QLabel(text)
        label.setStyleSheet("font-size: 11px; color: #64748b;border: none;")
        
        layout.addWidget(dot)
        layout.addWidget(label)
        
        return widget

    def create_stat_pill(self, label, value, color):
        """Crée une pastille statistique"""
        pill = QFrame()
        pill.setStyleSheet(f"""
            QFrame {{
                background: {color}10;
                border-radius: 20px;
                padding: 6px 14px;
            }}
        """)
        
        layout = QHBoxLayout(pill)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet("font-size: 10px; color: #64748b;border: none;")
        
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {color};border: none;")
        
        layout.addWidget(label_lbl)
        layout.addWidget(value_lbl)
        
        return pill

    def create_metric_pill(self, label, value, unit):
        """Crée une pastille métrique compacte"""
        pill = QFrame()
        pill.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.15);
                border-radius: 12px;
                padding: 8px 16px;
            }
        """)
        
        layout = QVBoxLayout(pill)
        layout.setSpacing(4)
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet("""
            font-size: 10px;
            font-weight: 600;
            color: rgba(255,255,255,0.7);
            border: none;
        """)
        
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("""
            font-size: 16px;
            font-weight: 800;
            color: white;
            border: none;
        """)
        
        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet("""
            font-size: 9px;
            color: rgba(255,255,255,0.5);
            border: none;
        """)
        
        layout.addWidget(label_lbl)
        value_layout = QHBoxLayout()
        value_layout.addWidget(value_lbl)
        value_layout.addWidget(unit_lbl)
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        return pill
    

    #---------------------------------- GESTION DE DOCUMENTS ET CONTACTS UTILES ----------------------------------

    def create_documents_tab(self):
        """Onglet des documents et contacts avec scroll area"""
        tab = QWidget()
        
        # Scroll Area principale
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        # Conteneur interne
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 16, 0, 16)
        container_layout.setSpacing(24)
        
        # Documents annexes
        container_layout.addWidget(self.create_modern_documents_section())
        
        # Contacts utiles
        container_layout.addWidget(self.create_modern_contacts_section())
        
        # Actions d'impression
        container_layout.addLayout(self.create_modern_print_section())
        
        # Espacement final
        container_layout.addSpacing(20)
        
        scroll_area.setWidget(container)
        
        # Layout principal de l'onglet
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
        return tab

    def create_modern_documents_section(self):
        """Crée une section des documents moderne avec icônes et catégories"""
        
        docs_card = QFrame()
        docs_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 24px;
            }
        """)
        
        layout = QVBoxLayout(docs_card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)
        
        # En-tête avec icône
        header_layout = QHBoxLayout()
        
        title_icon = QLabel("📁")
        title_icon.setStyleSheet("""
            font-size: 24px;
            background: #eef2ff;
            padding: 10px;
            border-radius: 16px;
        """)
        
        title_text = QLabel("DOCUMENTS ANNEXES")
        title_text.setStyleSheet("""
            font-size: 16px;
            font-weight: 800;
            color: #0f172a;
        """)
        
        subtitle_text = QLabel("Téléchargez vos documents contractuels")
        subtitle_text.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
        """)
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_text)
        title_layout.addWidget(subtitle_text)
        
        header_layout.addWidget(title_icon)
        header_layout.addSpacing(12)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Badge nombre de documents
        doc_count = QLabel("6 documents disponibles")
        doc_count.setStyleSheet("""
            background: #f1f5f9;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            color: #475569;
        """)
        header_layout.addWidget(doc_count)
        
        layout.addLayout(header_layout)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height: 1px; margin: 8px 0;")
        layout.addWidget(sep)
        
        # Grille des documents avec catégories
        # Catégorie 1: Contrats
        cat_title = QLabel("📄 CONTRATS & ATTESTATIONS")
        cat_title.setStyleSheet("""
            font-size: 12px;
            font-weight: 700;
            color: #3b82f6;
            letter-spacing: 0.5px;
            margin-top: 8px;
            margin-bottom: 12px;
        """)
        layout.addWidget(cat_title)
        
        docs_grid1 = QGridLayout()
        docs_grid1.setSpacing(12)
        
        documents_contrats = [
            ("📄 Contrat d'assurance", "contrat.pdf", "1.2 MB", "📅 06/04/2026"),
            ("🛡️ Attestation", "attestation.pdf", "0.3 MB", "📅 06/04/2026"),
            ("📝 Avenant n°1", "avenant.pdf", "0.8 MB", "📅 15/03/2026"),
        ]
        
        for i, (name, file, size, date) in enumerate(documents_contrats):
            doc_widget = self.create_modern_doc_item(name, file, size, date, "#3b82f6")
            docs_grid1.addWidget(doc_widget, i // 2, i % 2)
        
        layout.addLayout(docs_grid1)
        
        # Catégorie 2: Financiers
        cat_title2 = QLabel("💰 DOCUMENTS FINANCIERS")
        cat_title2.setStyleSheet("""
            font-size: 12px;
            font-weight: 700;
            color: #10b981;
            letter-spacing: 0.5px;
            margin-top: 16px;
            margin-bottom: 12px;
        """)
        layout.addWidget(cat_title2)
        
        docs_grid2 = QGridLayout()
        docs_grid2.setSpacing(12)
        
        documents_financiers = [
            ("💳 Relevé de paiement", "paiement.pdf", "0.5 MB", "📅 06/04/2026"),
            ("📊 Devis initial", "devis.pdf", "0.4 MB", "📅 01/03/2026"),
            ("🧾 Quittance", "quittance.pdf", "0.6 MB", "📅 06/04/2026"),
        ]
        
        for i, (name, file, size, date) in enumerate(documents_financiers):
            doc_widget = self.create_modern_doc_item(name, file, size, date, "#10b981")
            docs_grid2.addWidget(doc_widget, i // 2, i % 2)
        
        layout.addLayout(docs_grid2)
        
        # Catégorie 3: Généraux
        cat_title3 = QLabel("📋 DOCUMENTS GÉNÉRAUX")
        cat_title3.setStyleSheet("""
            font-size: 12px;
            font-weight: 700;
            color: #8b5cf6;
            letter-spacing: 0.5px;
            margin-top: 16px;
            margin-bottom: 12px;
        """)
        layout.addWidget(cat_title3)
        
        docs_grid3 = QGridLayout()
        docs_grid3.setSpacing(12)
        
        documents_generaux = [
            ("📋 Conditions générales", "conditions.pdf", "2.5 MB", "📅 01/01/2026"),
            ("📈 Rapport annuel", "rapport.pdf", "1.8 MB", "📅 31/12/2025"),
        ]
        
        for i, (name, file, size, date) in enumerate(documents_generaux):
            doc_widget = self.create_modern_doc_item(name, file, size, date, "#8b5cf6")
            docs_grid3.addWidget(doc_widget, i // 2, i % 2)
        
        layout.addLayout(docs_grid3)
        
        return docs_card

    def create_modern_doc_item(self, name, file, size, date, color):
        """Crée un élément de document moderne"""
        
        doc_btn = QPushButton()
        doc_btn.setCursor(Qt.PointingHandCursor)
        doc_btn.setProperty("file", file)
        
        doc_btn.setStyleSheet(f"""
            QPushButton {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 16px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: #f1f5f9;
                border-color: {color};
            }}
        """)
        
        # Layout interne du bouton
        btn_layout = QHBoxLayout(doc_btn)
        btn_layout.setContentsMargins(16, 12, 16, 12)
        btn_layout.setSpacing(12)
        
        # Icône
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {color}15;
                border-radius: 12px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel(name.split()[0])
        icon_lbl.setStyleSheet(f"font-size: 24px; background: transparent;")
        icon_layout.addWidget(icon_lbl)
        
        btn_layout.addWidget(icon_container)
        
        # Infos
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #1e293b;
        """)
        
        details_layout = QHBoxLayout()
        details_layout.setSpacing(12)
        
        size_lbl = QLabel(size)
        size_lbl.setStyleSheet("""
            font-size: 11px;
            color: #64748b;
        """)
        
        date_lbl = QLabel(date)
        date_lbl.setStyleSheet("""
            font-size: 11px;
            color: #94a3b8;
        """)
        
        details_layout.addWidget(size_lbl)
        details_layout.addWidget(date_lbl)
        details_layout.addStretch()
        
        info_layout.addWidget(name_lbl)
        info_layout.addLayout(details_layout)
        
        btn_layout.addLayout(info_layout, 1)
        
        # Bouton téléchargement
        download_icon = QLabel("📥")
        download_icon.setStyleSheet(f"""
            font-size: 18px;
            background: {color}10;
            padding: 8px;
            border-radius: 10px;
        """)
        btn_layout.addWidget(download_icon)
        
        self.doc_buttons[file] = doc_btn
        
        return doc_btn

    def create_modern_contacts_section(self):
        """Crée une section des contacts moderne avec cartes"""
        
        contacts_card = QFrame()
        contacts_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 24px;
            }
        """)
        
        layout = QVBoxLayout(contacts_card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title_icon = QLabel("📞")
        title_icon.setStyleSheet("""
            font-size: 24px;
            background: #eef2ff;
            padding: 10px;
            border-radius: 16px;
        """)
        
        title_text = QLabel("CONTACTS UTILES")
        title_text.setStyleSheet("""
            font-size: 16px;
            font-weight: 800;
            color: #0f172a;
        """)
        
        subtitle_text = QLabel("Assistance et services disponibles 24/7")
        subtitle_text.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
        """)
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_text)
        title_layout.addWidget(subtitle_text)
        
        header_layout.addWidget(title_icon)
        header_layout.addSpacing(12)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height: 1px; margin: 8px 0;")
        layout.addWidget(sep)
        
        # Grille des contacts
        contacts_grid = QGridLayout()
        contacts_grid.setSpacing(16)
        
        contacts = [
            ("👤", "Agent commercial", "Mme TAMAR HAMBEN", "+237 6XX XX XX XX", "jean.dupont@assurance.com", "#3b82f6"),
            ("🛡️", "Assistance 24/7", "Service client", "+237 800 00 00 00", "assistance@amsassurance.com", "#10b981"),
            ("🚗", "Dépannage", "Auto Assistance", "+237 699 99 99 99", None, "#f59e0b"),
            ("⚖️", "Sinistres", "Déclaration sinistre", "+237 6XX XX XX XX", "sinistres@amsassurance.com", "#ef4444"),
        ]
        
        for i, (icon, role, name, phone, email, color) in enumerate(contacts):
            contact_card = self.create_modern_contact_card(icon, role, name, phone, email, color)
            contacts_grid.addWidget(contact_card, i // 2, i % 2)
        
        layout.addLayout(contacts_grid)
        
        return contacts_card

    def create_modern_contact_card(self, icon, role, name, phone, email, color):
        """Crée une carte de contact moderne"""
        
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: #f8fafc;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }}
            QFrame:hover {{
                border-color: {color};
                background: white;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # En-tête avec icône
        header_layout = QHBoxLayout()
        
        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {color}15;
                border-radius: 12px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 20px; background: transparent;")
        icon_layout.addWidget(icon_lbl)
        
        role_lbl = QLabel(role)
        role_lbl.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 700;
            color: {color};
            letter-spacing: 0.5px;
        """)
        
        header_layout.addWidget(icon_container)
        header_layout.addSpacing(8)
        header_layout.addWidget(role_lbl)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Nom
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #1e293b;
        """)
        layout.addWidget(name_lbl)
        
        # Téléphone (cliquable)
        phone_container = QFrame()
        phone_container.setStyleSheet(f"""
            QFrame {{
                background: {color}10;
                border-radius: 12px;
                padding: 8px 12px;
            }}
        """)
        phone_layout = QHBoxLayout(phone_container)
        phone_layout.setContentsMargins(0, 0, 0, 0)
        
        phone_icon = QLabel("📱")
        phone_icon.setStyleSheet("font-size: 14px;")
        
        phone_lbl = QLabel(phone)
        phone_lbl.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {color};
        """)
        
        phone_layout.addWidget(phone_icon)
        phone_layout.addSpacing(8)
        phone_layout.addWidget(phone_lbl)
        phone_layout.addStretch()
        
        layout.addWidget(phone_container)
        
        # Email si disponible
        if email:
            email_container = QFrame()
            email_container.setStyleSheet(f"""
                QFrame {{
                    background: #f1f5f9;
                    border-radius: 12px;
                    padding: 8px 12px;
                }}
            """)
            email_layout = QHBoxLayout(email_container)
            email_layout.setContentsMargins(0, 0, 0, 0)
            
            email_icon = QLabel("✉️")
            email_icon.setStyleSheet("font-size: 14px;")
            
            email_lbl = QLabel(email)
            email_lbl.setStyleSheet("""
                font-size: 11px;
                color: #64748b;
            """)
            
            email_layout.addWidget(email_icon)
            email_layout.addSpacing(8)
            email_layout.addWidget(email_lbl)
            email_layout.addStretch()
            
            layout.addWidget(email_container)
        
        return card

    def create_modern_print_section(self):
        """Crée une section d'impression moderne avec actions rapides"""
        
        print_section = QVBoxLayout()
        print_section.setSpacing(20)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title_icon = QLabel("🖨️")
        title_icon.setStyleSheet("""
            font-size: 24px;
            background: #eef2ff;
            padding: 10px;
            border-radius: 16px;
        """)
        
        title_text = QLabel("ACTIONS D'IMPRESSION")
        title_text.setStyleSheet("""
            font-size: 16px;
            font-weight: 800;
            color: #0f172a;
        """)
        
        subtitle_text = QLabel("Générez et imprimez vos documents officiels")
        subtitle_text.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
        """)
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_text)
        title_layout.addWidget(subtitle_text)
        
        header_layout.addWidget(title_icon)
        header_layout.addSpacing(12)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        print_section.addLayout(header_layout)
        
        # Grille des actions
        btn_grid = QGridLayout()
        btn_grid.setSpacing(16)
        
        actions = [
            ("📄", "CARTE ROSE", "carte_rose", "Document officiel d'assurance", "#3b82f6"),
            ("🎫", "VIGNETTE", "vignette", "Vignette à apposer sur le pare-brise", "#10b981"),
            ("🧾", "QUITTANCE", "quittance", "Preuve de paiement", "#f59e0b"),
            ("🛡️", "ATTESTATION", "attestation", "Attestation d'assurance", "#8b5cf6"),
            ("📊", "DEVIS", "devis", "Devis détaillé", "#ef4444"),
            ("📑", "RAPPORT COMPLET", "rapport", "Rapport complet du véhicule", "#1e293b"),
        ]
        
        self.print_buttons = {}
        
        for i, (icon, label, key, tooltip, color) in enumerate(actions):
            btn = self.create_modern_print_button(icon, label, key, tooltip, color)
            self.print_buttons[key] = btn
            btn_grid.addWidget(btn, i // 3, i % 3)
        
        print_section.addLayout(btn_grid)
        
        return print_section

    def create_modern_print_button(self, icon, label, key, tooltip, color):
        """Crée un bouton d'impression moderne"""
        
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setMinimumHeight(80)
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 20px;
                padding: 16px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {color}10;
                border-color: {color};
            }}
        """)
        
        # Layout interne
        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(20, 16, 20, 16)
        btn_layout.setSpacing(16)
        
        # Icône
        icon_container = QFrame()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {color}15;
                border-radius: 15px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 26px; background: transparent;")
        icon_layout.addWidget(icon_lbl)
        
        btn_layout.addWidget(icon_container)
        
        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 800;
            color: {color};
        """)
        
        tooltip_lbl = QLabel(tooltip)
        tooltip_lbl.setStyleSheet("""
            font-size: 11px;
            color: #64748b;
        """)
        
        text_layout.addWidget(label_lbl)
        text_layout.addWidget(tooltip_lbl)
        
        btn_layout.addLayout(text_layout, 1)
        
        # Flèche
        arrow = QLabel("→")
        arrow.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 700;
            color: {color};
            opacity: 0.5;
        """)
        btn_layout.addWidget(arrow)
        
        return btn


    #---------------------------------- GESTION DE L'HISTORIQUE DU CONTRAT ----------------------------------------

    def create_history_tab(self):
        """Onglet de l'historique et des échéances avec scroll area"""
        tab = QWidget()
        
        # Scroll Area principale
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        # Conteneur interne
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 16, 0, 16)
        container_layout.setSpacing(24)
        
        # Calendrier des échéances
        container_layout.addWidget(self.create_modern_calendar_section())
        
        # Historique du véhicule
        container_layout.addWidget(self.create_modern_history_section())
        
        # Notifications
        container_layout.addWidget(self.create_modern_notifications_section())
        
        # Espacement final
        container_layout.addSpacing(20)
        
        scroll_area.setWidget(container)
        
        # Layout principal de l'onglet
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
        return tab

    def create_modern_calendar_section(self):
        """Crée une section des échéances moderne avec timeline"""
        
        calendar_card = QFrame()
        calendar_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 24px;
            }
        """)
        
        layout = QVBoxLayout(calendar_card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title_icon = QLabel("📅")
        title_icon.setStyleSheet("""
            font-size: 24px;
            background: #eef2ff;
            padding: 10px;
            border-radius: 16px;
        """)
        
        title_text = QLabel("PROCHAINES ÉCHÉANCES")
        title_text.setStyleSheet("""
            font-size: 16px;
            font-weight: 800;
            color: #0f172a;
        """)
        
        subtitle_text = QLabel("Suivez vos échéances importantes")
        subtitle_text.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
        """)
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_text)
        title_layout.addWidget(subtitle_text)
        
        header_layout.addWidget(title_icon)
        header_layout.addSpacing(12)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height: 1px; margin: 8px 0;")
        layout.addWidget(sep)
        
        # Timeline des échéances
        date_fin = self.data.get('date_fin')
        days_left = 0
        if date_fin:
            from datetime import date, datetime
            if isinstance(date_fin, date):
                days_left = (date_fin - date.today()).days
            elif isinstance(date_fin, str):
                try:
                    date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d").date()
                    days_left = (date_fin_obj - date.today()).days
                except:
                    pass
        
        echeances = [
            ("Renouvellement contrat", self.format_date(date_fin), days_left, "contract"),
            ("Paiement mensuel", self.format_date(self.data.get('prochain_paiement', 'N/A')), 0, "payment"),
            ("Visite technique", self.format_date(self.data.get('visite_technique', 'N/A')), 0, "technical"),
            ("Révision périodique", self.format_date(self.data.get('revision', 'N/A')), 0, "revision")
        ]
        
        for i, (event, date, delay, type_) in enumerate(echeances):
            timeline_item = self.create_timeline_item(event, date, delay, type_, i == 0)
            layout.addWidget(timeline_item)
        
        return calendar_card

    def create_timeline_item(self, event, date, days_left, type_, is_first=False):
        """Crée un élément de timeline moderne"""
        
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background: transparent;
            }
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)
        
        # Timeline verticale avec cercle
        timeline_container = QVBoxLayout()
        timeline_container.setAlignment(Qt.AlignTop)
        timeline_container.setSpacing(0)
        
        # Cercle
        circle = QFrame()
        circle.setFixedSize(40, 40)
        
        if days_left > 0:
            if days_left <= 7:
                circle.setStyleSheet("""
                    QFrame {
                        background: #ef4444;
                        border-radius: 20px;
                        border: 2px solid #fecaca;
                    }
                """)
                icon = "⚠️"
            elif days_left <= 30:
                circle.setStyleSheet("""
                    QFrame {
                        background: #f59e0b;
                        border-radius: 20px;
                        border: 2px solid #fed7aa;
                    }
                """)
                icon = "⏰"
            else:
                circle.setStyleSheet("""
                    QFrame {
                        background: #10b981;
                        border-radius: 20px;
                        border: 2px solid #a7f3d0;
                    }
                """)
                icon = "✅"
        elif "Expiré" in event or days_left < 0:
            circle.setStyleSheet("""
                QFrame {
                    background: #ef4444;
                    border-radius: 20px;
                    border: 2px solid #fecaca;
                }
            """)
            icon = "❌"
        else:
            circle.setStyleSheet("""
                QFrame {
                    background: #94a3b8;
                    border-radius: 20px;
                    border: 2px solid #e2e8f0;
                }
            """)
            icon = "📅"
        
        circle_layout = QVBoxLayout(circle)
        circle_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 18px; background: transparent;")
        circle_layout.addWidget(icon_lbl)
        
        timeline_container.addWidget(circle)
        
        # Ligne de connexion (sauf pour le dernier)
        if not is_first:
            line = QFrame()
            line.setFixedSize(2, 30)
            line.setStyleSheet("background: #e2e8f0;")
            timeline_container.addWidget(line, alignment=Qt.AlignHCenter)
        
        layout.addLayout(timeline_container)
        
        # Contenu
        content_widget = QFrame()
        content_widget.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(8)
        
        # En-tête de l'événement
        event_layout = QHBoxLayout()
        
        event_lbl = QLabel(event)
        event_lbl.setStyleSheet("""
            font-size: 15px;
            font-weight: 700;
            color: #1e293b;
        """)
        
        event_layout.addWidget(event_lbl)
        event_layout.addStretch()
        
        # Date
        date_container = QFrame()
        date_container.setStyleSheet("""
            QFrame {
                background: #eef2ff;
                border-radius: 20px;
                padding: 4px 12px;
            }
        """)
        date_layout = QHBoxLayout(date_container)
        date_layout.setContentsMargins(8, 4, 8, 4)
        
        date_icon = QLabel("📅")
        date_icon.setStyleSheet("font-size: 11px;")
        
        date_lbl = QLabel(date)
        date_lbl.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #3b82f6;
        """)
        
        date_layout.addWidget(date_icon)
        date_layout.addWidget(date_lbl)
        
        event_layout.addWidget(date_container)
        
        content_layout.addLayout(event_layout)
        
        # Délai restant
        if days_left > 0:
            delay_text = f"🔔 {days_left} jours restants"
            delay_color = "#ef4444" if days_left <= 7 else "#f59e0b" if days_left <= 30 else "#10b981"
            
            delay_lbl = QLabel(delay_text)
            delay_lbl.setStyleSheet(f"""
                font-size: 12px;
                font-weight: 600;
                color: {delay_color};
                padding: 6px 12px;
                background: {delay_color}10;
                border-radius: 20px;
            """)
            content_layout.addWidget(delay_lbl)
        elif days_left < 0 or "Expiré" in event:
            delay_lbl = QLabel("⚠️ Échéance dépassée")
            delay_lbl.setStyleSheet("""
                font-size: 12px;
                font-weight: 600;
                color: #ef4444;
                padding: 6px 12px;
                background: #ef444410;
                border-radius: 20px;
            """)
            content_layout.addWidget(delay_lbl)
        
        layout.addWidget(content_widget, 1)
        
        return item

    def create_modern_history_section(self):
        """Crée une section d'historique moderne avec timeline"""
        
        history_card = QFrame()
        history_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 24px;
            }
        """)
        
        layout = QVBoxLayout(history_card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title_icon = QLabel("📋")
        title_icon.setStyleSheet("""
            font-size: 24px;
            background: #eef2ff;
            padding: 10px;
            border-radius: 16px;
        """)
        
        title_text = QLabel("HISTORIQUE DU VÉHICULE")
        title_text.setStyleSheet("""
            font-size: 16px;
            font-weight: 800;
            color: #0f172a;
        """)
        
        subtitle_text = QLabel("Suivi chronologique des événements")
        subtitle_text.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
        """)
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_text)
        title_layout.addWidget(subtitle_text)
        
        header_layout.addWidget(title_icon)
        header_layout.addSpacing(12)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Badge nombre d'événements
        events_count = 4
        count_badge = QLabel(f"{events_count} événements")
        count_badge.setStyleSheet("""
            background: #f1f5f9;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            color: #475569;
        """)
        header_layout.addWidget(count_badge)
        
        layout.addLayout(header_layout)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height: 1px; margin: 8px 0;")
        layout.addWidget(sep)
        
        # Timeline des événements
        events = self.data.get('historique', [
            ("📄 Contrat souscrit", self.format_date(self.data.get('date_debut', '')), f"Prime: {self.format_amount(self.data.get('prime_nette', 0))} FCFA", "#10b981"),
            ("🔄 Renouvellement", self.format_date(self.data.get('date_fin', '')), f"Prime: {self.format_amount(self.data.get('prime_nette', 0))} FCFA", "#3b82f6"),
            ("📝 Modification garantie", self.format_date(self.data.get('date_fin', '')), "Ajout vol + incendie", "#8b5cf6"),
            ("💰 Paiement effectué", self.format_date(self.data.get('date_fin', '')), f"Montant: {self.format_amount(self.data.get('prime_nette', 0))} FCFA", "#f59e0b")
        ])
        
        for i, (event, date, detail, color) in enumerate(events):
            history_item = self.create_history_timeline_item(event, date, detail, color, i == len(events) - 1)
            layout.addWidget(history_item)
        
        # Bouton voir plus
        view_more_btn = QPushButton("VOIR TOUT L'HISTORIQUE →")
        view_more_btn.setCursor(Qt.PointingHandCursor)
        view_more_btn.setStyleSheet("""
            QPushButton {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 14px;
                font-size: 13px;
                font-weight: 600;
                color: #3b82f6;
                margin-top: 8px;
            }
            QPushButton:hover {
                background: #eef2ff;
                border-color: #3b82f6;
            }
        """)
        layout.addWidget(view_more_btn)
        
        return history_card

    def create_history_timeline_item(self, event, date, detail, color, is_last=False):
        """Crée un élément de timeline pour l'historique"""
        
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background: transparent;
            }
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)
        
        # Timeline
        timeline_container = QVBoxLayout()
        timeline_container.setAlignment(Qt.AlignTop)
        timeline_container.setSpacing(0)
        
        # Cercle
        circle = QFrame()
        circle.setFixedSize(36, 36)
        circle.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 18px;
                border: 2px solid white;
            }}
        """)
        
        circle_layout = QVBoxLayout(circle)
        circle_layout.setAlignment(Qt.AlignCenter)
        
        # Extraire l'icône de l'événement
        icon = event[0] if event else "📌"
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 16px; background: transparent; color: white;")
        circle_layout.addWidget(icon_lbl)
        
        timeline_container.addWidget(circle)
        
        # Ligne de connexion
        if not is_last:
            line = QFrame()
            line.setFixedSize(2, 50)
            line.setStyleSheet(f"background: {color}40;")
            timeline_container.addWidget(line, alignment=Qt.AlignHCenter)
        
        layout.addLayout(timeline_container)
        
        # Contenu
        content_widget = QFrame()
        content_widget.setStyleSheet(f"""
            QFrame {{
                background: {color}08;
                border-radius: 16px;
                border-left: 3px solid {color};
            }}
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(8)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        event_lbl = QLabel(event)
        event_lbl.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: {color};
        """)
        
        header_layout.addWidget(event_lbl)
        header_layout.addStretch()
        
        date_lbl = QLabel(date)
        date_lbl.setStyleSheet("""
            font-size: 11px;
            font-weight: 500;
            color: #64748b;
            background: #f1f5f9;
            padding: 4px 10px;
            border-radius: 20px;
        """)
        header_layout.addWidget(date_lbl)
        
        content_layout.addLayout(header_layout)
        
        # Détail
        detail_lbl = QLabel(detail)
        detail_lbl.setStyleSheet("""
            font-size: 12px;
            color: #475569;
        """)
        detail_lbl.setWordWrap(True)
        content_layout.addWidget(detail_lbl)
        
        layout.addWidget(content_widget, 1)
        
        return item

    def create_modern_notifications_section(self):
        """Crée une section des notifications moderne"""
        
        notif_card = QFrame()
        notif_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 24px;
            }
        """)
        
        layout = QVBoxLayout(notif_card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title_icon = QLabel("🔔")
        title_icon.setStyleSheet("""
            font-size: 24px;
            background: #eef2ff;
            padding: 10px;
            border-radius: 16px;
        """)
        
        title_text = QLabel("NOTIFICATIONS")
        title_text.setStyleSheet("""
            font-size: 16px;
            font-weight: 800;
            color: #0f172a;
        """)
        
        subtitle_text = QLabel("Alertes et informations importantes")
        subtitle_text.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
        """)
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_text)
        title_layout.addWidget(subtitle_text)
        
        header_layout.addWidget(title_icon)
        header_layout.addSpacing(12)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Badge non lues
        unread_badge = QLabel("3 nouvelles")
        unread_badge.setStyleSheet("""
            background: #ef4444;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        """)
        header_layout.addWidget(unread_badge)
        
        layout.addLayout(header_layout)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height: 1px; margin: 8px 0;")
        layout.addWidget(sep)
        
        # Générer des notifications dynamiques
        notifications = []
        
        # Vérifier l'expiration
        date_fin = self.data.get('date_fin')
        if date_fin:
            from datetime import date, datetime
            days_left = 0
            if isinstance(date_fin, date):
                days_left = (date_fin - date.today()).days
            elif isinstance(date_fin, str):
                try:
                    date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d").date()
                    days_left = (date_fin_obj - date.today()).days
                except:
                    pass
            
            if 0 < days_left <= 30:
                notifications.append(("⚠️ Contrat à échéance", f"Votre contrat expire dans {days_left} jours", "warning", "urgent"))
            elif days_left <= 0:
                notifications.append(("❌ Contrat expiré", "Votre contrat d'assurance a expiré", "error", "urgent"))
        
        notifications.extend([
            ("✅ Paiement confirmé", "Votre paiement du mois a bien été reçu", "success", "new"),
            ("📄 Nouveau document", "Votre attestation d'assurance est disponible", "info", "new"),
            ("💡 Astuce", "Activez le prélèvement automatique pour ne plus rien oublier", "tip", "old"),
            ("🔄 Renouvellement", "Pensez à renouveler votre contrat avant le 06/07/2026", "warning", "old")
        ])
        
        colors = {
            "warning": {"bg": "#fef3c7", "border": "#f59e0b", "icon": "⚠️"},
            "error": {"bg": "#fee2e2", "border": "#ef4444", "icon": "❌"},
            "success": {"bg": "#dcfce7", "border": "#10b981", "icon": "✅"},
            "info": {"bg": "#eef2ff", "border": "#3b82f6", "icon": "ℹ️"},
            "tip": {"bg": "#fce7f3", "border": "#ec4899", "icon": "💡"}
        }
        
        for i, (title, msg, type_, status) in enumerate(notifications):
            notif_item = self.create_notification_item(title, msg, type_, colors[type_], status == "new")
            layout.addWidget(notif_item)
        
        # Bouton tout marquer comme lu
        mark_read_btn = QPushButton("Tout marquer comme lu")
        mark_read_btn.setCursor(Qt.PointingHandCursor)
        mark_read_btn.setStyleSheet("""
            QPushButton {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 12px;
                font-size: 12px;
                font-weight: 600;
                color: #64748b;
                margin-top: 8px;
            }
            QPushButton:hover {
                background: #f1f5f9;
                color: #1e293b;
            }
        """)
        layout.addWidget(mark_read_btn)
        
        return notif_card

    def create_notification_item(self, title, message, type_, colors, is_new):
        """Crée un élément de notification moderne"""
        
        notif = QFrame()
        notif.setStyleSheet(f"""
            QFrame {{
                background: {colors['bg']};
                border-radius: 16px;
                border-left: 4px solid {colors['border']};
                margin-bottom: 8px;
            }}
        """)
        
        layout = QHBoxLayout(notif)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        # Icône
        icon_container = QFrame()
        icon_container.setFixedSize(44, 44)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {colors['border']}20;
                border-radius: 12px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel(colors['icon'])
        icon_lbl.setStyleSheet(f"font-size: 22px; background: transparent;")
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        # Contenu
        content_layout = QVBoxLayout()
        content_layout.setSpacing(6)
        
        title_layout = QHBoxLayout()
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: {colors['border']};
        """)
        
        title_layout.addWidget(title_lbl)
        title_layout.addStretch()
        
        if is_new:
            new_badge = QLabel("NOUVEAU")
            new_badge.setStyleSheet("""
                background: #ef4444;
                color: white;
                font-size: 9px;
                font-weight: 700;
                padding: 3px 8px;
                border-radius: 20px;
            """)
            title_layout.addWidget(new_badge)
        
        content_layout.addLayout(title_layout)
        
        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet("""
            font-size: 12px;
            color: #475569;
        """)
        msg_lbl.setWordWrap(True)
        content_layout.addWidget(msg_lbl)
        
        layout.addLayout(content_layout, 1)
        
        # Bouton action
        action_btn = QPushButton("Voir")
        action_btn.setCursor(Qt.PointingHandCursor)
        action_btn.setStyleSheet(f"""
            QPushButton {{
                background: {colors['border']};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {colors['border']}dd;
            }}
        """)
        layout.addWidget(action_btn)
        
        return notif
  

    #---------------------------------- GESTION DES FINANCES DU CONTRAT ---------------------------------------------


    def create_finances_tab(self):
        """Onglet des finances et paiement avec données réelles du contrat"""
        tab = QWidget()
        
        # Scroll Area principale
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        # Conteneur interne
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 16, 0, 16)
        container_layout.setSpacing(24)
        
        # Carte récapitulative financière (avec données réelles)
        container_layout.addWidget(self.create_financial_recap_card())
        
        # Historique des paiements
        container_layout.addWidget(self.create_payment_history_table())
        
        # Échéancier des paiements
        if self.contract_data and self.contract_data.get('contract', {}):
            container_layout.addWidget(self.create_payment_schedule_table())
        
        # Espacement final
        container_layout.addSpacing(20)
        
        scroll_area.setWidget(container)
        
        # Layout principal de l'onglet
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
        return tab

    # ==================== CARTE FINANCIÈRE RÉCAPITULATIVE ====================

    def create_financial_recap_card(self):
        """Crée la carte récapitulative financière avec données du contrat"""
        
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
        
        # Titre
        title_layout = QHBoxLayout()
        title_icon = QLabel("💰")
        title_icon.setStyleSheet("font-size: 20px; background: transparent;")
        title_text = QLabel("RÉCAPITULATIF FINANCIER")
        title_text.setStyleSheet("color: white; font-size: 16px; font-weight: 700; letter-spacing: 1px; background: transparent;")
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        # Récupérer les données du contrat
        if self.contract_data:
            amounts = self.contract_data.get('amounts', {})
            payment = self.contract_data.get('payment', {})
            contract_info = self.contract_data.get('contract', {})
        else:
            amounts = self._get_default_amounts()
            payment = self._get_default_payment()
            contract_info = {}
        
        # Montant principal
        amount_layout = self._create_amount_layout(amounts, payment)
        main_layout.addLayout(amount_layout)
        
        # Frais supplémentaires
        if amounts.get('frais'):
            frais_section = self._create_frais_section(amounts.get('frais', {}))
            main_layout.addLayout(frais_section)
        
        # Total TTC
        pttc_layout = self._create_pttc_layout(amounts)
        main_layout.addLayout(pttc_layout)
        
        # Section validation paiement
        validation_section = self._create_payment_validation_section(payment)
        main_layout.addWidget(validation_section)
        
        return recap_frame

    def _create_amount_layout(self, amounts, payment):
        """Crée le layout des montants principaux"""
        amount_layout = QHBoxLayout()
        amount_layout.setSpacing(30)
        
        # Montant total à payer
        left_amount = QVBoxLayout()
        left_amount.setSpacing(8)
        
        total_lbl = QLabel("MONTANT TOTAL À PAYER")
        total_lbl.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px; font-weight: 600; letter-spacing: 1px; background: transparent;")
        
        total_ttc = amounts.get('prime_totale_ttc', amounts.get('total_ttc', 0))
        amount_lbl = QLabel(f"{total_ttc:,.0f}".replace(",", " "))
        amount_lbl.setStyleSheet("color: white; font-size: 42px; font-weight: 800; background: transparent;")
        
        currency_lbl = QLabel("FCFA")
        currency_lbl.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 14px; background: transparent;")
        
        left_amount.addWidget(total_lbl)
        left_amount.addWidget(amount_lbl)
        left_amount.addWidget(currency_lbl)
        
        # Badge de statut paiement
        statut = payment.get('statut_label', 'Non payé')
        statut_color = "#10b981" if statut == "Entièrement payé" else "#f59e0b" if statut == "Paiement partiel" else "#ef4444"
        
        statut_badge = QLabel(statut)
        statut_badge.setStyleSheet(f"""
            background: {statut_color}20;
            color: {statut_color};
            border-radius: 20px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 600;
        """)
        left_amount.addWidget(statut_badge)
        
        # Détails à droite
        right_details = QVBoxLayout()
        right_details.setSpacing(10)
        
        # Prime brute
        prime_brute = amounts.get('prime_pure', amounts.get('gross_premium', 0))
        brut_widget = self._create_detail_row("Prime brute", f"{prime_brute:,.0f}".replace(",", " "), "#ffffff")
        right_details.addLayout(brut_widget)
        
        # Réduction
        reduction = amounts.get('discount', 0)
        if reduction > 0:
            reduction_percent = amounts.get('discount_percent', 0)
            red_widget = self._create_detail_row("Réduction", f"- {reduction:,.0f}".replace(",", " "), "#fbbf24", f"({reduction_percent:.1f}%)")
            right_details.addLayout(red_widget)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: rgba(255,255,255,0.2); max-height: 1px; margin: 5px 0;")
        right_details.addWidget(sep)
        
        # Net à payer
        net_paye = amounts.get('prime_totale_ttc', amounts.get('net_premium', total_ttc))
        net_widget = self._create_detail_row("Net à payer", f"{net_paye:,.0f}".replace(",", " "), "#fbbf24", bold=True)
        right_details.addLayout(net_widget)
        
        # Déjà payé
        deja_paye = payment.get('montant_paye', 0)
        if deja_paye > 0:
            paye_widget = self._create_detail_row("Déjà payé", f"{deja_paye:,.0f}".replace(",", " "), "#10b981")
            right_details.addLayout(paye_widget)
        
        amount_layout.addLayout(left_amount, 1)
        amount_layout.addLayout(right_details, 1)
        
        return amount_layout

    def _create_frais_section(self, frais):
        """Crée la section des frais"""
        frais_layout = QVBoxLayout()
        
        frais_title = QLabel("📋 DÉTAIL DES FRAIS")
        frais_title.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 11px; font-weight: 600; letter-spacing: 1px; margin-top: 10px; background: transparent;")
        frais_layout.addWidget(frais_title)
        
        frais_grid = QGridLayout()
        frais_grid.setSpacing(10)
        frais_grid.setContentsMargins(0, 5, 0, 5)
        
        frais_items = [
            ("📄 Carte Rose", frais.get('carte_rose', 0)),
            ("🔧 Accessoires", frais.get('accessoires', 0)),
            ("📊 TVA", frais.get('tva', 0)),
            ("📁 Fichier ASAC", frais.get('asac_fee', 0)),
            ("🎫 Vignette", frais.get('vignette', 0)),
            ("📜 Timbre", frais.get('timbre', 0)),
        ]
        
        for i, (label, value) in enumerate(frais_items):
            if value > 0:
                item_layout = self._create_frais_row(label, value)
                frais_grid.addLayout(item_layout, i // 3, i % 3)
        
        frais_layout.addLayout(frais_grid)
        return frais_layout

    def _create_pttc_layout(self, amounts):
        """Crée le layout du total TTC"""
        pttc_layout = QHBoxLayout()
        pttc_layout.setContentsMargins(0, 15, 0, 0)
        
        pttc_label = QLabel("TOTAL TOUTES TAXES COMPRISES (PTTC)")
        pttc_label.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 13px; font-weight: 600; background: transparent;")
        
        total_ttc = amounts.get('prime_totale_ttc', amounts.get('total_ttc', 0))
        pttc_value = QLabel(f"{total_ttc:,.0f}".replace(",", " "))
        pttc_value.setStyleSheet("color: #fbbf24; font-size: 28px; font-weight: 800; background: transparent;")
        
        pttc_currency = QLabel("FCFA")
        pttc_currency.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 14px; background: transparent;")
        
        pttc_layout.addWidget(pttc_label)
        pttc_layout.addStretch()
        pttc_layout.addWidget(pttc_value)
        pttc_layout.addWidget(pttc_currency)
        
        return pttc_layout

    def _create_payment_validation_section(self, payment):
        """Crée la section de validation de paiement"""
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
        
        # Titre
        validation_title = QLabel("✅ VALIDATION DU PAIEMENT")
        validation_title.setStyleSheet("color: white; font-size: 13px; font-weight: 700; letter-spacing: 1px; background: transparent;")
        validation_layout.addWidget(validation_title)
        
        # Mode de paiement
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(15)
        
        mode_label = QLabel("Mode de paiement :")
        mode_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px; background: transparent;")
        
        self.payment_mode = QComboBox()
        self.payment_mode.addItems(["Espèces", "Carte bancaire", "Virement", "Chèque", "Orange Money", "MTN Mobile Money"])
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
        
        reste_a_payer = payment.get('reste_a_payer', 0)
        montant_label = QLabel(f"Montant versé (Reste: {reste_a_payer:,.0f} FCFA) :")
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
        self.montant_verse.textChanged.connect(self._update_balance_display)
        
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
        
        # Statut
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
        
        # Bouton validation
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
        """)
        btn_validate.clicked.connect(self._validate_payment)
        validation_layout.addWidget(btn_validate)
        
        return validation_frame

    # ==================== HISTORIQUE DES PAIEMENTS ====================

    def create_payment_history_table(self):
        """Crée le tableau d'historique des paiements"""
        
        history_card = QFrame()
        history_card.setProperty("class", "InfoCard")
        history_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 24px;
            }
        """)
        
        layout = QVBoxLayout(history_card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title_icon = QLabel("📜")
        title_icon.setStyleSheet("""
            font-size: 24px;
            background: #eef2ff;
            padding: 10px;
            border-radius: 16px;
        """)
        
        title_text = QLabel("HISTORIQUE DES PAIEMENTS")
        title_text.setStyleSheet("font-size: 16px; font-weight: 800; color: #0f172a;")
        
        subtitle_text = QLabel("Suivi des transactions effectuées")
        subtitle_text.setStyleSheet("font-size: 12px; color: #64748b;")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_text)
        title_layout.addWidget(subtitle_text)
        
        header_layout.addWidget(title_icon)
        header_layout.addSpacing(12)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Badge nombre de paiements
        payment_count = len(self.payment_history) if hasattr(self, 'payment_history') and self.payment_history else 0
        count_badge = QLabel(f"{payment_count} paiement(s)")
        count_badge.setStyleSheet("""
            background: #f1f5f9;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            color: #475569;
        """)
        header_layout.addWidget(count_badge)
        
        layout.addLayout(header_layout)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height: 1px; margin: 8px 0;")
        layout.addWidget(sep)
        
        # Tableau
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Date", "Mode", "Montant", "Statut"])
        
        for col in range(4):
            if col in [0, 1, 3]:
                table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
            else:
                table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
        
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setFocusPolicy(Qt.NoFocus)
        table.setFixedHeight(min(300, 50 + payment_count * 45) if payment_count > 0 else 100)
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
        
        if hasattr(self, 'payment_history') and self.payment_history:
            for row, payment in enumerate(self.payment_history):
                table.insertRow(row)
                
                # Date
                date_str = payment.get('date', '')
                if hasattr(payment, 'date_paiement'):
                    date_str = payment.date_paiement.strftime('%d/%m/%Y') if payment.date_paiement else ''
                date_item = QTableWidgetItem(date_str)
                date_item.setFont(QFont("Segoe UI", 10))
                table.setItem(row, 0, date_item)
                
                # Mode
                mode_str = payment.get('mode', '')
                if hasattr(payment, 'mode_paiement'):
                    mode_str = payment.mode_paiement.value if hasattr(payment.mode_paiement, 'value') else str(payment.mode_paiement)
                mode_item = QTableWidgetItem(mode_str)
                mode_item.setFont(QFont("Segoe UI", 10))
                table.setItem(row, 1, mode_item)
                
                # Montant
                amount = payment.get('montant', 0)
                if hasattr(payment, 'montant'):
                    amount = payment.montant
                amount_item = QTableWidgetItem(f"{amount:,.0f}".replace(",", " "))
                amount_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                table.setItem(row, 2, amount_item)
                
                # Statut
                status_item = QTableWidgetItem("✅ Confirmé")
                status_item.setForeground(QColor("#10b981"))
                status_item.setFont(QFont("Segoe UI", 10))
                table.setItem(row, 3, status_item)
        else:
            # Aucun paiement
            table.setRowCount(1)
            no_data_item = QTableWidgetItem("Aucun paiement enregistré")
            no_data_item.setTextAlignment(Qt.AlignCenter)
            table.setSpan(0, 0, 1, 4)
            table.setItem(0, 0, no_data_item)
        
        layout.addWidget(table)
        
        return history_card
    # ==================== ÉCHÉANCIER DES PAIEMENTS ====================

    def create_payment_schedule_table(self):
        """Crée le tableau d'échéancier des paiements"""
        
        schedule_card = QFrame()
        schedule_card.setProperty("class", "InfoCard")
        schedule_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 24px;
            }
        """)
        
        layout = QVBoxLayout(schedule_card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title_icon = QLabel("📅")
        title_icon.setStyleSheet("""
            font-size: 24px;
            background: #eef2ff;
            padding: 10px;
            border-radius: 16px;
        """)
        
        title_text = QLabel("ÉCHÉANCIER DES PAIEMENTS")
        title_text.setStyleSheet("font-size: 16px; font-weight: 800; color: #0f172a;")
        
        subtitle_text = QLabel("Prochaines échéances à venir")
        subtitle_text.setStyleSheet("font-size: 12px; color: #64748b;")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_text)
        title_layout.addWidget(subtitle_text)
        
        header_layout.addWidget(title_icon)
        header_layout.addSpacing(12)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height: 1px; margin: 8px 0;")
        layout.addWidget(sep)
        
        if self.payment_schedule:
            for echeance in self.payment_schedule[:5]:
                item = self._create_schedule_item_widget(echeance)
                layout.addWidget(item)
        else:
            no_data_lbl = QLabel("Aucune échéance planifiée")
            no_data_lbl.setStyleSheet("font-size: 13px; color: #64748b; padding: 20px; text-align: center;")
            no_data_lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_lbl)
        
        return schedule_card

    def _create_schedule_item_widget(self, echeance):
        """Crée un widget pour un élément d'échéancier"""
        
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
                margin-bottom: 8px;
            }
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        # Numéro de mensualité
        numero_lbl = QLabel(f"{echeance.get('numero', '')}")
        numero_lbl.setFixedSize(40, 40)
        numero_lbl.setAlignment(Qt.AlignCenter)
        numero_lbl.setStyleSheet("""
            background: #eef2ff;
            color: #3b82f6;
            border-radius: 20px;
            font-size: 16px;
            font-weight: 800;
        """)
        
        layout.addWidget(numero_lbl)
        
        # Informations
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        
        date_lbl = QLabel(f"📅 {echeance.get('date_echeance', '')}")
        date_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #1e293b;")
        
        montant = echeance.get('montant', 0)
        montant_lbl = QLabel(f"{montant:,.0f} FCFA".replace(",", " "))
        montant_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #3b82f6;")
        
        info_layout.addWidget(date_lbl)
        info_layout.addWidget(montant_lbl)
        
        layout.addLayout(info_layout, 1)
        
        # Statut
        statut = echeance.get('statut', 'à_venir')
        if statut == 'paye':
            status_lbl = QLabel("✅ Payé")
            status_lbl.setStyleSheet("background: #10b98115; color: #10b981; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 600;")
        else:
            status_lbl = QLabel("⏳ À venir")
            status_lbl.setStyleSheet("background: #f59e0b15; color: #f59e0b; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 600;")
        
        layout.addWidget(status_lbl)
        
        return item

    # ==================== MÉTHODES UTILITAIRES ====================

    def _create_detail_row(self, label, value, color="#ffffff", suffix="", bold=False):
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

    def _create_frais_row(self, label, value):
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

    def _update_balance_display(self):
        """Met à jour l'affichage du solde"""
        try:
            if self.contract_data:
                reste_a_payer = self.contract_data.get('payment', {}).get('reste_a_payer', 0)
            else:
                reste_a_payer = float(self.data.get('prime_nette', 0))
            
            montant_verse = self._get_montant_verse_value()
            solde = reste_a_payer - montant_verse
            
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
        except:
            pass

    def _get_montant_verse_value(self):
        """Récupère la valeur du montant versé"""
        try:
            text = self.montant_verse.text()
            if not text:
                return 0.0
            cleaned = text.replace(" ", "").replace(",", ".")
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0

    def _validate_payment(self):
        """Version utilisant le contrôleur"""
        montant_verse = self._get_montant_verse_value()
        
        if montant_verse <= 0:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir un montant valide")
            return
        
        if not self.payment_ctrl:
            QMessageBox.warning(self, "Erreur", "Contrôleur de paiement non disponible")
            return
        
        # Récupérer l'ID du véhicule
        vehicle_id = self.data.get('id')
        if not vehicle_id and hasattr(self.data, 'id'):
            vehicle_id = self.data.id
        
        if not vehicle_id:
            QMessageBox.warning(self, "Erreur", "ID du véhicule non trouvé")
            return
        
        # Récupérer le contrat via le contrôleur
        contrat = self.contract_ctrl.get_contract_by_vehicle(vehicle_id)
        
        if not contrat:
            QMessageBox.warning(self, "Erreur", f"Aucun contrat trouvé pour le véhicule {vehicle_id}")
            return
        
        print(f"Contrat trouvé: ID={contrat.id}")
        
        reste_a_payer = contrat.prime_totale_ttc - contrat.montant_paye
        
        if montant_verse > reste_a_payer + 0.01:
            reply = QMessageBox.question(
                self,
                "Montant excessif",
                f"Le montant versé ({montant_verse:,.0f} FCFA) dépasse le solde restant ({reste_a_payer:,.0f} FCFA).\n\nSouhaitez-vous continuer ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Mode de paiement
        mode_text = self.payment_mode.currentText()
        mode_mapping = {
            "Espèces": "CASH",
            "Carte bancaire": "CARD",
            "Virement": "TRANSFER",
            "Chèque": "CHECK",
            "Orange Money": "ORANGE_MONEY",
            "MTN Mobile Money": "MTN_MONEY",
        }
        mode = mode_mapping.get(mode_text, "CASH")
        
        # Appeler le contrôleur AVEC contrat_id
        success, payment, message = self.payment_ctrl.create_payment(
            data={
                'contrat_id': contrat.id,  # ← CRUCIAL: passer l'ID du contrat
                'montant': montant_verse,
                'mode_paiement': mode,
                'notes': f"Paiement effectué via {mode_text}"
            },
            user_id=self._get_current_user_id(),
            ip=self._get_local_ip()
        )
        
        if success:
            QMessageBox.information(
                self,
                "Paiement validé",
                f"Paiement de {montant_verse:,.0f} FCFA effectué par {mode_text}\n\n"
                f"Reçu: {payment.numero_recu}\n\n"
                f"Solde restant : {max(0, reste_a_payer - montant_verse):,.0f} FCFA"
            )
            self.montant_verse.clear()
            self._load_contract_data()
        else:
            QMessageBox.warning(self, "Erreur", f"Erreur: {message}")
         
    def _get_local_ip(self) -> str:
        """Récupère l'IP locale"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _get_current_user_id(self):
        """Récupère l'ID de l'utilisateur actuel"""
        if self.controller and hasattr(self.controller, 'get_current_user_id'):
            return self.controller.get_current_user_id()
        return 1  # Valeur par défaut

    def _get_default_amounts(self):
        """Retourne des montants par défaut depuis self.data"""
        return {
            'prime_pure': float(self.data.get('prime_nette', 0)),
            'gross_premium': float(self.data.get('prime_brute', 0)),
            'prime_totale_ttc': float(self.data.get('prime_nette', 0)),
            'total_ttc': float(self.data.get('prime_nette', 0)),
            'discount': float(self.data.get('prime_brute', 0)) - float(self.data.get('prime_nette', 0)),
            'discount_percent': 0,
            'frais': {
                'carte_rose': float(self.data.get('carte_rose', 0)),
                'accessoires': float(self.data.get('accessoires', 0)),
                'tva': float(self.data.get('tva', 0)),
                'asac_fee': float(self.data.get('fichier_asac', 0)),
                'vignette': float(self.data.get('vignette', 0)),
            }
        }

    def _get_default_payment(self):
        """Retourne des informations de paiement par défaut"""
        prime = float(self.data.get('prime_nette', 0))
        return {
            'montant_paye': 0,
            'reste_a_payer': prime,
            'statut': 'NON_PAYE',
            'statut_label': 'Non payé'
        }