"""
Onglet Client du Dossier 360 - Design 3 colonnes
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGroupBox,
    QGridLayout, QPushButton, QMessageBox, QScrollArea, QListWidget,
    QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from typing import Optional, List, Dict

from addons.sinistres.views.widgets.dashboard_widgets import (
    KpiCard, ProgressBicolor, GaugeWidget, PieChartWidget, MapPlaceholder
)


class ClientTab(QWidget):
    """Onglet Client - Vue enrichie 3 colonnes"""
    
    def __init__(self, dossier_360):
        super().__init__()
        self.dossier_360 = dossier_360
        self._client = None
        self._contrat = None
        self._vehicule = None
        self.setup_ui()
    
    # ============================================================
    # UI
    # ============================================================
    
    def setup_ui(self):
        # Scroll principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: #f8fafc;")
        
        content = QWidget()
        content.setStyleSheet("background-color: #f8fafc;")
        
        main_layout = QHBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 3 colonnes
        main_layout.addWidget(self._build_col_left(), 1)
        main_layout.addWidget(self._build_col_center(), 1)
        main_layout.addWidget(self._build_col_right(), 1)
        
        scroll.setWidget(content)
        
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)
    
    # ============================================================
    # COLONNE GAUCHE
    # ============================================================
    
    def _build_col_left(self) -> QWidget:
        col = QWidget()
        layout = QVBoxLayout(col)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # --- Carte Contrat ---
        layout.addWidget(self._build_card_contrat())
        
        # --- Carte Véhicule ---
        layout.addWidget(self._build_card_vehicule())
        
        # --- Carte Historique ---
        layout.addWidget(self._build_card_historique())
        
        # --- Boutons d'action ---
        layout.addLayout(self._build_action_buttons())
        
        layout.addStretch()
        return col
    
    def _build_card_contrat(self) -> QFrame:
        card = self._make_card("📄 Contrat", "#3b82f6")
        grid = QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(10)
        
        # Ligne 1 : N° Police
        grid.addWidget(self._key("N° Police :"), 0, 0)
        self.lbl_contrat_numero = self._value("—")
        grid.addWidget(self.lbl_contrat_numero, 0, 1)
        
        # Badge statut
        self.lbl_contrat_statut = QLabel("—")
        self.lbl_contrat_statut.setStyleSheet(self._badge_style("#f59e0b"))
        self.lbl_contrat_statut.setAlignment(Qt.AlignCenter)
        self.lbl_contrat_statut.setMaximumWidth(100)
        grid.addWidget(self.lbl_contrat_statut, 0, 2)
        
        # Ligne 2 : Type
        grid.addWidget(self._key("Type :"), 1, 0)
        self.lbl_contrat_type = self._value("—")
        grid.addWidget(self.lbl_contrat_type, 1, 1, 1, 2)
        
        # Ligne 3 : Montant payé + barre
        grid.addWidget(self._key("Montant payé :"), 2, 0)
        self.lbl_contrat_paye = self._value("—", bold=True)
        grid.addWidget(self.lbl_contrat_paye, 2, 1, 1, 2)
        
        self.progress_contrat = ProgressBicolor()
        grid.addWidget(self.progress_contrat, 3, 0, 1, 3)
        
        # Ligne 4 : Solde
        grid.addWidget(self._key("Solde restant :"), 4, 0)
        self.lbl_contrat_solde = self._value("—", color="#ef4444", bold=True)
        grid.addWidget(self.lbl_contrat_solde, 4, 1, 1, 2)
        
        # Ligne 5 : Période
        grid.addWidget(self._key("Période :"), 5, 0)
        self.lbl_contrat_periode = self._value("—")
        grid.addWidget(self.lbl_contrat_periode, 5, 1, 1, 2)
        
        card.layout().addLayout(grid)
        return card
    
    def _build_card_vehicule(self) -> QFrame:
        card = self._make_card("🚗 Véhicule assuré", "#22c55e")
        grid = QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(10)
        
        # Ligne 1 : Immat
        grid.addWidget(self._key("Immatriculation :"), 0, 0)
        self.lbl_veh_immat = self._value("—", bold=True)
        grid.addWidget(self.lbl_veh_immat, 0, 1)
        
        # Badge PROFORMAT
        self.lbl_veh_statut = QLabel("—")
        self.lbl_veh_statut.setStyleSheet(self._badge_style("#f59e0b"))
        self.lbl_veh_statut.setAlignment(Qt.AlignCenter)
        self.lbl_veh_statut.setMaximumWidth(100)
        grid.addWidget(self.lbl_veh_statut, 0, 2)
        
        # Ligne 2 : Année
        grid.addWidget(self._key("Année :"), 1, 0)
        self.lbl_veh_annee = self._value("—")
        grid.addWidget(self.lbl_veh_annee, 1, 1, 1, 2)
        
        # Ligne 3 : Valeur neuve
        grid.addWidget(self._key("Valeur neuve :"), 2, 0)
        self.lbl_veh_valeur = self._value("—", bold=True)
        grid.addWidget(self.lbl_veh_valeur, 2, 1, 1, 2)
        
        self.progress_veh = ProgressBicolor()
        grid.addWidget(self.progress_veh, 3, 0, 1, 3)
        
        card.layout().addLayout(grid)
        return card
    
    def _build_card_historique(self) -> QFrame:
        card = self._make_card("📊 Historique client", "#ef4444")
        grid = QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(10)
        
        # Ligne 1 : Sinistres déclarés
        grid.addWidget(self._key("Sinistres déclarés :"), 0, 0)
        self.lbl_hist_sinistres = self._value("0", bold=True)
        grid.addWidget(self.lbl_hist_sinistres, 0, 1)
        
        # Pastilles colorées (5 max)
        self.hist_dots = QLabel("")
        self.hist_dots.setStyleSheet("font-size: 14px;")
        grid.addWidget(self.hist_dots, 0, 2)
        
        # Ligne 2 : Ratio S/P
        grid.addWidget(self._key("Ratio S/P estimé :"), 1, 0)
        self.lbl_hist_ratio = self._value("0.00%", bold=True)
        grid.addWidget(self.lbl_hist_ratio, 1, 1)
        
        # Mini-jauge (progress)
        self.progress_ratio = ProgressBicolor()
        grid.addWidget(self.progress_ratio, 2, 0, 1, 3)
        
        card.layout().addLayout(grid)
        return card
    
    def _build_action_buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        
        for icon, text, slot in [
            ("👤", "Voir la fiche client", self._on_voir_client),
            ("📄", "Voir le contrat", self._on_voir_contrat),
            ("🚗", "Voir le véhicule", self._on_voir_vehicule),
        ]:
            btn = QPushButton(f"{icon} {text}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 11px;
                    color: #1e293b;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #e8f0fe;
                    border-color: #1a73e8;
                    color: #1a73e8;
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        
        return row
    
    # ============================================================
    # COLONNE CENTRE
    # ============================================================
    
    def _build_col_center(self) -> QWidget:
        col = QWidget()
        layout = QVBoxLayout(col)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Carte Dossiers critiques
        layout.addWidget(self._build_card_dossiers_critiques())
        
        # Carte Risque
        layout.addWidget(self._build_card_risque())
        
        # Carte Jauge risque global
        layout.addWidget(self._build_card_gauge())
        
        layout.addStretch()
        return col
    
    def _build_card_dossiers_critiques(self) -> QFrame:
        card = self._make_card("📋 Dossiers critiques récents", "#8b5cf6")
        
        self.table_dossiers = QTableWidget()
        self.table_dossiers.setColumnCount(5)
        self.table_dossiers.setHorizontalHeaderLabels([
            "Dossier", "Client", "Branche", "Date", "Montant payé"
        ])
        self.table_dossiers.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_dossiers.setMaximumHeight(180)
        self.table_dossiers.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                gridline-color: #f1f5f9;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 6px;
                font-weight: bold;
                font-size: 11px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        card.layout().addWidget(self.table_dossiers)
        return card
    
    def _build_card_risque(self) -> QFrame:
        card = self._make_card("⚠️ Risque", "#f59e0b")
        grid = QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(10)
        
        grid.addWidget(self._key("Statut :"), 0, 0)
        self.lbl_risque_statut = self._value("—", bold=True)
        grid.addWidget(self.lbl_risque_statut, 0, 1)
        
        self.lbl_risque_badge = QLabel("—")
        self.lbl_risque_badge.setStyleSheet(self._badge_style("#f59e0b"))
        self.lbl_risque_badge.setAlignment(Qt.AlignCenter)
        self.lbl_risque_badge.setMaximumWidth(100)
        grid.addWidget(self.lbl_risque_badge, 0, 2)
        
        grid.addWidget(self._key("Prime TTC :"), 1, 0)
        self.lbl_risque_prime = self._value("—", bold=True)
        grid.addWidget(self.lbl_risque_prime, 1, 1, 1, 2)
        
        grid.addWidget(self._key("Montant payé :"), 2, 0)
        self.lbl_risque_paye = self._value("—", bold=True)
        grid.addWidget(self.lbl_risque_paye, 2, 1, 1, 2)
        
        self.progress_risque = ProgressBicolor()
        grid.addWidget(self.progress_risque, 3, 0, 1, 3)
        
        card.layout().addLayout(grid)
        return card
    
    def _build_card_gauge(self) -> QFrame:
        card = self._make_card("📊 Tableau de risque global", "#ef4444")
        
        self.gauge = GaugeWidget()
        card.layout().addWidget(self.gauge)
        
        return card
    
    # ============================================================
    # COLONNE DROITE
    # ============================================================
    
    def _build_col_right(self) -> QWidget:
        col = QWidget()
        layout = QVBoxLayout(col)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Camembert
        layout.addWidget(self._build_card_pie())
        
        # Carte géographique
        layout.addWidget(self._build_card_map())
        
        layout.addStretch()
        return col
    
    def _build_card_pie(self) -> QFrame:
        card = self._make_card("🥧 Répartition des risques", "#06b6d4")
        
        self.pie = PieChartWidget()
        self.pie.set_data([
            ("Incendie", 50, "#3b82f6"),
            ("Auto", 30, "#22c55e"),
            ("Autres", 20, "#ef4444"),
        ])
        card.layout().addWidget(self.pie)
        
        # Légende
        legend = QHBoxLayout()
        for label, color in [("Incendie", "#3b82f6"), ("Auto", "#22c55e"), ("Autres", "#ef4444")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 14px;")
            legend.addWidget(dot)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #64748b; font-size: 11px;")
            legend.addWidget(lbl)
        legend.addStretch()
        card.layout().addLayout(legend)
        
        return card
    
    def _build_card_map(self) -> QFrame:
        card = self._make_card("🗺️ Carte géographique", "#10b981")
        
        self.map = MapPlaceholder()
        card.layout().addWidget(self.map)
        
        return card
    
    # ============================================================
    # HELPERS UI
    # ============================================================
    
    def _make_card(self, title: str, color: str = "#1a73e8") -> QFrame:
        """Carte blanche avec titre coloré"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 15)
        layout.setSpacing(10)
        
        # En-tête
        header = QHBoxLayout()
        header.setSpacing(8)
        
        icon = QLabel(title.split()[0])
        icon.setStyleSheet(f"font-size: 16px; color: {color};")
        header.addWidget(icon)
        
        title_lbl = QLabel(" ".join(title.split()[1:]))
        title_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        header.addWidget(title_lbl)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #f1f5f9; max-height: 1px; border: none;")
        layout.addWidget(sep)
        
        return card
    
    def _key(self, text: str) -> QLabel:
        """Label de clé (à gauche)"""
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        return lbl
    
    def _value(self, text: str, color: str = "#1e293b", bold: bool = False) -> QLabel:
        """Label de valeur (à droite)"""
        lbl = QLabel(text)
        weight = "bold" if bold else "500"
        lbl.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: {weight};")
        return lbl
    
    def _badge_style(self, color: str) -> str:
        """Style pour badge coloré"""
        return f"""
            background-color: {color};
            color: white;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """
    
    # ============================================================
    # CHARGEMENT DES DONNÉES
    # ============================================================
    
    def update_data(self, data):
        """Met à jour l'onglet avec les données du sinistre"""
        try:
            # Charger les infos depuis le sinistre
            client_id = data.get('client_id')
            contrat_id = data.get('contrat_id')
            
            self._client = self._charger_client(client_id)
            self._contrat = self._charger_contrat(contrat_id)
            self._vehicule = self._charger_vehicule(self._contrat)
            
            # Mettre à jour chaque carte
            self._update_contrat()
            self._update_vehicule()
            self._update_historique(client_id, data.get('id'))
            self._update_risque()
            self._update_dossiers_critiques(client_id)
            self._update_carte()
        
        except Exception as e:
            print(f"Erreur update ClientTab: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_contrat(self):
        c = self._contrat
        if not c:
            self.lbl_contrat_numero.setText("Contrat introuvable")
            return
        
        self.lbl_contrat_numero.setText(c.get('numero_police', '—'))
        
        statut = str(c.get('statut', '—')).upper()
        self.lbl_contrat_statut.setText(statut)
        color = {"ACTIF": "#22c55e", "PROFORMAT": "#f59e0b",
                 "EXPIRE": "#ef4444", "RESILIE": "#64748b"}.get(statut, "#64748b")
        self.lbl_contrat_statut.setStyleSheet(self._badge_style(color))
        
        self.lbl_contrat_type.setText(c.get('type_contrat') or '—')
        
        prime = c.get('prime_totale_ttc') or 0
        paye = c.get('montant_paye') or 0
        solde = max(0, prime - paye)
        percent = (paye / prime * 100) if prime > 0 else 0
        
        self.lbl_contrat_paye.setText(self._format_montant(paye))
        self.lbl_contrat_solde.setText(self._format_montant(solde))
        self.progress_contrat.set_values(percent, "#22c55e", "#f59e0b")
        
        debut = self._format_date(c.get('date_debut'))
        fin = self._format_date(c.get('date_fin'))
        self.lbl_contrat_periode.setText(f"{debut} → {fin}")
    
    def _update_vehicule(self):
        v = self._vehicule
        if not v:
            self.lbl_veh_immat.setText("Aucun véhicule")
            self.lbl_veh_statut.setText("—")
            return
        
        self.lbl_veh_immat.setText(v.get('immatriculation', '—'))
        
        # Badge statut contrat
        statut = str(self._contrat.get('statut', '—')).upper() if self._contrat else '—'
        self.lbl_veh_statut.setText(statut)
        color = {"ACTIF": "#22c55e", "PROFORMAT": "#f59e0b"}.get(statut, "#64748b")
        self.lbl_veh_statut.setStyleSheet(self._badge_style(color))
        
        self.lbl_veh_annee.setText(str(v.get('annee') or '—'))
        
        valeur = v.get('valeur_neuf') or 0
        self.lbl_veh_valeur.setText(self._format_montant(valeur))
        self.progress_veh.set_values(100, "#3b82f6", "#e2e8f0")
    
    def _update_historique(self, client_id, sinistre_id):
        if not client_id:
            return
        
        try:
            sc = self.dossier_360.sinistre_controller
            sinistres = sc.rechercher_sinistres({'client_id': client_id}) or []
            autres = [s for s in sinistres if s.get('id') != sinistre_id]
            
            nb = len(autres)
            self.lbl_hist_sinistres.setText(str(nb))
            
            # Pastilles (max 5)
            dots = "●" * min(nb, 5) + "○" * max(0, 5 - nb)
            self.hist_dots.setText(dots)
            self.hist_dots.setStyleSheet(
                f"color: #ef4444; font-size: 14px;" if nb > 0 else "color: #e2e8f0; font-size: 14px;"
            )
            
            montant = sum(s.get('montant_net', 0) or 0 for s in autres)
            prime = (self._contrat or {}).get('prime_totale_ttc', 0) or 1
            ratio = (montant / prime * 100) if prime > 0 else 0
            self.lbl_hist_ratio.setText(f"{ratio:.2f}%")
            self.progress_ratio.set_values(min(ratio, 100), "#22c55e", "#ef4444")
        except Exception as e:
            print(f"Erreur historique: {e}")
    
    def _update_risque(self):
        c = self._contrat or {}
        statut = str(c.get('statut', '—')).upper()
        
        self.lbl_risque_statut.setText(statut)
        self.lbl_risque_badge.setText(statut)
        color = {"ACTIF": "#22c55e", "PROFORMAT": "#f59e0b"}.get(statut, "#64748b")
        self.lbl_risque_badge.setStyleSheet(self._badge_style(color))
        
        prime = c.get('prime_totale_ttc') or 0
        paye = c.get('montant_paye') or 0
        self.lbl_risque_prime.setText(self._format_montant(prime))
        self.lbl_risque_paye.setText(self._format_montant(paye))
        
        percent = (paye / prime * 100) if prime > 0 else 0
        self.progress_risque.set_values(percent, "#22c55e", "#ef4444")
        
        # Jauge
        self.gauge.set_value(percent, 100)
    
    def _update_dossiers_critiques(self, client_id):
        if not client_id:
            self.table_dossiers.setRowCount(0)
            return
        
        try:
            sc = self.dossier_360.sinistre_controller
            sinistres = sc.rechercher_sinistres({'client_id': client_id, 'limit': 5}) or []
            self.table_dossiers.setRowCount(len(sinistres))
            
            for i, s in enumerate(sinistres):
                self.table_dossiers.setItem(i, 0, QTableWidgetItem(s.get('numero_sinistre', '')))
                self.table_dossiers.setItem(i, 1, QTableWidgetItem(s.get('client_nom', '—')))
                self.table_dossiers.setItem(i, 2, QTableWidgetItem(s.get('branche', '')))
                self.table_dossiers.setItem(i, 3, QTableWidgetItem(
                    s.get('date_survenance', '')[:10] if s.get('date_survenance') else ''
                ))
                self.table_dossiers.setItem(i, 4, QTableWidgetItem(
                    self._format_montant(s.get('montant_net', 0))
                ))
        except Exception as e:
            print(f"Erreur dossiers critiques: {e}")
    
    def _update_carte(self):
        """Met à jour la carte avec la localisation du client"""
        if self._client:
            ville = self._client.get('ville', 'Inconnue')
            self.map.lbl_info.setText(f"Zone : {ville}")
    
    # ============================================================
    # CHARGEMENT BACKEND
    # ============================================================
    
    def _charger_client(self, client_id) -> Optional[dict]:
        if not client_id:
            return None
        try:
            from addons.sinistres.controllers.automobile_controller import AutomobileController
            ac = AutomobileController()
            ac.set_current_user(self.dossier_360.user)
            return ac.get_contact(client_id)
        except Exception as e:
            print(f"Erreur client: {e}")
            return None
    
    def _charger_contrat(self, contrat_id) -> Optional[dict]:
        if not contrat_id:
            return None
        try:
            from addons.sinistres.controllers.automobile_controller import AutomobileController
            ac = AutomobileController()
            ac.set_current_user(self.dossier_360.user)
            return ac.get_contrat(contrat_id)
        except Exception as e:
            print(f"Erreur contrat: {e}")
            return None
    
    def _charger_vehicule(self, contrat) -> Optional[dict]:
        if not contrat:
            return None
        vid = contrat.get('vehicle_id')
        if not vid:
            return None
        try:
            from addons.sinistres.controllers.automobile_controller import AutomobileController
            ac = AutomobileController()
            ac.set_current_user(self.dossier_360.user)
            return ac.service.get_vehicle(vid)
        except Exception:
            return None
    
    # ============================================================
    # FORMATAGE
    # ============================================================
    
    def _format_montant(self, montant) -> str:
        if montant is None:
            return "—"
        try:
            return f"{float(montant):,.0f} FCFA".replace(",", " ")
        except (ValueError, TypeError):
            return str(montant)
    
    def _format_date(self, date_val) -> str:
        if not date_val:
            return "—"
        try:
            s = str(date_val)
            if 'T' in s:
                s = s.split('T')[0]
            parts = s.split('-')
            if len(parts) == 3:
                return f"{parts[2]}/{parts[1]}/{parts[0]}"
            return s
        except Exception:
            return str(date_val)
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def _on_voir_client(self):
        cid = self.dossier_360.sinistre_data.get('client_id') if self.dossier_360.sinistre_data else None
        if not cid:
            QMessageBox.warning(self, "Info", "Aucun client associé")
            return
        QMessageBox.information(self, "Client", f"Ouverture de la fiche client #{cid}")
    
    def _on_voir_contrat(self):
        cid = self.dossier_360.sinistre_data.get('contrat_id') if self.dossier_360.sinistre_data else None
        if not cid:
            QMessageBox.warning(self, "Info", "Aucun contrat associé")
            return
        QMessageBox.information(self, "Contrat", f"Ouverture du contrat #{cid}")
    
    def _on_voir_vehicule(self):
        QMessageBox.information(self, "Véhicule", "Ouverture de la fiche véhicule")