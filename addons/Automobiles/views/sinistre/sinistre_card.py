# # addons/Automobiles/views/sinistre/sinistre_card.py
# """
# Carte moderne pour l'affichage des sinistres
# """

# from PySide6.QtWidgets import (
#     QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
#     QWidget, QSizePolicy
# )
# from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
# from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QFont

# from addons.Automobiles.views.style import Colors, Fonts, Spacing
# from addons.Automobiles.models.sinistre_models import StatutSinistre, TypeSinistre


# class SinistreCard(QFrame):
#     """Carte moderne pour l'affichage d'un sinistre"""
    
#     def __init__(self, sinistre, on_view, on_edit, parent=None):
#         super().__init__(parent)
#         self.sinistre = sinistre
#         self.on_view = on_view
#         self.on_edit = on_edit
#         self._hover = False
        
#         self.setFixedHeight(160)
#         self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
#         self.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {Colors.WHITE};
#                 border: 1px solid {Colors.BORDER};
#                 border-radius: 16px;
#             }}
#             QFrame:hover {{
#                 border-color: {Colors.PRIMARY};
#                 background-color: {Colors.GRAY_200};
#             }}
#         """)
        
#         # Ombre portée
#         self.setGraphicsEffect(self._create_shadow())
        
#         self.setup_ui()
    
#     def _create_shadow(self):
#         """Crée l'effet d'ombre"""
#         from PySide6.QtWidgets import QGraphicsDropShadowEffect
#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(20)
#         shadow.setXOffset(0)
#         shadow.setYOffset(4)
#         shadow.setColor(QColor(0, 0, 0, 15))
#         return shadow
    
#     def setup_ui(self):
#         """Configure l'interface de la carte"""
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(0)
        
#         # --- Bandeau coloré à gauche (indicateur de statut) ---
#         self.color_bar = QFrame()
#         self.color_bar.setFixedWidth(6)
#         self.color_bar.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {self._get_statut_color(self.sinistre.statut)};
#                 border-radius: 0px;
#             }}
#         """)
#         layout.addWidget(self.color_bar)
        
#         # --- Contenu principal ---
#         content = QWidget()
#         content_layout = QHBoxLayout(content)
#         content_layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
#         content_layout.setSpacing(Spacing.LG)
        
#         # --- Colonne gauche : Icône + Infos principales ---
#         left = QWidget()
#         left_layout = QHBoxLayout(left)
#         left_layout.setSpacing(Spacing.MD)
        
#         # Icône du type
#         icon_label = QLabel(self._get_type_icon(self.sinistre.type))
#         icon_label.setStyleSheet(f"""
#             font-size: 36px;
#             background-color: {self._get_type_color(self.sinistre.type)};
#             border-radius: 12px;
#             padding: 10px;
#             min-width: 56px;
#             min-height: 56px;
#         """)
#         icon_label.setAlignment(Qt.AlignCenter)
#         left_layout.addWidget(icon_label)
        
#         # Informations
#         info = QWidget()
#         info_layout = QVBoxLayout(info)
#         info_layout.setSpacing(Spacing.XS)
        
#         # N° dossier et type
#         header_layout = QHBoxLayout()
#         header_layout.setSpacing(Spacing.SM)
        
#         numero_label = QLabel(f"#{self.sinistre.numero_dossier}")
#         numero_label.setStyleSheet(f"""
#             font-size: {Fonts.H3}px;
#             font-weight: {Fonts.BOLD};
#             color: {Colors.TEXT_PRIMARY};
#             letter-spacing: 0.5px;
#         """)
#         header_layout.addWidget(numero_label)
        
#         # Badge type
#         type_badge = QLabel(self.sinistre.get_type_label())
#         type_badge.setStyleSheet(f"""
#             background-color: {Colors.PRIMARY}15;
#             color: {Colors.PRIMARY};
#             border-radius: 12px;
#             padding: 2px 14px;
#             font-size: 11px;
#             font-weight: {Fonts.MEDIUM};
#             border: 1px solid {Colors.PRIMARY}30;
#         """)
#         header_layout.addWidget(type_badge)
#         header_layout.addStretch()
        
#         info_layout.addLayout(header_layout)
        
#         # Véhicule et propriétaire
#         details_layout = QHBoxLayout()
#         details_layout.setSpacing(Spacing.LG)
        
