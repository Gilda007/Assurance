
"""
Dialogue de création de mission d'expertise — Design v5.0 (maquette)
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QDateEdit, QScrollArea, QPushButton, QMessageBox,
    QWidget, QFrame, QButtonGroup, QDoubleSpinBox, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QColor, QPixmap

from pathlib import Path
import qtawesome as qta


# ═══════════════════════════════════════════════════════════════════
# STYLES
# ═══════════════════════════════════════════════════════════════════

STYLE = """
    QDialog { background: #f4f4f5; }

    QFrame#Card {
        background: #ffffff;
        border-radius: 12px;
    }

    QLabel { background: transparent; }
    QLabel#Title {
        font-size: 18px; font-weight: 700; color: #18181b;
    }
    QLabel#Subtitle {
        font-size: 13px; color: #71717a;
    }
    QLabel#SectionLabel {
        font-size: 11px; font-weight: 700; color: #3f3f46;
        letter-spacing: 0.5px;
    }

    /* Champs */
    QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QTextEdit {
        background: #ffffff;
        border: 1px solid #d4d4d8;
        border-radius: 8px;
        padding: 9px 12px;
        font-size: 13px;
        color: #18181b;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
    QDoubleSpinBox:focus, QTextEdit:focus {
        border: 1px solid #2563eb;
    }
    QComboBox::drop-down, QDateEdit::drop-down { border: none; width: 28px; }
    QComboBox::down-arrow, QDateEdit::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #71717a;
        margin-right: 10px;
    }

    /* Boutons */
    QPushButton#BtnCancel {
        background: #ffffff;
        border: 1px solid #d4d4d8;
        border-radius: 8px;
        padding: 8px 18px;
        font-size: 13px;
        font-weight: 500;
        color: #18181b;
    }
    QPushButton#BtnCancel:hover { background: #fafafa; }

    QPushButton#BtnPrimary {
        background: #1d4ed8;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 13px;
        font-weight: 600;
        color: #ffffff;
    }
    QPushButton#BtnPrimary:hover { background: #1e40af; }

    QPushButton#BtnClose {
        background: transparent; border: none;
    }
    QPushButton#BtnClose:hover { background: #f4f4f5; border-radius: 6px; }

    /* Sélecteur segmenté */
    QPushButton#Segment {
        background: #e4e4e7;
        border: none;
        border-radius: 6px;
        padding: 8px 14px;
        font-size: 13px;
        font-weight: 600;
        color: #52525b;
    }
    QPushButton#Segment:checked {
        background: #1d4ed8;
        color: #ffffff;
    }
