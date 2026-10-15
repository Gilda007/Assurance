


"""
Dialogue de création de règlement — Design moderne 2 colonnes
Toutes les icônes utilisent qtawesome (FontAwesome)
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox,
    QPushButton, QMessageBox, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QPixmap

import qtawesome as qta
from datetime import datetime
from typing import Dict, List, Optional


# ================================================================
# HELPERS — ICÔNES
# ================================================================

def make_icon_label(icon_name: str, color: str = "#64748b", size: int = 16) -> QLabel:
    """Crée un QLabel contenant une icône FontAwesome."""
    lbl = QLabel()
    try:
        icon = qta.icon(icon_name, color=color)
        lbl.setPixmap(icon.pixmap(QSize(size, size)))
    except Exception as e:
        print(f"⚠️ Icône '{icon_name}' introuvable : {e}")
        lbl.setText("●")
        lbl.setStyleSheet(f"color: {color}; font-size: {size}px;")
    
    lbl.setFixedSize(size + 4, size + 4)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet("background: transparent; border: none;")
    return lbl


# ================================================================
# WIDGETS PERSONNALISÉS
# ================================================================

class AvatarWidget(QLabel):
    """Avatar circulaire avec initiales"""
    
    def __init__(self, initiales: str = "?", size: int = 56, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.set_initiales(initiales)
    
    def set_initiales(self, initiales: str):
        self.initiales = initiales or "?"
        self.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6366f1, stop:1 #8b5cf6
                );
                color: white;
                border-radius: {self.width() // 2}px;
                font-size: {self.width() // 3}px;
                font-weight: 700;
                border: 2px solid white;
            }}
        """)
        self.setText(self.initiales)


class BeneficiaryCard(QFrame):
    """Carte d'information du bénéficiaire sélectionné"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 12))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        self.setup_ui()
        self._show_empty_state()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # En-tête avec icône
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        
        header_icon = make_icon_label('fa5s.user-tag', color='#0f172a', size=14)
        header_row.addWidget(header_icon)
        
        header = QLabel("Bénéficiaire")
        header.setStyleSheet("""
            color: #0f172a;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
        """)
        header_row.addWidget(header)
        header_row.addStretch()
        
        layout.addLayout(header_row)
        
        # Séparateur
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #e2e8f0;")
        layout.addWidget(sep)
        
        # Zone contenu
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        layout.addLayout(self.content_layout)
        
        layout.addStretch()
    
    def _clear_content(self):
        """Vide le contenu."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
    
    def _show_empty_state(self):
        """Affiche l'état vide."""
        self._clear_content()
        
        empty = QLabel("Aucun bénéficiaire sélectionné")
        empty.setAlignment(Qt.AlignCenter)
        empty.setStyleSheet("""
            color: #94a3b8;
            font-size: 12px;
            font-style: italic;
            padding: 20px;
            background: transparent;
        """)
        self.content_layout.addWidget(empty)
    
    def set_beneficiaire(self, benef: dict):
        """Affiche les infos du bénéficiaire."""
        self._clear_content()
        
        if not benef:
            self._show_empty_state()
            return
        
        # ─── Avatar + Nom ───
        top = QHBoxLayout()
        top.setSpacing(12)
        
        nom = benef.get('nom', '')
        prenom = benef.get('prenom', '')
        initiales = (nom[:1] + prenom[:1]).upper() or "?"
        
        avatar = AvatarWidget(initiales, 48)
        top.addWidget(avatar)
        
        name_block = QVBoxLayout()
        name_block.setSpacing(2)
        
        nom_complet = benef.get('nom_complet', 'N/A')
        name_lbl = QLabel(nom_complet)
        name_lbl.setStyleSheet("""
            color: #0f172a;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
        """)
        name_block.addWidget(name_lbl)
        
        type_ben = benef.get('type_beneficiaire', 'N/A')
        type_lbl = QLabel(type_ben)
        type_lbl.setStyleSheet("""
            color: #64748b;
            font-size: 11px;
            background: transparent;
        """)
        name_block.addWidget(type_lbl)
        
        top.addLayout(name_block)
        top.addStretch()
        
        self.content_layout.addLayout(top)
        
        # ─── Coordonnées ───
        coord_block = QVBoxLayout()
        coord_block.setSpacing(6)
        
        def add_info(icon_name, label, value, color="#1e293b"):
            if not value:
                return
            row = QHBoxLayout()
            row.setSpacing(8)
            
            ico = make_icon_label(icon_name, color='#64748b', size=14)
            row.addWidget(ico)
            
            lbl = QLabel(label)
            lbl.setStyleSheet("""
                color: #94a3b8;
                font-size: 10px;
                background: transparent;
            """)
            lbl.setFixedWidth(50)
            row.addWidget(lbl)
            
            val = QLabel(str(value))
            val.setStyleSheet(f"""
                color: {color};
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            """)
            val.setWordWrap(True)
            row.addWidget(val, 1)
            
            coord_block.addLayout(row)
        
        # Téléphone
        tel = benef.get('telephone') or benef.get('portable')
        add_info('fa5s.phone', 'Tél.', tel)
        
        # Email
        add_info('fa5s.envelope', 'Email', benef.get('email'))
        
        # Code / Agrément
        code = benef.get('code') or benef.get('agrement')
        if code:
            add_info('fa5s.id-card', 'Code', code)
        
        # Ville
        add_info('fa5s.map-marker-alt', 'Ville', benef.get('ville'))
        
        self.content_layout.addLayout(coord_block)
        
        # ─── Statut ───
        statut_row = QHBoxLayout()
        statut_row.setSpacing(8)
        
        is_actif = benef.get('est_actif', True)
        dot_color = '#10b981' if is_actif else '#ef4444'
        dot_icon = 'fa5s.circle' if is_actif else 'fa5s.circle'
        
        dot = make_icon_label(dot_icon, color=dot_color, size=10)
        statut_row.addWidget(dot)
        
        statut_lbl = QLabel("Actif" if is_actif else "Inactif")
        statut_lbl.setStyleSheet(f"""
            color: {dot_color};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        """)
        statut_row.addWidget(statut_lbl)
        statut_row.addStretch()
        
        self.content_layout.addLayout(statut_row)