#         immat = self.sinistre.vehicule.immatriculation if self.sinistre.vehicule else "N/A"
#         marque = self.sinistre.vehicule.marque if self.sinistre.vehicule else ""
#         modele = self.sinistre.vehicule.modele if self.sinistre.vehicule else ""
#         vehicule_text = f"{immat} - {marque} {modele}".strip()
#         if vehicule_text.endswith("-"):
#             vehicule_text = vehicule_text[:-1]
        
#         vehicule_label = QLabel(f"🚗 {vehicule_text}")
#         vehicule_label.setStyleSheet(f"""
#             font-size: {Fonts.SMALL}px;
#             color: {Colors.TEXT_SECONDARY};
#         """)
#         details_layout.addWidget(vehicule_label)
        
#         if self.sinistre.client:
#             client_text = f"{self.sinistre.client.nom} {self.sinistre.client.prenom or ''}".strip()
#             client_label = QLabel(f"👤 {client_text}")
#             client_label.setStyleSheet(f"""
#                 font-size: {Fonts.SMALL}px;
#                 color: {Colors.TEXT_SECONDARY};
#             """)
#             details_layout.addWidget(client_label)
        
#         details_layout.addStretch()
#         info_layout.addLayout(details_layout)
        
#         # Date et lieu
#         date_str = self.sinistre.date_survenue.strftime("%d/%m/%Y à %H:%M") if self.sinistre.date_survenue else ""
#         lieu = self.sinistre.lieu or ""
#         lieu_text = f" • {lieu}" if lieu else ""
#         date_label = QLabel(f"📅 {date_str}{lieu_text}")
#         date_label.setStyleSheet(f"""
#             font-size: 12px;
#             color: {Colors.TEXT_MUTED};
#         """)
#         info_layout.addWidget(date_label)
        
#         left_layout.addWidget(info)
#         content_layout.addWidget(left, 2)
        
#         # --- Colonne droite : Statut et montant ---
#         right = QWidget()
#         right_layout = QVBoxLayout(right)
#         right_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
#         right_layout.setSpacing(Spacing.SM)
        
#         # Montant
#         montant = f"{self.sinistre.estimation_preliminaire:,.0f} FCFA"
#         montant_label = QLabel(montant)
#         montant_label.setStyleSheet(f"""
#             font-size: {Fonts.H3}px;
#             font-weight: {Fonts.BOLD};
#             color: {Colors.TEXT_PRIMARY};
#         """)
#         right_layout.addWidget(montant_label, alignment=Qt.AlignRight)
        
#         # Statut avec badge
#         statut_color = self._get_statut_color(self.sinistre.statut)
#         statut_text = self.sinistre.statut.value.upper()
        
#         statut_badge = QFrame()
#         statut_badge.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {statut_color}15;
#                 border: 1px solid {statut_color}40;
#                 border-radius: 20px;
#                 padding: 4px 16px;
#             }}
#         """)
#         statut_layout = QHBoxLayout(statut_badge)
#         statut_layout.setContentsMargins(8, 4, 8, 4)
#         statut_layout.setSpacing(Spacing.SM)
        
#         # Point indicateur
#         dot = QLabel("●")
#         dot.setStyleSheet(f"""
#             color: {statut_color};
#             font-size: 10px;
#         """)
#         statut_layout.addWidget(dot)
        
#         statut_label = QLabel(statut_text)
#         statut_label.setStyleSheet(f"""
#             color: {statut_color};
#             font-size: 12px;
#             font-weight: {Fonts.BOLD};
#             letter-spacing: 0.5px;
#         """)
#         statut_layout.addWidget(statut_label)
        
#         right_layout.addWidget(statut_badge, alignment=Qt.AlignRight)
        
#         # Jours écoulés
#         jours = self.sinistre.jours_ecoules
#         if jours > 15:
#             jours_color = "#dc2626"
#             jours_icon = "🔴"
#         elif jours > 7:
#             jours_color = "#f59e0b"
#             jours_icon = "🟡"
#         else:
#             jours_color = "#16a34a"
#             jours_icon = "🟢"
        
#         jours_label = QLabel(f"{jours_icon} {jours} jours")
#         jours_label.setStyleSheet(f"""
#             font-size: 12px;
#             color: {jours_color};
#             font-weight: {Fonts.MEDIUM};
#         """)
#         right_layout.addWidget(jours_label, alignment=Qt.AlignRight)
        
