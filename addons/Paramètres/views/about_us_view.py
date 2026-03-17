from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QCursor

class AboutUsView(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.setObjectName("AboutUsPage")
        self.setStyleSheet("background-color: #f8fafc;") # Fond Slate 50
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(0, 50, 0, 50)

        # --- CONTENEUR CENTRAL ---
        card = QFrame()
        card.setFixedWidth(550)
        card.setStyleSheet("background-color: white; border-radius: 20px; border: 1px solid #e2e8f0;")
        self._add_shadow(card)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(25)

        # Logo et Titre
        header_v = QVBoxLayout()
        header_v.setSpacing(5)
        logo = QLabel("AMS AUTO")
        logo.setStyleSheet("font-size: 32px; font-weight: 900; color: #0f172a; letter-spacing: -1px;")
        logo.setAlignment(Qt.AlignCenter)
        
        badge = QLabel("VERSION 1.1.0 PROFESSIONAL")
        badge.setStyleSheet("""
            background-color: #eff6ff; color: #2563eb; padding: 4px 12px; 
            border-radius: 12px; font-weight: 800; font-size: 10px;
        """)
        badge.setAlignment(Qt.AlignCenter)
        
        header_v.addWidget(logo)
        header_v.addWidget(badge, alignment=Qt.AlignCenter)
        card_layout.addLayout(header_v)

        # Description
        desc = QLabel(
            "Système intelligent de gestion d'assurance automobile.\n"
            "Optimisation des flux de travail et gestion sécurisée des polices."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #64748b; font-size: 14px; line-height: 150%;")
        card_layout.addWidget(desc)

        # Grille d'infos
        info_box = QFrame()
        info_box.setStyleSheet("background-color: #f8fafc; border-radius: 12px; padding: 15px;")
        info_grid = QVBoxLayout(info_box)
        
        infos = [
            ("Développeur", "Fearless / AMS Project Group"),
            ("Licence", "Propriétaire - Entreprise"),
            ("Base de données", "PostgreSQL / SQLite Local")
        ]
        
        for label, val in infos:
            row = QHBoxLayout()
            l = QLabel(label); l.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600;")
            v = QLabel(val); v.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: 700;")
            row.addWidget(l); row.addStretch(); row.addWidget(v)
            info_grid.addLayout(row)
        
        card_layout.addWidget(info_box)

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_support = self._create_btn("🌐 Support", "#ffffff", "#1e293b", True)
        self.btn_update = self._create_btn("🔄 Mises à jour", "#2563eb", "#ffffff", False)
        btn_layout.addWidget(self.btn_support)
        btn_layout.addWidget(self.btn_update)
        card_layout.addLayout(btn_layout)

        main_layout.addWidget(card)
        
        # Footer
        footer = QLabel("© 2026 AMS Project Group. Tous droits réservés.")
        footer.setStyleSheet("color: #94a3b8; font-size: 11px; margin-top: 20px;")
        main_layout.addWidget(footer, alignment=Qt.AlignCenter)

    def _create_btn(self, text, bg, fg, border=False):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(42)
        border_style = "border: 1px solid #e2e8f0;" if border else "border: none;"
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg}; color: {fg}; {border_style}
                border-radius: 8px; font-weight: bold; font-size: 13px; padding: 0 15px;
            }}
            QPushButton:hover {{ background-color: {'#f1f5f9' if border else '#1d4ed8'}; }}
        """)
        return btn

    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)