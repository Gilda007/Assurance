

"""
Tableau de bord LOMETA - Command Center
Design inspiré des dashboards modernes avec cartes et graphiques
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QMessageBox,
    QPushButton, QMenu, QHeaderView, QFileDialog, QGridLayout,
    QScrollArea, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QAction, QColor, QFont

from datetime import datetime, timedelta
from typing import Optional, List, Dict

from addons.sinistres.views.widgets.chart_widgets import (
    DonutChart, LineChart, StackedBarChart, KpiCircleCard, CircleValue
)
from addons.sinistres.views.widgets.connected_users import ConnectedUsersCard
from addons.sinistres.views.widgets.finance_widgets import (
    FinanceSummaryCard, FinancePipelineCard
)

from addons.sinistres.views.widgets.shadow_helper import apply_card_shadow
from addons.sinistres.views.widgets.recent_claims_widget import RecentClaimsWidget
from addons.sinistres.views.widgets.performance_widgets import (
    PerformanceCard, AlertsBanner, TopClaimsCard
)
# ============================================================
# CONFIGURATION DES STATUTS
# ============================================================

STATUT_COLORS = {
    'OUVERT': '#f59e0b',
    'EN_INSTRUCTION': '#3b82f6',
    'EN_EXPERTISE': '#8b5cf6',
    'EN_EVALUATION': '#ec4899',
    'VALIDE': '#06b6d4',
    'EN_REGLEMENT': '#f97316',
    'EN_RECOURS': '#ef4444',
    'CLOTURE': '#22c55e',
    'REOUVERT': '#dc2626',
}

BRANCHE_COLORS = {
    'AUTO': '#3b82f6',
    'INCENDIE': '#ef4444',
    'RC': '#f59e0b',
    'TRANSPORT': '#8b5cf6',
    'SANTE': '#22c55e',
}

IMPRESSIONS_PAR_STATUT = {
    'OUVERT': [('ACCUSE_RECEPTION', '📩 Accusé'), ('FICHE_DECLARATION', '📄 Fiche')],
    'EN_INSTRUCTION': [('FICHE_INSTRUCTION', '📋 Fiche')],
    'EN_EXPERTISE': [('FICHE_EXPERTISE', '🔬 Fiche')],
    'EN_EVALUATION': [('FICHE_EVALUATION', '💰 Fiche')],
    'VALIDE': [('FICHE_VALIDEE', '✅ Fiche')],
    'EN_REGLEMENT': [('FICHE_REGLEMENT', '💳 Fiche')],
    'EN_RECOURS': [('FICHE_RECOURS', '⚖️ Fiche')],
    'CLOTURE': [('FICHE_DEFINITIVE', '📁 Fiche')],
    'REOUVERT': [('FICHE_REOUVERTURE', '🔄 Fiche')],
}


# ============================================================
# CARTE DE BASE
# ============================================================

from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor


class DashboardCard(QFrame):
    """Carte avec titre, icône, actions et effet d'ombrage subtil"""
    
    def __init__(self, title: str, icon: str = "", parent=None):
        super().__init__(parent)
        apply_card_shadow(self)
        # ============================================================
        # Style de la carte
        # ============================================================
        self.setStyleSheet("""
            QFrame#DashboardCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        self.setObjectName("DashboardCard")
        
        # ============================================================
        # ✅ Effet d'ombrage subtil
        # ============================================================
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)              # Flou doux
        shadow.setXOffset(0)                  # Pas de décalage horizontal
        shadow.setYOffset(3)                  # Léger décalage vertical
        shadow.setColor(QColor(15, 23, 42, 30))  # Noir bleuté, alpha 30/255
        self.setGraphicsEffect(shadow)
        
        # ============================================================
        # Layout principal
        # ============================================================
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(18, 15, 18, 15)
        self._main_layout.setSpacing(10)
        
        # ============================================================
        # En-tête : icône + titre + menu
        # ============================================================
        header = QHBoxLayout()
        header.setSpacing(8)
        
        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 16px;")
            header.addWidget(icon_lbl)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        header.addWidget(title_lbl)
        header.addStretch()
        
        # Menu ⋮
        menu_btn = QLabel("⋮")
        menu_btn.setStyleSheet("font-size: 16px; color: #94a3b8;")
        menu_btn.setCursor(Qt.PointingHandCursor)
        header.addWidget(menu_btn)
        
        self._main_layout.addLayout(header)
        
        # ============================================================
        # Zone de contenu
        # ============================================================
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        self._main_layout.addLayout(self.content_layout)
    
    def add_widget(self, widget):
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        self.content_layout.addLayout(layout)

# ============================================================
# PAGE PRINCIPALE
# ============================================================

class DashboardPage(QWidget):
    """Tableau de bord LOMETA - Command Center"""
    refresh_progress = Signal(int, str)
    refresh_error = Signal(str)
    refresh_finished = Signal()
    def __init__(self, controller, user, referentiel_controller=None,
                 expertise_controller=None, evaluation_controller=None,
                 reglement_controller=None, recours_controller=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.referentiel_controller = referentiel_controller
        self.expertise_controller = expertise_controller
        self.evaluation_controller = evaluation_controller
        self.reglement_controller = reglement_controller
        self.recours_controller = recours_controller
        self._sinistres_data = []
        self.setup_ui()
        self.refresh()
    
    # ============================================================
    # UI
    # ============================================================
    
    def setup_ui(self):
        # Scroll principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8fafc;
            }
        """)
        
        content = QWidget()
        content.setStyleSheet("background-color: #f8fafc;")
        
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # ============================================================
        # LIGNE 1 : KPI Header (Total + compteurs + carte)
        # ============================================================
        main_layout.addWidget(self._build_kpi_header())
        main_layout.addWidget(self._build_alerts_banner())

        
        # ============================================================
        # LIGNE 2 : 3 colonnes
        # ============================================================
        row2 = QHBoxLayout()
        row2.setSpacing(15)
        
        # Colonne 1 : Volume par branche + Value pipeline
        col1 = QVBoxLayout()
        col1.setSpacing(15)
        col1.addWidget(self._build_volume_branch_card())
        col1.addWidget(self._build_finance_pipeline_card())
        col1.addWidget(self._build_finance_summary_card())
        col1.addWidget(self._build_performance_card())
        col1.addStretch()
        row2.addLayout(col1, 1)
        
        # Colonne 2 : Trends + Recent claims
        col2 = QVBoxLayout()
        col2.setSpacing(15)
        col2.addWidget(self._build_trends_card())
        col2.addWidget(self._build_recent_claims_card())
        col2.addWidget(self._build_value_pipeline_card())
        col2.addStretch()
        row2.addLayout(col2, 2)
        
        # Colonne 3 : Carte + Expertise stream
        col3 = QVBoxLayout()
        col3.setSpacing(15)
        col3.addWidget(self._build_connected_users_card())
        col3.addWidget(self._build_map_card())
        col3.addWidget(self._build_expertise_stream_card())
        col3.addWidget(self._build_top_claims_card()) 
        col3.addStretch()
        row2.addLayout(col3, 1)
        
        main_layout.addLayout(row2)
        
        scroll.setWidget(content)
        
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)
    
    # ============================================================
    # KPI HEADER
    # ============================================================
  
    def _build_connected_users_card(self) -> QWidget:
        self.connected_users_card = ConnectedUsersCard()
        self.connected_users_card.refresh_requested.connect(self._refresh_connected_users)
        self.connected_users_card.disconnect_requested.connect(self._on_disconnect_user)
        self.connected_users_card.show_sessions_requested.connect(self._on_show_sessions)
        self.connected_users_card.block_user_requested.connect(self._on_block_user)
        return self.connected_users_card

    def _refresh_connected_users(self):
        """Rafraîchit la liste des utilisateurs connectés"""
        try:
            users = []
            if hasattr(self.controller, 'get_active_users'):
                users = self.controller.get_active_users(minutes=30) or []
            
            if hasattr(self, 'connected_users_card'):
                self.connected_users_card.set_users(users)
        except Exception as e:
            print(f"Erreur refresh connected users: {e}")

    def _on_disconnect_user(self, user: dict):
        """Déconnecte un utilisateur après confirmation"""
        user_id = user.get('id')
        nom = user.get('nom') or user.get('username') or 'Utilisateur'
        
        # Vérifications locales (doublons de sécurité)
        if self.user and getattr(self.user, 'id', None) == user_id:
            QMessageBox.warning(self, "Action impossible",
                "Vous ne pouvez pas vous déconnecter vous-même.")
            return
        
        if getattr(self.user, 'role', '') != 'admin':
            QMessageBox.warning(self, "Droits insuffisants",
                "Seul un administrateur peut déconnecter un utilisateur.")
            return
        
        # Récupérer le nombre de sessions
        sessions = []
        try:
            if hasattr(self.controller, 'get_user_sessions'):
                sessions = self.controller.get_user_sessions(user_id) or []
        except Exception:
            pass
        
        # Dialogue de confirmation
        from addons.sinistres.views.dialogs_files.disconnect_user_dialog import DisconnectUserDialog
        dialog = DisconnectUserDialog(user, len(sessions) or 1, parent=self)
        
        if dialog.exec() != DisconnectUserDialog.Accepted:
            return
        
        # Déconnexion via le contrôleur
        try:
            success = self.controller.disconnect_user(user_id, dialog.get_reason())
            if success:
                QMessageBox.information(self, "✅ Déconnexion",
                    f"L'utilisateur {nom} a été déconnecté.")
                self._refresh_connected_users()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    def refresh_async(self):
        """Version non-bloquante avec progression"""
        if self._refreshing:
            return
        
        self._refreshing = True
        
        try:
            # Étape 1 (10-30%)
            self.refresh_progress.emit(10, "Chargement des statistiques...")
            QApplication.processEvents()
            
            stats = self.controller.get_statistiques() or {}
            par_statut = stats.get('par_statut', {}) or {}
            total = stats.get('total', 0) or 0
            self.refresh_progress.emit(30, f"{total} sinistres trouvés")
            QApplication.processEvents()
            
            # Étape 2 (30-60%)
            self.refresh_progress.emit(40, "Chargement des sinistres récents...")
            QApplication.processEvents()
            
            sinistres = self.controller.rechercher_sinistres({'limit': 50}) or []
            self._sinistres_data = sinistres
            self.refresh_progress.emit(60, f"{len(sinistres)} sinistres chargés")
            QApplication.processEvents()
            
            # Étape 3 (60-85%)
            self.refresh_progress.emit(70, "Enrichissement des données...")
            QApplication.processEvents()
            
            enriched = self._enrichir_sinistres(sinistres)
            self.refresh_progress.emit(85, "Données prêtes")
            QApplication.processEvents()
            
            # Étape 4 (85-100%)
            self.refresh_progress.emit(90, "Mise à jour des graphiques...")
            QApplication.processEvents()
            
            # Rendu de tous les composants
            self._update_branch_chart(enriched)
            self._update_pipeline_chart(enriched)
            self._update_trends_chart(enriched)
            self._update_recent_table(enriched)
            self._update_expertise_stream()
            
            # Mettre à jour les KPI
            nb_ouvert = par_statut.get('OUVERT', 0)
            nb_cloture = par_statut.get('CLOTURE', 0)
            nb_recours = par_statut.get('EN_RECOURS', 0)
            
            today = datetime.now().date()
            nb_today = 0
            for s in sinistres:
                date_str = s.get('date_declaration') or s.get('created_at')
                if not date_str:
                    continue
                try:
                    d = datetime.fromisoformat(str(date_str)[:19]).date()
                    if d == today:
                        nb_today += 1
                except Exception:
                    pass
            
            if hasattr(self, 'kpi_bar') and self.kpi_bar:
                self.kpi_bar.set_data(
                    total=total, claims=total,
                    open_=nb_ouvert, closed=nb_cloture,
                    recourse=nb_recours, today=nb_today,
                )
            
            # Autres cartes
            self._refresh_connected_users()
            self._refresh_finance_cards()
            self._refresh_alerts()
            self._refresh_performance()
            self._refresh_top_claims(enriched)
            
            self.refresh_progress.emit(100, "Terminé")
            QApplication.processEvents()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.refresh_error.emit(str(e))
        finally:
            self._refreshing = False
            self.refresh_finished.emit()
    
    def _on_show_sessions(self, user: dict):
        """Affiche les sessions actives d'un utilisateur"""
        user_id = user.get('id')
        nom = user.get('nom') or user.get('username') or 'Utilisateur'
        
        try:
            sessions = []
            if hasattr(self.controller, 'get_user_sessions'):
                sessions = self.controller.get_user_sessions(user_id) or []
            
            if not sessions:
                QMessageBox.information(self, "Sessions",
                    f"Aucune session active pour {nom}.")
                return
            
            lines = [f"Sessions actives de {nom} ({len(sessions)}) :\n"]
            for i, s in enumerate(sessions, 1):
                ip = s.get('ip_address') or 'IP inconnue'
                last = (s.get('last_activity') or '')[:19].replace('T', ' ')
                ua = (s.get('user_agent') or 'Inconnu')[:60]
                lines.append(f"{i}. IP: {ip}")
                lines.append(f"   Dernière activité: {last}")
                lines.append(f"   Navigateur: {ua}\n")
            
            QMessageBox.information(self, "Sessions actives", "\n".join(lines))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    def _build_finance_summary_card(self) -> QWidget:
        """Carte Résumé Financier"""
        self.finance_summary_card = FinanceSummaryCard()
        return self.finance_summary_card

    def _build_finance_pipeline_card(self) -> QWidget:
        """Carte Pipeline Financier"""
        self.finance_pipeline_card = FinancePipelineCard()
        return self.finance_pipeline_card

    def _on_block_user(self, user: dict):
        """Bloque un utilisateur"""
        user_id = user.get('id')
        nom = user.get('nom') or user.get('username') or 'Utilisateur'
        
        if self.user and getattr(self.user, 'id', None) == user_id:
            QMessageBox.warning(self, "Action impossible",
                "Vous ne pouvez pas bloquer votre propre compte.")
            return
        
        if getattr(self.user, 'role', '') != 'admin':
            QMessageBox.warning(self, "Droits insuffisants",
                "Seul un administrateur peut bloquer un compte.")
            return
        
        reply = QMessageBox.question(self, "Confirmation",
            f"Bloquer le compte de {nom} ?\n\n"
            f"• Toutes ses sessions seront fermées\n"
            f"• Il ne pourra plus se reconnecter",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            success = self.controller.block_user(user_id, "Blocage administratif")
            if success:
                QMessageBox.information(self, "✅ Compte bloqué",
                    f"L'utilisateur {nom} a été bloqué.")
                self._refresh_connected_users()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    def _build_kpi_header(self) -> QWidget:
        """Construit la barre KPI Claims (design anneau + stats)"""
        from addons.sinistres.views.widgets.kpi_claims_bar import KpiClaimsBar
        
        self.kpi_bar = KpiClaimsBar()
        return self.kpi_bar
    
    def _make_stat_box(self, label: str, value: str, color: str) -> QFrame:
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-left: 4px solid {color};
                border-radius: 10px;
            }}
        """)
        box.setMinimumWidth(140)
        
        layout = QVBoxLayout(box)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(4)
        
        title = QLabel(f"● {label}")
        title.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: 600;")
        layout.addWidget(title)
        
        val = QLabel(value)
        val.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
        layout.addWidget(val)
        
        box.value_label = val
        return box
    
    # ============================================================
    # VOLUME PAR BRANCHE (DONUT)
    # ============================================================
    
    def _build_volume_branch_card(self) -> DashboardCard:
        card = DashboardCard("Claim Volume & Value by Branch", "🥧")
        
        self.donut_branches = DonutChart()
        self.donut_branches.setMinimumHeight(200)
        card.add_widget(self.donut_branches)
        
        # Légende
        self.legend_branches = QLabel("")
        self.legend_branches.setStyleSheet("font-size: 11px; color: #64748b;")
        self.legend_branches.setWordWrap(True)
        card.add_widget(self.legend_branches)
        
        return card
    
    # ============================================================
    # VALUE PIPELINE (BARRES EMPILÉES)
    # ============================================================
    
    def _build_value_pipeline_card(self) -> DashboardCard:
        card = DashboardCard("Claim Value Pipeline", "📊")
        
        self.bars_pipeline = StackedBarChart()
        self.bars_pipeline.setMinimumHeight(150)
        card.add_widget(self.bars_pipeline)
        
        # Légende
        legend_row = QHBoxLayout()
        for label, color in [("Reported", "#3b82f6"), ("Reserved", "#f59e0b"), ("Paid", "#22c55e")]:
            item = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 14px;")
            item.addWidget(dot)
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 10px; color: #64748b;")
            item.addWidget(lbl)
            legend_row.addLayout(item)
        legend_row.addStretch()
        card.add_layout(legend_row)
        
        return card
    
    # ============================================================
    # TRENDS (LINE CHART)
    # ============================================================
    
    def _build_trends_card(self) -> DashboardCard:
        card = DashboardCard("Claim Volume Trends", "📈")
        
        # Dropdown simulé
        period_row = QHBoxLayout()
        period_row.addStretch()
        period_lbl = QLabel("Last 30 days ▾")
        period_lbl.setStyleSheet("""
            font-size: 11px;
            color: #64748b;
            padding: 4px 10px;
            background-color: #f1f5f9;
            border-radius: 6px;
        """)
        period_row.addWidget(period_lbl)
        card.add_layout(period_row)
        
        # 2 graphes côte à côte
        charts_row = QHBoxLayout()
        charts_row.setSpacing(15)
        
        # Graphe A : Volume
        chart_a = QVBoxLayout()
        chart_a_title = QLabel("A. Claim Intake (Volume)")
        chart_a_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #1e293b;")
        chart_a.addWidget(chart_a_title)
        
        self.line_intake = LineChart(color="#3b82f6")
        self.line_intake.setMinimumHeight(120)
        chart_a.addWidget(self.line_intake)
        
        charts_row.addLayout(chart_a, 1)
        
        # Graphe B : Value
        chart_b = QVBoxLayout()
        chart_b_title = QLabel("B. Claim Closure (Volume)")
        chart_b_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #1e293b;")
        chart_b.addWidget(chart_b_title)
        
        self.line_closure = LineChart(color="#22c55e")
        self.line_closure.setMinimumHeight(120)
        chart_b.addWidget(self.line_closure)
        
        charts_row.addLayout(chart_b, 1)
        
        card.add_layout(charts_row)
        return card
    
    # ============================================================
    # RECENT CLAIMS (TABLEAU)
    # ============================================================
    def _build_recent_claims_card(self) -> DashboardCard:
        """Carte Recent Claims avec toggle cartes/tableau"""
        card = DashboardCard("Recent Claims", "📋")
        
        # ✅ Nouveau widget
        self.recent_claims_widget = RecentClaimsWidget(self.statut_colors if hasattr(self, 'statut_colors') else STATUT_COLORS)
        
        # Connexions des signaux
        self.recent_claims_widget.view_detail_requested.connect(self._on_voir_detail)
        self.recent_claims_widget.modify_requested.connect(self._on_modifier)
        self.recent_claims_widget.print_requested.connect(self._on_imprimer)
        self.recent_claims_widget.view_all_requested.connect(self._on_view_all_claims)
        
        card.add_widget(self.recent_claims_widget)
        
        # ✅ Agrandir la carte
        card.setMinimumHeight(400)
        
        return card

    # ============================================================
    # MAP CARD
    # ============================================================
    
    def _build_map_card(self) -> DashboardCard:
        card = DashboardCard("Répartition Géographique", "🗺️")
        
        map_frame = QFrame()
        map_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border-radius: 8px;
            }
        """)
        map_frame.setMinimumHeight(180)
        
        map_layout = QVBoxLayout(map_frame)
        map_layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel("🗺️")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignCenter)
        map_layout.addWidget(icon)
        
        text = QLabel("Carte des sinistres\n(à intégrer)")
        text.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        text.setAlignment(Qt.AlignCenter)
        map_layout.addWidget(text)
        
        card.add_widget(map_frame)
        return card
    
    # ============================================================
    # EXPERTISE STREAM
    # ============================================================
   
    def _build_expertise_stream_card(self) -> DashboardCard:
        card = DashboardCard("Expertise Stream: Real-time", "⚡")
        
        # ✅ Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Conteneur interne
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        self.stream_layout = QVBoxLayout(container)
        self.stream_layout.setContentsMargins(0, 0, 6, 0)
        self.stream_layout.setSpacing(6)
        
        scroll.setWidget(container)
        
        # ✅ Hauteur fixe maximale
        scroll.setMinimumHeight(200)
        scroll.setMaximumHeight(300)
        
        card.add_widget(scroll)
        return card

    # ============================================================
    # CHARGEMENT DES DONNÉES
    # ============================================================
    
    def refresh(self):
        """
        Rafraîchit le tableau de bord :
        - Barre KPI Claims (anneau + 5 stats)
        - Donut Volume & Value par branche
        - Barres empilées Value Pipeline
        - Line chart Trends (Intake / Closure)
        - Tableau Recent Claims
        - Flux Expertise Stream
        """
        try:
            # ============================================================
            # 1. STATISTIQUES GLOBALES
            # ============================================================
            stats = self.controller.get_statistiques() or {}
            par_statut = stats.get('par_statut', {}) or {}
            total = stats.get('total', 0) or 0
            
            # ============================================================
            # 2. SINISTRES RÉCENTS (pour le tableau + calculs)
            # ============================================================
            sinistres = self.controller.rechercher_sinistres({'limit': 50}) or []
            self._sinistres_data = sinistres
            
            # ============================================================
            # 3. CALCUL DES KPI
            # ============================================================
            
            # --- Nombre par statut ---
            nb_ouvert = par_statut.get('OUVERT', 0)
            nb_cloture = par_statut.get('CLOTURE', 0)
            nb_recours = par_statut.get('EN_RECOURS', 0)
            
            # --- New Today (déclarations d'aujourd'hui) ---
            from datetime import datetime
            today = datetime.now().date()
            nb_today = 0
            for s in sinistres:
                date_str = s.get('date_declaration') or s.get('created_at')
                if not date_str:
                    continue
                try:
                    d = datetime.fromisoformat(str(date_str)[:19]).date()
                    if d == today:
                        nb_today += 1
                except Exception:
                    pass
            
            # ============================================================
            # 4. MISE À JOUR DE LA BARRE KPI
            # ============================================================
            if hasattr(self, 'kpi_bar') and self.kpi_bar:
                self.kpi_bar.set_data(
                    total=total,
                    claims=total,
                    open_=nb_ouvert,
                    closed=nb_cloture,
                    recourse=nb_recours,
                    today=nb_today,
                )
            
            # ============================================================
            # 5. ENRICHISSEMENT DES SINISTRES (nom client)
            # ============================================================
            sinistres_enrichis = self._enrichir_sinistres(sinistres)
            
            # ============================================================
            # 6. GRAPHIQUES
            # ============================================================
            
            # --- 6a. Donut Volume & Value par branche ---
            self._update_branch_chart(sinistres_enrichis)
            
            # --- 6b. Barres empilées Value Pipeline ---
            self._update_pipeline_chart(sinistres_enrichis)
            
            # --- 6c. Line chart Trends (Intake / Closure) ---
            self._update_trends_chart(sinistres_enrichis)
            
            # --- 6d. Tableau Recent Claims ---
            self._update_recent_table(sinistres_enrichis)
            
            # --- 6e. Flux Expertise Stream ---
            self._update_expertise_stream()

            # --- 6f. Utilisateurs connectés ---
            self._refresh_connected_users()

            # --- 6g. Cartes financières ---
            self._refresh_finance_cards()

            # --- 6h. Alertes ---
            self._refresh_alerts()

            # --- 6i. Performance ---
            self._refresh_performance()

            # --- 6j. Top 5 ---
            self._refresh_top_claims(sinistres_enrichis)
            # ============================================================
            # 7. LOG
            # ============================================================
            print(f"✅ Dashboard rafraîchi : "
                f"{total} sinistres | "
                f"{nb_ouvert} ouverts | "
                f"{nb_cloture} clôturés | "
                f"{nb_recours} recours | "
                f"{nb_today} aujourd'hui")
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.warning(
                self, "Erreur",
                f"Erreur lors du rafraîchissement du tableau de bord :\n{str(e)}"
            )

    def _enrichir_sinistres(self, sinistres: List[dict]) -> List[dict]:
        enriched = []
        for s in sinistres:
            s_copy = dict(s)
            if not s_copy.get('client_nom'):
                s_copy['client_nom'] = self._get_client_nom(s_copy.get('client_id'))
            enriched.append(s_copy)
        return enriched
    
    def _get_client_nom(self, client_id) -> str:
        """Récupère le nom du client"""
        if not client_id:
            return 'N/A'
        try:
            from addons.sinistres.controllers.automobile_controller import AutomobileController
            ac = AutomobileController()
            ac.set_current_user(self.user)
            client = ac.get_contact(client_id)
            if client:
                nom = client.get('nom', '') or ''
                prenom = client.get('prenom', '') or ''
                return f"{nom} {prenom}".strip() or f"Client #{client_id}"
        except Exception as e:
            print(f"Erreur get_client_nom({client_id}): {e}")
        return f"Client #{client_id}"

    def _build_financial_summary_card(self) -> DashboardCard:
        card = DashboardCard("Résumé Financier", "💰")
        
        # Grille 2x2 de mini-tuiles
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # --- 4 KPI financiers ---
        self.fin_estime = self._make_finance_tile(
            "Total Estimé", "0 FCFA", "#3b82f6", "📊"
        )
        self.fin_provision = self._make_finance_tile(
            "Provisions", "0 FCFA", "#f59e0b", "🛡️"
        )
        self.fin_regle = self._make_finance_tile(
            "Total Réglé", "0 FCFA", "#22c55e", "💳"
        )
        self.fin_recours = self._make_finance_tile(
            "Recours", "0 FCFA", "#ef4444", "⚖️"
        )
        
        grid.addWidget(self.fin_estime, 0, 0)
        grid.addWidget(self.fin_provision, 0, 1)
        grid.addWidget(self.fin_regle, 1, 0)
        grid.addWidget(self.fin_recours, 1, 1)
        
        card.add_layout(grid)
        return card

    def _make_finance_tile(self, label: str, value: str, color: str, icon: str) -> QFrame:
        """Tuile KPI financier"""
        tile = QFrame()
        tile.setStyleSheet(f"""
            QFrame {{
                background-color: {color}10;
                border: 1px solid {color}30;
                border-left: 3px solid {color};
                border-radius: 8px;
            }}
        """)
        tile.setMinimumHeight(60)
        
        layout = QVBoxLayout(tile)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)
        
        # Ligne 1 : icône + label
        header = QHBoxLayout()
        header.setSpacing(4)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 12px;")
        header.addWidget(icon_lbl)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 10px; color: {color}; font-weight: 600;")
        header.addWidget(lbl)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Ligne 2 : valeur
        val = QLabel(value)
        val.setStyleSheet(f"font-size: 14px; font-weight: bold; color: #1e293b;")
        layout.addWidget(val)
        
        tile.value_label = val
        return tile
    
    def _refresh_finance_cards(self):
        """Rafraîchit les cartes financières"""
        try:
            # Récupérer les stats financières via le contrôleur
            stats = {}
            if hasattr(self.controller, 'get_statistiques_financieres'):
                stats = self.controller.get_statistiques_financieres() or {}
            
            # Sinon, calculer depuis les sinistres
            if not stats:
                sinistres = self._sinistres_data or []
                stats = {
                    'estime': sum(s.get('montant_estime', 0) or 0 for s in sinistres),
                    'provision': sum(s.get('provision', 0) or 0 for s in sinistres),
                    'regle': sum(s.get('montant_regle', 0) or 0 for s in sinistres),
                    'recours': sum(s.get('montant_recours', 0) or 0 for s in sinistres),
                }
            
            # Mettre à jour les cartes
            if hasattr(self, 'finance_summary_card'):
                self.finance_summary_card.set_data({
                    'estime': stats.get('estime', 0),
                    'provision': stats.get('provision', 0),
                    'regle': stats.get('regle', 0),
                    'recours': stats.get('recours', 0),
                })
            
            if hasattr(self, 'finance_pipeline_card'):
                self.finance_pipeline_card.set_data({
                    'estime': stats.get('estime', 0),
                    'provision': stats.get('provision', 0),
                    'regle': stats.get('regle', 0),
                    'recours': stats.get('recours', 0),
                })
        except Exception as e:
            print(f"Erreur refresh finance: {e}")
            import traceback
            traceback.print_exc()

    # ============================================================
    # MISE À JOUR DES GRAPHIQUES
    # ============================================================
    
    def _update_branch_chart(self, sinistres: list):
        """Met à jour le donut Volume par branche"""
        from collections import Counter
        
        # --- Compter par branche ---
        counter = Counter()
        for s in sinistres:
            br = (s.get('branche') or 'AUTRE').upper()
            counter[br] += 1
        
        if not counter:
            self.donut_branches.set_data([], "0 claims")
            self.legend_branches.setText("Aucune donnée")
            return
        
        # --- Préparer les données ---
        data = []
        legend_lines = []
        for br, count in counter.most_common():
            color = BRANCHE_COLORS.get(br, '#64748b')
            data.append((br, count, color))
            legend_lines.append(f"{br}: {count}")
        
        # --- Centre : total ---
        center_text = f"{len(sinistres)}"
        self.donut_branches.set_data(data, center_text)
        
        # --- Légende ---
        self.legend_branches.setText("  •  ".join(legend_lines))

    def _update_pipeline_chart(self, sinistres: list):
        """
        Met à jour les barres empilées Value Pipeline.
        Utilise les champs déjà sérialisés par le contrôleur.
        """
        from datetime import datetime
        from collections import defaultdict
        
        months_data = defaultdict(lambda: {'reported': 0, 'reserved': 0, 'paid': 0})
        
        now = datetime.now()
        for i in range(5, -1, -1):
            y, m = now.year, now.month - i
            while m <= 0:
                m += 12
                y -= 1
            months_data[f"{y}-{m:02d}"]
        
        has_data = False
        
        for s in sinistres:
            date_str = s.get('date_survenance') or s.get('created_at')
            if not date_str:
                continue
            try:
                d = datetime.fromisoformat(str(date_str)[:19])
                key = f"{d.year}-{d.month:02d}"
                if key not in months_data:
                    continue
                
                # ✅ Champs sérialisés par le contrôleur
                reported = float(s.get('montant_estime') or 0)
                reserved = float(s.get('provision') or 0)
                paid = float(s.get('montant_regle') or 0)
                
                if reported or reserved or paid:
                    has_data = True
                
                months_data[key]['reported'] += reported
                months_data[key]['reserved'] += reserved
                months_data[key]['paid'] += paid
            except Exception:
                pass
        
        # --- Si aucune donnée → afficher un placeholder ---
        if not has_data:
            self.bars_pipeline.set_data(
                ['—'],
                [
                    {'label': 'Reported', 'color': '#3b82f6', 'values': [0]},
                    {'label': 'Reserved', 'color': '#f59e0b', 'values': [0]},
                    {'label': 'Paid', 'color': '#22c55e', 'values': [0]},
                ]
            )
            return
        
        # --- Construire les séries ---
        sorted_keys = sorted(months_data.keys())
        mois_lbl = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                    'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc']
        
        labels, reported, reserved, paid = [], [], [], []
        for key in sorted_keys:
            try:
                y, m = key.split('-')
                labels.append(f"{mois_lbl[int(m) - 1]} {y[2:]}")
                reported.append(months_data[key]['reported'])
                reserved.append(months_data[key]['reserved'])
                paid.append(months_data[key]['paid'])
            except Exception:
                continue
        
        self.bars_pipeline.set_data(labels, [
            {'label': 'Reported', 'color': '#3b82f6', 'values': reported},
            {'label': 'Reserved', 'color': '#f59e0b', 'values': reserved},
            {'label': 'Paid', 'color': '#22c55e', 'values': paid},
        ])

    def _update_trends_chart(self, sinistres: list):
        """
        Met à jour les 2 courbes de tendance :
        - Intake (déclarations par jour sur 15 jours)
        - Closure (clôtures par jour sur 15 jours)
        """
        from datetime import datetime, timedelta
        from collections import Counter
        
        # --- Préparer les 15 derniers jours ---
        today = datetime.now().date()
        jours = [(today - timedelta(days=i)) for i in range(14, -1, -1)]
        labels = [d.strftime('%Y-%m-%d') for d in jours]
        
        # --- Compter par jour ---
        intake_par_jour = Counter()
        closure_par_jour = Counter()
        
        for s in sinistres:
            # Intake
            date_decl = s.get('date_declaration') or s.get('created_at')
            if date_decl:
                try:
                    d = datetime.fromisoformat(str(date_decl)[:19]).date()
                    if d in jours:
                        intake_par_jour[d] += 1
                except Exception:
                    pass
            
            # Closure
            date_clot = s.get('date_cloture')
            if date_clot:
                try:
                    d = datetime.fromisoformat(str(date_clot)[:19]).date()
                    if d in jours:
                        closure_par_jour[d] += 1
                except Exception:
                    pass
        
        # --- Séries ---
        intake_series = [intake_par_jour.get(d, 0) for d in jours]
        closure_series = [closure_par_jour.get(d, 0) for d in jours]
        
        # --- Mise à jour ---
        self.line_intake.set_data(intake_series, labels, "#3b82f6")
        self.line_closure.set_data(closure_series, labels, "#22c55e")
  
    def _update_recent_table(self, sinistres: list):
        """Met à jour la carte Recent Claims"""
        if hasattr(self, 'recent_claims_widget'):
            self.recent_claims_widget.set_sinistres(sinistres)

    def _on_view_all_claims(self):
        """Ouvre la page de recherche avec tous les sinistres"""
        try:
            # Remonter au parent (LometaSinistresMainView)
            parent = self.parent()
            while parent and not hasattr(parent, 'switch_page'):
                parent = parent.parent()
            
            if parent and hasattr(parent, 'switch_page'):
                # Trouver l'index de la page recherche (généralement index 2)
                parent.switch_page(2)
        except Exception as e:
            print(f"Erreur navigation: {e}")

    def _update_expertise_stream(self):
        """Met à jour le flux d'expertises (5 dernières missions)"""
        
        # --- Vider ---
        while self.stream_layout.count():
            item = self.stream_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # --- Récupérer les missions récentes ---
        missions = []
        try:
            if self.expertise_controller:
                missions = self.expertise_controller.get_all_missions() or []
        except Exception as e:
            print(f"Erreur chargement missions: {e}")
        
        # --- Si aucune donnée, afficher un message ---
        if not missions:
            empty = QLabel("Aucune expertise récente")
            empty.setStyleSheet("color: #94a3b8; font-size: 11px; font-style: italic; padding: 20px;")
            empty.setAlignment(Qt.AlignCenter)
            self.stream_layout.addWidget(empty)
            return
        
        # --- Afficher les 5 plus récentes ---
        from datetime import datetime
        for mission in missions[:5]:
            # Déterminer la couleur selon le statut
            statut = (mission.get('statut') or '').upper()
            statut_colors = {
                'CREEE': '#64748b',
                'AFFECTEE': '#3b82f6',
                'EN_COURS': '#f59e0b',
                'RAPPORT_RECU': '#8b5cf6',
                'RAPPORT_REÇU': '#8b5cf6',
                'VALIDE': '#22c55e',
                'ANNULE': '#ef4444',
            }
            color = statut_colors.get(statut, '#64748b')
            
            # Construire l'item
            item = QFrame()
            item.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border-left: 3px solid {color};
                    border-radius: 6px;
                    padding: 6px;
                }}
            """)
            
            layout = QVBoxLayout(item)
            layout.setContentsMargins(8, 6, 8, 6)
            layout.setSpacing(3)
            
            # Temps relatif
            date_str = mission.get('date_mission') or mission.get('created_at')
            time_label = self._format_relative_time(date_str)
            
            time_lbl = QLabel(time_label)
            time_lbl.setStyleSheet(f"font-size: 9px; color: {color}; font-weight: bold;")
            layout.addWidget(time_lbl)
            
            # Numéro mission + sinistre
            numero = mission.get('numero_mission') or 'N/A'
            sinistre_num = mission.get('sinistre_numero') or ''
            expert = mission.get('expert_nom') or 'Expert non affecté'
            header_text = f"{numero} - {sinistre_num}" if sinistre_num else numero
            num_lbl = QLabel(header_text)
            num_lbl.setStyleSheet("font-size: 11px; color: #1e293b; font-weight: 600;")
            layout.addWidget(num_lbl)
            
            # Action (statut + expert)
            action_lbl = QLabel(f"→ {statut} ({expert})")
            action_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-style: italic;")
            layout.addWidget(action_lbl)
            
            self.stream_layout.addWidget(item)

    def _format_relative_time(self, date_str) -> str:
        """Formate une date en temps relatif ('2m ago', '1h ago', etc.)"""
        if not date_str:
            return "—"
        try:
            from datetime import datetime
            d = datetime.fromisoformat(str(date_str)[:19])
            delta = datetime.now() - d
            seconds = int(delta.total_seconds())
            
            if seconds < 60:
                return f"[{seconds}s ago]"
            elif seconds < 3600:
                return f"[{seconds // 60}m ago]"
            elif seconds < 86400:
                return f"[{seconds // 3600}h ago]"
            else:
                return f"[{seconds // 86400}d ago]"
        except Exception:
            return "[—]"

    def _build_financial_pipeline_card(self) -> DashboardCard:
        card = DashboardCard("Pipeline Financier", "📈")
        
        self.financial_progress = QVBoxLayout()
        self.financial_progress.setSpacing(10)
        card.add_layout(self.financial_progress)
        
        return card

    def _update_financial_cards(self, stats: dict):
        """Met à jour les cartes financières"""
        # --- Résumé ---
        total_estime = stats.get('montant_estime_total', 0) or 0
        total_provision = stats.get('provision_total', 0) or 0
        total_regle = stats.get('montant_regle_total', 0) or 0
        total_recours = stats.get('montant_recours_total', 0) or 0
        
        self.fin_estime.value_label.setText(
            f"{total_estime:,.0f} FCFA".replace(",", " ")
        )
        self.fin_provision.value_label.setText(
            f"{total_provision:,.0f} FCFA".replace(",", " ")
        )
        self.fin_regle.value_label.setText(
            f"{total_regle:,.0f} FCFA".replace(",", " ")
        )
        self.fin_recours.value_label.setText(
            f"{total_recours:,.0f} FCFA".replace(",", " ")
        )
        
        # --- Pipeline (barres horizontales) ---
        while self.financial_progress.count():
            item = self.financial_progress.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        items = [
            ("Estimé", total_estime, "#3b82f6"),
            ("Provisionné", total_provision, "#f59e0b"),
            ("Réglé", total_regle, "#22c55e"),
            ("Récupéré (recours)", total_recours, "#ef4444"),
        ]
        
        max_val = max([v for _, v, _ in items] + [1])
        
        for label, value, color in items:
            row = self._make_progress_row(label, value, max_val, color)
            self.financial_progress.addWidget(row)

    def _make_progress_row(self, label: str, value: float, max_val: float, color: str) -> QFrame:
        """Ligne avec barre de progression horizontale"""
        row = QFrame()
        row.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(row)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(2)
        
        # Ligne label + valeur
        header = QHBoxLayout()
        
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        header.addWidget(lbl)
        header.addStretch()
        
        val_lbl = QLabel(f"{value:,.0f} FCFA".replace(",", " "))
        val_lbl.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {color};")
        header.addWidget(val_lbl)
        
        layout.addLayout(header)
        
        # Barre
        bar = QFrame()
        bar.setFixedHeight(6)
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {color}20;
                border-radius: 3px;
            }}
        """)
        
        # Remplissage proportionnel
        ratio = (value / max_val) if max_val > 0 else 0
        fill = QFrame(bar)
        fill.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        
        # Utiliser un layout pour positionner
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(0)
        
        fill.setFixedWidth(int(200 * ratio))  # Largeur proportionnelle (fixe)
        bar_layout.addWidget(fill)
        bar_layout.addStretch()
        
        layout.addWidget(bar)
        return row


    # ============================================================
    # ACTIONS TABLEAU
    # ============================================================
    
    def _on_recent_double_clicked(self, index):
        """Double-clic sur une ligne du tableau récent"""
        row = index.row()
        if 0 <= row < len(self._sinistres_data):
            self._on_voir_detail(self._sinistres_data[row])
    
    def _show_context_menu(self, position):
        """Menu contextuel du tableau"""
        row = self.table_recent.currentRow()
        if row < 0 or row >= len(self._sinistres_data):
            return
        
        data = self._sinistres_data[row]
        statut = data.get('statut', '')
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 13px;
                color: #1e293b;
            }
            QMenu::item:selected {
                background-color: #f1f5f9;
                color: #1a73e8;
            }
        """)
        
        # Voir détail
        action_detail = QAction("👁️  Voir le détail", self)
        action_detail.triggered.connect(lambda: self._on_voir_detail(data))
        menu.addAction(action_detail)
        
        # Modifier
        action_modifier = QAction("✏️  Modifier", self)
        action_modifier.setEnabled(statut != 'CLOTURE')
        action_modifier.triggered.connect(lambda: self._on_modifier(data))
        menu.addAction(action_modifier)
        
        menu.addSeparator()
        
        # Imprimer
        action_imprimer = QAction("🖨️  Imprimer", self)
        action_imprimer.triggered.connect(lambda: self._on_imprimer(data))
        menu.addAction(action_imprimer)
        
        menu.exec(self.table_recent.viewport().mapToGlobal(position))
    
    def _on_voir_detail(self, data: dict):
        """Ouvre le détail du sinistre"""
        sinistre_id = data.get('id')
        if not sinistre_id:
            QMessageBox.warning(self, "Erreur", "Sinistre non trouvé")
            return
        
        try:
            from addons.sinistres.views.dossier_360 import Dossier360View
            
            dossier = Dossier360View(
                sinistre_id=sinistre_id,
                sinistre_controller=self.controller,
                referentiel_controller=self.referentiel_controller,
                expertise_controller=self.expertise_controller,
                evaluation_controller=self.evaluation_controller,
                reglement_controller=self.reglement_controller,
                recours_controller=self.recours_controller,
                user=self.user
            )
            dossier.setWindowTitle(f"Dossier 360° - {data.get('numero_sinistre', 'N/A')}")
            dossier.setMinimumSize(1200, 800)
            dossier.show()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur d'ouverture: {str(e)}")
    
    def _on_modifier(self, data: dict):
        QMessageBox.information(self, "Modifier",
            f"Modification du sinistre {data.get('numero_sinistre')}")
    
    def _on_imprimer(self, data: dict):
        statut = data.get('statut', '')
        numero = data.get('numero_sinistre', 'N/A')
        
        if statut not in IMPRESSIONS_PAR_STATUT:
            QMessageBox.warning(self, "Impression impossible",
                f"Le statut '{statut}' ne permet pas l'impression.")
            return
        
        types_dispo = IMPRESSIONS_PAR_STATUT[statut]
        if len(types_dispo) == 1:
            self._generer_impression(data, types_dispo[0][0])
        else:
            menu = QMenu(self)
            for code, label in types_dispo:
                action = QAction(label, self)
                action.triggered.connect(
                    lambda checked=False, c=code: self._generer_impression(data, c)
                )
                menu.addAction(action)
            menu.exec(self.cursor().pos())
    
    def _generer_impression(self, data: dict, type_impression: str):
        """Génère réellement le PDF"""
        numero = data.get('numero_sinistre', 'N/A')
        
        try:
            # --- Demander où sauvegarder ---
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le document",
                f"{type_impression}_{numero}.pdf",
                "PDF (*.pdf)"
            )
            
            if not filename:
                return
            
            # --- Récupérer les données complètes du sinistre ---
            sinistre_complet = data
            try:
                if hasattr(self.controller, 'get_sinistre_complet'):
                    sinistre_complet = self.controller.get_sinistre_complet(data.get('id')) or data
                elif hasattr(self.controller, 'get_sinistre'):
                    sinistre_complet = self.controller.get_sinistre(data.get('id')) or data
            except Exception as e:
                print(f"Erreur récupération sinistre: {e}")
            
            # --- Enrichir avec les infos client ---
            if not sinistre_complet.get('client_nom'):
                sinistre_complet['client_nom'] = self._get_client_nom(
                    sinistre_complet.get('client_id')
                )
            
            # --- Générer le PDF ---
            from addons.sinistres.services.impression_service import ImpressionService
            service = ImpressionService()
            
            success = service.generer_document(
                sinistre_data=sinistre_complet,
                type_document=type_impression,
                filepath=filename,
            )
            
            if success:
                # --- Ouvrir le PDF automatiquement ---
                reply = QMessageBox.information(
                    self,
                    "✅ Document généré",
                    f"Le document a été généré avec succès :\n\n"
                    f"📄 {filename}\n\n"
                    f"Voulez-vous l'ouvrir ?",
                    QMessageBox.Open | QMessageBox.Close,
                    QMessageBox.Open,
                )
                
                if reply == QMessageBox.Open:
                    self._ouvrir_fichier(filename)
            else:
                QMessageBox.warning(
                    self, "Erreur",
                    "Impossible de générer le document."
                )
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Erreur",
                f"Erreur lors de la génération :\n{str(e)}"
            )

    def _ouvrir_fichier(self, filepath: str):
        """Ouvre un fichier avec l'application par défaut"""
        import subprocess
        import platform
        import os
        
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', filepath])
            else:
                subprocess.call(['xdg-open', filepath])
        except Exception as e:
            print(f"Erreur ouverture fichier: {e}")

    def _build_alerts_banner(self) -> AlertsBanner:
        """Bandeau d'alertes"""
        self.alerts_banner = AlertsBanner()
        self.alerts_banner.alert_clicked.connect(self._on_alert_clicked)
        return self.alerts_banner


    def _build_performance_card(self) -> PerformanceCard:
        """Carte Performance"""
        self.performance_card = PerformanceCard()
        return self.performance_card


    def _build_top_claims_card(self) -> TopClaimsCard:
        """Carte Top 5"""
        self.top_claims_card = TopClaimsCard(STATUT_COLORS)
        self.top_claims_card.claim_clicked.connect(self._on_voir_detail)
        return self.top_claims_card


    def _refresh_alerts(self):
        """Rafraîchit le bandeau d'alertes"""
        try:
            alertes = []
            if hasattr(self.controller, 'get_alertes'):
                alertes = self.controller.get_alertes() or []
            
            if hasattr(self, 'alerts_banner'):
                self.alerts_banner.set_alerts(alertes)
        except Exception as e:
            print(f"Erreur refresh alerts: {e}")


    def _refresh_performance(self):
        """Rafraîchit la carte Performance"""
        try:
            stats = {}
            if hasattr(self.controller, 'get_statistiques_performance'):
                stats = self.controller.get_statistiques_performance() or {}
            
            if hasattr(self, 'performance_card'):
                self.performance_card.set_data(stats)
        except Exception as e:
            print(f"Erreur refresh performance: {e}")


    def _refresh_top_claims(self, sinistres: list):
        """Rafraîchit le Top 5"""
        try:
            if hasattr(self, 'top_claims_card'):
                self.top_claims_card.set_sinistres(sinistres)
        except Exception as e:
            print(f"Erreur refresh top claims: {e}")


    def _on_alert_clicked(self, alert_type: str):
        """Gère le clic sur une alerte"""
        QMessageBox.information(
            self, "Alerte",
            f"Type d'alerte : {alert_type}\n\n"
            f"Redirection vers la page correspondante (à implémenter)."
        )