class SummaryCard(QFrame):
    """Carte de récapitulatif du règlement"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 12))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # En-tête avec icône
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        
        header_icon = make_icon_label('fa5s.clipboard-list', color='#0f172a', size=14)
        header_row.addWidget(header_icon)
        
        header = QLabel("Récapitulatif")
        header.setStyleSheet("""
            color: #0f172a;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
        """)
        header_row.addWidget(header)
        header_row.addStretch()
        
        layout.addLayout(header_row)
        
        # Séparateur
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #e2e8f0;")
        layout.addWidget(sep)
        
        # Contenu
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        layout.addLayout(self.content_layout)
        
        # Statut
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet("""
            QFrame {
                background: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 8px;
            }
        """)
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(12, 8, 12, 8)
        status_layout.setSpacing(8)
        
        self.status_dot = make_icon_label('fa5s.circle', color='#10b981', size=10)
        status_layout.addWidget(self.status_dot)
        
        self.status_label = QLabel("En attente des informations")
        self.status_label.setStyleSheet("""
            color: #059669;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        layout.addWidget(self.status_frame)
    
    def update_content(self, data: dict):
        """Met à jour le récapitulatif."""
        # Vider
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
        
        # Ajouter les lignes
        lignes = [
            ('fa5s.check', 'Bénéficiaire', data.get('beneficiaire_nom', '—')),
            ('fa5s.check', 'Montant', f"{data.get('montant', 0):,.0f} FCFA"),
            ('fa5s.check', 'Type', data.get('type_paiement', '—')),
        ]
        
        for icon_name, label, value in lignes:
            row = QHBoxLayout()
            row.setSpacing(8)
            
            check = make_icon_label(icon_name, color='#10b981', size=12)
            row.addWidget(check)
            
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("""
                color: #64748b;
                font-size: 12px;
                background: transparent;
            """)
            row.addWidget(lbl)
            
            val = QLabel(str(value))
            val.setStyleSheet("""
                color: #0f172a;
                font-size: 12px;
                font-weight: 600;
                background: transparent;
            """)
            val.setWordWrap(True)
            row.addWidget(val, 1)
            
            self.content_layout.addLayout(row)
    
    def set_status(self, message: str, status_type: str = "info"):
        """Définit le statut."""
        colors = {
            'ready':   ("#10b981", "#f0fdf4", "#bbf7d0", "#059669"),
            'warning': ("#f59e0b", "#fffbeb", "#fde68a", "#92400e"),
            'error':   ("#ef4444", "#fef2f2", "#fecaca", "#991b1b"),
            'info':    ("#3b82f6", "#eff6ff", "#bfdbfe", "#1e40af"),
        }
        dot_color, bg, border, text = colors.get(status_type, colors['info'])
        
        self.status_frame.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
        """)
        
        # Mettre à jour l'icône du point
        icon = qta.icon('fa5s.circle', color=dot_color)
        self.status_dot.setPixmap(icon.pixmap(QSize(10, 10)))
        
        self.status_label.setStyleSheet(f"""
            color: {text};
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)
        self.status_label.setText(message)


# ================================================================
# DIALOGUE PRINCIPAL
# ================================================================