#         # Boutons d'action
#         btn_layout = QHBoxLayout()
#         btn_layout.setSpacing(Spacing.SM)
#         btn_layout.setAlignment(Qt.AlignRight)
        
#         btn_view = QPushButton("Voir")
#         btn_view.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: transparent;
#                 color: {Colors.PRIMARY};
#                 border: 1px solid {Colors.PRIMARY}40;
#                 border-radius: 8px;
#                 padding: 6px 16px;
#                 font-size: 12px;
#                 font-weight: {Fonts.MEDIUM};
#             }}
#             QPushButton:hover {{
#                 background-color: {Colors.PRIMARY}10;
#                 border-color: {Colors.PRIMARY};
#             }}
#         """)
#         btn_view.clicked.connect(lambda: self.on_view(self.sinistre))
        
#         btn_edit = QPushButton("Modifier")
#         btn_edit.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: {Colors.PRIMARY};
#                 color: white;
#                 border: none;
#                 border-radius: 8px;
#                 padding: 6px 16px;
#                 font-size: 12px;
#                 font-weight: {Fonts.MEDIUM};
#             }}
#             QPushButton:hover {{
#                 background-color: {Colors.PRIMARY_DARK};
#             }}
#         """)
#         btn_edit.clicked.connect(lambda: self.on_edit(self.sinistre))
        
#         btn_layout.addWidget(btn_view)
#         btn_layout.addWidget(btn_edit)
#         right_layout.addLayout(btn_layout)
        
#         content_layout.addWidget(right, 1)
#         layout.addWidget(content)
    
#     def _get_statut_color(self, statut):
#         """Retourne la couleur associée à un statut"""
#         colors = {
#             StatutSinistre.DECLARE: "#2563eb",
#             StatutSinistre.EN_INSTRUCTION: "#f59e0b",
#             StatutSinistre.EN_ATTENTE: "#f59e0b",
#             StatutSinistre.EXPERTISE: "#8b5cf6",
#             StatutSinistre.VALIDE: "#16a34a",
#             StatutSinistre.REJETE: "#dc2626",
#             StatutSinistre.INDEMNISE: "#16a34a",
#             StatutSinistre.CLOS: "#64748b",
#         }
#         return colors.get(statut, "#64748b")
    
#     def _get_type_icon(self, type_enum):
#         """Retourne l'icône associée à un type"""
#         icons = {
#             TypeSinistre.ACCIDENT: "💥",
#             TypeSinistre.VOL: "🔓",
#             TypeSinistre.INCENDIE: "🔥",
#             TypeSinistre.DEGAT_NATUREL: "🌊",
#             TypeSinistre.BRIS_GLACE: "🪟",
#             TypeSinistre.VANDALISME: "💢",
#             TypeSinistre.COLLISION: "🚗💥",
#             TypeSinistre.AUTRE: "📌"
#         }
#         return icons.get(type_enum, "📌")
    
#     def _get_type_color(self, type_enum):
#         """Retourne la couleur associée à un type"""
#         colors = {
#             TypeSinistre.ACCIDENT: "#fee2e2",
#             TypeSinistre.VOL: "#fef3c7",
#             TypeSinistre.INCENDIE: "#fca5a5",
#             TypeSinistre.DEGAT_NATUREL: "#bfdbfe",
#             TypeSinistre.BRIS_GLACE: "#d1fae5",
#             TypeSinistre.VANDALISME: "#fbcfe8",
#             TypeSinistre.COLLISION: "#fecaca",
#             TypeSinistre.AUTRE: "#e5e7eb"
#         }
#         return colors.get(type_enum, "#e5e7eb")
    
#     def enterEvent(self, event):
#         """Animation au survol"""
#         self._hover = True
#         self.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {Colors.GRAY_200};
#                 border: 2px solid {Colors.PRIMARY};
#                 border-radius: 16px;
#             }}
#         """)
#         super().enterEvent(event)
    
#     def leaveEvent(self, event):
#         """Animation à la sortie du survol"""
#         self._hover = False
#         self.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {Colors.WHITE};
#                 border: 1px solid {Colors.BORDER};
#                 border-radius: 16px;
#             }}
#         """)
#         super().leaveEvent(event)


