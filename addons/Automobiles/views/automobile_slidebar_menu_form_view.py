# automobile_slidebar_menu_form_view.py

import os
import re
from datetime import date, datetime, timedelta
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QListWidget, QListWidgetItem, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QProgressBar, QLabel, QLineEdit, 
    QComboBox, QPushButton, QFrame, QGraphicsDropShadowEffect, 
    QWidget, QScrollArea, QTextEdit, QDateEdit, QMessageBox, 
    QApplication, QGroupBox, QSplitter, QTabWidget, QFormLayout, QStackedWidget,
    QSpinBox, QDoubleSpinBox, QButtonGroup, QRadioButton, QSizePolicy
)
from PySide6.QtCore import QSize, Qt, Signal, QDate, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QPixmap, QFont, QLinearGradient, QBrush

from icons.icons import get_icon, get_icon_pixmap


class SlideMenu(QWidget):
    """
    Barre latérale complète pour le formulaire véhicule
    Fonctionnalités :
    - Menu burger pour étendre/réduire
    - Barre de progression globale (remplissage des sections)
    - Boutons de navigation avec icônes
    - Bouton Enregistrer avec barre de progression
    - Bouton Annuler
    - Animation fluide
    - Thème sombre
    """
    
    section_changed = Signal(int)
    toggled = Signal(bool)
    save_clicked = Signal()
    cancel_clicked = Signal()

    EXPANDED_WIDTH = 280
    COLLAPSED_WIDTH = 72

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._buttons = []
        self._current_index = 0
        self._animations = []
        self._collapsed = False
        self._section_widgets = {}
        self._total_sections = 0
        self._completed_sections = 0
        
        self.setObjectName("SlideMenu")
        self.setFixedWidth(self.EXPANDED_WIDTH)
        self.setMinimumHeight(500)
        
        # ✅ Style complet - thème sombre
        self.setStyleSheet("""
            QWidget#SlideMenu {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a,
                    stop:0.5 #1a1a2e,
                    stop:1 #16213e
                );
                border: none;
                border-right: 1px solid rgba(255,255,255,0.05);
                margin: 0px;
                padding: 0px;
            }
            QPushButton#MenuBtn {
                color: #94a3b8;
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 10px 14px;
                text-align: left;
                font-size: 13px;
                margin: 2px 8px;
                font-weight: 500;
            }
            QPushButton#MenuBtn:hover {
                background: rgba(255,255,255,0.06);
                color: #e2e8f0;
            }
            QPushButton#MenuBtn:checked {
                background: #3b82f6;
                color: white;
            }
            QPushButton#MenuBtn:checked:hover {
                background: #3b82f6;
            }
            QPushButton#SaveBtn {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6,
                    stop:1 #6366f1
                );
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 13px;
                font-weight: 600;
                margin: 4px 12px;
            }
            QPushButton#SaveBtn:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb,
                    stop:1 #4f46e5
                );
            }
            QPushButton#SaveBtn:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1d4ed8,
                    stop:1 #4338ca
                );
            }
            QPushButton#SaveBtn:disabled {
                background: #475569;
                color: #94a3b8;
            }
            QPushButton#CancelBtn {
                background: transparent;
                color: #94a3b8;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 12px;
                font-weight: 500;
                margin: 2px 12px 8px 12px;
            }
            QPushButton#CancelBtn:hover {
                background: rgba(239, 68, 68, 0.1);
                color: #fca5a5;
                border-color: rgba(239, 68, 68, 0.3);
            }
            QPushButton#CancelBtn:pressed {
                background: rgba(239, 68, 68, 0.2);
            }
            QProgressBar#SaveProgress {
                border: none;
                border-radius: 4px;
                background-color: rgba(255,255,255,0.08);
                height: 4px;
                max-height: 4px;
                margin: 0px 12px 6px 12px;
            }
            QProgressBar#SaveProgress::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6,
                    stop:1 #8b5cf6
                );
                border-radius: 4px;
            }
            QLabel#TitleLabel {
                color: #f8fafc;
                font-size: 18px;
                font-weight: 700;
                background: transparent;
                letter-spacing: 0.5px;
            }
            QLabel#SubtitleLabel {
                color: #94a3b8;
                font-size: 12px;
                background: transparent;
            }
            QLabel#ProgressTitle {
                color: #94a3b8;
                font-size: 11px;
                font-weight: 600;
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QLabel#ProgressText {
                color: #64748b;
                font-size: 11px;
                background: transparent;
            }
            QLabel#ProgressPercent {
                color: #8b5cf6;
                font-size: 14px;
                font-weight: 700;
                background: transparent;
            }
        """)
        
        # ✅ Animations
        self.width_animation = QPropertyAnimation(self, b"fixedWidth")
        self.width_animation.setDuration(350)
        self.width_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        self._progress_animation = None
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ========== EN-TÊTE ==========
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.02);
                border-bottom: 1px solid rgba(255,255,255,0.06);
                padding: 16px 16px 12px 16px;
            }
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(2)
        
        # Ligne 1: Burger + Titre
        header_top = QHBoxLayout()
        header_top.setSpacing(10)
        
        # Burger button
        self.burger_btn = QPushButton()
        self.burger_btn.setFixedSize(38, 38)
        self.burger_btn.setCursor(Qt.PointingHandCursor)
        self.burger_btn.setIcon(get_icon('menu', color="#94a3b8", size=20))
        self.burger_btn.setIconSize(QSize(20, 20))
        self.burger_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.10);
            }
        """)
        self.burger_btn.clicked.connect(self.toggle)
        header_top.addWidget(self.burger_btn)
        
        # Titre
        title_label = QLabel("AutoAssure")
        title_label.setObjectName("TitleLabel")
        header_top.addWidget(title_label)
        header_top.addStretch()
        
        header_layout.addLayout(header_top)
        
        # Sous-titre
        subtitle = QLabel("Saisie de dossier")
        subtitle.setObjectName("SubtitleLabel")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)

        # ========== BARRE DE PROGRESSION GLOBALE ==========
        progress_container = QFrame()
        progress_container.setStyleSheet("""
            QFrame {
                background: transparent;
                padding: 14px 16px 16px 16px;
                border-bottom: 1px solid rgba(255,255,255,0.06);
            }
        """)
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setSpacing(8)
        
        # Ligne: "PROGRESSION GLOBALE" + "X/6 sections"
        progress_header = QHBoxLayout()
        
        progress_title = QLabel("PROGRESSION GLOBALE")
        progress_title.setObjectName("ProgressTitle")
        progress_header.addWidget(progress_title)
        progress_header.addStretch()
        
        self.progress_text = QLabel("0/6 sections complétées")
        self.progress_text.setObjectName("ProgressText")
        progress_header.addWidget(self.progress_text)
        
        progress_layout.addLayout(progress_header)
        
        # Barre de progression
        progress_bar_bg = QFrame()
        progress_bar_bg.setFixedHeight(6)
        progress_bar_bg.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.06);
                border-radius: 3px;
            }
        """)
        progress_bar_bg.setMinimumWidth(100)
        
        self.progress_bar_fill = QFrame()
        self.progress_bar_fill.setFixedHeight(6)
        self.progress_bar_fill.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:0.5 #6366f1, stop:1 #8b5cf6);
                border-radius: 3px;
                max-width: 100%;
            }
        """)
        self.progress_bar_fill.setFixedWidth(0)
        
        progress_bar_layout = QHBoxLayout(progress_bar_bg)
        progress_bar_layout.setContentsMargins(0, 0, 0, 0)
        progress_bar_layout.addWidget(self.progress_bar_fill)
        
        progress_layout.addWidget(progress_bar_bg)
        
        # Pourcentage
        self.progress_percent = QLabel("0%")
        self.progress_percent.setObjectName("ProgressPercent")
        self.progress_percent.setAlignment(Qt.AlignRight)
        progress_layout.addWidget(self.progress_percent)
        
        layout.addWidget(progress_container)

        # ========== BOUTONS DE NAVIGATION ==========
        self.button_container = QVBoxLayout()
        self.button_container.setSpacing(2)
        self.button_container.setContentsMargins(8, 12, 8, 8)
        layout.addLayout(self.button_container)
        
        layout.addStretch()

        # ========== ZONE ENREGISTREMENT ==========
        save_container = QFrame()
        save_container.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.02);
                border-top: 1px solid rgba(255,255,255,0.06);
                padding: 8px 0px 12px 0px;
            }
        """)
        save_layout = QVBoxLayout(save_container)
        save_layout.setSpacing(6)
        save_layout.setContentsMargins(0, 8, 0, 8)

        # ✅ Barre de progression d'enregistrement
        self.save_progress = QProgressBar()
        self.save_progress.setObjectName("SaveProgress")
        self.save_progress.setRange(0, 100)
        self.save_progress.setValue(0)
        self.save_progress.setTextVisible(False)
        self.save_progress.setVisible(False)
        save_layout.addWidget(self.save_progress)

        # ✅ Bouton Enregistrer
        self.save_btn = QPushButton()
        self.save_btn.setObjectName("SaveBtn")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setIcon(get_icon('save', color='white', size=16))
        self.save_btn.setIconSize(QSize(16, 16))
        self.save_btn.setText("  ENREGISTRER")
        self.save_btn.setFixedHeight(42)
        self.save_btn.clicked.connect(self.save_clicked.emit)
        save_layout.addWidget(self.save_btn)

        # ✅ Bouton Annuler
        self.cancel_btn = QPushButton()
        self.cancel_btn.setObjectName("CancelBtn")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setText("Annuler la saisie")
        self.cancel_btn.setFixedHeight(36)
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)
        save_layout.addWidget(self.cancel_btn)

        layout.addWidget(save_container)

    def add_section(self, label, widget=None, icon_name='file-document'):
        """Ajoute une section au menu avec style checkbox et icône"""
        btn = QPushButton()
        btn.setObjectName("MenuBtn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(38)
        btn.setCheckable(True)
        btn.setToolTip(label)
        
        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(12, 0, 12, 0)
        btn_layout.setSpacing(10)
        
        # ✅ Checkbox style (carré vide ou cochée)
        checkbox_indicator = QLabel()
        checkbox_indicator.setObjectName("checkbox_indicator")
        checkbox_indicator.setFixedSize(18, 18)
        checkbox_indicator.setAlignment(Qt.AlignCenter)
        checkbox_indicator.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.05);
                border: 2px solid rgba(255,255,255,0.15);
                border-radius: 4px;
                font-size: 12px;
                color: transparent;
            }
        """)
        btn_layout.addWidget(checkbox_indicator)
        
        # ✅ Icône
        icon_label = QLabel()
        icon_label.setObjectName("icon_label")
        icon_pix = get_icon_pixmap(icon_name, color='#94a3b8', size=16)
        if icon_pix:
            icon_label.setPixmap(icon_pix)
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")
        btn_layout.addWidget(icon_label)
        
        # ✅ Texte
        text_label = QLabel(label)
        text_label.setObjectName("text_label")
        text_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 500;
            background: transparent;
            color: #94a3b8;
        """)
        btn_layout.addWidget(text_label)
        btn_layout.addStretch()
        
        # Stocker les références
        btn._checkbox_indicator = checkbox_indicator
        btn._icon_label = icon_label
        btn._text_label = text_label
        btn._section_index = len(self._buttons)
        btn._section_widget = widget
        btn._completed = False
        btn._icon_name = icon_name
        btn._label = label
        
        btn.clicked.connect(lambda checked, idx=len(self._buttons): self._on_button_clicked(idx))
        
        self.button_container.addWidget(btn)
        self._buttons.append(btn)
        
        if widget:
            self._section_widgets[label] = widget
        
        if len(self._buttons) == 1:
            btn.setChecked(True)
            self._update_button_style(btn, True)
        
        self._total_sections = len(self._buttons)
        self._animate_button_enter(btn)
        self.update_progress()
        
        return btn

    def _update_button_style(self, btn, is_active):
        """Met à jour le style du bouton"""
        icon_color = '#3b82f6' if is_active else '#94a3b8'
        text_color = '#f1f5f9' if is_active else '#94a3b8'
        
        # Checkbox
        if btn._completed:
            btn._checkbox_indicator.setStyleSheet("""
                QLabel {
                    background: #10b981;
                    border: 2px solid #10b981;
                    border-radius: 4px;
                    color: white;
                    font-size: 12px;
                }
            """)
            btn._checkbox_indicator.setText("✓")
        else:
            btn._checkbox_indicator.setStyleSheet(f"""
                QLabel {{
                    background: {'rgba(59, 130, 246, 0.15)' if is_active else 'rgba(255,255,255,0.05)'};
                    border: 2px solid {'#3b82f6' if is_active else 'rgba(255,255,255,0.15)'};
                    border-radius: 4px;
                    font-size: 12px;
                    color: transparent;
                }}
            """)
            btn._checkbox_indicator.setText("")
        
        # Icône
        icon_pix = get_icon_pixmap(btn._icon_name, color=icon_color, size=16)
        if icon_pix:
            btn._icon_label.setPixmap(icon_pix)
        
        # Texte
        btn._text_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: {'600' if is_active else '500'};
            background: transparent;
            color: {text_color};
        """)

    def mark_section_completed(self, index, completed=True):
        """Marque une section comme complétée"""
        if 0 <= index < len(self._buttons):
            btn = self._buttons[index]
            btn._completed = completed
            self._update_button_style(btn, btn.isChecked())
            self.update_progress()

    def update_progress(self):
        """Met à jour la barre de progression avec animation"""
        total = len(self._buttons)
        completed = sum(1 for btn in self._buttons if btn._completed)
        percentage = int((completed / total) * 100) if total > 0 else 0
        
        # ✅ Récupérer la largeur du conteneur parent
        progress_bar_bg = self.progress_bar_fill.parent()
        if progress_bar_bg:
            bar_width = progress_bar_bg.width()
        else:
            bar_width = 200
        
        target_width = int(bar_width * percentage / 100) if bar_width > 0 else 0
        current_width = self.progress_bar_fill.width()
        
        if target_width != current_width:
            # ✅ Arrêter l'animation existante
            if self._progress_animation:
                self._progress_animation.stop()
                self._progress_animation.deleteLater()
                self._progress_animation = None
            
            # ✅ Créer une nouvelle animation
            self._progress_animation = QPropertyAnimation(self.progress_bar_fill, b"fixedWidth")
            self._progress_animation.setDuration(500)
            self._progress_animation.setStartValue(current_width)
            self._progress_animation.setEndValue(target_width)
            self._progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._progress_animation.start()
            self._animations.append(self._progress_animation)
        
        self.progress_percent.setText(f"{percentage}%")
        self.progress_text.setText(f"{completed}/{total} sections complétées")

    def set_save_progress(self, value):
        """Définit la progression de l'enregistrement (0-100)"""
        if value > 0 and value < 100:
            self.save_progress.setVisible(True)
            self.save_progress.setValue(value)
            self.save_btn.setEnabled(False)
            self.save_btn.setText("  ENREGISTREMENT...")
        elif value >= 100:
            self.save_progress.setVisible(True)
            self.save_progress.setValue(100)
            self.save_btn.setEnabled(False)
            self.save_btn.setText("  TERMINÉ ✓")
            QTimer.singleShot(2000, self._hide_save_progress)
        else:
            self._hide_save_progress()

    def _hide_save_progress(self):
        """Cache la barre de progression et réactive le bouton"""
        self.save_progress.setVisible(False)
        self.save_progress.setValue(0)
        self.save_btn.setEnabled(True)
        self.save_btn.setText("  ENREGISTRER")
        if self._collapsed:
            self.save_btn.setText("")

    def _animate_button_enter(self, btn):
        """Animation d'entrée pour un bouton"""
        anim = QPropertyAnimation(btn, b"maximumHeight")
        anim.setDuration(250)
        anim.setStartValue(0)
        anim.setEndValue(38)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._animations.append(anim)

    def _animate_button_switch(self, btn):
        """Animation lors du changement de section"""
        anim = QPropertyAnimation(btn._icon_label, b"geometry")
        anim.setDuration(150)
        geo = btn._icon_label.geometry()
        anim.setStartValue(geo)
        anim.setEndValue(geo.adjusted(2, 2, -4, -4))
        anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        anim.start()
        self._animations.append(anim)

    def _on_button_clicked(self, index):
        """Gère le clic sur un bouton"""
        if index == self._current_index:
            return
        
        if 0 <= self._current_index < len(self._buttons):
            old_btn = self._buttons[self._current_index]
            old_btn.setChecked(False)
            self._update_button_style(old_btn, False)
        
        btn = self._buttons[index]
        btn.setChecked(True)
        self._update_button_style(btn, True)
        self._animate_button_switch(btn)
        
        self._current_index = index
        self.section_changed.emit(index)

    def set_current_section(self, index):
        """Change la section active"""
        if 0 <= index < len(self._buttons):
            self._on_button_clicked(index)

    def get_current_section(self):
        """Retourne l'index de la section active"""
        return self._current_index

    def get_section_widget(self, index):
        """Retourne le widget d'une section"""
        if 0 <= index < len(self._buttons):
            return self._buttons[index]._section_widget
        return None

    def toggle(self):
        """Bascule entre mode réduit et étendu"""
        self._collapsed = not self._collapsed
        target_width = self.COLLAPSED_WIDTH if self._collapsed else self.EXPANDED_WIDTH

        self.width_animation.setStartValue(self.width())
        self.width_animation.setEndValue(target_width)
        self.width_animation.start()
        
        def set_fixed_width():
            self.setFixedWidth(target_width)
        self.width_animation.finished.connect(set_fixed_width)

        # Boutons
        for btn in self._buttons:
            text_label = btn.findChild(QLabel, "text_label")
            if text_label:
                text_label.setVisible(not self._collapsed)
            
            checkbox = btn.findChild(QLabel, "checkbox_indicator")
            if checkbox:
                checkbox.setVisible(not self._collapsed)
            
            icon_label = btn.findChild(QLabel, "icon_label")
            if icon_label:
                if self._collapsed:
                    icon_label.setFixedSize(32, 32)
                    icon_pix = get_icon_pixmap(btn._icon_name, color='#94a3b8', size=20)
                    if icon_pix:
                        icon_label.setPixmap(icon_pix)
                    btn.setFixedHeight(44)
                else:
                    icon_label.setFixedSize(24, 24)
                    icon_pix = get_icon_pixmap(btn._icon_name, color='#94a3b8', size=16)
                    if icon_pix:
                        icon_label.setPixmap(icon_pix)
                    btn.setFixedHeight(38)
            
            if self._collapsed:
                btn.setStyleSheet("""
                    QPushButton#MenuBtn {
                        color: #94a3b8;
                        background: transparent;
                        border: none;
                        border-radius: 8px;
                        padding: 8px 0px;
                        text-align: center;
                        margin: 2px 4px;
                    }
                    QPushButton#MenuBtn:hover {
                        background: rgba(255,255,255,0.06);
                        color: #e2e8f0;
                    }
                    QPushButton#MenuBtn:checked {
                        background: #3b82f6;
                        color: white;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton#MenuBtn {
                        color: #94a3b8;
                        background: transparent;
                        border: none;
                        border-radius: 8px;
                        padding: 10px 14px;
                        text-align: left;
                        font-size: 13px;
                        margin: 2px 8px;
                        font-weight: 500;
                    }
                    QPushButton#MenuBtn:hover {
                        background: rgba(255,255,255,0.06);
                        color: #e2e8f0;
                    }
                    QPushButton#MenuBtn:checked {
                        background: #3b82f6;
                        color: white;
                    }
                """)
            
            self._update_button_style(btn, btn.isChecked())

        # Bouton Enregistrer
        if self._collapsed:
            self.save_btn.setText("")
            self.save_btn.setIconSize(QSize(20, 20))
            self.save_btn.setIcon(get_icon('save', color='white', size=20))
            self.save_btn.setToolTip("Enregistrer le véhicule")
            self.cancel_btn.setVisible(False)
            self.save_progress.setVisible(False)
        else:
            self.save_btn.setText("  ENREGISTRER")
            self.save_btn.setIconSize(QSize(16, 16))
            self.save_btn.setIcon(get_icon('save', color='white', size=16))
            self.save_btn.setToolTip("")
            self.cancel_btn.setVisible(True)

        # Progression
        self.progress_text.setVisible(not self._collapsed)
        self.progress_percent.setVisible(not self._collapsed)
        self.progress_bar_fill.parent().setVisible(not self._collapsed)
        
        self.toggled.emit(self._collapsed)

    def is_collapsed(self):
        """Retourne True si le menu est réduit"""
        return self._collapsed

    def set_progress(self, value):
        """Définit la progression manuellement (0-100)"""
        total = len(self._buttons)
        completed = int((value / 100) * total)
        for i in range(total):
            self.mark_section_completed(i, i < completed)

    def reset_sections(self):
        """Réinitialise toutes les sections (non complétées)"""
        for btn in self._buttons:
            btn._completed = False
            self._update_button_style(btn, btn.isChecked())
        self.update_progress()

    def get_section_count(self):
        """Retourne le nombre total de sections"""
        return len(self._buttons)

    def get_completed_count(self):
        """Retourne le nombre de sections complétées"""
        return sum(1 for btn in self._buttons if btn._completed)

    def resizeEvent(self, event):
        """Met à jour la progression lors du redimensionnement"""
        super().resizeEvent(event)
        QTimer.singleShot(50, self.update_progress)

    def showEvent(self, event):
        """Appelé quand le widget est affiché"""
        super().showEvent(event)
        QTimer.singleShot(100, self.update_progress)