class ReglementDialog(QDialog):
    """Dialogue de création de règlement — Design 2 colonnes"""
    
    reglement_created = Signal(dict)
    
    def __init__(self, sinistre_id, reglement_controller, user, 
                 sinistre_info=None, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.reglement_controller = reglement_controller
        self.user = user
        
        # Permissions
        from addons.sinistres.services.permission_service import PermissionService
        from addons.sinistres.security.permissions_helper import PermissionsUI
        self.permission_service = PermissionService()
        self.permissions_ui = PermissionsUI(user, self.permission_service)
        
        self.sinistre_info = sinistre_info or {}
        self.evaluations = []
        self._tous_beneficiaires = []
        
        self.setWindowTitle("Créer un règlement")
        self.setModal(True)
        self.setMinimumSize(1100, 720)
        self.setStyleSheet("""
            QDialog {
                background: #f1f5f9;
            }
        """)
        
        self.setup_ui()
        self._appliquer_permissions()
        self.load_data()
    
    def _appliquer_permissions(self):
        """Cache les boutons selon les permissions."""
        self.permissions_ui.masquer_si_non_autorise(
            self.btn_creer, 'reglement', 'CREATE'
        )
    
    # ================================================================
    # LAYOUT PRINCIPAL
    # ================================================================
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # En-tête
        main_layout.addWidget(self._build_header())
        
        # Corps : 2 colonnes
        body = QHBoxLayout()
        body.setSpacing(16)
        
        # Colonne gauche
        left_col = QVBoxLayout()
        left_col.setSpacing(12)
        left_col.addWidget(self._build_form_card())
        left_col.addStretch()
        
        # Colonne droite
        right_col = QVBoxLayout()
        right_col.setSpacing(12)
        
        self.beneficiary_card = BeneficiaryCard()
        right_col.addWidget(self.beneficiary_card)
        
        self.summary_card = SummaryCard()
        right_col.addWidget(self.summary_card)
        right_col.addStretch()
        
        left_widget = QFrame()
        left_widget.setStyleSheet("background: transparent;")
        left_widget.setLayout(left_col)
        
        right_widget = QFrame()
        right_widget.setStyleSheet("background: transparent;")
        right_widget.setFixedWidth(320)
        right_widget.setLayout(right_col)
        
        body.addWidget(left_widget, 1)
        body.addWidget(right_widget)
        
        main_layout.addLayout(body, 1)
        
        # Pied
        main_layout.addWidget(self._build_footer())
        
        # Connexions
        self.input_beneficiaire.currentIndexChanged.connect(self._update_summary)
        self.input_evaluation.currentIndexChanged.connect(self._update_summary)
        self.input_montant.valueChanged.connect(self._update_summary)
        self.input_type_paiement.currentIndexChanged.connect(self._update_summary)
    
    # ================================================================
    # EN-TÊTE
    # ================================================================
    
    def _build_header(self) -> QFrame:
        """En-tête avec titre + badges."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        header.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # Titre
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        
        title_icon = make_icon_label('fa5s.credit-card', color='#1a73e8', size=22)
        title_row.addWidget(title_icon)
        
        title = QLabel("Créer un règlement")
        title.setStyleSheet("""
            color: #0f172a;
            font-size: 20px;
            font-weight: 800;
            background: transparent;
        """)
        title_row.addWidget(title)
        title_row.addStretch()
        
        layout.addLayout(title_row)
        
        # Badges
        badges = QHBoxLayout()
        badges.setSpacing(10)
        
        # Badge sinistre
        num_sinistre = self.sinistre_info.get('numero_sinistre', 'N/A')
        badges.addWidget(self._make_badge(
            'fa5s.file-alt',
            f"Sinistre: {num_sinistre}",
            "#dbeafe", "#1e40af"
        ))
        
        # Badge client
        client_nom = self.sinistre_info.get('client_nom', 'N/A')
        badges.addWidget(self._make_badge(
            'fa5s.user',
            f"Client: {client_nom}",
            "#f1f5f9", "#475569"
        ))
        
        # Badge montant
        self.lbl_montant_dispo = self._make_badge(
            'fa5s.coins',
            "Montant disponible: 0 FCFA",
            "#d1fae5", "#065f46"
        )
        badges.addWidget(self.lbl_montant_dispo)
        
        badges.addStretch()
        layout.addLayout(badges)
        
        return header
    
    def _make_badge(self, icon_name: str, text: str, bg: str, fg: str) -> QLabel:
        """Crée un badge avec icône FontAwesome."""
        # Créer un widget avec icône + texte
        badge = QLabel()
        badge.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 16px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
                border: none;
            }}
        """)
        
        # Utiliser du HTML avec l'icône en image
        try:
            icon = qta.icon(icon_name, color=fg)
            pixmap = icon.pixmap(QSize(12, 12))
            # Sauvegarder temporairement en base64 pour l'utiliser dans HTML
            from PySide6.QtCore import QBuffer, QByteArray
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            pixmap.save(buffer, "PNG")
            img_bytes = bytes(buffer.data().toBase64())
            img_data = img_bytes.decode('ascii')
            badge.setText(
                f'<img src="data:image/png;base64,{img_data}" '
                f'width="12" height="12" style="vertical-align:middle;"> {text}'
            )
        except Exception:
            badge.setText(text)
        
        badge.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        return badge
    
    # ================================================================
    # FORMULAIRE
    # ================================================================
    
    def _build_form_card(self) -> QFrame:
        """Carte principale du formulaire."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)
        
        # Titre avec icône
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        title_icon = make_icon_label('fa5s.info-circle', color='#1a73e8', size=14)
        title_row.addWidget(title_icon)
        
        title = QLabel("Informations du règlement")
        title.setStyleSheet("""
            color: #0f172a;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
        """)
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)
        
        # Séparateur
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #e2e8f0;")
        layout.addWidget(sep)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Bénéficiaire
        self.input_beneficiaire = QComboBox()
        self.input_beneficiaire.setEditable(True)
        self.input_beneficiaire.setInsertPolicy(QComboBox.NoInsert)
        self.input_beneficiaire.setMinimumHeight(36)
        self.input_beneficiaire.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                color: #0f172a;
            }
            QComboBox:hover { border-color: #3b82f6; }
            QComboBox:focus { border-color: #1a73e8; }
            QComboBox::drop-down { border: none; width: 24px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
                margin-right: 8px;
            }
        """)
        self.input_beneficiaire.addItem("-- Sélectionner un bénéficiaire --", None)
        form.addRow("Bénéficiaire *:", self.input_beneficiaire)
        
        # Filtre
        self.input_type_beneficiaire = QComboBox()
        self.input_type_beneficiaire.setMinimumHeight(36)
        self.input_type_beneficiaire.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                color: #0f172a;
            }
            QComboBox:hover { border-color: #3b82f6; }
            QComboBox::drop-down { border: none; width: 24px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
                margin-right: 8px;
            }
        """)
        self.input_type_beneficiaire.addItem("Tous", None)
        self.input_type_beneficiaire.addItem(
            qta.icon('fa5s.users', color='#475569'), "Tiers", "TIERS"
        )
        self.input_type_beneficiaire.addItem(
            qta.icon('fa5s.user-tie', color='#7c3aed'), "Experts", "EXPERT"
        )
        self.input_type_beneficiaire.addItem(
            qta.icon('fa5s.user', color='#2563eb'), "Assurés", "ASSURE"
        )
        self.input_type_beneficiaire.addItem(
            qta.icon('fa5s.car', color='#0891b2'), "Conducteurs", "CONDUCTEUR"
        )
        self.input_type_beneficiaire.addItem(
            qta.icon('fa5s.user-injured', color='#dc2626'), "Victimes", "VICTIME"
        )
        self.input_type_beneficiaire.addItem(
            qta.icon('fa5s.wrench', color='#f59e0b'), "Garages", "GARAGE"
        )
        self.input_type_beneficiaire.addItem(
            qta.icon('fa5s.gavel', color='#16a34a'), "Avocats", "AVOCAT"
        )
        self.input_type_beneficiaire.addItem(
            qta.icon('fa5s.hospital', color='#dc2626'), "Hôpitaux", "HOPITAL"
        )
        self.input_type_beneficiaire.currentIndexChanged.connect(self._filtrer_beneficiaires)
        form.addRow("Filtrer par:", self.input_type_beneficiaire)
        
        # Évaluation
        self.input_evaluation = QComboBox()
        self.input_evaluation.setMinimumHeight(36)
        self.input_evaluation.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                color: #0f172a;
            }
            QComboBox:hover { border-color: #3b82f6; }
            QComboBox::drop-down { border: none; width: 24px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
                margin-right: 8px;
            }
        """)
        self.input_evaluation.addItem("-- Sélectionner une évaluation --", None)
        self.input_evaluation.currentIndexChanged.connect(self._on_evaluation_changed)
        form.addRow("Évaluation associée:", self.input_evaluation)
        
        # Montant
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        self.input_montant.setMinimumHeight(36)
        self.input_montant.setStyleSheet("""
            QDoubleSpinBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                color: #0f172a;
            }
            QDoubleSpinBox:focus { border-color: #1a73e8; }
        """)
        form.addRow("Montant *:", self.input_montant)
        
        # Type paiement
        self.input_type_paiement = QComboBox()
        self.input_type_paiement.setMinimumHeight(36)
        self.input_type_paiement.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                color: #0f172a;
            }
            QComboBox:hover { border-color: #3b82f6; }
            QComboBox::drop-down { border: none; width: 24px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
                margin-right: 8px;
            }
        """)
        self.input_type_paiement.addItem(
            qta.icon('fa5s.money-check', color='#16a34a'), "CHÈQUE", "CHEQUE"
        )
        self.input_type_paiement.addItem(
            qta.icon('fa5s.university', color='#2563eb'), "VIREMENT", "VIREMENT"
        )
        self.input_type_paiement.addItem(
            qta.icon('fa5s.mobile-alt', color='#f59e0b'), "MOBILE MONEY", "MOBILE_MONEY"
        )
        self.input_type_paiement.currentIndexChanged.connect(self._on_type_paiement_changed)
        form.addRow("Type paiement:", self.input_type_paiement)
        
        layout.addLayout(form)
        
        # Détails paiement
        self.paiement_details_group = QGroupBox("Détails du paiement")
        self.paiement_details_group.setStyleSheet("""
            QGroupBox {
                font-weight: 700;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                background: white;
            }
        """)
        self.paiement_details_group.hide()
        
        details_layout = QFormLayout(self.paiement_details_group)
        details_layout.setSpacing(10)
        
        # Chèque
        self.input_cheque_numero = QLineEdit()
        self.input_cheque_numero.setPlaceholderText("Numéro du chèque")
        self.input_cheque_numero.setMinimumHeight(34)
        self.input_cheque_numero.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #1a73e8; }
        """)
        details_layout.addRow("Numéro chèque:", self.input_cheque_numero)
        
        self.input_cheque_banque = QLineEdit()
        self.input_cheque_banque.setPlaceholderText("Banque émettrice")
        self.input_cheque_banque.setMinimumHeight(34)
        self.input_cheque_banque.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #1a73e8; }
        """)
        details_layout.addRow("Banque émettrice:", self.input_cheque_banque)
        
        # Virement
        self.input_virement_ref = QLineEdit()
        self.input_virement_ref.setPlaceholderText("Référence du virement")
        self.input_virement_ref.setMinimumHeight(34)
        self.input_virement_ref.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #1a73e8; }
        """)
        details_layout.addRow("Référence virement:", self.input_virement_ref)
        
        # Mobile Money
        self.input_mobile_numero = QLineEdit()
        self.input_mobile_numero.setPlaceholderText("Numéro Mobile Money")
        self.input_mobile_numero.setMinimumHeight(34)
        self.input_mobile_numero.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #1a73e8; }
        """)
        details_layout.addRow("Numéro mobile:", self.input_mobile_numero)
        
        self.input_mobile_operateur = QComboBox()
        self.input_mobile_operateur.setMinimumHeight(34)
        self.input_mobile_operateur.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }
        """)
        self.input_mobile_operateur.addItems(["ORANGE", "MTN", "NEXTTEL", "CAMTEL"])
        details_layout.addRow("Opérateur:", self.input_mobile_operateur)
        
        layout.addWidget(self.paiement_details_group)
        
        # Observations
        obs_row = QHBoxLayout()
        obs_row.setSpacing(8)
        
        obs_icon = make_icon_label('fa5s.comment-alt', color='#0f172a', size=14)
        obs_row.addWidget(obs_icon)
        
        obs_lbl = QLabel("Observations:")
        obs_lbl.setStyleSheet("""
            color: #0f172a;
            font-size: 13px;
            font-weight: 600;
            background: transparent;
        """)
        obs_row.addWidget(obs_lbl)
        obs_row.addStretch()
        
        layout.addLayout(obs_row)
        
        self.input_observations = QTextEdit()
        self.input_observations.setPlaceholderText("Saisissez vos observations...")
        self.input_observations.setMaximumHeight(80)
        self.input_observations.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                background: white;
                color: #0f172a;
            }
            QTextEdit:focus { border-color: #1a73e8; }
        """)
        layout.addWidget(self.input_observations)
        
        return card
    
    # ================================================================
    # PIED
    # ================================================================
    
    def _build_footer(self) -> QFrame:
        """Pied avec boutons."""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(12)
        
        layout.addStretch()
        
        # Annuler
        self.btn_annuler = QPushButton("  Annuler")
        self.btn_annuler.setCursor(Qt.PointingHandCursor)
        self.btn_annuler.setMinimumHeight(40)
        self.btn_annuler.setIcon(qta.icon('fa5s.times', color='#475569'))
        self.btn_annuler.setIconSize(QSize(12, 12))
        self.btn_annuler.setStyleSheet("""
            QPushButton {
                background: white;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background: #f8fafc;
                border-color: #cbd5e1;
            }
        """)
        self.btn_annuler.clicked.connect(self.reject)
        layout.addWidget(self.btn_annuler)
        
        # Créer
        self.btn_creer = QPushButton("  Créer le règlement")
        self.btn_creer.setCursor(Qt.PointingHandCursor)
        self.btn_creer.setMinimumHeight(40)
        self.btn_creer.setIcon(qta.icon('fa5s.check', color='white'))
        self.btn_creer.setIconSize(QSize(14, 14))
        self.btn_creer.setStyleSheet("""
            QPushButton {
                background: #1a73e8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 28px;
                font-size: 13px;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover { background: #1557b0; }
            QPushButton:pressed { background: #0d47a1; }
            QPushButton:disabled {
                background: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self.btn_creer.clicked.connect(self.creer_reglement)
        layout.addWidget(self.btn_creer)
        
        return footer
    
    # ================================================================
    # CHARGEMENT
    # ================================================================
    
    def load_data(self):
        """Charge les données initiales."""
        try:
            self._charger_beneficiaires()
            self._charger_evaluations()
        except Exception as e:
            print(f"❌ Erreur chargement données: {e}")
            import traceback
            traceback.print_exc()
    
    def _charger_beneficiaires(self):
        """Charge la liste des tiers + experts."""
        try:
            self._tous_beneficiaires = self.reglement_controller.get_beneficiaires()
            
            print(f"📋 {len(self._tous_beneficiaires)} bénéficiaire(s) chargé(s)")
            
            self.input_beneficiaire.blockSignals(True)
            self.input_beneficiaire.clear()
            self.input_beneficiaire.addItem(
                "-- Sélectionner un bénéficiaire --", None
            )
            
            for b in self._tous_beneficiaires:
                display = self._format_beneficiaire_display(b)
                # Ajouter avec une icône FontAwesome
                icon = self._get_beneficiaire_icon(b)
                self.input_beneficiaire.addItem(icon, display, b)
            
            self.input_beneficiaire.blockSignals(False)
        
        except Exception as e:
            print(f"❌ Erreur chargement bénéficiaires: {e}")
    
    def _get_beneficiaire_icon(self, b: dict):
        """Retourne une icône FontAwesome pour un bénéficiaire."""
        type_ben = b.get('type_beneficiaire', 'AUTRE')
        
        icon_map = {
            'EXPERT':     ('fa5s.user-tie', '#7c3aed'),
            'ASSURE':     ('fa5s.user', '#2563eb'),
            'GARAGE':     ('fa5s.wrench', '#f59e0b'),
            'AVOCAT':     ('fa5s.gavel', '#16a34a'),
            'HOPITAL':    ('fa5s.hospital', '#dc2626'),
            'HUISSIER':   ('fa5s.file-signature', '#0891b2'),
            'CONDUCTEUR': ('fa5s.car', '#0891b2'),
            'VICTIME':    ('fa5s.user-injured', '#dc2626'),
            'TEMOIN':     ('fa5s.eye', '#64748b'),
        }
        
        icon_name, color = icon_map.get(type_ben, ('fa5s.user-circle', '#64748b'))
        try:
            return qta.icon(icon_name, color=color)
        except Exception:
            return qta.icon('fa5s.user-circle', color='#64748b')
    
    def _format_beneficiaire_display(self, b: dict) -> str:
        """Formate l'affichage d'un bénéficiaire (sans emoji)."""
        nom_complet = b.get('nom_complet') or 'Sans nom'
        type_ben = b.get('type_beneficiaire') or 'AUTRE'
        
        infos = []
        if b.get('telephone'):
            infos.append(b['telephone'])
        elif b.get('portable'):
            infos.append(b['portable'])
        
        if b.get('agrement'):
            infos.append(b['agrement'])
        
        info_str = f"  ·  {'  ·  '.join(infos)}" if infos else ""
        
        return f"{nom_complet}  ({type_ben}){info_str}"
    
    def _filtrer_beneficiaires(self):
        """Filtre les bénéficiaires."""
        type_filtre = self.input_type_beneficiaire.currentData()
        current = self.input_beneficiaire.currentData()
        
        self.input_beneficiaire.blockSignals(True)
        self.input_beneficiaire.clear()
        self.input_beneficiaire.addItem("-- Sélectionner un bénéficiaire --", None)
        
        for b in self._tous_beneficiaires:
            type_b = b.get('type_beneficiaire') or 'AUTRE'
            
            if type_filtre == 'EXPERT':
                if b.get('source') != 'EXPERT':
                    continue
            elif type_filtre == 'TIERS':
                if b.get('source') != 'TIERS':
                    continue
            elif type_filtre:
                if type_b != type_filtre:
                    continue
            
            display = self._format_beneficiaire_display(b)
            icon = self._get_beneficiaire_icon(b)
            self.input_beneficiaire.addItem(icon, display, b)
        
        self.input_beneficiaire.blockSignals(False)
        
        if current:
            for i in range(self.input_beneficiaire.count()):
                if self.input_beneficiaire.itemData(i) == current:
                    self.input_beneficiaire.setCurrentIndex(i)
                    break
        
        self._update_summary()
    
    def _charger_evaluations(self):
        """Charge les évaluations validées."""
        try:
            self.evaluations = self.reglement_controller.get_evaluations_by_sinistre(
                self.sinistre_id
            )
            self.input_evaluation.clear()
            self.input_evaluation.addItem(
                qta.icon('fa5s.clipboard-list', color='#64748b'),
                "-- Sélectionner une évaluation --", None
            )
            
            total_disponible = 0
            for ev in self.evaluations:
                if ev.get('est_validee'):
                    display = f"{ev.get('numero_evaluation')} - {ev.get('montant_net', 0):,.0f} FCFA"
                    self.input_evaluation.addItem(
                        qta.icon('fa5s.check-circle', color='#16a34a'),
                        display, ev
                    )
                    total_disponible += ev.get('montant_net', 0)
            
            self.lbl_montant_dispo.setText(
                f"Montant disponible: {total_disponible:,.0f} FCFA"
            )
        
        except Exception as e:
            print(f"❌ Erreur chargement évaluations: {e}")
    
    # ================================================================
    # ÉVÉNEMENTS
    # ================================================================
    
    def _on_evaluation_changed(self):
        """Met à jour le montant max."""
        evaluation = self.input_evaluation.currentData()
        if evaluation:
            self.input_montant.setMaximum(evaluation.get('montant_net', 0))
            self.input_montant.setValue(evaluation.get('montant_net', 0))
        else:
            self.input_montant.setMaximum(999999999)
        
        self._update_summary()
    
    def _on_type_paiement_changed(self):
        """Affiche les détails selon le type."""
        type_paiement = self.input_type_paiement.currentData() or self.input_type_paiement.currentText()
        
        for widget in [
            self.input_cheque_numero, self.input_cheque_banque,
            self.input_virement_ref,
            self.input_mobile_numero, self.input_mobile_operateur,
        ]:
            widget.hide()
        
        if type_paiement == "CHEQUE":
            self.input_cheque_numero.show()
            self.input_cheque_banque.show()
            self.paiement_details_group.show()
        elif type_paiement == "VIREMENT":
            self.input_virement_ref.show()
            self.paiement_details_group.show()
        elif type_paiement == "MOBILE_MONEY":
            self.input_mobile_numero.show()
            self.input_mobile_operateur.show()
            self.paiement_details_group.show()
        else:
            self.paiement_details_group.hide()
        
        self._update_summary()
    
    def _update_summary(self):
        """Met à jour les cartes."""
        benef = self.input_beneficiaire.currentData()
        self.beneficiary_card.set_beneficiaire(benef)
        
        type_paiement = (
            self.input_type_paiement.currentData() 
            or self.input_type_paiement.currentText()
        )
        
        data = {
            'beneficiaire_nom': benef.get('nom_complet', '—') if benef else '—',
            'montant': self.input_montant.value(),
            'type_paiement': type_paiement,
        }
        self.summary_card.update_content(data)
        
        if benef and data['montant'] > 0:
            self.summary_card.set_status("Prêt à créer", "ready")
        elif benef:
            self.summary_card.set_status("Saisissez un montant", "warning")
        else:
            self.summary_card.set_status("Sélectionnez un bénéficiaire", "info")
    
    # ================================================================
    # CRÉATION
    # ================================================================
    
    # def creer_reglement(self):
    #     """Crée le règlement."""
    #     try:
    #         # 1. Sinistre
    #         if not self.sinistre_id:
    #             QMessageBox.warning(self, "Validation", "Aucun sinistre associé.")
    #             return
            
    #         # 2. Bénéficiaire
    #         beneficiaire_data = self.input_beneficiaire.currentData()
    #         if not beneficiaire_data:
    #             QMessageBox.warning(self, "Validation", "Sélectionnez un bénéficiaire.")
    #             self.input_beneficiaire.setFocus()
    #             return
            
    #         # 3. Montant
    #         montant = float(self.input_montant.value())
    #         if montant <= 0:
    #             QMessageBox.warning(self, "Validation", "Le montant doit être positif.")
    #             self.input_montant.setFocus()
    #             return
            
    #         # 4. Évaluation
    #         evaluation_data = self.input_evaluation.currentData()
    #         evaluation_id = None
            
    #         if evaluation_data:
    #             evaluation_id = evaluation_data.get('id')
    #             montant_net = float(evaluation_data.get('montant_net', 0))
                
    #             try:
    #                 reglements_existants = self.reglement_controller.get_reglements_by_evaluation(
    #                     evaluation_id
    #                 )
    #                 total_deja_engage = sum(
    #                     float(r.get('montant', 0))
    #                     for r in reglements_existants
    #                     if r.get('statut') not in ('ANNULE', 'REJETE')
    #                 )
    #                 montant_disponible = montant_net - total_deja_engage
                    
    #                 if montant > montant_net:
    #                     QMessageBox.warning(
    #                         self, "Contrôle FIN-001",
    #                         f"Montant ({montant:,.0f}) > évaluation ({montant_net:,.0f})"
    #                     )
    #                     return
                    
    #                 if total_deja_engage > 0 and montant > montant_disponible:
    #                     QMessageBox.warning(
    #                         self, "Contrôle FIN-002",
    #                         f"Montant ({montant:,.0f}) > disponible ({montant_disponible:,.0f})"
    #                     )
    #                     return
    #             except Exception as e:
    #                 print(f"⚠️ Vérification évaluation échouée : {e}")
    #         else:
    #             reply = QMessageBox.question(
    #                 self, "Avertissement",
    #                 "Aucune évaluation associée.\nContinuer quand même ?",
    #                 QMessageBox.Yes | QMessageBox.No,
    #                 QMessageBox.No
    #             )
    #             if reply != QMessageBox.Yes:
    #                 return
            
    #         # 5. Type paiement
    #         type_paiement = (
    #             self.input_type_paiement.currentData()
    #             or self.input_type_paiement.currentText()
    #         )
    #         if not type_paiement:
    #             QMessageBox.warning(self, "Validation", "Sélectionnez un type.")
    #             return
            
    #         # 6. Détails paiement
    #         details_paiement = self._valider_details_paiement(type_paiement)
    #         if details_paiement is None:
    #             return
            
    #         # 7. Bénéficiaire
    #         source = beneficiaire_data.get('source', 'TIERS')
    #         beneficiaire_id = None
    #         beneficiaire_nom = beneficiaire_data.get('nom_complet', 'N/A')
            
    #         if source == 'EXPERT':
    #             try:
    #                 beneficiaire_id = self._get_or_create_beneficiaire_for_expert(
    #                     beneficiaire_data
    #                 )
    #                 if not beneficiaire_id:
    #                     QMessageBox.critical(
    #                         self, "Erreur",
    #                         "Impossible de créer le bénéficiaire pour l'expert."
    #                     )
    #                     return
    #             except Exception as e:
    #                 QMessageBox.critical(
    #                     self, "Erreur",
    #                     f"Erreur création bénéficiaire : {e}"
    #                 )
    #                 return
    #         else:
    #             beneficiaire_id = beneficiaire_data.get('id')
    #             if not beneficiaire_id:
    #                 QMessageBox.warning(self, "Validation", "ID bénéficiaire manquant.")
    #                 return
            
    #         # 8. Données finales
    #         data = {
    #             'sinistre_id': self.sinistre_id,
    #             'beneficiaire_id': beneficiaire_id,
    #             'beneficiaire_nom': beneficiaire_nom,
    #             'montant': montant,
    #             'type_paiement': type_paiement,
    #             'observations': self.input_observations.toPlainText().strip() or None,
    #             'created_by': self.user.id if self.user else None,
    #         }
            
    #         if evaluation_id:
    #             data['evaluation_id'] = evaluation_id
            
    #         data.update(details_paiement)
            
    #         # 9. Confirmation
    #         recap = self._build_recap(data, beneficiaire_data)
    #         reply = QMessageBox.question(
    #             self,
    #             "Confirmer la création",
    #             f"Voulez-vous créer ce règlement ?\n\n{recap}",
    #             QMessageBox.Yes | QMessageBox.No,
    #             QMessageBox.Yes
    #         )
    #         if reply != QMessageBox.Yes:
    #             return
            
    #         # 10. Création
    #         print(f"📝 Création règlement : {data}")
    #         result = self.reglement_controller.creer_reglement(data)
            
    #         if not result:
    #             QMessageBox.critical(self, "Erreur", "Création échouée.")
    #             return
            
    #         # 11. Succès
    #         self.reglement_created.emit(result)
            
    #         QMessageBox.information(
    #             self,
    #             "Succès",
    #             f"Règlement créé avec succès !\n\n"
    #             f"N° : {result.get('numero_reglement', 'N/A')}\n"
    #             f"Bénéficiaire : {beneficiaire_nom}\n"
    #             f"Montant : {montant:,.0f} FCFA\n"
    #             f"Type : {type_paiement}\n"
    #             f"Statut : CRÉÉ"
    #         )
            
    #         self.accept()
        
    #     except Exception as e:
    #         print(f"❌ Erreur : {e}")
    #         import traceback
    #         traceback.print_exc()
    #         QMessageBox.critical(self, "Erreur", f"Erreur : {e}")
    
    def creer_reglement(self):
        """
        Crée un règlement avec toutes les validations.
        
        Envoie au service :
        - beneficiaire_source : 'BENEFICIAIRE' | 'TIERS' | 'EXPERT'
        - beneficiaire_id : ID dans la table source (info)
        - beneficiaire_data : dict complet (pour résolution par identité)
        """
        try:
            # ============================================================
            # 1. VALIDATION DU SINISTRE
            # ============================================================
            if not self.sinistre_id:
                QMessageBox.warning(
                    self, "Validation",
                    "Aucun sinistre associé au règlement."
                )
                return
            
            # ============================================================
            # 2. VALIDATION DU BÉNÉFICIAIRE
            # ============================================================
            beneficiaire_data = self.input_beneficiaire.currentData()
            if not beneficiaire_data:
                QMessageBox.warning(
                    self, "Validation",
                    "Veuillez sélectionner un bénéficiaire."
                )
                self.input_beneficiaire.setFocus()
                return
            
            # Vérifier qu'on a bien les données d'identité
            nom = (beneficiaire_data.get('nom') or '').strip()
            if not nom:
                QMessageBox.warning(
                    self, "Validation",
                    "Le bénéficiaire sélectionné n'a pas de nom."
                )
                return
            
            # ============================================================
            # 3. VALIDATION DU MONTANT
            # ============================================================
            montant = float(self.input_montant.value())
            if montant <= 0:
                QMessageBox.warning(
                    self, "Validation",
                    "Le montant doit être strictement positif."
                )
                self.input_montant.setFocus()
                return
            
            # ============================================================
            # 4. VALIDATION DE L'ÉVALUATION
            # ============================================================
            evaluation_data = self.input_evaluation.currentData()
            evaluation_id = None
            
            if evaluation_data:
                evaluation_id = evaluation_data.get('id')
                montant_net = float(evaluation_data.get('montant_net', 0))
                
                # Contrôle FIN-001
                if montant > montant_net:
                    QMessageBox.warning(
                        self, "Contrôle FIN-001",
                        f"Le montant ({montant:,.0f} FCFA) dépasse "
                        f"l'évaluation ({montant_net:,.0f} FCFA)."
                    )
                    return
                
                # Contrôle FIN-002 (cumul)
                try:
                    reglements_existants = (
                        self.reglement_controller.get_reglements_by_evaluation(
                            evaluation_id
                        )
                    )
                    total_deja_engage = sum(
                        float(r.get('montant', 0))
                        for r in reglements_existants
                        if r.get('statut') not in ('ANNULE', 'REJETE')
                    )
                    disponible = montant_net - total_deja_engage
                    
                    if total_deja_engage > 0 and montant > disponible:
                        QMessageBox.warning(
                            self, "Contrôle FIN-002",
                            f"Le montant ({montant:,.0f} FCFA) dépasse "
                            f"le disponible ({disponible:,.0f} FCFA) "
                            f"après déduction des règlements existants "
                            f"({total_deja_engage:,.0f} FCFA)."
                        )
                        return
                except Exception as e:
                    print(f"⚠️ Vérification évaluation échouée : {e}")
            else:
                # Avertissement : pas d'évaluation associée
                reply = QMessageBox.question(
                    self, "Avertissement",
                    "Aucune évaluation n'est associée à ce règlement.\n\n"
                    "Le règlement ne pourra pas être validé sans évaluation.\n\n"
                    "Voulez-vous continuer ?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # ============================================================
            # 5. VALIDATION DU TYPE DE PAIEMENT
            # ============================================================
            type_paiement = (
                self.input_type_paiement.currentData()
                or self.input_type_paiement.currentText()
            )
            
            if type_paiement not in ('CHEQUE', 'VIREMENT', 'MOBILE_MONEY'):
                QMessageBox.warning(
                    self, "Validation",
                    f"Type de paiement invalide : {type_paiement}"
                )
                return
            
            # ============================================================
            # 6. VALIDATION DES DÉTAILS SELON LE TYPE
            # ============================================================
            details_paiement = self._valider_details_paiement(type_paiement)
            if details_paiement is None:
                return  # Erreur déjà affichée
            
            # ============================================================
            # 7. CONSTRUCTION DES DONNÉES DU RÈGLEMENT
            # ============================================================
            data = {
                'sinistre_id': self.sinistre_id,
                
                # ✅ Source + ID (info)
                'beneficiaire_source': beneficiaire_data.get('source', 'BENEFICIAIRE'),
                'beneficiaire_id': beneficiaire_data.get('id'),
                
                # ✅ Données complètes (pour résolution par identité)
                # Le service fera la recherche/création dans lometa_beneficiaires
                'beneficiaire_data': beneficiaire_data,
                
                # Nom d'affichage (info)
                'beneficiaire_nom': beneficiaire_data.get('nom_complet', 'N/A'),
                
                'montant': montant,
                'type_paiement': type_paiement,
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None,
            }
            
            if evaluation_id:
                data['evaluation_id'] = evaluation_id
            
            data.update(details_paiement)
            
            # ============================================================
            # 8. RÉCAPITULATIF ET CONFIRMATION
            # ============================================================
            recap = self._build_recap(data, beneficiaire_data)
            
            reply = QMessageBox.question(
                self,
                "Confirmer la création",
                f"Voulez-vous créer ce règlement ?\n\n{recap}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # ============================================================
            # 9. CRÉATION DU RÈGLEMENT
            # ============================================================
            print(f"📝 Création règlement : source={data['beneficiaire_source']}, "
                f"source_id={data['beneficiaire_id']}, montant={montant:,.0f}")

            print(f"📝 Détails : {data}")
            
            result = self.reglement_controller.creer_reglement(data)
            
            if not result:
                QMessageBox.critical(
                    self, "Erreur",
                    "Le règlement n'a pas pu être créé.\n"
                    "Vérifiez les logs pour plus de détails."
                )
                return
            
            # ============================================================
            # 10. SUCCÈS
            # ============================================================
            self.reglement_created.emit(result)
            
            QMessageBox.information(
                self,
                "✅ Succès",
                f"Règlement créé avec succès !\n\n"
                f"📌 N° Règlement : {result.get('numero_reglement', 'N/A')}\n"
                f"💰 Montant : {montant:,.0f} FCFA\n"
                f"💳 Type : {type_paiement}\n"
                f"📊 Statut : CRÉÉ\n\n"
                f"Le règlement doit maintenant être validé par un responsable."
            )
            
            self.accept()
        
        except Exception as e:
            print(f"❌ Erreur création règlement : {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Erreur",
                f"Erreur lors de la création :\n{str(e)}"
            )

    # ================================================================
    # MÉTHODES PRIVÉES
    # ================================================================
    
    # def _valider_details_paiement(self, type_paiement: str) -> Optional[dict]:
    #     """Valide les détails selon le type."""
    #     details = {}
        
    #     if type_paiement == "CHEQUE":
    #         numero = self.input_cheque_numero.text().strip()
    #         banque = self.input_cheque_banque.text().strip()
            
    #         if not numero:
    #             QMessageBox.warning(self, "Validation", "N° chèque obligatoire.")
    #             self.input_cheque_numero.setFocus()
    #             return None
    #         if not banque:
    #             QMessageBox.warning(self, "Validation", "Banque obligatoire.")
    #             self.input_cheque_banque.setFocus()
    #             return None
            
    #         details['numero_cheque'] = numero
    #         details['banque_emetteur'] = banque
        
    #     elif type_paiement == "VIREMENT":
    #         ref = self.input_virement_ref.text().strip()
    #         if not ref:
    #             QMessageBox.warning(self, "Validation", "Référence virement obligatoire.")
    #             self.input_virement_ref.setFocus()
    #             return None
    #         details['reference_virement'] = ref
        
    #     elif type_paiement == "MOBILE_MONEY":
    #         num = self.input_mobile_numero.text().strip()
    #         op = self.input_mobile_operateur.currentText()
    #         if not num:
    #             QMessageBox.warning(self, "Validation", "Numéro mobile obligatoire.")
    #             self.input_mobile_numero.setFocus()
    #             return None
    #         details['reference_mobile'] = num
    #         details['operateur_mobile'] = op
        
    #     return details
    
    def _valider_details_paiement(self, type_paiement: str) -> Optional[dict]:
        """
        Valide les détails spécifiques au type de paiement.
        
        Returns:
            dict avec les détails, ou None si erreur.
        """
        details = {}
        
        # ─── CHÈQUE ───
        if type_paiement == "CHEQUE":
            numero_cheque = self.input_cheque_numero.text().strip()
            banque_emetteur = self.input_cheque_banque.text().strip()
            
            if not numero_cheque:
                QMessageBox.warning(
                    self, "Validation",
                    "Le numéro de chèque est obligatoire (règle PAY-CHQ-001)."
                )
                self.input_cheque_numero.setFocus()
                return None
            
            if not banque_emetteur:
                QMessageBox.warning(
                    self, "Validation",
                    "La banque émettrice est obligatoire pour un chèque."
                )
                self.input_cheque_banque.setFocus()
                return None
            
            details['numero_cheque'] = numero_cheque
            details['banque_emetteur'] = banque_emetteur
        
        # ─── VIREMENT ───
        elif type_paiement == "VIREMENT":
            reference_virement = self.input_virement_ref.text().strip()
            
            if not reference_virement:
                QMessageBox.warning(
                    self, "Validation",
                    "La référence de virement est obligatoire."
                )
                self.input_virement_ref.setFocus()
                return None
            
            details['reference_virement'] = reference_virement
        
        # ─── MOBILE MONEY ───
        elif type_paiement == "MOBILE_MONEY":
            numero_mobile = self.input_mobile_numero.text().strip()
            operateur = self.input_mobile_operateur.currentText()
            
            if not numero_mobile:
                QMessageBox.warning(
                    self, "Validation",
                    "Le numéro Mobile Money est obligatoire."
                )
                self.input_mobile_numero.setFocus()
                return None
            
            if not operateur:
                QMessageBox.warning(
                    self, "Validation",
                    "L'opérateur Mobile Money est obligatoire."
                )
                return None
            
            details['reference_mobile'] = numero_mobile
            details['operateur_mobile'] = operateur
        
        else:
            QMessageBox.warning(
                self, "Validation",
                f"Type de paiement inconnu : {type_paiement}"
            )
            return None
        
        return details

    def _get_or_create_beneficiaire_for_expert(
        self, expert_data: dict
    ) -> Optional[int]:
        """Récupère ou crée un bénéficiaire pour un expert."""
        try:
            nom = (expert_data.get('nom') or '').strip()
            prenom = (expert_data.get('prenom') or '').strip()
            
            try:
                benefs_existants = self.reglement_controller.get_beneficiaires('EXPERT')
                for b in benefs_existants:
                    if (b.get('nom', '').strip() == nom
                            and (b.get('prenom') or '').strip() == prenom):
                        return b.get('id')
            except Exception:
                pass
            
            nouveau = self.reglement_controller.creer_beneficiaire({
                'type_beneficiaire': 'EXPERT',
                'nom': nom,
                'prenom': prenom or None,
                'telephone': (
                    expert_data.get('telephone')
                    or expert_data.get('portable')
                ),
                'email': expert_data.get('email'),
                'adresse': expert_data.get('adresse'),
                'ville': expert_data.get('ville'),
                'code_postal': expert_data.get('code_postal'),
                'pays': expert_data.get('pays'),
                'created_by': self.user.id if self.user else None,
            })
            
            if nouveau and nouveau.get('id'):
                return nouveau.get('id')
            return None
        except Exception as e:
            print(f"❌ Erreur création bénéficiaire expert : {e}")
            return None
    
    # def _build_recap(self, data: dict, beneficiaire_data: dict) -> str:
    #     """Construit le texte du récap."""
    #     lines = []
        
    #     num_sinistre = self.sinistre_info.get('numero_sinistre', 'N/A')
    #     lines.append(f"Sinistre : {num_sinistre}")
        
    #     nom = beneficiaire_data.get('nom_complet', 'N/A')
    #     type_ben = beneficiaire_data.get('type_beneficiaire', 'N/A')
    #     lines.append(f"Bénéficiaire : {nom} ({type_ben})")
        
    #     if beneficiaire_data.get('source') == 'EXPERT':
    #         lines.append(f"  → Bénéficiaire créé automatiquement")
        
    #     lines.append(f"Montant : {data['montant']:,.0f} FCFA")
    #     lines.append(f"Type : {data['type_paiement']}")
        
    #     if data.get('numero_cheque'):
    #         lines.append(f"N° chèque : {data['numero_cheque']}")
    #     if data.get('reference_virement'):
    #         lines.append(f"Réf. : {data['reference_virement']}")
    #     if data.get('reference_mobile'):
    #         lines.append(f"Mobile : {data['reference_mobile']}")
        
    #     return "\n".join(lines)

    def _build_recap(self, data: dict, beneficiaire_data: dict) -> str:
        """
        Construit le texte du récapitulatif pour la confirmation.
        """
        lines = []
        
        # ─── Sinistre ───
        num_sinistre = self.sinistre_info.get('numero_sinistre', 'N/A')
        lines.append(f"Sinistre : {num_sinistre}")
        
        # ─── Bénéficiaire ───
        source = beneficiaire_data.get('source', '')
        nom_complet = beneficiaire_data.get('nom_complet', 'N/A')
        type_ben = beneficiaire_data.get('type_beneficiaire', 'N/A')
        is_benef = beneficiaire_data.get('is_beneficiaire', False)
        
        if source == 'BENEFICIAIRE':
            lines.append(f"Bénéficiaire : {nom_complet} ({type_ben}) [enregistré]")
        elif source in ('TIERS', 'EXPERT'):
            lines.append(f"Bénéficiaire : {nom_complet} ({type_ben}) [{source}]")
            lines.append(f"   → Résolution automatique dans lometa_beneficiaires")
        
        # Contact
        tel = (
            beneficiaire_data.get('telephone')
            or beneficiaire_data.get('portable')
        )
        if tel:
            lines.append(f"Téléphone : {tel}")
        
        # ─── Montant ───
        lines.append(f"Montant : {data['montant']:,.0f} FCFA")
        
        # ─── Type de paiement ───
        lines.append(f"Type : {data['type_paiement']}")
        
        # ─── Détails spécifiques ───
        if data.get('numero_cheque'):
            lines.append(f"N° chèque : {data['numero_cheque']}")
            if data.get('banque_emetteur'):
                lines.append(f"Banque : {data['banque_emetteur']}")
        
        if data.get('reference_virement'):
            lines.append(f"Réf. virement : {data['reference_virement']}")
        
        if data.get('reference_mobile'):
            lines.append(f"Mobile : {data['reference_mobile']}")
            if data.get('operateur_mobile'):
                lines.append(f"Opérateur : {data['operateur_mobile']}")
        
        # ─── Évaluation ───
        if data.get('evaluation_id'):
            evaluation_data = self.input_evaluation.currentData()
            if evaluation_data:
                num_eval = evaluation_data.get('numero_evaluation', 'N/A')
                montant_net = evaluation_data.get('montant_net', 0)
                lines.append(
                    f"Évaluation : {num_eval} ({montant_net:,.0f} FCFA)"
                )
        
        # ─── Observations ───
        if data.get('observations'):
            obs = data['observations'][:60]
            suffix = '...' if len(data['observations']) > 60 else ''
            lines.append(f"Observations : {obs}{suffix}")
        
        return "\n".join(lines)