# # ============================================================================
# # VERSION AMÉLIORÉE DE LA CARTE AVEC ANIMATION
# # ============================================================================

# class AnimatedSinistreCard(SinistreCard):
#     """Carte avec animation à l'affichage"""
    
#     def __init__(self, sinistre, on_view, on_edit, parent=None):
#         super().__init__(sinistre, on_view, on_edit, parent)
#         self.setGraphicsEffect(None)  # Enlever l'ombre pour l'animation
        
#         # Animation d'apparition
#         self.animation = QPropertyAnimation(self, b"maximumHeight")
#         self.animation.setDuration(300)
#         self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
#         self.animation.setStartValue(0)
#         self.animation.setEndValue(160)
#         self.animation.start()
        
#         # Opacité
#         self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
#         self.opacity_anim.setDuration(300)
#         self.opacity_anim.setStartValue(0)
#         self.opacity_anim.setEndValue(1)
#         self.opacity_anim.start()
# addons/Automobiles/views/sinistre/sinistre_card.py
"""
Carte professionnelle premium pour l'affichage des sinistres
Design épuré, moderne et élégant
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QFont

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.models.sinistre_models import StatutSinistre, TypeSinistre


class SinistreCard(QFrame):
    """
    Carte professionnelle premium pour l'affichage d'un sinistre
    Design inspiré des dashboards modernes (Linear, Stripe, etc.)
    """
    
    # Couleurs pour les différents statuts (palette professionnelle)
    STATUS_COLORS = {
        StatutSinistre.DECLARE: {
            'primary': "#2563eb",
            'light': "#dbeafe",
            'text': "#1e40af",
            'badge': "Nouveau"
        },
        StatutSinistre.EN_INSTRUCTION: {
            'primary': "#f59e0b",
            'light': "#fef3c7",
            'text': "#92400e",
            'badge': "En cours"
        },
        StatutSinistre.EN_ATTENTE: {
            'primary': "#f59e0b",
            'light': "#fef3c7",
            'text': "#92400e",
            'badge': "En attente"
        },
        StatutSinistre.EXPERTISE: {
            'primary': "#8b5cf6",
            'light': "#ede9fe",
            'text': "#5b21b6",
            'badge': "Expertise"
        },
        StatutSinistre.VALIDE: {
            'primary': "#16a34a",
            'light': "#dcfce7",
            'text': "#166534",
            'badge': "Validé"
        },
        StatutSinistre.REJETE: {
            'primary': "#dc2626",
            'light': "#fee2e2",
            'text': "#991b1b",
            'badge': "Rejeté"
        },
        StatutSinistre.INDEMNISE: {
            'primary': "#16a34a",
            'light': "#dcfce7",
            'text': "#166534",
            'badge': "Indemnisé"
        },
        StatutSinistre.CLOS: {
            'primary': "#64748b",
            'light': "#f1f5f9",
            'text': "#334155",
            'badge': "Clos"
        }
    }
    
    TYPE_ICONS = {
        TypeSinistre.ACCIDENT: "💥",
        TypeSinistre.VOL: "🔓",
        TypeSinistre.INCENDIE: "🔥",
        TypeSinistre.DEGAT_NATUREL: "🌊",
        TypeSinistre.BRIS_GLACE: "🪟",
        TypeSinistre.VANDALISME: "💢",
        TypeSinistre.COLLISION: "🚗💥",
        TypeSinistre.AUTRE: "📌"
    }
    
    TYPE_LABELS = {
        TypeSinistre.ACCIDENT: "Accident",
        TypeSinistre.VOL: "Vol",
        TypeSinistre.INCENDIE: "Incendie",
        TypeSinistre.DEGAT_NATUREL: "Dégât naturel",
        TypeSinistre.BRIS_GLACE: "Bris de glace",
        TypeSinistre.VANDALISME: "Vandalisme",
        TypeSinistre.COLLISION: "Collision",
        TypeSinistre.AUTRE: "Autre"
    }
    
    def __init__(self, sinistre, on_view, on_edit, parent=None):
        super().__init__(parent)
        self.sinistre = sinistre
        self.on_view = on_view
        self.on_edit = on_edit
        self._hover = False
        
        # Dimensions
        self.setFixedHeight(260)
        self.setMinimumWidth(340)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Style de base
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.WHITE};
                border-radius: 20px;
            }}
        """)
        
        # Ombre portée
        self._setup_shadow()
        
        self.setup_ui()
    
    def _setup_shadow(self):
        """Configure l'effet d'ombre"""
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
        self._shadow = shadow
    
    def setup_ui(self):
        """Configure l'interface de la carte"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- EN-TÊTE ---
        header = self._create_header()
        main_layout.addWidget(header)
        
        # --- CORPS ---
        body = self._create_body()
        main_layout.addWidget(body, 1)
    
    def _create_header(self):
        """Crée l'en-tête de la carte"""
        statut_info = self.STATUS_COLORS.get(self.sinistre.statut, self.STATUS_COLORS[StatutSinistre.DECLARE])
        
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {statut_info['light']};
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 12, 24, 12)
        
        # --- Groupe gauche : Icône + Type ---
        left_group = QWidget()
        left_layout = QHBoxLayout(left_group)
        left_layout.setSpacing(16)
        
        # Icône avec fond
        icon_container = QFrame()
        icon_container.setFixedSize(52, 52)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: {statut_info['primary']};
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel(self.TYPE_ICONS.get(self.sinistre.type, "📌"))
        icon_label.setStyleSheet("font-size: 24px; color: white;")
        icon_layout.addWidget(icon_label)
        
        left_layout.addWidget(icon_container)
        
        # Informations
        info = QWidget()
        info_layout = QVBoxLayout(info)
        info_layout.setSpacing(2)
        
        # Type
        type_label = QLabel(self.TYPE_LABELS.get(self.sinistre.type, "Autre"))
        type_label.setStyleSheet(f"""
            font-size: 10px;
            font-weight: {Fonts.REGULAR};
            color: {Colors.TEXT_PRIMARY};
        """)
        info_layout.addWidget(type_label)
        
        # Badge statut
        badge = QLabel(f"● {statut_info['badge']}")
        badge.setStyleSheet(f"""
            color: {statut_info['primary']};
            font-size: 12px;
            font-weight: {Fonts.REGULAR};
        """)
        info_layout.addWidget(badge)
        
        left_layout.addWidget(info)
        
        # --- Groupe droit : N° dossier ---
        numero_label = QLabel(f"#{self.sinistre.numero_dossier}")
        numero_label.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: 13px;
            font-weight: {Fonts.MEDIUM};
        """)
        
        layout.addWidget(left_group, 1)
        layout.addWidget(numero_label)
        
        return header
    
    def _create_body(self):
        """Crée le corps de la carte"""
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 16, 24, 16)
        body_layout.setSpacing(10)
        
        # --- Ligne 1 : Véhicule ---
        row1 = QHBoxLayout()
        
        vehicle_text = self._get_vehicle_text()
        vehicle_label = QLabel(f"🚗 {vehicle_text}")
        vehicle_label.setStyleSheet(f"""
            font-size: {Fonts.H5}px;
            font-weight: {Fonts.SEMIBOLD};
            color: {Colors.TEXT_PRIMARY};
        """)
        row1.addWidget(vehicle_label)
        row1.addStretch()
        
        body_layout.addLayout(row1)
        
        # --- Ligne 2 : Client ---
        client_text = self._get_client_text()
        if client_text:
            client_label = QLabel(f"👤 {client_text}")
            client_label.setStyleSheet(f"""
                font-size: 14px;
                color: {Colors.TEXT_SECONDARY};
            """)
            body_layout.addWidget(client_label)
        
        # --- Ligne 3 : Date + Lieu ---
        row3 = QHBoxLayout()
        row3.setSpacing(16)
        
        # Date
        date_text = self.sinistre.date_survenue.strftime("%d/%m/%Y à %H:%M") if self.sinistre.date_survenue else ""
        date_label = QLabel(f"📅 {date_text}")
        date_label.setStyleSheet(f"""
            font-size: 13px;
            color: {Colors.TEXT_MUTED};
        """)
        row3.addWidget(date_label)
        
        # Lieu
        if self.sinistre.lieu:
            lieu_label = QLabel(f"📍 {self.sinistre.lieu[:35]}")
            lieu_label.setStyleSheet(f"""
                font-size: 13px;
                color: {Colors.TEXT_MUTED};
            """)
            row3.addWidget(lieu_label)
        
        row3.addStretch()
        
        # Jours écoulés
        jours = self.sinistre.jours_ecoules
        jours_info = self._get_jours_info(jours)
        jours_label = QLabel(f"{jours_info['icon']} {jours} jours")
        jours_label.setStyleSheet(f"""
            font-size: 13px;
            color: {jours_info['color']};
            font-weight: {Fonts.MEDIUM};
        """)
        row3.addWidget(jours_label)
        
        body_layout.addLayout(row3)
        
        # --- Séparateur ---
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER}; max-height: 1px;")
        body_layout.addWidget(sep)
        
        # --- Bas : Montant + Boutons ---
        bottom = QHBoxLayout()
        bottom.setSpacing(12)
        
        # Montant
        montant = f"{self.sinistre.estimation_preliminaire:,.0f} FCFA"
        montant_label = QLabel(montant)
        montant_label.setStyleSheet(f"""
            font-size: {Fonts.H2}px;
            font-weight: {Fonts.SEMIBOLD};
            color: {Colors.PRIMARY};
        """)
        bottom.addWidget(montant_label)
        
        bottom.addStretch()
        
        # Boutons
        btn_view = QPushButton("👁️")
        btn_view.setCursor(Qt.PointingHandCursor)
        btn_view.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: {Fonts.MEDIUM};
            }}
            QPushButton:hover {{
                background-color: {Colors.GRAY_50};
                border-color: {Colors.PRIMARY};
                color: {Colors.PRIMARY};
            }}
        """)
        btn_view.clicked.connect(lambda: self.on_view(self.sinistre))
        
        btn_edit = QPushButton("✏️")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: {Fonts.MEDIUM};
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_DARK};
            }}
        """)
        btn_edit.clicked.connect(lambda: self.on_edit(self.sinistre))
        
        bottom.addWidget(btn_view)
        bottom.addWidget(btn_edit)
        
        body_layout.addLayout(bottom)
        
        return body
    
    def _get_vehicle_text(self):
        """Retourne le texte du véhicule"""
        if not self.sinistre.vehicule:
            return "N/A"
        immat = self.sinistre.vehicule.immatriculation or ""
        marque = self.sinistre.vehicule.marque or ""
        modele = self.sinistre.vehicule.modele or ""
        return f"{immat} - {marque} {modele}".strip().strip('-')
    
    def _get_client_text(self):
        """Retourne le texte du client"""
        if not self.sinistre.client:
            return ""
        nom = self.sinistre.client.nom or ""
        prenom = self.sinistre.client.prenom or ""
        return f"{nom} {prenom}".strip()
    
    def _get_jours_info(self, jours):
        """Retourne les informations sur les jours écoulés"""
        if jours > 15:
            return {'icon': '🔴', 'color': '#dc2626'}
        elif jours > 7:
            return {'icon': '🟡', 'color': '#f59e0b'}
        else:
            return {'icon': '🟢', 'color': '#16a34a'}
    
    def enterEvent(self, event):
        """Animation au survol"""
        if hasattr(self, '_shadow'):
            self._shadow.setBlurRadius(40)
            self._shadow.setYOffset(12)
            self._shadow.setColor(QColor(0, 0, 0, 30))
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.WHITE};
                border-radius: 20px;
            }}
        """)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Animation à la sortie du survol"""
        if hasattr(self, '_shadow'):
            self._shadow.setBlurRadius(30)
            self._shadow.setYOffset(8)
            self._shadow.setColor(QColor(0, 0, 0, 20))
        super().leaveEvent(event)


# ============================================================================
# VERSION AVEC ANIMATION D'APPARITION
# ============================================================================

class AnimatedSinistreCard(SinistreCard):
    """Carte avec animation à l'affichage"""
    
    def __init__(self, sinistre, on_view, on_edit, parent=None):
        super().__init__(sinistre, on_view, on_edit, parent)
        
        # Animation d'apparition
        self.anim_height = QPropertyAnimation(self, b"maximumHeight")
        self.anim_height.setDuration(400)
        self.anim_height.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim_height.setStartValue(0)
        self.anim_height.setEndValue(260)
        self.anim_height.start()
        
        # Animation d'opacité
        self.anim_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_opacity.setDuration(400)
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)
        self.anim_opacity.start()