"""


def _section(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("SectionLabel")
    return lbl


# ═══════════════════════════════════════════════════════════════════
# DIALOGUE
# ═══════════════════════════════════════════════════════════════════

class MissionDialog(QDialog):
    mission_created = Signal(dict)

    def __init__(self, sinistre_id, expertise_controller, user,
                 sinistre_info=None, expert_controller=None, parent=None,
                 force_type_code: str = None, force_mission_parente_id: int = None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.expertise_controller = expertise_controller
        self.expert_controller = expert_controller or expertise_controller
        self.user = user
        self.sinistre_info = sinistre_info or {}
        self.force_type_code = force_type_code
        self.force_mission_parente_id = force_mission_parente_id

        try:
            from addons.sinistres.services.file_service import get_file_service
            self.file_service = get_file_service()
        except ImportError:
            self.file_service = None

        self._types_mission = []
        self._type_buttons = {}  # code -> QPushButton segmenté

        self.setWindowTitle("Créer une mission")
        self.setModal(True)
        self.setMinimumSize(720, 640)
        self.setStyleSheet(STYLE)

        self._setup_ui()
        self._load_types_mission()
        self._load_experts()
        self._update_summary()

    def _get_user_id(self):
        if not self.user:
            return None
        if hasattr(self.user, 'id'):
            return self.user.id
        if isinstance(self.user, dict):
            return self.user.get('id') or self.user.get('user_id')
        return getattr(self.user, 'user_id', None)

    # ═══════════════════════════════════════════════════════════════
    # UI
    # ═══════════════════════════════════════════════════════════════
    # def _setup_ui(self):
    #     root = QVBoxLayout(self)
    #     root.setContentsMargins(24, 24, 24, 24)
    #     root.setAlignment(Qt.AlignCenter)

    #     # Carte
    #     self.card = QFrame()
    #     self.card.setObjectName("Card")
    #     self.card.setFixedWidth(640)
    #     shadow = QGraphicsDropShadowEffect(self.card)
    #     shadow.setBlurRadius(24)
    #     shadow.setColor(QColor(0, 0, 0, 20))
    #     shadow.setOffset(0, 4)
    #     self.card.setGraphicsEffect(shadow)

    #     cl = QVBoxLayout(self.card)
    #     cl.setContentsMargins(32, 28, 32, 24)
    #     cl.setSpacing(18)

    #     # ─── HEADER ───
    #     cl.addLayout(self._build_header())
    #     cl.addWidget(self._separator())

    #     # ─── TYPE ───
    #     cl.addWidget(_section("MISSION TYPE"))
    #     self.segment_row = QHBoxLayout()
    #     self.segment_row.setSpacing(0)
    #     cl.addLayout(self.segment_row)

    #     # ─── EXPERT ───
    #     cl.addWidget(_section("EXPERT"))
    #     self.input_expert = QComboBox()
    #     self.input_expert.setEditable(True)
    #     self.input_expert.addItem("— Sélectionner un expert —", None)
    #     self.input_expert.currentIndexChanged.connect(self._on_expert_changed)
    #     cl.addWidget(self.input_expert)

    #     # Petit lien "Créer un expert"
    #     link_row = QHBoxLayout()
    #     link_row.setContentsMargins(0, -6, 0, 0)
    #     self.btn_new_expert = QPushButton("+ Créer un expert")
    #     self.btn_new_expert.setCursor(Qt.PointingHandCursor)
    #     self.btn_new_expert.setStyleSheet("""
    #         QPushButton {
    #             background: transparent;
    #             color: #1d4ed8;
    #             border: none;
    #             font-size: 12px;
    #             text-align: left;
    #             padding: 0;
    #         }
    #         QPushButton:hover { text-decoration: underline; }
    #     """)
    #     self.btn_new_expert.clicked.connect(self._open_new_expert_dialog)
    #     link_row.addWidget(self.btn_new_expert)
    #     link_row.addStretch()
    #     cl.addLayout(link_row)

    #     # ─── PERIOD ───
    #     cl.addWidget(_section("PERIOD"))
    #     period_row = QHBoxLayout()
    #     period_row.setSpacing(12)
    #     self.input_date_mission = self._date_field("From")
    #     self.input_echeance = self._date_field("To")
    #     self.input_date_mission.dateChanged.connect(self._update_summary)
    #     self.input_echeance.dateChanged.connect(self._update_summary)
    #     period_row.addWidget(self.input_date_mission, 1)
    #     period_row.addWidget(self.input_echeance, 1)
    #     cl.addLayout(period_row)

    #     # ─── AMOUNT ───
    #     cl.addWidget(_section("MISSION AMOUNT"))
    #     amount_row = QHBoxLayout()
    #     amount_row.setSpacing(0)
    #     self.input_montant = QDoubleSpinBox()
    #     self.input_montant.setRange(0, 999999999)
    #     self.input_montant.setDecimals(0)
    #     self.input_montant.setSingleStep(10000)
    #     self.input_montant.setGroupSeparatorShown(True)
    #     self.input_montant.setButtonSymbols(QDoubleSpinBox.NoButtons)
    #     self.input_montant.setStyleSheet("""
    #         QDoubleSpinBox {
    #             background: #ffffff;
    #             border: 1px solid #d4d4d8;
    #             border-top-right-radius: 0;
    #             border-bottom-right-radius: 0;
    #             border-right: none;
    #             padding: 9px 12px;
    #             font-size: 13px;
    #             color: #18181b;
    #         }
    #         QDoubleSpinBox:focus { border-color: #2563eb; }
    #     """)
    #     self.input_montant.valueChanged.connect(self._update_summary)
    #     amount_row.addWidget(self.input_montant, 1)

    #     unit = QLabel("FCFA")
    #     unit.setStyleSheet("""
    #         background: #f4f4f5;
    #         border: 1px solid #d4d4d8;
    #         border-top-right-radius: 8px;
    #         border-bottom-right-radius: 8px;
    #         padding: 9px 14px;
    #         font-size: 12px;
    #         font-weight: 600;
    #         color: #52525b;
    #     """)
    #     amount_row.addWidget(unit)
    #     cl.addLayout(amount_row)

    #     # ─── ZONE CONTRE-EXPERTISE (masquée par défaut) ───
    #     self.parent_block = QFrame()
    #     self.parent_block.setVisible(False)
    #     pl = QVBoxLayout(self.parent_block)
    #     pl.setContentsMargins(0, 0, 0, 0)
    #     pl.setSpacing(10)

    #     pl.addWidget(self._separator())
    #     pl.addWidget(_section("PARENT MISSION (contre-expertise)"))

    #     self.parent_combo = QComboBox()
    #     self.parent_combo.currentIndexChanged.connect(self._on_parent_changed)
    #     pl.addWidget(self.parent_combo)

    #     pl.addWidget(_section("REASON"))
    #     self.motif_input = QTextEdit()
    #     self.motif_input.setPlaceholderText("Expliquez pourquoi cette contre-expertise est nécessaire…")
    #     self.motif_input.setFixedHeight(60)
    #     self.motif_input.textChanged.connect(self._update_summary)
    #     pl.addWidget(self.motif_input)

    #     cl.addWidget(self.parent_block)

    #     # ─── DÉTAILS OPTIONNELS (repliés) ───
    #     self.details_toggle = QPushButton("＋ Options avancées")
    #     self.details_toggle.setCursor(Qt.PointingHandCursor)
    #     self.details_toggle.setCheckable(True)
    #     self.details_toggle.setStyleSheet("""
    #         QPushButton {
    #             background: transparent; border: none;
    #             color: #71717a; font-size: 12px;
    #             text-align: left; padding: 0;
    #         }
    #         QPushButton:hover { color: #18181b; }
    #     """)
    #     self.details_toggle.toggled.connect(self._toggle_details)
    #     cl.addWidget(self.details_toggle)

    #     self.details_block = QWidget()
    #     self.details_block.setVisible(False)
    #     dl = QVBoxLayout(self.details_block)
    #     dl.setContentsMargins(0, 8, 0, 0)
    #     dl.setSpacing(10)

    #     dl.addWidget(_section("TYPE D'EXPERTISE"))
    #     self.input_type = QComboBox()
    #     self.input_type.addItems([
    #         "auto_materiel", "auto_corporel", "batiment", "transport",
    #         "medical", "judiciaire", "contenant", "marchandise"
    #     ])
    #     dl.addWidget(self.input_type)

    #     dl.addWidget(_section("DOMAINE"))
    #     self.input_domaine = QLineEdit()
    #     self.input_domaine.setPlaceholderText("Ex : Carrosserie, Électricité…")
    #     self.input_domaine.textChanged.connect(self._update_summary)
    #     dl.addWidget(self.input_domaine)

    #     dl.addWidget(_section("OBSERVATIONS"))
    #     self.input_observations = QTextEdit()
    #     self.input_observations.setPlaceholderText("Instructions pour l'expert…")
    #     self.input_observations.setFixedHeight(60)
    #     dl.addWidget(self.input_observations)

    #     cl.addWidget(self.details_block)

    #     cl.addStretch()
    #     cl.addWidget(self._separator())

    #     # ─── FOOTER ───
    #     footer = QHBoxLayout()
    #     footer.addStretch()
    #     self.btn_annuler = QPushButton("Cancel")
    #     self.btn_annuler.setObjectName("BtnCancel")
    #     self.btn_annuler.setCursor(Qt.PointingHandCursor)
    #     self.btn_annuler.clicked.connect(self.reject)
    #     footer.addWidget(self.btn_annuler)

    #     self.btn_creer = QPushButton("Create mission")
    #     self.btn_creer.setObjectName("BtnPrimary")
    #     self.btn_creer.setCursor(Qt.PointingHandCursor)
    #     self.btn_creer.clicked.connect(self.creer_mission)
    #     footer.addWidget(self.btn_creer)
    #     cl.addLayout(footer)

    #     root.addWidget(self.card)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ScrollArea pour permettre au formulaire de grandir
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #f4f4f5;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #d4d4d8;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #a1a1aa; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        container = QWidget()
        container.setStyleSheet("background: #f4f4f5;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(24, 24, 24, 24)
        container_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Carte
        self.card = QFrame()
        self.card.setObjectName("Card")
        self.card.setFixedWidth(640)
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        self.card.setGraphicsEffect(shadow)

        cl = QVBoxLayout(self.card)
        cl.setContentsMargins(32, 28, 32, 24)
        cl.setSpacing(18)

        # ─── HEADER ───
        cl.addLayout(self._build_header())
        cl.addWidget(self._separator())

        # ─── TYPE DE MISSION ───
        cl.addWidget(_section("MISSION TYPE"))
        self.segment_row = QHBoxLayout()
        self.segment_row.setSpacing(0)
        cl.addLayout(self.segment_row)

        # ─── EXPERT ───
        cl.addWidget(_section("EXPERT"))
        self.input_expert = QComboBox()
        self.input_expert.setEditable(True)
        self.input_expert.addItem("— Sélectionner un expert —", None)
        self.input_expert.currentIndexChanged.connect(self._on_expert_changed)
        cl.addWidget(self.input_expert)

        # Petit lien "Créer un expert"
        link_row = QHBoxLayout()
        link_row.setContentsMargins(0, -6, 0, 0)
        self.btn_new_expert = QPushButton("+ Créer un expert")
        self.btn_new_expert.setCursor(Qt.PointingHandCursor)
        self.btn_new_expert.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #1d4ed8;
                border: none;
                font-size: 12px;
                text-align: left;
                padding: 0;
            }
            QPushButton:hover { text-decoration: underline; }
        """)
        self.btn_new_expert.clicked.connect(self._open_new_expert_dialog)
        link_row.addWidget(self.btn_new_expert)
        link_row.addStretch()
        cl.addLayout(link_row)

        # ─── PÉRIODE ───
        cl.addWidget(_section("PERIOD"))
        period_row = QHBoxLayout()
        period_row.setSpacing(12)
        self.input_date_mission = self._date_field("From")
        self.input_echeance = self._date_field("To")
        self.input_date_mission.dateChanged.connect(self._update_summary)
        self.input_echeance.dateChanged.connect(self._update_summary)
        period_row.addWidget(self.input_date_mission, 1)
        period_row.addWidget(self.input_echeance, 1)
        cl.addLayout(period_row)

        # ─── MONTANT ───
        cl.addWidget(_section("MISSION AMOUNT"))
        amount_row = QHBoxLayout()
        amount_row.setSpacing(0)
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        self.input_montant.setGroupSeparatorShown(True)
        self.input_montant.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.input_montant.setStyleSheet("""
            QDoubleSpinBox {
                background: #ffffff;
                border: 1px solid #d4d4d8;
                border-top-right-radius: 0;
                border-bottom-right-radius: 0;
                border-right: none;
                padding: 9px 12px;
                font-size: 13px;
                color: #18181b;
            }
            QDoubleSpinBox:focus { border-color: #2563eb; }
        """)
        self.input_montant.valueChanged.connect(self._update_summary)
        amount_row.addWidget(self.input_montant, 1)

        unit = QLabel("FCFA")
        unit.setStyleSheet("""
            background: #f4f4f5;
            border: 1px solid #d4d4d8;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            padding: 9px 14px;
            font-size: 12px;
            font-weight: 600;
            color: #52525b;
        """)
        amount_row.addWidget(unit)
        cl.addLayout(amount_row)

        # ─── ZONE CONTRE-EXPERTISE (masquée par défaut) ───
        self.parent_block = QFrame()
        self.parent_block.setVisible(False)
        pl = QVBoxLayout(self.parent_block)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(10)

        pl.addWidget(self._separator())
        pl.addWidget(_section("PARENT MISSION (contre-expertise)"))

        self.parent_combo = QComboBox()
        self.parent_combo.currentIndexChanged.connect(self._on_parent_changed)
        pl.addWidget(self.parent_combo)

        pl.addWidget(_section("REASON"))
        self.motif_input = QTextEdit()
        self.motif_input.setPlaceholderText(
            "Expliquez pourquoi cette contre-expertise est nécessaire…"
        )
        self.motif_input.setFixedHeight(60)
        self.motif_input.textChanged.connect(self._update_summary)
        pl.addWidget(self.motif_input)

        cl.addWidget(self.parent_block)

        # ─── DÉTAILS OPTIONNELS ───
        self.details_toggle = QPushButton("＋ Options avancées")
        self.details_toggle.setCursor(Qt.PointingHandCursor)
        self.details_toggle.setCheckable(True)
        self.details_toggle.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                color: #71717a; font-size: 12px;
                text-align: left; padding: 0;
            }
            QPushButton:hover { color: #18181b; }
        """)
        self.details_toggle.toggled.connect(self._toggle_details)
        cl.addWidget(self.details_toggle)

        self.details_block = QWidget()
        self.details_block.setVisible(False)
        dl = QVBoxLayout(self.details_block)
        dl.setContentsMargins(0, 8, 0, 0)
        dl.setSpacing(10)

        dl.addWidget(_section("TYPE D'EXPERTISE"))
        self.input_type = QComboBox()
        self.input_type.addItems([
            "auto_materiel", "auto_corporel", "batiment", "transport",
            "medical", "judiciaire", "contenant", "marchandise"
        ])
        dl.addWidget(self.input_type)

        dl.addWidget(_section("DOMAINE"))
        self.input_domaine = QLineEdit()
        self.input_domaine.setPlaceholderText("Ex : Carrosserie, Électricité…")
        self.input_domaine.textChanged.connect(self._update_summary)
        dl.addWidget(self.input_domaine)

        dl.addWidget(_section("OBSERVATIONS"))
        self.input_observations = QTextEdit()
        self.input_observations.setPlaceholderText("Instructions pour l'expert…")
        self.input_observations.setFixedHeight(60)
        dl.addWidget(self.input_observations)

        cl.addWidget(self.details_block)

        cl.addWidget(self._separator())

        # ─── FOOTER ───
        footer = QHBoxLayout()
        footer.addStretch()
        self.btn_annuler = QPushButton("Cancel")
        self.btn_annuler.setObjectName("BtnCancel")
        self.btn_annuler.setCursor(Qt.PointingHandCursor)
        self.btn_annuler.clicked.connect(self.reject)
        footer.addWidget(self.btn_annuler)

        self.btn_creer = QPushButton("Create mission")
        self.btn_creer.setObjectName("BtnPrimary")
        self.btn_creer.setCursor(Qt.PointingHandCursor)
        self.btn_creer.clicked.connect(self.creer_mission)
        footer.addWidget(self.btn_creer)
        cl.addLayout(footer)

        container_layout.addWidget(self.card)
        scroll.setWidget(container)
        root.addWidget(scroll)

    # ─── Header ───
    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        # Bloc titre
        block = QVBoxLayout()
        block.setSpacing(2)
        num = self.sinistre_info.get('numero_sinistre', 'N/A')
        title = QLabel(f"Expert mission {num}")
        title.setObjectName("Title")
        block.addWidget(title)
        subtitle = QLabel("Création et configuration de la mission")
        subtitle.setObjectName("Subtitle")
        block.addWidget(subtitle)
        row.addLayout(block, 1)

        # Bouton fermer
        btn_close = QPushButton()
        btn_close.setObjectName("BtnClose")
        btn_close.setFixedSize(28, 28)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setIcon(qta.icon('fa5s.times', color='#52525b'))
        btn_close.setIconSize(QSize(12, 12))
        btn_close.clicked.connect(self.reject)
        row.addWidget(btn_close, 0, Qt.AlignTop)

        return row

    def _separator(self) -> QFrame:
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #e4e4e7; border: none;")
        return sep

    def _date_field(self, placeholder_label: str) -> QDateEdit:
        """Crée un QDateEdit stylé (avec popup calendrier)"""
        de = QDateEdit()
        de.setCalendarPopup(True)
        de.setDisplayFormat("dd/MM/yyyy")
        de.setDate(QDate.currentDate())
        return de

    def _toggle_details(self, checked: bool):
        self.details_block.setVisible(checked)
        self.details_toggle.setText(
            "－ Masquer les options" if checked else "＋ Options avancées"
        )
        self.card.adjustSize()  # ✅

    # ═══════════════════════════════════════════════════════════════
    # SÉLECTEUR DE TYPE (segmenté)
    # ═══════════════════════════════════════════════════════════════
    def _load_types_mission(self):
        try:
            types = self.expertise_controller.get_types_mission(actifs_only=True)
            self._types_mission = types

            # Nettoyer
            while self.segment_row.count():
                item = self.segment_row.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self._type_buttons.clear()

            if not types:
                lbl = QLabel("Aucun type de mission actif dans le référentiel")
                lbl.setStyleSheet("color: #dc2626; font-size: 12px;")
                self.segment_row.addWidget(lbl)
                self.btn_creer.setEnabled(False)
                return

            self._button_group = QButtonGroup(self)
            self._button_group.setExclusive(True)

            for i, t in enumerate(types):
                btn = QPushButton(t['libelle'])
                btn.setObjectName("Segment")
                btn.setCheckable(True)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setFixedHeight(38)
                # Premier et dernier coins arrondis
                if i == 0:
                    btn.setStyleSheet(STYLE + """
                        QPushButton#Segment {
                            border-top-right-radius: 0;
                            border-bottom-right-radius: 0;
                        }
                    """)
                elif i == len(types) - 1:
                    btn.setStyleSheet(STYLE + """
                        QPushButton#Segment {
                            border-top-left-radius: 0;
                            border-bottom-left-radius: 0;
                        }
                    """)
                else:
                    btn.setStyleSheet(STYLE + """
                        QPushButton#Segment {
                            border-radius: 0;
                        }
                    """)

                self._button_group.addButton(btn, i)
                self._type_buttons[t['code']] = btn
                self.segment_row.addWidget(btn, 1)

            # Connexion
            self._button_group.buttonClicked.connect(self._on_type_changed)

            # Sélection par défaut
            target = self.force_type_code or 'EXPERTISE'
            if target not in self._type_buttons and types:
                target = types[0]['code']

            if target in self._type_buttons:
                self._type_buttons[target].setChecked(True)
                self._on_type_changed(self._type_buttons[target])

            # Pré-sélection parente
            if self.force_mission_parente_id:
                self.parent_block.setVisible(True)
                self._load_missions_parentes()
                for i in range(self.parent_combo.count()):
                    d = self.parent_combo.itemData(i)
                    if d and d['id'] == self.force_mission_parente_id:
                        self.parent_combo.setCurrentIndex(i)
                        break

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Chargement types : {e}")

    def _get_selected_type(self) -> dict:
        for code, btn in self._type_buttons.items():
            if btn.isChecked():
                for t in self._types_mission:
                    if t['code'] == code:
                        return t
        return None

    def _on_type_changed(self, button):
        t = self._get_selected_type()
        if not t:
            return
        needs_parent = t.get('necessite_mission_parente', False)
        self.parent_block.setVisible(needs_parent)
        if needs_parent:
            self._load_missions_parentes()
        self.setWindowTitle(f"Créer une mission — {t['libelle']}")
        self._update_summary()

        # ✅ Force le recalcul de la taille
        self.card.adjustSize()

    # ═══════════════════════════════════════════════════════════════
    # MISSIONS PARENTES
    # ═══════════════════════════════════════════════════════════════
    def _load_missions_parentes(self):
        self.parent_combo.clear()
        self.parent_combo.addItem("— Sélectionner une mission garagiste —", None)
        t = self._get_selected_type()
        if not t:
            return
        missions = self.expertise_controller.get_missions_parentes_possibles(self.sinistre_id)
        expected = t.get('type_mission_parente_code')
        if expected:
            missions = [m for m in missions if m.get('type_mission_code') == expected]
        if not missions:
            self.parent_combo.addItem("Aucune mission éligible", None)
            self.parent_combo.setEnabled(False)
            return
        self.parent_combo.setEnabled(True)
        for m in missions:
            montant = float(m.get('montant_estime') or 0)
            label = (
                f"{m['numero_mission']} — {m.get('expert_nom') or 'N/A'} — "
                f"{montant:,.0f} FCFA".replace(',', ' ')
            )
            self.parent_combo.addItem(label, m)

    def _on_parent_changed(self, index):
        parente = self.parent_combo.currentData()
        if not parente:
            self._update_summary()
            return
        montant = float(parente.get('montant_estime') or 0)
        if montant > 0:
            self.input_montant.setValue(montant)
        self._update_summary()

    # ═══════════════════════════════════════════════════════════════
    # EXPERTS
    # ═══════════════════════════════════════════════════════════════
    def _load_experts(self):
        try:
            self.input_expert.clear()
            self.input_expert.addItem("— Sélectionner un expert —", None)
            experts = self.expert_controller.get_experts_actifs() or []
            for expert in experts:
                nom = (expert.get('nom') or '') + ' ' + (expert.get('prenom') or '')
                domaines = expert.get('domaines') or []
                suffix = f" · {', '.join(domaines)}" if domaines else ''
                fallback = f"Expert #{expert.get('id')}"
                label = f"{nom.strip() or fallback}{suffix}"
                self.input_expert.addItem(label, expert)
        except Exception as e:
            print(f"[MissionDialog] load_experts: {e}")

    def _on_expert_changed(self, index):
        self._update_summary()

    def _open_new_expert_dialog(self):
        try:
            from addons.sinistres.views.dialogs_files.expert_dialog import ExpertDialog
        except ImportError:
            QMessageBox.warning(self, "Indisponible", "expert_dialog.py introuvable")
            return
        d = ExpertDialog(expert_controller=self.expert_controller, user=self.user, parent=self)
        if d.exec() == QDialog.Accepted:
            self._load_experts()

    def _update_summary(self):
        """Le récapitulatif n'est plus affiché, mais on garde la validation live"""
        pass

    # ═══════════════════════════════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════════════════════════════
    def creer_mission(self):
        try:
            t = self._get_selected_type()
            if not t:
                QMessageBox.warning(self, "Validation", "Sélectionnez un type de mission")
                return
            expert = self.input_expert.currentData()
            if not expert:
                QMessageBox.warning(self, "Validation", "Sélectionnez un expert")
                return
            date_mission = self.input_date_mission.date().toPython()
            echeance = self.input_echeance.date().toPython()
            if date_mission > echeance:
                QMessageBox.warning(self, "Validation", "La date de mission doit précéder l'échéance")
                return
            data = {
                'sinistre_id': self.sinistre_id,
                'type_mission_code': t['code'],
                'type_expertise': self.input_type.currentText(),
                'domaine': self.input_domaine.text().strip() or None,
                'expert_id': expert.get('id'),
                'date_mission': date_mission,
                'date_echeance': echeance,
                'montant_estime': self.input_montant.value() or None,
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self._get_user_id(),
            }
            if t.get('necessite_mission_parente'):
                parente = self.parent_combo.currentData()
                if not parente:
                    QMessageBox.warning(self, "Validation", "Sélectionnez une mission parente")
                    return
                motif = self.motif_input.toPlainText().strip()
                if not motif:
                    QMessageBox.warning(self, "Validation", "Le motif de la contre-expertise est obligatoire")
                    return
                data['mission_parente_id'] = parente['id']
                data['motif_contre_expertise'] = motif
                data['montant_devis_garagiste'] = parente.get('montant_estime')

            result = self.expertise_controller.creer_mission(data)
            if result:
                self.mission_created.emit(result)
                QMessageBox.information(
                    self, "Succès",
                    f"Mission {result.get('numero_mission')} créée"
                )
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))