"""
Widgets réutilisables pour l'onglet Dommages
KpiDamageCard, DamageRow, ExpandedPanel
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QSizePolicy, QTextEdit, QScrollArea, QDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPixmap
from pathlib import Path
import os
import os.path
from typing import Optional


# ============================================================
# KPI DAMAGE CARD (donut + valeur)
# ============================================================

# class KpiDamageCard(QFrame):
#     """Carte KPI avec donut de pourcentage + valeur principale"""
    
#     def __init__(self, title: str, value: str, percent: float = 0,
#                  color: str = "#1a73e8", suffix: str = "",
#                  icon: str = None, footer="", parent=None):
#         super().__init__(parent)
        
#         self.setStyleSheet("""
#             QFrame#KpiDamageCard {
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 10px;
#             }
#         """)
#         self.setObjectName("KpiDamageCard")
#         self.setMinimumHeight(110)
#         self.setMaximumHeight(130)
        
#         # --- Layout principal (vertical) ---
#         root = QVBoxLayout(self)
#         root.setContentsMargins(0, 0, 0, 0)
#         root.setSpacing(0)
        
#         # --- Bandeau titre bleu ---
#         header = QFrame()
#         header.setStyleSheet("""
#             QFrame {
#                 background-color: #2c5282;
#                 border-top-left-radius: 10px;
#                 border-top-right-radius: 10px;
#             }
#         """)
#         header.setFixedHeight(34)
        
#         h_layout = QHBoxLayout(header)
#         h_layout.setContentsMargins(15, 0, 15, 0)
        
#         title_lbl = QLabel(title)
#         title_lbl.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
#         h_layout.addWidget(title_lbl)
#         h_layout.addStretch()
        
#         root.addWidget(header)
        
#         # --- Corps (donut + valeur) ---
#         body = QWidget()
#         body_layout = QHBoxLayout(body)
#         body_layout.setContentsMargins(15, 10, 15, 12)
#         body_layout.setSpacing(12)
        
#         # Donut
#         if percent > 0 or suffix == "%":
#             self.donut = DonutPercent()
#             self.donut.set_data(percent, color)
#             self.donut.setFixedSize(50, 50)
#             body_layout.addWidget(self.donut)
        
#         # Valeur
#         v_layout = QVBoxLayout()
#         v_layout.setSpacing(2)
#         v_layout.setAlignment(Qt.AlignVCenter)
        
#         self.lbl_value = QLabel(value)
#         self.lbl_value.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e293b;")
#         v_layout.addWidget(self.lbl_value)
        
#         if suffix:
#             suffix_lbl = QLabel(suffix)
#             suffix_lbl.setStyleSheet("""
#                 background-color: #f1f5f9;
#                 color: #64748b;
#                 padding: 2px 8px;
#                 border-radius: 8px;
#                 font-size: 10px;
#                 font-weight: bold;
#             """)
#             suffix_lbl.setMaximumWidth(90)
#             suffix_lbl.setAlignment(Qt.AlignCenter)
#             v_layout.addWidget(suffix_lbl)
        
#         body_layout.addLayout(v_layout, 1)
        
#         # Icône optionnelle
#         if icon:
#             icon_lbl = QLabel(icon)
#             icon_lbl.setStyleSheet("font-size: 26px; color: #94a3b8;")
#             body_layout.addWidget(icon_lbl)
#         if footer:
#             self.lbl_footer = QLabel(footer)
#             self.lbl_footer.setStyleSheet("font-size: 10px; color: #64748b;")
#             layout.addWidget(self.lbl_footer)
        
#         root.addWidget(body, 1)

#     def set_footer(self, text):
#         if hasattr(self, 'lbl_footer'):
#             self.lbl_footer.setText(text)
    
#     def set_value(self, value: str):
#         self.lbl_value.setText(value)

from addons.sinistres.views.widgets.progress_widgets import ProgressBarKpi
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt


