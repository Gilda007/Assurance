


"""
Page de gestion des rôles et permissions — Design moderne v2.0
Menu contextuel + bouton ⋯ sur le tableau, matrices interactives fonctionnelles
Design avec icônes FontAwesome
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QMessageBox, QTabWidget, QFrame,
    QCheckBox, QGridLayout, QScrollArea, QComboBox, QDialog, QLineEdit,
    QGraphicsDropShadowEffect, QMenu, QSizePolicy, QAbstractItemView,
    QInputDialog, QSpinBox, QTextEdit, QFormLayout
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor, QFont, QAction

import qtawesome as qta

from datetime import datetime
from typing import Optional, List, Dict


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def _safe_bool(v) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        return v.strip().lower() not in ('', 'none', 'null', '0', 'false')
    return bool(v)


def make_icon_label(icon_name: str, color: str = "#1a73e8", size: int = 20) -> QLabel:
    """Crée un QLabel contenant une icône FontAwesome"""
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
    lbl.setStyleSheet(lbl.styleSheet() + "background: transparent;")
    return lbl


# ═══════════════════════════════════════════════════════════════════
# WIDGETS PERSONNALISÉS
# ═══════════════════════════════════════════════════════════════════

class StatCard(QFrame):
    """Carte statistique moderne avec icône FontAwesome"""
    def __init__(self, icon_name: str, title: str, value: str, 
                 color_bg: str, color_fg: str, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(90)
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
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)
        
        # Icône FontAwesome
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {color_bg};
                border-radius: 10px;
                border: none;
            }}
        """)
        il = QVBoxLayout(icon_container)
        il.setContentsMargins(0, 0, 0, 0)
        il.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel()
        try:
            icon = qta.icon(icon_name, color=color_fg)
            icon_lbl.setPixmap(icon.pixmap(QSize(22, 22)))
        except Exception as e:
            print(f"⚠️ Icône '{icon_name}' introuvable : {e}")
            icon_lbl.setText("●")
            icon_lbl.setStyleSheet(f"color: {color_fg}; font-size: 18px;")
        
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(icon_lbl.styleSheet() + "background: transparent; border: none;")
        il.addWidget(icon_lbl)
        layout.addWidget(icon_container)
        
        tl = QVBoxLayout()
        tl.setSpacing(2)
        
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500; background: transparent;")
        
        v_lbl = QLabel(str(value))
        v_lbl.setStyleSheet(f"color: {color_fg}; font-size: 22px; font-weight: 800; background: transparent;")
        v_lbl.setObjectName("stat_value")
        
        tl.addWidget(t_lbl)
        tl.addWidget(v_lbl)
        layout.addLayout(tl, 1)


class StatusBadge(QLabel):
    """Badge arrondi actif/inactif"""
    def __init__(self, is_active: bool, parent=None):
        super().__init__(parent)
        if is_active:
            bg, fg, label = "#d1fae5", "#065f46", "Actif"
        else:
            bg, fg, label = "#fee2e2", "#991b1b", "Inactif"
        self.setText(f"  {label}  ")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 11px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
                border: none;
            }}
        """)
        self.setFixedHeight(22)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)


class LevelBadge(QLabel):
    """Badge niveau"""
    def __init__(self, level: int, parent=None):
        super().__init__(parent)
        if level >= 80:
            bg, fg = "#fee2e2", "#991b1b"
        elif level >= 50:
            bg, fg = "#fef3c7", "#92400e"
        elif level >= 30:
            bg, fg = "#dbeafe", "#1e40af"
        else:
            bg, fg = "#e2e8f0", "#475569"
        self.setText(f"  N{level}  ")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 11px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 700;
                border: none;
            }}
        """)
        self.setFixedHeight(22)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)


class SystemBadge(QLabel):
    """Badge système/personnalisé"""
    def __init__(self, is_system: bool, parent=None):
        super().__init__(parent)
        if is_system:
            bg, fg, label = "#ede9fe", "#6d28d9", "Système"
        else:
            bg, fg, label = "#f1f5f9", "#475569", "Personnalisé"
        self.setText(f"  {label}  ")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 11px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
                border: none;
            }}
        """)
        self.setFixedHeight(22)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)


# ═══════════════════════════════════════════════════════════════════
# DIALOG : CRÉATION / ÉDITION DE RÔLE
# ═══════════════════════════════════════════════════════════════════

class RoleDialog(QDialog):
    """Dialogue de création / édition de rôle"""
    
    role_saved = Signal(dict)
    
    def __init__(self, role_data: Optional[dict] = None, parent=None):
        super().__init__(parent)
        self.role_data = role_data
        self.is_edit = role_data is not None
        
        self.setWindowTitle("Modifier le rôle" if self.is_edit else "Nouveau rôle")
        self.setMinimumWidth(500)
        self.setStyleSheet("background: white;")
        
        self._setup_ui()
        if self.is_edit:
            self._fill_form()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # ✅ Titre avec icône
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        
        title_icon = QLabel()
        icon_name = 'fa5s.user-edit' if self.is_edit else 'fa5s.user-plus'
        title_icon.setPixmap(qta.icon(icon_name, color='#2563eb').pixmap(QSize(24, 24)))
        title_row.addWidget(title_icon)
        
        title = QLabel("Modifier le rôle" if self.is_edit else "Créer un nouveau rôle")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #0f172a;")
        title_row.addWidget(title)
        title_row.addStretch()
        
        layout.addLayout(title_row)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)
        
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Ex: MANAGER, AGENT...")
        self.input_code.setStyleSheet(self._input_style())
        form.addRow("Code * :", self.input_code)
        
        self.input_libelle = QLineEdit()
        self.input_libelle.setPlaceholderText("Nom affiché")
        self.input_libelle.setStyleSheet(self._input_style())
        form.addRow("Libellé * :", self.input_libelle)
        
        self.input_description = QTextEdit()
        self.input_description.setPlaceholderText("Description (optionnel)")
        self.input_description.setMaximumHeight(80)
        self.input_description.setStyleSheet(self._input_style())
        form.addRow("Description :", self.input_description)
        
        self.input_niveau = QSpinBox()
        self.input_niveau.setRange(0, 100)
        self.input_niveau.setValue(50)
        self.input_niveau.setSuffix(" / 100")
        self.input_niveau.setStyleSheet(self._input_style())
        form.addRow("Niveau :", self.input_niveau)
        
        layout.addLayout(form)
        
        # ✅ Info avec icône
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(12, 10, 12, 10)
        info_layout.setSpacing(8)
        
        info_icon = QLabel()
        info_icon.setPixmap(qta.icon('fa5s.info-circle', color='#64748b').pixmap(QSize(14, 14)))
        info_layout.addWidget(info_icon)
        
        info = QLabel("Le code doit être unique. Les rôles système ne peuvent être supprimés.")
        info.setStyleSheet("color: #64748b; font-size: 11px; background: transparent;")
        info.setWordWrap(True)
        info_layout.addWidget(info, 1)
        
        layout.addWidget(info_frame)
        
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        # ✅ Bouton Annuler avec icône
        btn_cancel = QPushButton("  Annuler")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setIcon(qta.icon('fa5s.times', color='#64748b'))
        btn_cancel.setIconSize(QSize(12, 12))
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 600;
                color: #64748b;
                text-align: left;
            }
            QPushButton:hover { background: #f8fafc; color: #1e293b; }
        """)
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)
        
        # ✅ Bouton Enregistrer avec icône
        btn_save = QPushButton("  Enregistrer")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setIcon(qta.icon('fa5s.save', color='white'))
        btn_save.setIconSize(QSize(12, 12))
        btn_save.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        btn_save.clicked.connect(self._save)
        buttons.addWidget(btn_save)
        
        layout.addLayout(buttons)
    
    def _input_style(self) -> str:
        return """
            QLineEdit, QTextEdit, QSpinBox {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #1e293b;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
                border-color: #3b82f6;
                background: white;
            }
        """
    
    def _fill_form(self):
        self.input_code.setText(self.role_data.get('code', ''))
        self.input_libelle.setText(self.role_data.get('libelle', ''))
        self.input_description.setPlainText(self.role_data.get('description', '') or '')
        self.input_niveau.setValue(int(self.role_data.get('niveau', 50)))
        self.input_code.setReadOnly(True)
    
    def _save(self):
        code = self.input_code.text().strip().upper()
        libelle = self.input_libelle.text().strip()
        
        if not code:
            QMessageBox.warning(self, "Erreur", "Le code est obligatoire")
            return
        if not libelle:
            QMessageBox.warning(self, "Erreur", "Le libellé est obligatoire")
            return
        
        data = {
            'id': self.role_data.get('id') if self.is_edit else None,
            'code': code,
            'libelle': libelle,
            'description': self.input_description.toPlainText().strip() or None,
            'niveau': self.input_niveau.value(),
        }
        
        self.role_saved.emit(data)
        self.accept()


# ═══════════════════════════════════════════════════════════════════
# DIALOG : GESTION DES RÔLES D'UN UTILISATEUR
# ═══════════════════════════════════════════════════════════════════