class KpiDamageCard(QFrame):
    """
    Carte KPI avec barre de progression horizontale
    (Remplace le donut par une barre plus lisible)
    """
    
    def __init__(
        self,
        title: str,
        value: str,
        percent: float = 0,
        color: str = "#1a73e8",
        suffix: str = "",
        icon: str = None,
        footer: str = "",
        parent=None
    ):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QFrame#KpiDamageCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        self.setObjectName("KpiDamageCard")
        self.setMinimumHeight(140)
        self.setMaximumHeight(160)
        
        # --- Layout principal (vertical) ---
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # --- Bandeau titre bleu ---
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #2c5282;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        header.setFixedHeight(34)
        
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(15, 0, 15, 0)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        h_layout.addWidget(title_lbl)
        h_layout.addStretch()
        
        root.addWidget(header)
        
        # --- Corps (valeur + icône) ---
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(18, 12, 18, 12)
        body_layout.setSpacing(10)
        
        # Ligne 1 : valeur + icône
        value_row = QHBoxLayout()
        value_row.setSpacing(10)
        
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        value_row.addWidget(self.lbl_value)
        
        value_row.addStretch()
        
        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 28px; color: #94a3b8;")
            value_row.addWidget(icon_lbl)
        
        body_layout.addLayout(value_row)
        
        # Ligne 2 : barre de progression
        progress_row = QHBoxLayout()
        progress_row.setSpacing(10)
        
        self.progress_bar = ProgressBarKpi(
            height=8,
            color=color,
            bg_color="#e2e8f0"
        )
        progress_row.addWidget(self.progress_bar, 1)
        
        # Label du pourcentage
        self.lbl_percent = QLabel(f"{int(percent)}%")
        self.lbl_percent.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #1e293b;
        """)
        self.lbl_percent.setFixedWidth(45)
        self.lbl_percent.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        progress_row.addWidget(self.lbl_percent)
        
        body_layout.addLayout(progress_row)
        
        # Ligne 3 : footer / suffix (optionnel)
        if suffix or footer:
            footer_row = QHBoxLayout()
            footer_row.setSpacing(6)
            
            if suffix:
                suffix_lbl = QLabel(suffix)
                suffix_lbl.setStyleSheet("""
                    background-color: #f1f5f9;
                    color: #64748b;
                    padding: 2px 8px;
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: bold;
                """)
                suffix_lbl.setMaximumWidth(100)
                suffix_lbl.setAlignment(Qt.AlignCenter)
                footer_row.addWidget(suffix_lbl)
            
            if footer:
                self.lbl_footer = QLabel(footer)
                self.lbl_footer.setStyleSheet("font-size: 10px; color: #94a3b8;")
                footer_row.addWidget(self.lbl_footer)
            
            footer_row.addStretch()
            body_layout.addLayout(footer_row)
        else:
            self.lbl_footer = None
        
        body_layout.addStretch()
        root.addWidget(body, 1)
        
        # Initialiser la barre
        self.progress_bar.set_percent(percent)
    
    # ============================================================
    # MISE À JOUR
    # ============================================================
    
    def set_value(
        self,
        value: str,
        percent: float = None,
        donut_label: str = None
    ):
        """
        Met à jour la valeur et la barre
        (paramètre 'donut_label' gardé pour compatibilité ascendante)
        """
        self.lbl_value.setText(value)
        
        if percent is not None:
            self.progress_bar.set_percent(percent)
            self.lbl_percent.setText(f"{int(percent)}%")
        
        # compatibilité : si donut_label est fourni, l'utiliser comme pourcentage
        if donut_label and percent is None:
            try:
                pct = float(donut_label.replace('%', '').strip())
                self.progress_bar.set_percent(pct)
                self.lbl_percent.setText(f"{int(pct)}%")
            except (ValueError, AttributeError):
                pass
    
    def set_footer(self, text: str):
        """Met à jour le footer"""
        if self.lbl_footer:
            self.lbl_footer.setText(text)
    
    def set_color(self, color: str):
        """Change la couleur de la barre"""
        self.progress_bar.set_color(color)

        
# ============================================================
# DONUT PERCENT (cercle avec %)
# ============================================================

class DonutPercent(QWidget):
    """Petit donut circulaire avec pourcentage au centre"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._percent = 0
        self._color = "#1a73e8"
    
    def set_data(self, percent: float, color: str = "#1a73e8"):
        self._percent = max(0, min(100, percent))
        self._color = color
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        size = min(w, h) - 6
        rect = QRectF((w - size) / 2, (h - size) / 2, size, size)
        
        # Fond gris
        pen = QPen(QColor("#e2e8f0"), 5, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Arc coloré
        pen = QPen(QColor(self._color), 5, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        span = -int(self._percent / 100 * 360 * 16)
        painter.drawArc(rect, 90 * 16, span)
        
        # Pourcentage au centre
        painter.setPen(QColor("#1e293b"))
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{int(self._percent)}%")


# ============================================================
# DAMAGE ROW (ligne pliable)
# ============================================================

class DamageRow(QWidget):
    """Ligne d'un dommage, pliable pour afficher détails"""
    
    edit_clicked = Signal(dict)
    validate_clicked = Signal(dict)
    reject_clicked = Signal(dict)
    delete_clicked = Signal(dict)
    context_menu_requested = Signal(dict, object)
    
    def __init__(self, dommage: dict, parent=None):
        super().__init__(parent)
        self.dommage = dommage
        self._expanded = False


        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)


        self.setStyleSheet("""
            DamageRow {
                background-color: white;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # --- Ligne principale ---
        self.main_row = QWidget()
        main_layout = QHBoxLayout(self.main_row)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)
        
        # Chevron (expand)
        self.btn_chevron = QPushButton("▶")
        self.btn_chevron.setFixedSize(24, 24)
        self.btn_chevron.setCursor(Qt.PointingHandCursor)
        self.btn_chevron.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 10px;
                color: #64748b;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-radius: 4px;
            }
        """)
        self.btn_chevron.clicked.connect(self._toggle_expand)
        main_layout.addWidget(self.btn_chevron)
        
        # Type
        type_lbl = QLabel(dommage.get('type_dommage', 'N/A'))
        type_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #1e293b;")
        type_lbl.setFixedWidth(140)
        main_layout.addWidget(type_lbl)
        
        # Description
        desc_lbl = QLabel(dommage.get('description', '')[:60])
        desc_lbl.setStyleSheet("font-size: 11px; color: #64748b;")
        desc_lbl.setWordWrap(False)
        main_layout.addWidget(desc_lbl, 1)
        
        # Montant estimé
        estim_lbl = QLabel(self._format_montant(dommage.get('montant_estime', 0)))
        estim_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #1e293b;")
        estim_lbl.setFixedWidth(90)
        estim_lbl.setAlignment(Qt.AlignRight)
        main_layout.addWidget(estim_lbl)
        
        # Montant accepté
        accept_lbl = QLabel(self._format_montant(dommage.get('montant_accepte', 0)))
        accept_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #22c55e;")
        accept_lbl.setFixedWidth(90)
        accept_lbl.setAlignment(Qt.AlignRight)
        main_layout.addWidget(accept_lbl)
        
        # Statut évaluation
        statut = self._get_statut_evaluation(dommage)
        statut_lbl = QLabel(statut)
        statut_lbl.setStyleSheet(f"""
            background-color: {self._get_statut_color(statut)[0]};
            color: {self._get_statut_color(statut)[1]};
            padding: 2px 10px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: bold;
        """)
        statut_lbl.setFixedWidth(90)
        statut_lbl.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(statut_lbl)
        
        # Actions
        actions = QHBoxLayout()
        actions.setSpacing(4)
        
        for icon, signal in [
            ("✏️", self.edit_clicked),
            ("✔️", self.validate_clicked),
            ("❌", self.reject_clicked),
        ]:
            btn = QPushButton(icon)
            btn.setFixedSize(26, 26)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #f1f5f9;
                }
            """)
            btn.clicked.connect(lambda checked=False, s=signal: s.emit(dommage))
            actions.addWidget(btn)
        
        main_layout.addLayout(actions)
        
        root.addWidget(self.main_row)
        
        # --- Panneau étendu (caché par défaut) ---
        self.expanded_panel = self._build_expanded_panel(dommage)
        self.expanded_panel.hide()
        root.addWidget(self.expanded_panel)
    
    # def _build_expanded_panel(self, dommage: dict) -> QWidget:
    #     panel = QFrame()
    #     panel.setStyleSheet("""
    #         QFrame {
    #             background-color: #f8fafc;
    #             border-top: 1px solid #e2e8f0;
    #         }
    #     """)
        
    #     layout = QHBoxLayout(panel)
    #     layout.setContentsMargins(45, 15, 15, 15)
    #     layout.setSpacing(15)
        
    #     # --- Photos (gauche) ---
    #     photos_widget = QWidget()
    #     photos_layout = QHBoxLayout(photos_widget)
    #     photos_layout.setContentsMargins(0, 0, 0, 0)
    #     photos_layout.setSpacing(6)
        
    #     photos = dommage.get('photos', []) or []

    #     # Si aucune photo réelle, utiliser des placeholders cliquables
    #     if not photos:
    #         photos = [f"placeholder_{i}.png" for i in range(4)]

    #     # Créer les vignettes
    #     for i, photo_path in enumerate(photos):
    #         thumb = PhotoThumbnail(photo_path, all_photos=photos)
    #         thumb.clicked.connect(
    #             lambda path, p=photos, idx=i: self._open_photo_viewer(p, idx)
    #         )
    #         photos_layout.addWidget(thumb)
        
    #     layout.addWidget(photos_widget)
        
    #     # --- Rapport + description (droite) ---
    #     report_widget = QFrame()
    #     report_widget.setStyleSheet("""
    #         QFrame {
    #             background-color: white;
    #             border: 1px solid #e2e8f0;
    #             border-radius: 8px;
    #         }
    #     """)
        
    #     report_layout = QVBoxLayout(report_widget)
    #     report_layout.setContentsMargins(12, 10, 12, 10)
    #     report_layout.setSpacing(6)
        
    #     # Ligne rapport
    #     header_row = QHBoxLayout()
    #     header_row.setSpacing(8)
        
    #     doc_icon = QLabel("📕")
    #     doc_icon.setStyleSheet("font-size: 14px;")
    #     header_row.addWidget(doc_icon)
        
    #     doc_name = QLabel("Rapport d'estimation phare.pdf")
    #     doc_name.setStyleSheet("font-size: 11px; color: #1e293b; font-weight: 600;")
    #     header_row.addWidget(doc_name)
    #     header_row.addStretch()
        
    #     for icon in ["✏️", "✔️", "❌"]:
    #         btn = QPushButton(icon)
    #         btn.setFixedSize(22, 22)
    #         btn.setStyleSheet("""
    #             QPushButton {
    #                 background-color: transparent;
    #                 border: none;
    #                 border-radius: 4px;
    #                 font-size: 11px;
    #             }
    #             QPushButton:hover {
    #                 background-color: #f1f5f9;
    #             }
    #         """)
    #         header_row.addWidget(btn)
        
    #     report_layout.addLayout(header_row)
        
    #     # Description détaillée
    #     desc = QLabel(dommage.get('description', '') or "Aucune description détaillée")
    #     desc.setStyleSheet("font-size: 11px; color: #64748b;")
    #     desc.setWordWrap(True)
    #     report_layout.addWidget(desc)
        
    #     layout.addWidget(report_widget, 1)
        
    #     return panel

    def _build_expanded_panel(self, dommage: dict) -> QWidget:
        """
        Construit le panneau étendu avec :
        - Aperçu des photos (via FileService)
        - Rapport + description
        """
        # ============================================================
        # Conteneur principal du panneau
        # ============================================================
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame#ExpandedPanel {
                background-color: #f8fafc;
                border-top: 1px solid #e2e8f0;
            }
        """)
        panel.setObjectName("ExpandedPanel")
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(45, 15, 15, 15)
        layout.setSpacing(15)
        
        # ============================================================
        # GAUCHE : Photos
        # ============================================================
        photos_widget = self._build_photos_section(dommage)
        layout.addWidget(photos_widget)
        
        # ============================================================
        # DROITE : Rapport + description
        # ============================================================
        report_widget = self._build_report_section(dommage)
        layout.addWidget(report_widget, 1)
        
        return panel


    # ============================================================
    # SECTION PHOTOS
    # ============================================================

    def _build_photos_section(self, dommage: dict) -> QWidget:
        """Construit la section photos avec vignettes cliquables"""
        
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        
        # Layout vertical : titre + grille de photos
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(8)
        
        # --- Charger les photos ---
        photos_abs = self._load_photos_absolute(dommage)
        
        # --- Titre avec compteur ---
        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        
        title = QLabel(f"📷 Photos ({len(photos_abs)})")
        title.setStyleSheet("font-size: 11px; font-weight: bold; color: #1e293b;")
        title_row.addWidget(title)
        title_row.addStretch()
        vbox.addLayout(title_row)
        
        # --- Grille de vignettes ---
        if not photos_abs:
            # Aucune photo : placeholder
            empty = QLabel("Aucune photo")
            empty.setFixedSize(70, 50)
            empty.setStyleSheet("""
                background-color: white;
                border: 1px dashed #cbd5e1;
                border-radius: 6px;
                color: #94a3b8;
                font-size: 10px;
                font-style: italic;
            """)
            empty.setAlignment(Qt.AlignCenter)
            vbox.addWidget(empty)
        else:
            # Grille de vignettes (4 max affichées, +N si plus)
            photos_grid = QHBoxLayout()
            photos_grid.setSpacing(6)
            
            from addons.sinistres.views.widgets.damage_widgets import PhotoThumbnail
            
            # Afficher jusqu'à 4 photos, le reste en "+N"
            max_display = 4
            for i, abs_path in enumerate(photos_abs[:max_display]):
                thumb = PhotoThumbnail(abs_path, all_photos=photos_abs)
                thumb.clicked.connect(
                    lambda path, p=photos_abs, idx=i: self._open_photo_viewer(p, idx)
                )
                photos_grid.addWidget(thumb)
            
            # Badge "+N" si plus de photos
            if len(photos_abs) > max_display:
                more = len(photos_abs) - max_display
                badge = QLabel(f"+{more}")
                badge.setFixedSize(70, 50)
                badge.setStyleSheet("""
                    background-color: #e8f0fe;
                    color: #1a73e8;
                    border: 1px solid #bfdbfe;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: bold;
                """)
                badge.setAlignment(Qt.AlignCenter)
                badge.setCursor(Qt.PointingHandCursor)
                badge.setToolTip(f"Voir les {more} autres photos")
                badge.mousePressEvent = lambda e, p=photos_abs, idx=max_display: self._open_photo_viewer(p, idx)
                photos_grid.addWidget(badge)
            
            photos_grid.addStretch()
            vbox.addLayout(photos_grid)
        
        vbox.addStretch()
        return container


    # ============================================================
    # SECTION RAPPORT + DESCRIPTION
    # ============================================================

    def _build_report_section(self, dommage: dict) -> QFrame:
        """Construit la section rapport + description détaillée"""
        
        report_widget = QFrame()
        report_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        
        report_layout = QVBoxLayout(report_widget)
        report_layout.setContentsMargins(12, 10, 12, 10)
        report_layout.setSpacing(8)
        
        # --- Ligne 1 : Fichier rapport (si disponible) ---
        rapport = dommage.get('rapport') or {}
        rapport_nom = rapport.get('nom') or "Aucun rapport joint"
        rapport_path = rapport.get('chemin')
        
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        
        doc_icon = QLabel("📕" if rapport_path else "📄")
        doc_icon.setStyleSheet("font-size: 14px;")
        header_row.addWidget(doc_icon)
        
        doc_name = QLabel(rapport_nom)
        doc_name.setStyleSheet("""
            font-size: 11px;
            color: #1e293b;
            font-weight: 600;
        """)
        doc_name.setWordWrap(False)
        header_row.addWidget(doc_name)
        header_row.addStretch()
        
        # Boutons d'action sur le rapport
        if rapport_path:
            btn_open = QPushButton("👁️")
            btn_open.setFixedSize(22, 22)
            btn_open.setToolTip("Ouvrir le rapport")
            btn_open.setCursor(Qt.PointingHandCursor)
            btn_open.setStyleSheet(self._mini_btn_style())
            btn_open.clicked.connect(lambda: self._ouvrir_rapport(rapport_path))
            header_row.addWidget(btn_open)
        
        btn_attach = QPushButton("📎")
        btn_attach.setFixedSize(22, 22)
        btn_attach.setToolTip("Joindre un rapport")
        btn_attach.setCursor(Qt.PointingHandCursor)
        btn_attach.setStyleSheet(self._mini_btn_style())
        btn_attach.clicked.connect(lambda: self._joindre_rapport(dommage))
        header_row.addWidget(btn_attach)
        
        for icon, tooltip in [("✏️", "Modifier"), ("✔️", "Valider"), ("❌", "Rejeter")]:
            btn = QPushButton(icon)
            btn.setFixedSize(22, 22)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self._mini_btn_style())
            header_row.addWidget(btn)
        
        report_layout.addLayout(header_row)
        
        # --- Séparateur ---
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #f1f5f9; max-height: 1px; border: none;")
        report_layout.addWidget(sep)
        
        # --- Description détaillée ---
        description = dommage.get('description') or "Aucune description détaillée"
        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet("""
            font-size: 11px;
            color: #64748b;
            line-height: 1.5;
        """)
        desc_lbl.setWordWrap(True)
        desc_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        report_layout.addWidget(desc_lbl)
        
        # --- Ligne d'infos secondaires ---
        info_row = QHBoxLayout()
        info_row.setSpacing(12)
        
        # Date de création si dispo
        created = dommage.get('created_at')
        if created:
            date_str = str(created)[:10]
            lbl_date = QLabel(f"📅 {date_str}")
            lbl_date.setStyleSheet("color: #94a3b8; font-size: 10px;")
            info_row.addWidget(lbl_date)
        
        # ID évaluation si dispo
        eval_id = dommage.get('evaluation_id')
        if eval_id:
            lbl_eval = QLabel(f"🔗 Éval #{eval_id}")
            lbl_eval.setStyleSheet("color: #94a3b8; font-size: 10px;")
            info_row.addWidget(lbl_eval)
        
        info_row.addStretch()
        report_layout.addLayout(info_row)
        
        return report_widget


    # ============================================================
    # HELPERS PHOTOS
    # ============================================================

    def _load_photos_absolute(self, dommage: dict) -> list:
        """
        Charge les chemins absolus des photos d'un dommage.
        Gère :
        - Les chemins relatifs (via FileService)
        - Les chemins absolus (fallback, pour compatibilité)
        - Les URLs (http://...)
        """
        photos_raw = dommage.get('photos', []) or []
        
        if not photos_raw:
            return []
        
        # Si c'est une string JSON (parfois le cas), parser
        if isinstance(photos_raw, str):
            try:
                import json
                photos_raw = json.loads(photos_raw)
            except Exception:
                photos_raw = [photos_raw]
        
        if not isinstance(photos_raw, list):
            return []
        
        # Résoudre chaque chemin
        from addons.sinistres.services.file_service import get_file_service
        file_service = get_file_service()
        
        resolved = []
        for p in photos_raw:
            if not p:
                continue
            
            # Cas 1 : chemin absolu direct
            if os.path.isabs(p) and os.path.exists(p):
                resolved.append(p)
                continue
            
            # Cas 2 : URL http/https (à supporter plus tard)
            if p.startswith(('http://', 'https://')):
                # Pour l'instant on ignore, à étendre
                continue
            
            # Cas 3 : chemin relatif → résoudre via FileService
            abs_path = file_service.get_absolute_path(p)
            if abs_path:
                resolved.append(abs_path)
        
        return resolved


    def _open_photo_viewer(self, photos: list, index: int):
        """Ouvre le dialogue d'aperçu photo"""
        from addons.sinistres.views.widgets.damage_widgets import PhotoViewerDialog
        dialog = PhotoViewerDialog(photos, current_index=index, parent=self)
        dialog.exec()


    # ============================================================
    # HELPERS RAPPORT
    # ============================================================

    def _ouvrir_rapport(self, rapport_path: str):
        """Ouvre un rapport PDF ou DOCX"""
        import subprocess
        import platform
        
        # Résoudre le chemin via FileService
        from addons.sinistres.services.file_service import get_file_service
        file_service = get_file_service()
        
        abs_path = file_service.get_absolute_path(rapport_path)
        if not abs_path:
            QMessageBox.warning(self, "Erreur", "Fichier introuvable")
            return
        
        try:
            if platform.system() == 'Windows':
                os.startfile(abs_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', abs_path])
            else:  # Linux
                subprocess.call(['xdg-open', abs_path])
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible d'ouvrir le fichier: {e}")


    def _joindre_rapport(self, dommage: dict):
        """Ouvre un sélecteur pour joindre un rapport"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un rapport",
            "",
            "Documents (*.pdf *.doc *.docx *.xls *.xlsx);;Tous les fichiers (*)"
        )
        
        if not file_path:
            return
        
        # Copier via FileService (à implémenter)
        from addons.sinistres.services.file_service import get_file_service
        file_service = get_file_service()
        
        # TODO: ajouter méthode save_dommage_rapport dans FileService
        # Pour l'instant, on copie comme photo
        rel_path = file_service.save_dommage_photo(
            sinistre_id=self.dommage.get('sinistre_id'),
            source_path=file_path,
            compress=False
        )
        
        if rel_path:
            QMessageBox.information(
                self, "Succès",
                f"Rapport joint : {Path(file_path).name}\n\n"
                f"À associer au dommage (fonctionnalité à compléter)"
            )


    # ============================================================
    # STYLE BOUTONS MINI
    # ============================================================

    def _mini_btn_style(self) -> str:
        return """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """
  
    def _toggle_expand(self):
        self._expanded = not self._expanded
        if self._expanded:
            self.expanded_panel.show()
            self.btn_chevron.setText("▼")
        else:
            self.expanded_panel.hide()
            self.btn_chevron.setText("▶")
    
    # --- Helpers ---
    
    def _format_montant(self, montant) -> str:
        try:
            return f"FCFA {float(montant):,.0f}".replace(",", " ")
        except (ValueError, TypeError):
            return "FCFA 0"
    
    def _get_statut_evaluation(self, dommage: dict) -> str:
        if dommage.get('montant_accepte'):
            return "Validée"
        elif dommage.get('evaluation_id'):
            return "En attente"
        else:
            return "À évaluer"
    
    def _get_statut_color(self, statut: str):
        mapping = {
            "Validée": ("#dcfce7", "#166534"),
            "En attente": ("#fef3c7", "#92400e"),
            "À évaluer": ("#f1f5f9", "#64748b"),
        }
        return mapping.get(statut, ("#f1f5f9", "#64748b"))

    def _on_context_menu(self, pos):
        """Émet un signal pour que le parent affiche le menu"""
        global_pos = self.mapToGlobal(pos)
        self.context_menu_requested.emit(self.dommage, global_pos)
    
    def set_selected(self, selected: bool):
        """Met en surbrillance la ligne sélectionnée"""
        if selected:
            self.main_row.setStyleSheet("""
                QWidget {
                    background-color: #e8f0fe;
                }
            """)
        else:
            self.main_row.setStyleSheet("")

    def _open_photo_viewer(self, photos: list, index: int):
        """Ouvre le dialogue d'aperçu photo"""
        dialog = PhotoViewerDialog(photos, current_index=index, parent=self)
        dialog.exec()


class PhotoThumbnail(QLabel):
    """Vignette cliquable qui ouvre un aperçu"""
    
    clicked = Signal(str)  # émet le chemin de la photo
    
    def __init__(self, photo_path: str, all_photos: list = None, parent=None):
        super().__init__(parent)
        self.photo_path = photo_path
        self.all_photos = all_photos or [photo_path]
        
        self.setFixedSize(70, 50)
        self.setCursor(Qt.PointingHandCursor)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 24px;
            }
            QLabel:hover {
                border: 2px solid #1a73e8;
            }
        """)
        
        # Charger la photo si possible, sinon afficher un placeholder
        pixmap = QPixmap(photo_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(66, 46, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)
        else:
            self.setText("🖼️")
        
        self.setToolTip("Cliquez pour agrandir")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.photo_path)
        super().mousePressEvent(event)


class PhotoViewerDialog(QDialog):
    """Dialogue d'aperçu photo avec navigation"""
    
    def __init__(self, photos: list, current_index: int = 0, parent=None):
        super().__init__(parent)
        self.photos = photos
        self.current_index = max(0, min(current_index, len(photos) - 1))
        
        self.setWindowTitle("Aperçu photo")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e293b;
            }
        """)
        
        self._setup_ui()
        self._load_photo()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # --- Barre supérieure : nom + fermer ---
        header = QHBoxLayout()
        
        self.lbl_name = QLabel("")
        self.lbl_name.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        header.addWidget(self.lbl_name)
        header.addStretch()
        
        self.lbl_counter = QLabel("")
        self.lbl_counter.setStyleSheet("color: #94a3b8; font-size: 12px;")
        header.addWidget(self.lbl_counter)
        
        btn_close = QPushButton("✖")
        btn_close.setFixedSize(30, 30)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ef4444;
            }
        """)
        btn_close.clicked.connect(self.reject)
        header.addWidget(btn_close)
        
        layout.addLayout(header)
        
        # --- Zone photo + navigation ---
        content = QHBoxLayout()
        content.setSpacing(10)
        
        # Bouton précédent
        self.btn_prev = QPushButton("◀")
        self.btn_prev.setFixedSize(50, 50)
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
            QPushButton:disabled {
                color: rgba(255, 255, 255, 0.2);
                background-color: transparent;
            }
        """)
        self.btn_prev.clicked.connect(self._prev)
        content.addWidget(self.btn_prev)
        
        # Zone d'affichage de la photo
        self.photo_scroll = QScrollArea()
        self.photo_scroll.setWidgetResizable(True)
        self.photo_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        self.photo_container = QLabel()
        self.photo_container.setAlignment(Qt.AlignCenter)
        self.photo_container.setStyleSheet("background-color: transparent;")
        self.photo_scroll.setWidget(self.photo_container)
        content.addWidget(self.photo_scroll, 1)
        
        # Bouton suivant
        self.btn_next = QPushButton("▶")
        self.btn_next.setFixedSize(50, 50)
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setStyleSheet(self.btn_prev.styleSheet())
        self.btn_next.clicked.connect(self._next)
        content.addWidget(self.btn_next)
        
        layout.addLayout(content, 1)
        
        # --- Barre inférieure : zoom + retour ---
        footer = QHBoxLayout()
        
        self.btn_zoom_out = QPushButton("➖")
        self.btn_zoom_out.setFixedSize(32, 32)
        self.btn_zoom_out.setStyleSheet(self._zoom_btn_style())
        self.btn_zoom_out.clicked.connect(lambda: self._zoom(-0.2))
        footer.addWidget(self.btn_zoom_out)
        
        self.btn_zoom_in = QPushButton("➕")
        self.btn_zoom_in.setFixedSize(32, 32)
        self.btn_zoom_in.setStyleSheet(self._zoom_btn_style())
        self.btn_zoom_in.clicked.connect(lambda: self._zoom(0.2))
        footer.addWidget(self.btn_zoom_in)
        
        self.btn_reset = QPushButton("↺ 100%")
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                padding: 4px 12px;
                border: none;
                border-radius: 6px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)
        self.btn_reset.clicked.connect(self._reset_zoom)
        footer.addWidget(self.btn_reset)
        
        footer.addStretch()
        
        self.lbl_zoom = QLabel("100%")
        self.lbl_zoom.setStyleSheet("color: #94a3b8; font-size: 12px;")
        footer.addWidget(self.lbl_zoom)
        
        layout.addLayout(footer)
        
        # État du zoom
        self._zoom_factor = 1.0
        self._original_pixmap = None
        self._update_nav_buttons()
    
    def _zoom_btn_style(self):
        return """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """
    
    # def _load_photo(self):
    #     """Charge la photo courante"""
    #     if not self.photos:
    #         self.photo_container.setText("Aucune photo")
    #         return
        
    #     path = self.photos[self.current_index]
    #     pixmap = QPixmap(path)
        
    #     if pixmap.isNull():
    #         # Fallback : afficher un placeholder
    #         self.photo_container.setText("🖼️  Image non disponible")
    #         self.photo_container.setStyleSheet("color: white; font-size: 20px;")
    #         self._original_pixmap = None
    #     else:
    #         self._original_pixmap = pixmap
    #         self._reset_zoom()
        
    #     # Mise à jour du nom et du compteur
    #     import os
    #     self.lbl_name.setText(os.path.basename(path))
    #     self.lbl_counter.setText(f"{self.current_index + 1} / {len(self.photos)}")
    #     self._update_nav_buttons()
    
    def _load_photo(self):
        """Charge la photo courante"""
        if not self.photos:
            self.photo_container.setText("Aucune photo")
            return
        
        path = self.photos[self.current_index]
        
        # ✅ Résoudre le chemin via FileService si nécessaire
        if not os.path.isabs(path):
            from addons.sinistres.services.file_service import get_file_service
            file_service = get_file_service()
            abs_path = file_service.get_absolute_path(path)
            if abs_path:
                path = abs_path
        
        pixmap = QPixmap(path)
        
        if pixmap.isNull():
            self.photo_container.setText("🖼️  Image non disponible")
            self.photo_container.setStyleSheet("color: white; font-size: 20px;")
            self._original_pixmap = None
        else:
            self._original_pixmap = pixmap
            self._reset_zoom()
        
        # Mise à jour du nom
        self.lbl_name.setText(os.path.basename(path))
        self.lbl_counter.setText(f"{self.current_index + 1} / {len(self.photos)}")
        self._update_nav_buttons()

    def _update_nav_buttons(self):
        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(self.current_index < len(self.photos) - 1)
    
    def _prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self._load_photo()
    
    def _next(self):
        if self.current_index < len(self.photos) - 1:
            self.current_index += 1
            self._load_photo()
    
    def _zoom(self, delta: float):
        self._zoom_factor = max(0.2, min(3.0, self._zoom_factor + delta))
        self._apply_zoom()
    
    def _reset_zoom(self):
        self._zoom_factor = 1.0
        self._apply_zoom()
    
    def _apply_zoom(self):
        if not self._original_pixmap:
            return
        
        new_size = self._original_pixmap.size() * self._zoom_factor
        scaled = self._original_pixmap.scaled(
            new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.photo_container.setPixmap(scaled)
        self.photo_container.setFixedSize(scaled.size())
        self.lbl_zoom.setText(f"{int(self._zoom_factor * 100)}%")
    
    def keyPressEvent(self, event):
        """Navigation au clavier"""
        if event.key() == Qt.Key_Left:
            self._prev()
        elif event.key() == Qt.Key_Right:
            self._next()
        elif event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Plus, Qt.Key_Equal):
            self._zoom(0.2)
        elif event.key() == Qt.Key_Minus:
            self._zoom(-0.2)
        elif event.key() == Qt.Key_0:
            self._reset_zoom()
        else:
            super().keyPressEvent(event)