class ManageUserRolesDialog(QDialog):
    """Dialogue pour gérer les rôles d'un utilisateur"""
    
    roles_saved = Signal(int, list)
    
    def __init__(self, user_data: dict, all_roles: list, controller, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.all_roles = all_roles
        self.controller = controller
        
        self.user_id = user_data.get('id')
        self.username = user_data.get('username', 'N/A')
        
        self.current_roles = set()
        for r in user_data.get('roles', []) or []:
            if isinstance(r, dict):
                code = r.get('code')
                if code:
                    self.current_roles.add(code)
            else:
                self.current_roles.add(str(r))
        
        self.setWindowTitle(f"Gérer les rôles de {self.username}")
        self.setMinimumWidth(520)
        self.setMinimumHeight(500)
        self.setStyleSheet("background: white;")
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # ─── En-tête avec icône ───
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 10, 12, 10)
        hl.setSpacing(12)
        
        avatar = QLabel(self.username[0].upper() if self.username else "?")
        avatar.setFixedSize(44, 44)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3b82f6, stop:1 #6366f1);
            color: white;
            border-radius: 22px;
            font-size: 18px;
            font-weight: bold;
        """)
        hl.addWidget(avatar)
        
        info = QVBoxLayout()
        info.setSpacing(2)
        
        name_lbl = QLabel(self.user_data.get('nom_complet') or self.username)
        name_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #0f172a; background: transparent;")
        info.addWidget(name_lbl)
        
        email_lbl = QLabel(self.user_data.get('email', '—') or '—')
        email_lbl.setStyleSheet("color: #64748b; font-size: 11px; background: transparent;")
        info.addWidget(email_lbl)
        
        hl.addLayout(info)
        hl.addStretch()
        
        self.lbl_count = QLabel(f"0 rôle(s) sélectionné(s)")
        self.lbl_count.setStyleSheet("""
            background: #dbeafe;
            color: #1e40af;
            border-radius: 10px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 600;
        """)
        hl.addWidget(self.lbl_count)
        
        layout.addWidget(header)
        
        # ─── Titre liste ───
        title = QLabel("Sélectionnez les rôles à attribuer")
        title.setStyleSheet("font-size: 13px; font-weight: 700; color: #0f172a;")
        layout.addWidget(title)
        
        # ─── Barre actions rapides avec icônes ───
        actions = QHBoxLayout()
        actions.setSpacing(8)
        
        btn_all = QPushButton("  Tout cocher")
        btn_all.setCursor(Qt.PointingHandCursor)
        btn_all.setIcon(qta.icon('fa5s.check-square', color='#2563eb'))
        btn_all.setIconSize(QSize(12, 12))
        btn_all.setStyleSheet(self._btn_small_style())
        btn_all.clicked.connect(lambda: self._toggle_all(True))
        actions.addWidget(btn_all)
        
        btn_none = QPushButton("  Tout décocher")
        btn_none.setCursor(Qt.PointingHandCursor)
        btn_none.setIcon(qta.icon('fa5s.square', color='#64748b'))
        btn_none.setIconSize(QSize(12, 12))
        btn_none.setStyleSheet(self._btn_small_style())
        btn_none.clicked.connect(lambda: self._toggle_all(False))
        actions.addWidget(btn_none)
        
        btn_reset = QPushButton("  Rétablir")
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setIcon(qta.icon('fa5s.undo', color='#64748b'))
        btn_reset.setIconSize(QSize(12, 12))
        btn_reset.setStyleSheet(self._btn_small_style())
        btn_reset.clicked.connect(self._reset_to_current)
        actions.addWidget(btn_reset)
        
        actions.addStretch()
        layout.addLayout(actions)
        
        # ─── Liste scrollable ───
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                background: white;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #94a3b8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        
        content = QWidget()
        content.setStyleSheet("background: white;")
        self.roles_layout = QVBoxLayout(content)
        self.roles_layout.setContentsMargins(14, 14, 14, 14)
        self.roles_layout.setSpacing(8)
        
        self.role_checkboxes = {}
        
        if not self.all_roles:
            empty = QLabel("Aucun rôle disponible")
            empty.setStyleSheet("color: #94a3b8; font-size: 12px; padding: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.roles_layout.addWidget(empty)
        else:
            sorted_roles = sorted(
                self.all_roles,
                key=lambda r: -int(r.get('niveau', 0) or 0)
            )
            
            for role in sorted_roles:
                self.roles_layout.addWidget(self._build_role_row(role))
        
        self.roles_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        
        # ─── Boutons ───
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        btn_cancel = QPushButton("  Annuler")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setIcon(qta.icon('fa5s.times', color='#64748b'))
        btn_cancel.setIconSize(QSize(12, 12))
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 600;
                color: #64748b;
                text-align: left;
            }
            QPushButton:hover { background: #f8fafc; color: #1e293b; }
        """)
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)
        
        self.btn_save = QPushButton("  Enregistrer")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setIcon(qta.icon('fa5s.save', color='white'))
        self.btn_save.setIconSize(QSize(12, 12))
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        self.btn_save.clicked.connect(self._save)
        buttons.addWidget(self.btn_save)
        
        layout.addLayout(buttons)
        
        self._update_count()
    
    def _build_role_row(self, role: dict) -> QWidget:
        """Construit une ligne de rôle avec checkbox"""
        code = role.get('code', '')
        libelle = role.get('libelle', code)
        niveau = int(role.get('niveau', 0) or 0)
        is_system = _safe_bool(role.get('est_systeme'))
        description = role.get('description', '') or ''
        
        is_current = code in self.current_roles
        
        row = QFrame()
        row.setCursor(Qt.PointingHandCursor)
        row.setStyleSheet(f"""
            QFrame {{
                background: {'#eff6ff' if is_current else 'white'};
                border: 1px solid {'#bfdbfe' if is_current else '#e2e8f0'};
                border-radius: 8px;
            }}
            QFrame:hover {{
                background: #f8fafc;
                border-color: #cbd5e1;
            }}
        """)
        
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        
        check = QCheckBox()
        check.setChecked(is_current)
        check.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #cbd5e1;
                border-radius: 5px;
                background: white;
            }
            QCheckBox::indicator:hover { border-color: #3b82f6; }
            QCheckBox::indicator:checked {
                background: #2563eb;
                border-color: #2563eb;
            }
        """)
        check.stateChanged.connect(self._on_check_changed)
        layout.addWidget(check)
        
        self.role_checkboxes[code] = check
        
        # ✅ Icône FontAwesome selon niveau
        icon_name = self._get_role_icon(niveau)
        icon_color = self._get_level_fg(niveau)
        icon = make_icon_label(icon_name, color=icon_color, size=18)
        icon.setFixedSize(36, 36)
        icon.setStyleSheet(f"""
            background: {self._get_level_bg(niveau)};
            border-radius: 9px;
        """)
        layout.addWidget(icon)
        
        info = QVBoxLayout()
        info.setSpacing(2)
        
        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        
        name = QLabel(libelle)
        name.setStyleSheet("font-size: 13px; font-weight: 700; color: #0f172a; background: transparent;")
        title_row.addWidget(name)
        
        code_lbl = QLabel(code)
        code_lbl.setStyleSheet("""
            color: #64748b;
            font-size: 10px;
            background: #f1f5f9;
            border-radius: 6px;
            padding: 1px 6px;
        """)
        title_row.addWidget(code_lbl)
        
        if is_system:
            sys_badge = QLabel("Système")
            sys_badge.setStyleSheet("""
                background: #ede9fe;
                color: #6d28d9;
                border-radius: 6px;
                padding: 1px 6px;
                font-size: 9px;
                font-weight: 700;
            """)
            title_row.addWidget(sys_badge)
        
        title_row.addStretch()
        info.addLayout(title_row)
        
        if description:
            desc = QLabel(description)
            desc.setStyleSheet("color: #64748b; font-size: 11px; background: transparent;")
            desc.setWordWrap(True)
            info.addWidget(desc)
        
        layout.addLayout(info, 1)
        
        level = QLabel(f"N{niveau}")
        level.setStyleSheet(f"""
            background: {self._get_level_bg(niveau)};
            color: {self._get_level_fg(niveau)};
            border-radius: 10px;
            padding: 3px 8px;
            font-size: 10px;
            font-weight: 700;
        """)
        layout.addWidget(level)
        
        return row
    
    def _get_role_icon(self, niveau: int) -> str:
        """Retourne le nom de l'icône FontAwesome selon le niveau"""
        if niveau >= 80:
            return "fa5s.crown"
        elif niveau >= 50:
            return "fa5s.user-cog"
        elif niveau >= 30:
            return "fa5s.user"
        return "fa5s.eye"
    
    def _get_level_bg(self, niveau: int) -> str:
        if niveau >= 80: return "#fee2e2"
        if niveau >= 50: return "#fef3c7"
        if niveau >= 30: return "#dbeafe"
        return "#e2e8f0"
    
    def _get_level_fg(self, niveau: int) -> str:
        if niveau >= 80: return "#991b1b"
        if niveau >= 50: return "#92400e"
        if niveau >= 30: return "#1e40af"
        return "#475569"
    
    def _btn_small_style(self) -> str:
        return """
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 11px;
                color: #1e293b;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
        """
    
    def _on_check_changed(self):
        self._update_count()
        self._highlight_selected()
    
    def _update_count(self):
        count = sum(1 for cb in self.role_checkboxes.values() if cb.isChecked())
        self.lbl_count.setText(f"{count} rôle(s) sélectionné(s)")
        
        if count == 0:
            self.lbl_count.setStyleSheet("""
                background: #fee2e2;
                color: #991b1b;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            """)
        else:
            self.lbl_count.setStyleSheet("""
                background: #dbeafe;
                color: #1e40af;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            """)
    
    def _highlight_selected(self):
        for code, cb in self.role_checkboxes.items():
            parent = cb.parent()
            while parent and not isinstance(parent, QFrame):
                parent = parent.parent()
            if parent:
                checked = cb.isChecked()
                parent.setStyleSheet(f"""
                    QFrame {{
                        background: {'#eff6ff' if checked else 'white'};
                        border: 1px solid {'#bfdbfe' if checked else '#e2e8f0'};
                        border-radius: 8px;
                    }}
                    QFrame:hover {{
                        background: #f8fafc;
                        border-color: #cbd5e1;
                    }}
                """)
    
    def _toggle_all(self, checked: bool):
        for cb in self.role_checkboxes.values():
            cb.setChecked(checked)
    
    def _reset_to_current(self):
        for code, cb in self.role_checkboxes.items():
            cb.setChecked(code in self.current_roles)
    
    def _save(self):
        selected = [
            code for code, cb in self.role_checkboxes.items()
            if cb.isChecked()
        ]
        
        if not selected:
            reply = QMessageBox.question(
                self, "Confirmation",
                f"⚠️ L'utilisateur {self.username} n'aura AUCUN rôle.\n\n"
                f"Il ne pourra plus accéder à l'application.\n\n"
                f"Continuer ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        self.roles_saved.emit(self.user_id, selected)
        self.accept()


# ═══════════════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════

class RolesPage(QWidget):
    """Page de gestion des rôles et permissions — Design moderne v2.0"""
    
    def __init__(self, permission_controller, user, parent=None):
        super().__init__(parent)
        self.controller = permission_controller
        self.user = user
        
        self._all_roles = []
        self._all_users = []
        self._filtered_roles = []
        self._filtered_users = []
        
        self._current_page = 1
        self._per_page = 20
        self._user_current_page = 1
        self._user_per_page = 20
        
        self.setup_ui()
        self.load_data()
    
    # ═══════════════════════════════════════════════════════════════
    # UI
    # ═══════════════════════════════════════════════════════════════
    
    def setup_ui(self):
        self.setStyleSheet("background: #f1f5f9;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        layout.addWidget(self._build_header())
        layout.addWidget(self._build_stats_row())
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar { background: transparent; }
            QTabBar::tab {
                padding: 12px 24px;
                background-color: transparent;
                border: none;
                border-bottom: 2px solid transparent;
                color: #64748b;
                font-size: 13px;
                font-weight: 600;
                margin-right: 4px;
            }
            QTabBar::tab:hover { color: #1e293b; }
            QTabBar::tab:selected {
                color: #2563eb;
                border-bottom: 2px solid #2563eb;
            }
        """)
        
        self.tabs.addTab(self._build_roles_tab(), "  Rôles  ")
        self.tabs.addTab(self._build_users_tab(), "  Utilisateurs  ")
        self.tabs.addTab(self._build_matrix_tab(), "  Matrice  ")
        
        self.tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tabs, 1)
    
    def _build_header(self):
        frame = QFrame()
        frame.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # ✅ Icône FontAwesome pour le titre
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet("""
            QFrame {
                background: #eff6ff;
                border-radius: 12px;
                border: 1px solid #dbeafe;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon('fa5s.user-shield', color='#2563eb').pixmap(QSize(24, 24)))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        # Titre + sous-titre
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("Rôles et Permissions")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a; background: transparent;")
        title_block.addWidget(title)
        
        sub = QLabel("Gestion des accès et habilitations")
        sub.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        title_block.addWidget(sub)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # ✅ Bouton refresh avec icône
        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedSize(34, 34)
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setToolTip("Actualiser")
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#64748b'))
        self.btn_refresh.setIconSize(QSize(14, 14))
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
        """)
        self.btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(self.btn_refresh)
        
        # ✅ Bouton Nouveau Rôle avec icône
        self.btn_creer = QPushButton("  Nouveau Rôle")
        self.btn_creer.setCursor(Qt.PointingHandCursor)
        self.btn_creer.setFixedHeight(38)
        self.btn_creer.setIcon(qta.icon('fa5s.plus-circle', color='white'))
        self.btn_creer.setIconSize(QSize(14, 14))
        self.btn_creer.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        self.btn_creer.clicked.connect(self._creer_role)
        layout.addWidget(self.btn_creer)
        
        return frame
    
    def _build_stats_row(self):
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        
        self.card_roles = StatCard(
            icon_name="fa5s.user-tag", 
            title="Total rôles", value="0",
            color_bg="#dbeafe", color_fg="#1e40af"
        )
        self.card_systeme = StatCard(
            icon_name="fa5s.cog", 
            title="Rôles système", value="0",
            color_bg="#ede9fe", color_fg="#6d28d9"
        )
        self.card_users = StatCard(
            icon_name="fa5s.users", 
            title="Utilisateurs", value="0",
            color_bg="#d1fae5", color_fg="#059669"
        )
        self.card_perms = StatCard(
            icon_name="fa5s.key", 
            title="Permissions", value="0",
            color_bg="#fef3c7", color_fg="#92400e"
        )
        
        layout.addWidget(self.card_roles)
        layout.addWidget(self.card_systeme)
        layout.addWidget(self.card_users)
        layout.addWidget(self.card_perms)
        
        return wrapper
    
    # ═══════════════════════════════════════════════════════════════
    # ONGLET RÔLES
    # ═══════════════════════════════════════════════════════════════
    
    def _build_roles_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
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
        
        cl = QVBoxLayout(card)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 16, 20, 16)
        hl.setSpacing(10)
        
        # Titre avec icône
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('fa5s.list', color='#2563eb').pixmap(QSize(14, 14)))
        title_row.addWidget(title_icon)
        
        title = QLabel("Liste des Rôles")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a; background: transparent;")
        title_row.addWidget(title)
        title_row.addStretch()
        
        hl.addLayout(title_row)
        hl.addStretch()
        
        self.role_search = QLineEdit()
        self.role_search.setPlaceholderText("Recherche")
        self.role_search.setFixedWidth(220)
        self.role_search.setStyleSheet(self._search_style())
        self.role_search.textChanged.connect(self._on_role_search)
        hl.addWidget(self.role_search)
        
        self.role_filter = QComboBox()
        self.role_filter.addItems(["Tous les rôles", "Système", "Personnalisé", "Actif", "Inactif"])
        self.role_filter.setStyleSheet(self._filter_style())
        self.role_filter.currentTextChanged.connect(self._on_role_filter)
        hl.addWidget(self.role_filter)
        
        btn_exp = QPushButton("  Export")
        btn_exp.setCursor(Qt.PointingHandCursor)
        btn_exp.setIcon(qta.icon('fa5s.download', color='#1e293b'))
        btn_exp.setIconSize(QSize(12, 12))
        btn_exp.setStyleSheet(self._btn_secondary())
        btn_exp.clicked.connect(lambda: self._export_data("roles"))
        hl.addWidget(btn_exp)
        
        cl.addWidget(header)
        
        # Table
        self.table_roles = QTableWidget()
        self.table_roles.setColumnCount(7)
        self.table_roles.setHorizontalHeaderLabels([
            "Code", "Libellé", "Niveau", "Type", "Statut", "Permissions", "Actions"
        ])
        self._style_table(self.table_roles)
        
        rh = self.table_roles.horizontalHeader()
        rh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        rh.setSectionResizeMode(1, QHeaderView.Stretch)
        rh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        rh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        rh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        rh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        rh.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table_roles.setColumnWidth(6, 60)
        
        self.table_roles.itemSelectionChanged.connect(self._on_role_selection)
        self.table_roles.cellDoubleClicked.connect(self._on_role_dbl_click)
        
        self.table_roles.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_roles.customContextMenuRequested.connect(self._show_roles_context_menu)
        
        cl.addWidget(self.table_roles)
        cl.addWidget(self._build_pagination("roles"))
        
        layout.addWidget(card)
        return tab
    
    # ═══════════════════════════════════════════════════════════════
    # ONGLET UTILISATEURS
    # ═══════════════════════════════════════════════════════════════
    
    def _build_users_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
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
        
        cl = QVBoxLayout(card)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
        
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 16, 20, 16)
        hl.setSpacing(10)
        
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('fa5s.users', color='#2563eb').pixmap(QSize(14, 14)))
        title_row.addWidget(title_icon)
        
        title = QLabel("Liste des Utilisateurs")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a; background: transparent;")
        title_row.addWidget(title)
        title_row.addStretch()
        
        hl.addLayout(title_row)
        hl.addStretch()
        
        self.user_search = QLineEdit()
        self.user_search.setPlaceholderText("Recherche")
        self.user_search.setFixedWidth(220)
        self.user_search.setStyleSheet(self._search_style())
        self.user_search.textChanged.connect(self._on_user_search)
        hl.addWidget(self.user_search)
        
        cl.addWidget(header)
        
        self.table_users = QTableWidget()
        self.table_users.setColumnCount(7)
        self.table_users.setHorizontalHeaderLabels([
            "ID", "Utilisateur", "Nom complet", "Email", "Rôles", "Statut", "Actions"
        ])
        self._style_table(self.table_users)
        
        uh = self.table_users.horizontalHeader()
        uh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        uh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        uh.setSectionResizeMode(2, QHeaderView.Stretch)
        uh.setSectionResizeMode(3, QHeaderView.Stretch)
        uh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        uh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        uh.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table_users.setColumnWidth(6, 60)
        
        self.table_users.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_users.customContextMenuRequested.connect(self._show_users_context_menu)
        
        cl.addWidget(self.table_users)
        cl.addWidget(self._build_pagination("users"))
        
        layout.addWidget(card)
        return tab
    
    # ═══════════════════════════════════════════════════════════════
    # ONGLET MATRICE
    # ═══════════════════════════════════════════════════════════════
    
    def _build_matrix_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
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
        
        cl = QVBoxLayout(card)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
        
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 16, 20, 16)
        hl.setSpacing(10)
        
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('fa5s.table', color='#2563eb').pixmap(QSize(14, 14)))
        title_row.addWidget(title_icon)
        
        title = QLabel("Matrice des Permissions")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a; background: transparent;")
        title_row.addWidget(title)
        title_row.addStretch()
        
        hl.addLayout(title_row)
        hl.addStretch()
        
        lbl = QLabel("Rôle :")
        lbl.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        hl.addWidget(lbl)
        
        self.combo_role_matrix = QComboBox()
        self.combo_role_matrix.setMinimumWidth(200)
        self.combo_role_matrix.setStyleSheet(self._filter_style())
        self.combo_role_matrix.currentIndexChanged.connect(self._load_matrix)
        hl.addWidget(self.combo_role_matrix)
        
        btn_all = QPushButton("  Tout cocher")
        btn_all.setCursor(Qt.PointingHandCursor)
        btn_all.setIcon(qta.icon('fa5s.check-square', color='#2563eb'))
        btn_all.setIconSize(QSize(12, 12))
        btn_all.setStyleSheet(self._btn_secondary())
        btn_all.clicked.connect(lambda: self._toggle_all_matrix(True))
        hl.addWidget(btn_all)
        
        btn_none = QPushButton("  Tout décocher")
        btn_none.setCursor(Qt.PointingHandCursor)
        btn_none.setIcon(qta.icon('fa5s.square', color='#64748b'))
        btn_none.setIconSize(QSize(12, 12))
        btn_none.setStyleSheet(self._btn_secondary())
        btn_none.clicked.connect(lambda: self._toggle_all_matrix(False))
        hl.addWidget(btn_none)

        # ✅ Bouton Preset
        btn_preset = QPushButton("  Presets")
        btn_preset.setCursor(Qt.PointingHandCursor)
        btn_preset.setIcon(qta.icon('fa5s.magic', color='#8b5cf6'))
        btn_preset.setIconSize(QSize(12, 12))
        btn_preset.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
                color: #1e293b;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
        """)

        # Menu déroulant des presets
        preset_menu = QMenu(btn_preset)
        preset_menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 6px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                color: #1e293b;
            }
            QMenu::item:selected { background: #eff6ff; color: #2563eb; }
        """)

        presets = [
            ('fa5s.eye', 'Lecture seule', 'readonly'),
            ('fa5s.user', 'Gestionnaire', 'gestionnaire'),
            ('fa5s.calculator', 'Comptable', 'comptable'),
            ('fa5s.crown', 'Administrateur', 'admin'),
        ]

        for icon_name, label, key in presets:
            action = preset_menu.addAction(
                qta.icon(icon_name, color='#2563eb'),
                f"  {label}"
            )
            action.triggered.connect(lambda checked=False, k=key: self._matrix_preset(k))

        btn_preset.setMenu(preset_menu)
        hl.addWidget(btn_preset)
        
        self.btn_save_matrix = QPushButton("  Enregistrer")
        self.btn_save_matrix.setCursor(Qt.PointingHandCursor)
        self.btn_save_matrix.setIcon(qta.icon('fa5s.save', color='white'))
        self.btn_save_matrix.setIconSize(QSize(12, 12))
        self.btn_save_matrix.setStyleSheet("""
            QPushButton {
                background: #22c55e;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover { background: #16a34a; }
        """)
        self.btn_save_matrix.clicked.connect(self._save_matrix)
        hl.addWidget(self.btn_save_matrix)
        
        cl.addWidget(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: white;")
        
        self.matrix_widget = QWidget()
        self.matrix_widget.setStyleSheet("background: white;")
        self.matrix_layout = QGridLayout(self.matrix_widget)
        self.matrix_layout.setSpacing(6)
        self.matrix_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll.setWidget(self.matrix_widget)
        cl.addWidget(scroll)
        
        layout.addWidget(card)
        return tab
    
    # ═══════════════════════════════════════════════════════════════
    # STYLES COMMUNS
    # ═══════════════════════════════════════════════════════════════
    
    def _search_style(self):
        return """
            QLineEdit {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
                color: #1e293b;
            }
            QLineEdit:focus { border-color: #3b82f6; background: white; }
        """
    
    def _filter_style(self):
        return """
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1e293b;
                min-width: 140px;
            }
            QComboBox:hover { border-color: #3b82f6; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #64748b;
                margin-right: 6px;
            }
        """
    
    def _btn_secondary(self):
        return """
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
                color: #1e293b;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
        """
    
    def _style_table(self, table):
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: none;
                gridline-color: transparent;
                outline: none;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f5f9;
                color: #1e293b;
                font-size: 12px;
            }
            QTableWidget::item:selected { background: #eff6ff; color: #1e293b; }
            QTableWidget::item:hover { background: #f8fafc; }
            QHeaderView::section {
                background: #f8fafc;
                padding: 12px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #475569;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                border-top: 1px solid #f1f5f9;
            }
            QScrollBar:vertical {
                background: transparent; width: 8px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1; border-radius: 4px; min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #94a3b8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(52)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setShowGrid(False)
    
    def _action_btn_style(self):
        return """
            QPushButton {
                background: transparent;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #f1f5f9;
                border-color: #cbd5e1;
            }
            QPushButton:pressed { background: #e2e8f0; }
        """
    
    def _menu_style(self):
        return """
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 6px;
                min-width: 230px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                color: #1e293b;
            }
            QMenu::item:selected { background: #eff6ff; color: #2563eb; }
            QMenu::item:disabled { color: #94a3b8; }
            QMenu::separator {
                height: 1px;
                background: #f1f5f9;
                margin: 4px 8px;
            }
        """
    
    def _build_pagination(self, kind: str):
        pag = QFrame()
        pag.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-top: 1px solid #f1f5f9;
            }
        """)
        layout = QHBoxLayout(pag)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(10)
        layout.addStretch()
        
        if kind == "roles":
            self.lbl_pagination = QLabel("0-0 de 0")
            self.lbl_pagination.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
            layout.addWidget(self.lbl_pagination)
            
            self.btn_prev = QPushButton("  Précédent")
            self.btn_prev.setCursor(Qt.PointingHandCursor)
            self.btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='#3b82f6'))
            self.btn_prev.setIconSize(QSize(10, 10))
            self.btn_prev.setStyleSheet(self._pag_btn_style())
            self.btn_prev.clicked.connect(self._go_prev_page)
            layout.addWidget(self.btn_prev)
            
            self.btn_next = QPushButton("Suivant  ")
            self.btn_next.setCursor(Qt.PointingHandCursor)
            self.btn_next.setIcon(qta.icon('fa5s.chevron-right', color='#3b82f6'))
            self.btn_next.setIconSize(QSize(10, 10))
            self.btn_next.setLayoutDirection(Qt.RightToLeft)
            self.btn_next.setStyleSheet(self._pag_btn_style())
            self.btn_next.clicked.connect(self._go_next_page)
            layout.addWidget(self.btn_next)
        else:
            self.lbl_pagination_users = QLabel("0-0 de 0")
            self.lbl_pagination_users.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
            layout.addWidget(self.lbl_pagination_users)
            
            self.btn_prev_users = QPushButton("  Précédent")
            self.btn_prev_users.setCursor(Qt.PointingHandCursor)
            self.btn_prev_users.setIcon(qta.icon('fa5s.chevron-left', color='#3b82f6'))
            self.btn_prev_users.setIconSize(QSize(10, 10))
            self.btn_prev_users.setStyleSheet(self._pag_btn_style())
            self.btn_prev_users.clicked.connect(self._go_prev_page_users)
            layout.addWidget(self.btn_prev_users)
            
            self.btn_next_users = QPushButton("Suivant  ")
            self.btn_next_users.setCursor(Qt.PointingHandCursor)
            self.btn_next_users.setIcon(qta.icon('fa5s.chevron-right', color='#3b82f6'))
            self.btn_next_users.setIconSize(QSize(10, 10))
            self.btn_next_users.setLayoutDirection(Qt.RightToLeft)
            self.btn_next_users.setStyleSheet(self._pag_btn_style())
            self.btn_next_users.clicked.connect(self._go_next_page_users)
            layout.addWidget(self.btn_next_users)
        
        return pag
    
    def _pag_btn_style(self):
        return """
            QPushButton {
                background: transparent;
                border: none;
                color: #3b82f6;
                font-size: 12px;
                font-weight: 600;
                padding: 4px 8px;
                text-align: left;
            }
            QPushButton:hover { color: #1d4ed8; text-decoration: underline; }
            QPushButton:disabled { color: #cbd5e1; text-decoration: none; }
        """
    
    # ═══════════════════════════════════════════════════════════════
    # CHARGEMENT
    # ═══════════════════════════════════════════════════════════════
    
    def load_data(self):
        self._load_roles()
        self._load_users()
        self._load_matrix_roles()
        self._update_stats()
    
    def _load_roles(self):
        try:
            roles = []
            if hasattr(self.controller, 'get_all_roles'):
                roles = self.controller.get_all_roles() or []
            self._all_roles = roles
            self._process_roles()
        except Exception as e:
            print(f"Erreur load roles: {e}")
            import traceback
            traceback.print_exc()
    
    def _process_roles(self):
        roles = list(self._all_roles)
        
        query = self.role_search.text().strip().lower() if hasattr(self, 'role_search') else ""
        if query:
            roles = [
                r for r in roles
                if query in str(r.get('code', '')).lower()
                or query in str(r.get('libelle', '')).lower()
                or query in str(r.get('description', '') or '').lower()
            ]
        
        f = self.role_filter.currentText() if hasattr(self, 'role_filter') else "Tous les rôles"
        if f == "Système":
            roles = [r for r in roles if _safe_bool(r.get('est_systeme'))]
        elif f == "Personnalisé":
            roles = [r for r in roles if not _safe_bool(r.get('est_systeme'))]
        elif f == "Actif":
            roles = [r for r in roles if _safe_bool(r.get('est_actif'))]
        elif f == "Inactif":
            roles = [r for r in roles if not _safe_bool(r.get('est_actif'))]
        
        self._filtered_roles = roles
        total = len(roles)
        
        start = (self._current_page - 1) * self._per_page
        end = start + self._per_page
        page = roles[start:end]
        
        self.table_roles.setRowCount(len(page))
        for i, r in enumerate(page):
            self._fill_role_row(i, r)
        
        self._update_pagination_roles(start, min(end, total))
    
    def _fill_role_row(self, row, role):
        code_item = QTableWidgetItem(role.get('code', ''))
        code_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        code_item.setForeground(QColor("#2563eb"))
        code_item.setData(Qt.UserRole, role)
        self.table_roles.setItem(row, 0, code_item)
        
        lib_item = QTableWidgetItem(role.get('libelle', ''))
        lib_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        self.table_roles.setItem(row, 1, lib_item)
        
        niveau = int(role.get('niveau', 0) or 0)
        lb = LevelBadge(niveau)
        lc = self._badge_container(lb)
        self.table_roles.setCellWidget(row, 2, lc)
        
        sb = SystemBadge(_safe_bool(role.get('est_systeme')))
        sc = self._badge_container(sb)
        self.table_roles.setCellWidget(row, 3, sc)
        
        ab = StatusBadge(_safe_bool(role.get('est_actif')))
        ac = self._badge_container(ab)
        self.table_roles.setCellWidget(row, 4, ac)
        
        perms = role.get('permissions', []) or []
        p_item = QTableWidgetItem(f"{len(perms)}")
        p_item.setTextAlignment(Qt.AlignCenter)
        p_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        self.table_roles.setItem(row, 5, p_item)
        
        # ✅ Bouton actions avec icône ellipsis
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(32, 28)
        btn.setIcon(qta.icon('fa5s.ellipsis-h', color='#64748b'))
        btn.setIconSize(QSize(14, 14))
        btn.setStyleSheet(self._action_btn_style())
        btn.clicked.connect(lambda c=False, r=role, b=btn: self._show_row_actions_menu(r, b))
        
        cont = QWidget()
        cl = QHBoxLayout(cont)
        cl.setContentsMargins(4, 6, 4, 6)
        cl.setAlignment(Qt.AlignCenter)
        cl.addWidget(btn)
        self.table_roles.setCellWidget(row, 6, cont)
    
    def _badge_container(self, badge):
        c = QWidget()
        l = QHBoxLayout(c)
        l.setContentsMargins(4, 6, 4, 6)
        l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        l.addWidget(badge)
        l.addStretch()
        return c
    
    def _load_users(self):
        try:
            users = []
            if hasattr(self.controller, 'get_all_users'):
                users = self.controller.get_all_users() or []
            self._all_users = users
            self._process_users()
        except Exception as e:
            print(f"Erreur load users: {e}")
    
    def _process_users(self):
        users = list(self._all_users)
        query = self.user_search.text().strip().lower() if hasattr(self, 'user_search') else ""
        if query:
            users = [
                u for u in users
                if query in str(u.get('username', '')).lower()
                or query in str(u.get('email', '') or '').lower()
                or query in str(u.get('nom_complet', '') or '').lower()
            ]
        
        self._filtered_users = users
        total = len(users)
        
        start = (self._user_current_page - 1) * self._user_per_page
        end = start + self._user_per_page
        page = users[start:end]
        
        self.table_users.setRowCount(len(page))
        for i, u in enumerate(page):
            self._fill_user_row(i, u)
        
        self._update_pagination_users(start, min(end, total))
    
    def _fill_user_row(self, row, u):
        id_item = QTableWidgetItem(str(u.get('id', '')))
        id_item.setData(Qt.UserRole, u)
        self.table_users.setItem(row, 0, id_item)
        
        un = QTableWidgetItem(u.get('username', ''))
        un.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        un.setForeground(QColor("#2563eb"))
        self.table_users.setItem(row, 1, un)
        
        nom = u.get('nom_complet') or f"{u.get('prenom', '')} {u.get('nom', '')}".strip() or "—"
        self.table_users.setItem(row, 2, QTableWidgetItem(nom))
        self.table_users.setItem(row, 3, QTableWidgetItem(u.get('email', '') or '—'))
        
        roles = u.get('roles', [])
        if isinstance(roles, list):
            rs = ", ".join([
                r.get('libelle', r) if isinstance(r, dict) else str(r)
                for r in roles
            ]) or "—"
        else:
            rs = str(roles) or "—"
        self.table_users.setItem(row, 4, QTableWidgetItem(rs))
        
        ab = StatusBadge(_safe_bool(u.get('est_actif', True)))
        ac = self._badge_container(ab)
        self.table_users.setCellWidget(row, 5, ac)
        
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(32, 28)
        btn.setIcon(qta.icon('fa5s.ellipsis-h', color='#64748b'))
        btn.setIconSize(QSize(14, 14))
        btn.setStyleSheet(self._action_btn_style())
        btn.clicked.connect(lambda c=False, ux=u, b=btn: self._show_user_actions_menu(ux, b))
        
        cont = QWidget()
        cl = QHBoxLayout(cont)
        cl.setContentsMargins(4, 6, 4, 6)
        cl.setAlignment(Qt.AlignCenter)
        cl.addWidget(btn)
        self.table_users.setCellWidget(row, 6, cont)
    
    def _load_matrix_roles(self):
        try:
            current = self.combo_role_matrix.currentData()
            self.combo_role_matrix.blockSignals(True)
            self.combo_role_matrix.clear()
            for r in self._all_roles:
                self.combo_role_matrix.addItem(
                    r.get('libelle', r.get('code', '')),
                    r.get('code')
                )
            if current:
                idx = self.combo_role_matrix.findData(current)
                if idx >= 0:
                    self.combo_role_matrix.setCurrentIndex(idx)
            self.combo_role_matrix.blockSignals(False)
            if self.combo_role_matrix.count() > 0:
                self._load_matrix()
        except Exception as e:
            print(f"Erreur load matrix roles: {e}")
    
    def _update_stats(self):
        total = len(self._all_roles)
        sys_count = sum(1 for r in self._all_roles if _safe_bool(r.get('est_systeme')))
        users = len(self._all_users)
        perms = sum(len(r.get('permissions', []) or []) for r in self._all_roles)
        
        for card, val in [
            (self.card_roles, total),
            (self.card_systeme, sys_count),
            (self.card_users, users),
            (self.card_perms, perms),
        ]:
            for lbl in card.findChildren(QLabel):
                if lbl.objectName() == "stat_value":
                    lbl.setText(str(val))
    
    # ═══════════════════════════════════════════════════════════════
    # MATRICE
    # ═══════════════════════════════════════════════════════════════
    
    # def _load_matrix(self):
    #     while self.matrix_layout.count():
    #         item = self.matrix_layout.takeAt(0)
    #         if item.widget():
    #             item.widget().deleteLater()
        
    #     role_code = self.combo_role_matrix.currentData()
    #     if not role_code:
    #         return
        
    #     role = next((r for r in self._all_roles if r.get('code') == role_code), None)
    #     if not role:
    #         return
        
    #     role_perms = {}
    #     for p in role.get('permissions', []) or []:
    #         if isinstance(p, dict):
    #             res = p.get('ressource')
    #             act = p.get('action')
    #             if res and act:
    #                 role_perms.setdefault(res, set()).add(act)
        
    #     self._matrix_checkboxes = {}
        
    #     header_lbl = QLabel("Ressource")
    #     header_lbl.setStyleSheet("font-weight: 700; font-size: 12px; color: #475569; padding: 8px;")
    #     self.matrix_layout.addWidget(header_lbl, 0, 0)
        
    #     actions = ['CREATE', 'READ', 'UPDATE', 'DELETE', 'VALIDATE', 'PAY', 'CLOSE']
    #     for j, action in enumerate(actions, 1):
    #         l = QLabel(action)
    #         l.setAlignment(Qt.AlignCenter)
    #         l.setStyleSheet("""
    #             font-weight: 700;
    #             font-size: 11px;
    #             color: #475569;
    #             padding: 8px 4px;
    #             background: #f8fafc;
    #             border-radius: 6px;
    #         """)
    #         self.matrix_layout.addWidget(l, 0, j)
        
    #     # ✅ Ressources avec icônes FontAwesome
    #     resources = [
    #         ('sinistre', 'fa5s.file-alt', 'Sinistre', '#3b82f6'),
    #         ('dommage', 'fa5s.exclamation-triangle', 'Dommage', '#f59e0b'),
    #         ('tiers', 'fa5s.users', 'Tiers', '#8b5cf6'),
    #         ('expertise', 'fa5s.microscope', 'Expertise', '#06b6d4'),
    #         ('evaluation', 'fa5s.calculator', 'Évaluation', '#f59e0b'),
    #         ('provision', 'fa5s.box', 'Provision', '#a855f7'),
    #         ('reglement', 'fa5s.credit-card', 'Règlement', '#22c55e'),
    #         ('recours', 'fa5s.balance-scale', 'Recours', '#ef4444'),
    #         ('referentiel', 'fa5s.book', 'Référentiel', '#84cc16'),
    #         ('utilisateur', 'fa5s.user', 'Utilisateur', '#64748b'),
    #         ('role', 'fa5s.user-shield', 'Rôle', '#dc2626'),
    #     ]
        
    #     for i, (res, icon_name, label, color) in enumerate(resources, 1):
    #         # Container avec icône + texte
    #         l_widget = QWidget()
    #         l_layout = QHBoxLayout(l_widget)
    #         l_layout.setContentsMargins(8, 6, 8, 6)
    #         l_layout.setSpacing(8)
            
    #         icon_lbl = QLabel()
    #         icon_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(QSize(14, 14)))
    #         icon_lbl.setFixedSize(16, 16)
    #         l_layout.addWidget(icon_lbl)
            
    #         text_lbl = QLabel(label)
    #         text_lbl.setStyleSheet("font-size: 12px; color: #1e293b; font-weight: 600; background: transparent;")
    #         l_layout.addWidget(text_lbl)
    #         l_layout.addStretch()
            
    #         l_widget.setStyleSheet("""
    #             QWidget {
    #                 background: #f8fafc;
    #                 border-radius: 6px;
    #             }
    #         """)
            
    #         self.matrix_layout.addWidget(l_widget, i, 0)
            
    #         for j, action in enumerate(actions, 1):
    #             c = QWidget()
    #             cl = QHBoxLayout(c)
    #             cl.setContentsMargins(0, 0, 0, 0)
    #             cl.setAlignment(Qt.AlignCenter)
                
    #             check = QCheckBox()
    #             check.setChecked(action in role_perms.get(res, set()))
    #             check.setStyleSheet("""
    #                 QCheckBox::indicator {
    #                     width: 18px;
    #                     height: 18px;
    #                     border: 2px solid #cbd5e1;
    #                     border-radius: 4px;
    #                     background: white;
    #                 }
    #                 QCheckBox::indicator:hover { border-color: #3b82f6; }
    #                 QCheckBox::indicator:checked {
    #                     background: #2563eb;
    #                     border-color: #2563eb;
    #                 }
    #             """)
    #             cl.addWidget(check)
                
    #             self._matrix_checkboxes[(res, action)] = check
    #             self.matrix_layout.addWidget(c, i, j)
    
    def _load_matrix(self):
        """
        Charge la matrice des permissions de manière DYNAMIQUE.
        
        Lit les ressources et actions depuis `constants.py` pour garantir
        que toutes les permissions sont configurables.
        
        Design :
        - Fond neutre (#f8fafc) pour les lignes de ressources
        - Seule l'icône de la ressource est colorée
        - En-têtes d'actions avec icône + texte
        """
        # ─── Vider la matrice ───
        while self.matrix_layout.count():
            item = self.matrix_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Nettoyer les layouts imbriqués
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
        
        role_code = self.combo_role_matrix.currentData()
        if not role_code:
            return
        
        role = next((r for r in self._all_roles if r.get('code') == role_code), None)
        if not role:
            return
        
        # ─── Permissions actuelles du rôle ───
        role_perms = {}
        for p in role.get('permissions', []) or []:
            if isinstance(p, dict):
                res = p.get('ressource')
                act = p.get('action')
                if res and act:
                    role_perms.setdefault(res, set()).add(act)
        
        # ═══════════════════════════════════════════════════════════════
        # 1. CHARGER RESSOURCES ET ACTIONS DEPUIS constants.py
        # ═══════════════════════════════════════════════════════════════
        
        # Configuration d'affichage des ressources : icône, libellé, couleur
        RESOURCES_CONFIG = {
            'sinistre':        ('fa5s.file-alt',              'Sinistre',         '#3b82f6'),
            'dommage':         ('fa5s.exclamation-triangle',  'Dommage',          '#f59e0b'),
            'tiers':           ('fa5s.users',                 'Tiers',            '#8b5cf6'),
            'expertise':       ('fa5s.microscope',            'Expertise',        '#06b6d4'),
            'expert':          ('fa5s.user-tie',              'Expert',           '#7c3aed'),
            'avocat':          ('fa5s.gavel',                 'Avocat',           '#16a34a'),
            'evaluation':      ('fa5s.calculator',            'Évaluation',       '#f59e0b'),
            'provision':       ('fa5s.box',                   'Provision',        '#a855f7'),
            'reglement':       ('fa5s.credit-card',           'Règlement',        '#22c55e'),
            'recours':         ('fa5s.balance-scale',         'Recours',          '#ef4444'),
            'beneficiaire':    ('fa5s.user-tag',              'Bénéficiaire',     '#0891b2'),
            'banque':          ('fa5s.university',            'Banque',           '#2563eb'),
            'compte_bancaire': ('fa5s.piggy-bank',            'Compte bancaire',  '#059669'),
            'note_credit':     ('fa5s.file-invoice',          'Note de crédit',   '#dc2626'),
            'document':        ('fa5s.folder-open',           'Document',         '#0ea5e9'),
            'tache':           ('fa5s.tasks',                 'Tâche',            '#64748b'),
            'notification':    ('fa5s.bell',                  'Notification',     '#f59e0b'),
            'referentiel':     ('fa5s.book',                  'Référentiel',      '#84cc16'),
            'utilisateur':     ('fa5s.user',                  'Utilisateur',      '#64748b'),
            'role':            ('fa5s.user-shield',           'Rôle',             '#dc2626'),
            'ecriture':        ('fa5s.book-open',             'Écriture',         '#0891b2'),
            'comptabilite':    ('fa5s.calculator',            'Comptabilité',     '#0ea5e9'),
        }
        
        # Ordre logique d'affichage des ressources
        RESOURCES_ORDER = [
            'sinistre', 'dommage', 'tiers',
            'expertise', 'expert', 'avocat',
            'evaluation', 'provision',
            'reglement', 'beneficiaire', 'banque', 'compte_bancaire', 'note_credit',
            'recours',
            'ecriture', 'comptabilite',
            'document', 'tache', 'notification',
            'referentiel', 'utilisateur', 'role',
        ]
        
        # Icônes et couleurs des actions
        ACTIONS_CONFIG = {
            'CREATE':    ('fa5s.plus',          '#22c55e'),
            'READ':      ('fa5s.eye',           '#3b82f6'),
            'UPDATE':    ('fa5s.edit',          '#f59e0b'),
            'DELETE':    ('fa5s.trash',         '#ef4444'),
            'VALIDATE':  ('fa5s.check',         '#10b981'),
            'CANCEL':    ('fa5s.ban',           '#dc2626'),
            'RECONCILE': ('fa5s.check-double',  '#0891b2'),
            'EXPORT':    ('fa5s.download',      '#8b5cf6'),
            'PAY':       ('fa5s.credit-card',   '#22c55e'),
            'CLOSE':     ('fa5s.lock',          '#64748b'),
        }
        
        # Ordre logique d'affichage des actions
        ACTIONS_ORDER = [
            'CREATE', 'READ', 'UPDATE', 'DELETE',
            'VALIDATE', 'CANCEL', 'RECONCILE', 'EXPORT',
            'PAY', 'CLOSE',
        ]
        
        # ─── Lecture depuis constants.py ───
        try:
            from addons.sinistres.security.constants import Resources, Actions
            
            all_resources = getattr(Resources, 'ALL', [])
            all_actions = getattr(Actions, 'ALL', [])
            
            # Filtrer selon ce qui existe dans constants.py
            resources = [
                (r, *RESOURCES_CONFIG.get(r, ('fa5s.cube', r.capitalize(), '#64748b')))
                for r in RESOURCES_ORDER
                if r in all_resources
            ]
            actions = [a for a in ACTIONS_ORDER if a in all_actions]
            
            # Fallback si constants.py est vide
            if not resources:
                resources = [
                    (r, *RESOURCES_CONFIG.get(r, ('fa5s.cube', r.capitalize(), '#64748b')))
                    for r in RESOURCES_ORDER
                ]
            if not actions:
                actions = ACTIONS_ORDER
        
        except ImportError:
            # Fallback : configuration en dur
            print("⚠️ constants.py introuvable, utilisation de la config par défaut")
            resources = [
                (r, *RESOURCES_CONFIG.get(r, ('fa5s.cube', r.capitalize(), '#64748b')))
                for r in RESOURCES_ORDER
            ]
            actions = ACTIONS_ORDER
        
        # ═══════════════════════════════════════════════════════════════
        # 2. INITIALISER LE STOCKAGE DES CHECKBOXES
        # ═══════════════════════════════════════════════════════════════
        self._matrix_checkboxes = {}
        
        # ═══════════════════════════════════════════════════════════════
        # 3. CONSTRUIRE L'EN-TÊTE (ligne 0)
        # ═══════════════════════════════════════════════════════════════
        
        # ─── Colonne 0 : "Ressource" ───
        header_lbl = QLabel("Ressource")
        header_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_lbl.setStyleSheet("""
            QLabel {
                font-weight: 800;
                font-size: 12px;
                color: #475569;
                padding: 12px 10px;
                background: #f1f5f9;
                border-radius: 6px;
            }
        """)
        self.matrix_layout.addWidget(header_lbl, 0, 0)
        
        # ─── Colonnes 1..N : actions ───
        for j, action in enumerate(actions, 1):
            icon_name, color = ACTIONS_CONFIG.get(action, ('fa5s.dot-circle', '#64748b'))
            
            # Container avec icône + texte
            lbl_widget = QWidget()
            lbl_widget.setStyleSheet("""
                QWidget {
                    background: #f1f5f9;
                    border-radius: 6px;
                }
            """)
            lbl_layout = QVBoxLayout(lbl_widget)
            lbl_layout.setContentsMargins(4, 8, 4, 8)
            lbl_layout.setSpacing(4)
            lbl_layout.setAlignment(Qt.AlignCenter)
            
            # ✅ Icône colorée
            icon_lbl = QLabel()
            try:
                icon_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(QSize(16, 16)))
            except Exception:
                icon_lbl.setText("●")
                icon_lbl.setStyleSheet(f"color: {color}; font-size: 12px;")
            icon_lbl.setAlignment(Qt.AlignCenter)
            icon_lbl.setStyleSheet("background: transparent;")
            lbl_layout.addWidget(icon_lbl)
            
            # Texte neutre
            text_lbl = QLabel(action)
            text_lbl.setAlignment(Qt.AlignCenter)
            text_lbl.setStyleSheet("""
                font-weight: 700;
                font-size: 10px;
                color: #475569;
                background: transparent;
            """)
            lbl_layout.addWidget(text_lbl)
            
            self.matrix_layout.addWidget(lbl_widget, 0, j)
        
        # ═══════════════════════════════════════════════════════════════
        # 4. CONSTRUIRE LES LIGNES DE RESSOURCES (lignes 1..N)
        # ═══════════════════════════════════════════════════════════════
        
        for i, (res, icon_name, label, color) in enumerate(resources, 1):
            
            # ─── Colonne 0 : Ressource (fond NEUTRE, seule l'icône est colorée) ───
            res_widget = QWidget()
            res_widget.setStyleSheet("""
                QWidget {
                    background: #f8fafc;
                    border-radius: 6px;
                }
            """)
            res_layout = QHBoxLayout(res_widget)
            res_layout.setContentsMargins(10, 8, 10, 8)
            res_layout.setSpacing(8)
            
            # ✅ Icône : SEUL élément coloré de la ligne
            icon_lbl = QLabel()
            try:
                icon_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(QSize(16, 16)))
            except Exception:
                icon_lbl.setText("●")
                icon_lbl.setStyleSheet(f"color: {color}; font-size: 12px;")
            icon_lbl.setFixedSize(18, 18)
            icon_lbl.setStyleSheet("background: transparent;")
            icon_lbl.setAlignment(Qt.AlignCenter)
            res_layout.addWidget(icon_lbl)
            
            # Texte neutre
            text_lbl = QLabel(label)
            text_lbl.setStyleSheet("""
                font-size: 12px;
                color: #1e293b;
                font-weight: 600;
                background: transparent;
            """)
            res_layout.addWidget(text_lbl)
            res_layout.addStretch()
            
            self.matrix_layout.addWidget(res_widget, i, 0)
            
            # ─── Colonnes 1..N : cases à cocher ───
            for j, action in enumerate(actions, 1):
                # Le conteneur de la case a un fond neutre
                cell = QWidget()
                cell.setStyleSheet("""
                    QWidget {
                        background: #fafbfc;
                        border-radius: 6px;
                    }
                    QWidget:hover {
                        background: #f1f5f9;
                    }
                """)
                cell_layout = QHBoxLayout(cell)
                cell_layout.setContentsMargins(0, 0, 0, 0)
                cell_layout.setAlignment(Qt.AlignCenter)
                
                # ✅ La checkbox : la coche prend la couleur de la ressource
                check = QCheckBox()
                check.setChecked(action in role_perms.get(res, set()))
                check.setCursor(Qt.PointingHandCursor)
                check.setToolTip(f"{action} sur {label}")
                check.setStyleSheet(f"""
                    QCheckBox::indicator {{
                        width: 20px;
                        height: 20px;
                        border: 2px solid #cbd5e1;
                        border-radius: 5px;
                        background: white;
                    }}
                    QCheckBox::indicator:hover {{
                        border-color: {color};
                    }}
                    QCheckBox::indicator:checked {{
                        background: {color};
                        border-color: {color};
                    }}
                """)
                
                cell_layout.addWidget(check)
                
                # Stocker la référence
                self._matrix_checkboxes[(res, action)] = check
                
                self.matrix_layout.addWidget(cell, i, j)
        
        # ═══════════════════════════════════════════════════════════════
        # 5. AJUSTER LES LARGEURS DE COLONNES
        # ═══════════════════════════════════════════════════════════════
        
        # Colonne ressource : large (prend l'espace restant)
        self.matrix_layout.setColumnStretch(0, 1)
        
        # Colonnes actions : étroites et égales
        for j in range(1, len(actions) + 1):
            self.matrix_layout.setColumnStretch(j, 0)
            self.matrix_layout.setColumnMinimumWidth(j, 70)
        
        # ═══════════════════════════════════════════════════════════════
        # 6. AJOUTER UN COMPTEUR DE PERMISSIONS
        # ═══════════════════════════════════════════════════════════════
        
        total_perms = sum(len(v) for v in role_perms.values())
        total_possible = len(resources) * len(actions)
        pourcentage = (total_perms * 100 // total_possible) if total_possible > 0 else 0
        
        info_row = len(resources) + 1
        info_lbl = QLabel(
            f"📊 {total_perms} / {total_possible} permissions accordées ({pourcentage}%)"
        )
        info_lbl.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 11px;
                font-weight: 600;
                padding: 14px;
                background: #f8fafc;
                border-radius: 6px;
            }
        """)
        info_lbl.setAlignment(Qt.AlignCenter)
        self.matrix_layout.addWidget(info_lbl, info_row, 0, 1, len(actions) + 1)

    def _toggle_all_matrix(self, checked):
        if not hasattr(self, '_matrix_checkboxes'):
            return
        for cb in self._matrix_checkboxes.values():
            cb.setChecked(checked)
    
    def _save_matrix(self):
        role_code = self.combo_role_matrix.currentData()
        if not role_code:
            return
        
        perms = []
        if hasattr(self, '_matrix_checkboxes'):
            for (res, act), cb in self._matrix_checkboxes.items():
                if cb.isChecked():
                    perms.append({'ressource': res, 'action': act})
        
        try:
            if hasattr(self.controller, 'set_role_permissions'):
                self.controller.set_role_permissions(role_code, perms)
                QMessageBox.information(
                    self, "Succès",
                    f"✅ {len(perms)} permission(s) enregistrée(s)"
                )
                self._load_roles()
            else:
                QMessageBox.information(
                    self, "Info",
                    "Fonction 'set_role_permissions' à implémenter."
                )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _select_all_resources(self, checked: bool):
        """Coche/décoche toutes les cases de la matrice."""
        if not hasattr(self, '_matrix_checkboxes'):
            return
        for cb in self._matrix_checkboxes.values():
            cb.setChecked(checked)

    def _select_resource_row(self, resource: str, checked: bool):
        """Coche/décoche une ligne complète (toutes les actions d'une ressource)."""
        if not hasattr(self, '_matrix_checkboxes'):
            return
        for (res, act), cb in self._matrix_checkboxes.items():
            if res == resource:
                cb.setChecked(checked)

    def _select_action_column(self, action: str, checked: bool):
        """Coche/décoche une colonne complète (toutes les ressources pour une action)."""
        if not hasattr(self, '_matrix_checkboxes'):
            return
        for (res, act), cb in self._matrix_checkboxes.items():
            if act == action:
                cb.setChecked(checked)

    def _matrix_preset(self, preset: str):
        """Applique un preset de permissions (lecture seule, gestion complète, etc.)."""
        if not hasattr(self, '_matrix_checkboxes'):
            return
        
        presets = {
            'readonly': {
                'all': ['READ'],
            },
            'gestionnaire': {
                'all': ['CREATE', 'READ', 'UPDATE'],
                'role': [],
                'utilisateur': [],
                'ecriture': ['READ'],
                'comptabilite': ['READ'],
            },
            'comptable': {
                'all': ['READ'],
                'reglement': ['CREATE', 'READ', 'UPDATE', 'PAY'],
                'compte_bancaire': ['READ', 'UPDATE'],
                'note_credit': ['CREATE', 'READ', 'UPDATE'],
                'ecriture': ['CREATE', 'READ', 'UPDATE', 'VALIDATE', 'CANCEL', 'RECONCILE', 'EXPORT'],
                'comptabilite': ['READ', 'EXPORT'],
            },
            'admin': {
                'all': ['CREATE', 'READ', 'UPDATE', 'DELETE', 'VALIDATE', 'CANCEL', 'RECONCILE', 'EXPORT', 'PAY', 'CLOSE'],
            },
        }
        
        if preset not in presets:
            return
        
        config = presets[preset]
        default_actions = config.get('all', [])
        
        # D'abord, tout décocher
        for cb in self._matrix_checkboxes.values():
            cb.setChecked(False)
        
        # Puis cocher selon le preset
        for (res, act), cb in self._matrix_checkboxes.items():
            if act in config.get(res, default_actions):
                cb.setChecked(True)
        
        QMessageBox.information(
            self, "Preset appliqué",
            f"Le preset '{preset}' a été appliqué.\n\n"
            f"N'oubliez pas de cliquer sur 💾 Enregistrer pour sauvegarder."
        )
    
    # ═══════════════════════════════════════════════════════════════
    # MENU CONTEXTUEL RÔLES (avec icônes FontAwesome)
    # ═══════════════════════════════════════════════════════════════
    
    def _show_roles_context_menu(self, pos):
        row = self.table_roles.currentRow()
        if row < 0:
            menu = QMenu(self)
            menu.setStyleSheet(self._menu_style())
            a = menu.addAction(
                qta.icon('fa5s.sync-alt', color='#64748b'),
                "  Actualiser"
            )
            a.triggered.connect(self.refresh)
            menu.exec(self.table_roles.viewport().mapToGlobal(pos))
            return
        
        item = self.table_roles.item(row, 0)
        if not item:
            return
        role = item.data(Qt.UserRole)
        if role:
            self._build_role_menu(role, self.table_roles.viewport().mapToGlobal(pos))
    
    def _show_row_actions_menu(self, role, button):
        self._build_role_menu(role, button.mapToGlobal(button.rect().bottomLeft()))
    
    def _build_role_menu(self, role, pos):
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        code = role.get('code', 'N/A')
        sys_role = _safe_bool(role.get('est_systeme'))
        actif = _safe_bool(role.get('est_actif'))
        
        # ✅ Voir les détails
        a_detail = menu.addAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails"
        )
        a_detail.triggered.connect(lambda: self._show_role_detail(role))
        
        # ✅ Éditer les permissions
        a_matrix = menu.addAction(
            qta.icon('fa5s.key', color='#f59e0b'),
            "  Éditer les permissions"
        )
        a_matrix.triggered.connect(lambda: self._goto_matrix(code))
        
        menu.addSeparator()
        
        # ✅ Modifier
        a_edit = menu.addAction(
            qta.icon('fa5s.edit', color='#f59e0b'),
            "  Modifier"
        )
        a_edit.triggered.connect(lambda: self._edit_from_menu(role))
        
        # ✅ Activer/Désactiver
        if actif:
            a_deact = menu.addAction(
                qta.icon('fa5s.ban', color='#ef4444'),
                "  Désactiver"
            )
            a_deact.setEnabled(not sys_role)
            a_deact.triggered.connect(lambda: self._deactivate_role(role))
        else:
            a_act = menu.addAction(
                qta.icon('fa5s.check', color='#22c55e'),
                "  Réactiver"
            )
            a_act.triggered.connect(lambda: self._activate_role(role))
        
        menu.addSeparator()
        
        # ✅ Dupliquer
        a_dup = menu.addAction(
            qta.icon('fa5s.copy', color='#8b5cf6'),
            "  Dupliquer"
        )
        a_dup.triggered.connect(lambda: self._duplicate_role(role))
        
        # ✅ Supprimer
        if not sys_role:
            a_del = menu.addAction(
                qta.icon('fa5s.trash-alt', color='#ef4444'),
                "  Supprimer"
            )
            a_del.triggered.connect(lambda: self._delete_role(role))
        
        menu.addSeparator()
        
        # ✅ Copier
        a_copy = menu.addAction(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier le code"
        )
        a_copy.triggered.connect(lambda: self._copy_to_clipboard(code))
        
        menu.exec(pos)
    
    # ═══════════════════════════════════════════════════════════════
    # MENU CONTEXTUEL USERS
    # ═══════════════════════════════════════════════════════════════
    
    def _show_users_context_menu(self, pos):
        row = self.table_users.currentRow()
        if row < 0:
            return
        item = self.table_users.item(row, 0)
        if not item:
            return
        u = item.data(Qt.UserRole)
        if u:
            self._build_user_menu(u, self.table_users.viewport().mapToGlobal(pos))
    
    def _show_user_actions_menu(self, u, button):
        self._build_user_menu(u, button.mapToGlobal(button.rect().bottomLeft()))
    
    def _build_user_menu(self, u, pos):
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        # ✅ Voir les détails
        a_detail = menu.addAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails"
        )
        a_detail.triggered.connect(lambda: self._show_user_detail(u))
        
        menu.addSeparator()
        
        # ✅ Gérer les rôles
        a_roles = menu.addAction(
            qta.icon('fa5s.user-tag', color='#8b5cf6'),
            "  Gérer les rôles"
        )
        a_roles.triggered.connect(lambda: self._manage_user_roles(u))
        
        # ✅ Réinitialiser mot de passe
        a_reset = menu.addAction(
            qta.icon('fa5s.key', color='#f59e0b'),
            "  Réinitialiser mot de passe"
        )
        a_reset.triggered.connect(lambda: self._reset_user_password(u))
        
        menu.addSeparator()
        
        # ✅ Activer/Désactiver compte
        actif = _safe_bool(u.get('est_actif', True))
        if actif:
            a_d = menu.addAction(
                qta.icon('fa5s.user-slash', color='#ef4444'),
                "  Désactiver le compte"
            )
            a_d.triggered.connect(lambda: self._toggle_user(u, False))
        else:
            a_a = menu.addAction(
                qta.icon('fa5s.user-check', color='#22c55e'),
                "  Activer le compte"
            )
            a_a.triggered.connect(lambda: self._toggle_user(u, True))
        
        menu.addSeparator()
        
        # ✅ Copier username
        a_copy = menu.addAction(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier le username"
        )
        a_copy.triggered.connect(lambda: self._copy_to_clipboard(u.get('username', '')))
        
        menu.exec(pos)
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS RÔLES (inchangées)
    # ═══════════════════════════════════════════════════════════════
    
    def _show_role_detail(self, role):
        perms = role.get('permissions', []) or []
        pl = "\n".join([
            f"  • {p.get('ressource', '?')}.{p.get('action', '?')}"
            if isinstance(p, dict) else f"  • {p}"
            for p in perms[:15]
        ]) or "  Aucune"
        if len(perms) > 15:
            pl += f"\n  ... +{len(perms) - 15} autres"
        
        QMessageBox.information(
            self, f"Rôle {role.get('code', 'N/A')}",
            f"<b>Code :</b> {role.get('code', 'N/A')}<br>"
            f"<b>Libellé :</b> {role.get('libelle', 'N/A')}<br>"
            f"<b>Description :</b> {role.get('description', '—') or '—'}<br>"
            f"<b>Niveau :</b> {role.get('niveau', 0)}/100<br>"
            f"<b>Type :</b> {'Système' if _safe_bool(role.get('est_systeme')) else 'Personnalisé'}<br>"
            f"<b>Statut :</b> {'✅ Actif' if _safe_bool(role.get('est_actif')) else '❌ Inactif'}<br><br>"
            f"<b>Permissions ({len(perms)}) :</b><br>{pl}"
        )
    
    def _goto_matrix(self, role_code):
        self.tabs.setCurrentIndex(2)
        idx = self.combo_role_matrix.findData(role_code)
        if idx >= 0:
            self.combo_role_matrix.setCurrentIndex(idx)
    
    def _edit_from_menu(self, role):
        for i in range(self.table_roles.rowCount()):
            item = self.table_roles.item(i, 0)
            if item and item.text() == role.get('code'):
                self.table_roles.selectRow(i)
                break
        self._edit_role(role)
    
    def _edit_role(self, role):
        d = RoleDialog(role_data=role, parent=self)
        d.role_saved.connect(lambda data: self._save_role(data, True))
        d.exec()
    
    def _save_role(self, data, is_edit):
        try:
            if is_edit:
                if hasattr(self.controller, 'update_role'):
                    self.controller.update_role(data['id'], data)
                else:
                    QMessageBox.information(self, "Info", "Fonction 'update_role' à implémenter.")
                    return
            else:
                if hasattr(self.controller, 'create_role'):
                    self.controller.create_role(data)
                else:
                    QMessageBox.information(self, "Info", "Fonction 'create_role' à implémenter.")
                    return
            QMessageBox.information(self, "Succès", f"Rôle {data['code']} enregistré")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _deactivate_role(self, role):
        if _safe_bool(role.get('est_systeme')):
            QMessageBox.warning(self, "Attention", "Les rôles système ne peuvent être désactivés.")
            return
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Désactiver le rôle {role.get('code')} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            if hasattr(self.controller, 'deactivate_role'):
                self.controller.deactivate_role(role.get('id'))
                QMessageBox.information(self, "Succès", "Rôle désactivé")
                self.refresh()
            else:
                QMessageBox.information(self, "Info", "Fonction 'deactivate_role' à implémenter.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _activate_role(self, role):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Réactiver le rôle {role.get('code')} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            if hasattr(self.controller, 'activate_role'):
                self.controller.activate_role(role.get('id'))
                QMessageBox.information(self, "Succès", "Rôle réactivé")
                self.refresh()
            else:
                QMessageBox.information(self, "Info", "Fonction 'activate_role' à implémenter.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _duplicate_role(self, role):
        new_code, ok = QInputDialog.getText(
            self, "Dupliquer", "Code du nouveau rôle :",
            text=f"{role.get('code', '')}_COPY"
        )
        if not ok or not new_code.strip():
            return
        new_lib, ok2 = QInputDialog.getText(
            self, "Dupliquer", "Libellé :",
            text=f"{role.get('libelle', '')} (copie)"
        )
        if not ok2 or not new_lib.strip():
            return
        data = {
            'code': new_code.strip().upper(),
            'libelle': new_lib.strip(),
            'description': role.get('description'),
            'niveau': role.get('niveau', 50),
            'est_systeme': False,
            'permissions': role.get('permissions', []) or [],
        }
        try:
            if hasattr(self.controller, 'create_role'):
                self.controller.create_role(data)
                QMessageBox.information(
                    self, "Succès",
                    f"Rôle {data['code']} créé avec {len(data['permissions'])} permission(s)"
                )
                self.refresh()
            else:
                QMessageBox.information(self, "Info", "Fonction 'create_role' à implémenter.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _delete_role(self, role):
        if _safe_bool(role.get('est_systeme')):
            QMessageBox.warning(self, "Attention", "Les rôles système ne peuvent être supprimés.")
            return
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Supprimer le rôle {role.get('code')} ?\n\nAction irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            if hasattr(self.controller, 'delete_role'):
                self.controller.delete_role(role.get('id'))
                QMessageBox.information(self, "Succès", "Rôle supprimé")
                self.refresh()
            else:
                QMessageBox.information(self, "Info", "Fonction 'delete_role' à implémenter.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS USERS (inchangées)
    # ═══════════════════════════════════════════════════════════════
    
    def _show_user_detail(self, u):
        roles = u.get('roles', [])
        if isinstance(roles, list):
            rs = ", ".join([
                r.get('libelle', '') if isinstance(r, dict) else str(r)
                for r in roles
            ]) or "—"
        else:
            rs = str(roles)
        QMessageBox.information(
            self, f"Utilisateur {u.get('username', 'N/A')}",
            f"<b>Username :</b> {u.get('username', 'N/A')}<br>"
            f"<b>Nom complet :</b> {u.get('nom_complet', '—')}<br>"
            f"<b>Email :</b> {u.get('email', '—') or '—'}<br>"
            f"<b>Rôles :</b> {rs}<br>"
            f"<b>Statut :</b> {'✅ Actif' if _safe_bool(u.get('est_actif', True)) else '❌ Inactif'}"
        )
    
    def _manage_user_roles(self, u: dict):
        if not self._all_roles:
            QMessageBox.warning(
                self, "Attention",
                "Aucun rôle disponible. Créez d'abord des rôles."
            )
            return
        
        dialog = ManageUserRolesDialog(
            user_data=u,
            all_roles=self._all_roles,
            controller=self.controller,
            parent=self,
        )
        dialog.roles_saved.connect(self._on_user_roles_saved)
        dialog.exec()
    
    def _on_user_roles_saved(self, user_id: int, selected_codes: list):
        try:
            user = next((x for x in self._all_users if x.get('id') == user_id), None)
            if not user:
                QMessageBox.warning(self, "Erreur", "Utilisateur introuvable")
                return
            
            current_codes = set()
            for r in user.get('roles', []) or []:
                if isinstance(r, dict):
                    code = r.get('code')
                    if code:
                        current_codes.add(code)
                else:
                    current_codes.add(str(r))
            
            selected_set = set(selected_codes)
            
            to_add = selected_set - current_codes
            to_remove = current_codes - selected_set
            
            if not to_add and not to_remove:
                QMessageBox.information(self, "Info", "Aucun changement")
                return
            
            has_assign = hasattr(self.controller, 'assign_role')
            has_revoke = hasattr(self.controller, 'revoke_role')
            
            if not has_assign or not has_revoke:
                QMessageBox.warning(
                    self, "Erreur",
                    "Les méthodes assign_role / revoke_role ne sont pas disponibles "
                    "dans le contrôleur."
                )
                return
            
            errors = []
            added = 0
            removed = 0
            
            for code in to_add:
                try:
                    ok = self.controller.assign_role(user_id, code)
                    if ok:
                        added += 1
                    else:
                        errors.append(f"Ajout {code} : échec")
                except Exception as e:
                    errors.append(f"Ajout {code} : {e}")
            
            for code in to_remove:
                try:
                    ok = self.controller.revoke_role(user_id, code)
                    if ok:
                        removed += 1
                    else:
                        errors.append(f"Retrait {code} : échec")
                except Exception as e:
                    errors.append(f"Retrait {code} : {e}")
            
            parts = []
            if added: parts.append(f"✅ {added} rôle(s) ajouté(s)")
            if removed: parts.append(f"🗑️ {removed} rôle(s) retiré(s)")
            msg = "\n".join(parts) or "Aucun changement"
            
            if errors:
                msg += "\n\n⚠️ Erreurs :\n" + "\n".join(errors[:5])
                QMessageBox.warning(self, "Partiellement appliqué", msg)
            else:
                QMessageBox.information(self, "Succès", msg)
            
            self.refresh()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _reset_user_password(self, u):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Réinitialiser le mot de passe de {u.get('username')} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            if hasattr(self.controller, 'reset_user_password'):
                pwd = self.controller.reset_user_password(u.get('id'))
                QMessageBox.information(
                    self, "Mot de passe réinitialisé",
                    f"<b>Nouveau mot de passe :</b><br><br>{pwd}<br><br>"
                    f"⚠️ Communiquez-le de manière sécurisée."
                )
            else:
                QMessageBox.information(self, "Info", "Fonction à implémenter.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _toggle_user(self, u, active):
        action = "activer" if active else "désactiver"
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous {action} le compte de {u.get('username')} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            if hasattr(self.controller, 'toggle_user_active'):
                self.controller.toggle_user_active(u.get('id'), active)
                QMessageBox.information(self, "Succès", f"Compte {action}é")
                self.refresh()
            else:
                QMessageBox.information(self, "Info", "Fonction à implémenter.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    # ═══════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════
    
    def _creer_role(self):
        d = RoleDialog(role_data=None, parent=self)
        d.role_saved.connect(lambda data: self._save_role(data, False))
        d.exec()
    
    def _on_role_selection(self):
        pass
    
    def _on_role_dbl_click(self, row, col):
        if col == 6:
            return
        item = self.table_roles.item(row, 0)
        if item:
            role = item.data(Qt.UserRole)
            if role:
                self._edit_role(role)
    
    def _on_role_search(self, text):
        self._current_page = 1
        self._process_roles()
    
    def _on_role_filter(self, text):
        self._current_page = 1
        self._process_roles()
    
    def _on_user_search(self, text):
        self._user_current_page = 1
        self._process_users()
    
    def _on_tab_changed(self, index):
        if index == 2:
            self._load_matrix_roles()
    
    def _update_pagination_roles(self, start, end):
        if self._filtered_roles:
            self.lbl_pagination.setText(
                f"{start + 1}-{end} de {len(self._filtered_roles)}"
            )
        else:
            self.lbl_pagination.setText("0-0 de 0")
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(end < len(self._filtered_roles))
    
    def _go_prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self._process_roles()
    
    def _go_next_page(self):
        if self._current_page * self._per_page < len(self._filtered_roles):
            self._current_page += 1
            self._process_roles()
    
    def _update_pagination_users(self, start, end):
        if self._filtered_users:
            self.lbl_pagination_users.setText(
                f"{start + 1}-{end} de {len(self._filtered_users)}"
            )
        else:
            self.lbl_pagination_users.setText("0-0 de 0")
        self.btn_prev_users.setEnabled(self._user_current_page > 1)
        self.btn_next_users.setEnabled(end < len(self._filtered_users))
    
    def _go_prev_page_users(self):
        if self._user_current_page > 1:
            self._user_current_page -= 1
            self._process_users()
    
    def _go_next_page_users(self):
        if self._user_current_page * self._user_per_page < len(self._filtered_users):
            self._user_current_page += 1
            self._process_users()
    
    def _copy_to_clipboard(self, text):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(str(text))
        QMessageBox.information(self, "Copié", f"'{text}' copié")
    
    def _export_data(self, kind):
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        if kind == "roles":
            data = self._all_roles
            headers = ["Code", "Libellé", "Description", "Niveau", "Système", "Actif", "Nb Permissions"]
            rows = [[
                r.get('code', ''), r.get('libelle', ''),
                r.get('description', '') or '',
                r.get('niveau', 0),
                'Oui' if _safe_bool(r.get('est_systeme')) else 'Non',
                'Oui' if _safe_bool(r.get('est_actif')) else 'Non',
                len(r.get('permissions', []) or []),
            ] for r in data]
            fname = f"roles_{datetime.now().strftime('%Y%m%d')}.csv"
        else:
            return
        
        if not data:
            QMessageBox.warning(self, "Export", "Aucune donnée")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Exporter", fname, "CSV (*.csv)")
        if not path:
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(headers)
                w.writerows(rows)
            QMessageBox.information(self, "Export réussi", f"{len(rows)} lignes")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    def refresh(self):
        self.load_data()