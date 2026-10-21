# """
# Dialogue de création d'évaluation avec calcul automatique du montant net
# """
# from PySide6.QtWidgets import (
#     QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
#     QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
#     QPushButton, QDialogButtonBox, QMessageBox, QFrame, QCheckBox
# )
# from PySide6.QtCore import Qt, Signal, QDate
# from PySide6.QtGui import QColor

# from datetime import datetime
# import qtawesome as qta


# class EvaluationDialog(QDialog):
#     """Dialogue de création d'évaluation avec calcul automatique"""
    
#     evaluation_created = Signal(dict)
    
#     def __init__(self, sinistre_id, evaluation_controller, user, sinistre_info=None, parent=None):
#         super().__init__(parent)
#         self.sinistre_id = sinistre_id
#         self.evaluation_controller = evaluation_controller
#         self.user = user
#         self.sinistre_info = sinistre_info or {}
        
#         self.setWindowTitle("Créer une évaluation")
#         self.setModal(True)
#         self.setMinimumWidth(600)
#         self.setup_ui()
#         self.load_data()
    
#     def setup_ui(self):
#         layout = QVBoxLayout(self)
#         layout.setSpacing(15)
        
#         # ============================================================
#         # EN-TÊTE AVEC INFOS SINISTRE
#         # ============================================================
#         header_frame = QFrame()
#         header_frame.setStyleSheet("""
#             QFrame {
#                 background-color: #f8fafc;
#                 border-radius: 8px;
#                 padding: 12px;
#                 border: 1px solid #e2e8f0;
#             }
#             QLabel {
#                 color: #1e293b;
#                 font-size: 12px;
#             }
#             QLabel.title {
#                 font-weight: bold;
#                 font-size: 14px;
#                 color: #1a73e8;
#             }
#         """)
#         header_layout = QVBoxLayout(header_frame)
        
#         title = QLabel("💰 Création d'évaluation")
#         title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
#         header_layout.addWidget(title)
        
#         info_layout = QHBoxLayout()
        
#         self.lbl_sinistre = QLabel(f"Sinistre: {self.sinistre_info.get('numero_sinistre', 'N/A')}")
#         info_layout.addWidget(self.lbl_sinistre)
        
#         self.lbl_client = QLabel(f"Client: {self.sinistre_info.get('client_nom', 'N/A')}")
#         info_layout.addWidget(self.lbl_client)
        
#         self.lbl_branche = QLabel(f"Branche: {self.sinistre_info.get('branche', 'N/A')}")
#         info_layout.addWidget(self.lbl_branche)
        
#         info_layout.addStretch()
#         header_layout.addLayout(info_layout)
        
#         layout.addWidget(header_frame)
        
#         # ============================================================
#         # SECTION 1: INFORMATIONS DE L'ÉVALUATION
#         # ============================================================
#         form_group = QGroupBox("Informations de l'évaluation")
#         form_group.setStyleSheet("""
#             QGroupBox {
#                 font-weight: bold;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 10px;
#                 margin-top: 10px;
#                 padding-top: 15px;
#             }
#             QGroupBox::title {
#                 subcontrol-origin: margin;
#                 left: 10px;
#                 padding: 0 10px;
#             }
#         """)
#         form_layout = QFormLayout(form_group)
#         form_layout.setSpacing(12)
        
#         # Type d'évaluation
#         self.input_type = QComboBox()
#         self.input_type.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
#         self.input_type.addItems([
#             "auto_materiel",
#             "auto_corporel",
#             "incendie",
#             "vol",
#             "degats_eau",
#             "rc_generale",
#             "defense_recours",
#             "transport_marchandises",
#             "transport_conteneurs"
#         ])
#         form_layout.addRow("Type d'évaluation *:", self.input_type)
        
#         # Catégorie (optionnel)
#         self.input_categorie = QLineEdit()
#         self.input_categorie.setPlaceholderText("Ex: Véhicule, Bâtiment... (optionnel)")
#         self.input_categorie.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
#         form_layout.addRow("Catégorie:", self.input_categorie)
        
#         layout.addWidget(form_group)
        
#         # ============================================================
#         # SECTION 2: CALCUL DU MONTANT
#         # ============================================================
#         calc_group = QGroupBox("Calcul du montant")
#         calc_group.setStyleSheet("""
#             QGroupBox {
#                 font-weight: bold;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 10px;
#                 margin-top: 10px;
#                 padding-top: 15px;
#             }
#             QGroupBox::title {
#                 subcontrol-origin: margin;
#                 left: 10px;
#                 padding: 0 10px;
#             }
#         """)
#         calc_layout = QFormLayout(calc_group)
#         calc_layout.setSpacing(12)
        
#         # Montant brut
#         self.input_montant_brut = QDoubleSpinBox()
#         self.input_montant_brut.setRange(0, 999999999)
#         self.input_montant_brut.setPrefix("FCFA ")
#         self.input_montant_brut.setDecimals(0)
#         self.input_montant_brut.setSingleStep(10000)
#         self.input_montant_brut.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
#         self.input_montant_brut.valueChanged.connect(self.calculer_net)
#         calc_layout.addRow("Montant brut *:", self.input_montant_brut)
        
#         # Franchise
#         self.input_franchise = QDoubleSpinBox()
#         self.input_franchise.setRange(0, 999999999)
#         self.input_franchise.setPrefix("FCFA ")
#         self.input_franchise.setDecimals(0)
#         self.input_franchise.setSingleStep(5000)
#         self.input_franchise.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
#         self.input_franchise.valueChanged.connect(self.calculer_net)
#         calc_layout.addRow("Franchise:", self.input_franchise)
        
#         # Taux de responsabilité
#         self.input_taux = QDoubleSpinBox()
#         self.input_taux.setRange(0, 100)
#         self.input_taux.setSuffix("%")
#         self.input_taux.setValue(100)
#         self.input_taux.setSingleStep(5)
#         self.input_taux.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
#         self.input_taux.valueChanged.connect(self.calculer_net)
#         calc_layout.addRow("Taux responsabilité:", self.input_taux)
        
#         # Résultat
#         result_frame = QFrame()
#         result_frame.setStyleSheet("""
#             QFrame {
#                 background-color: #f0f9ff;
#                 border: 1px solid #bae6fd;
#                 border-radius: 6px;
#                 padding: 10px;
#             }
#             QLabel {
#                 color: #0369a1;
#                 font-size: 14px;
#             }
#             QLabel.value {
#                 font-weight: bold;
#                 font-size: 18px;
#                 color: #1a73e8;
#             }
#         """)
#         result_layout = QVBoxLayout(result_frame)
        
#         self.lbl_net = QLabel("Montant net: 0 FCFA")
#         self.lbl_net.setStyleSheet("font-weight: bold; font-size: 18px; color: #1a73e8;")
#         self.lbl_net.setAlignment(Qt.AlignCenter)
#         result_layout.addWidget(self.lbl_net)
        
#         # Formule affichée
#         self.lbl_formule = QLabel("Formule: (Brut - Franchise) × Taux")
#         self.lbl_formule.setStyleSheet("color: #64748b; font-size: 11px;")
#         self.lbl_formule.setAlignment(Qt.AlignCenter)
#         result_layout.addWidget(self.lbl_formule)
        
#         calc_layout.addRow("", result_frame)
        
#         layout.addWidget(calc_group)
        
#         # ============================================================
#         # SECTION 3: DÉTAILS
#         # ============================================================
#         self.input_details = QTextEdit()
#         self.input_details.setPlaceholderText("Détails de l'évaluation, justifications...")
#         self.input_details.setMaximumHeight(80)
#         self.input_details.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px;")
#         layout.addWidget(QLabel("Détails:"))
#         layout.addWidget(self.input_details)
        
#         # ============================================================
#         # SECTION 4: RÉCAPITULATIF
#         # ============================================================
#         self.summary_frame = QFrame()
#         self.summary_frame.setStyleSheet("""
#             QFrame {
#                 background-color: #f0f9ff;
#                 border: 1px solid #bae6fd;
#                 border-radius: 8px;
#                 padding: 12px;
#             }
#             QLabel {
#                 color: #0369a1;
#                 font-size: 12px;
#             }
#             QLabel.title {
#                 font-weight: bold;
#                 font-size: 13px;
#             }
#         """)
#         summary_layout = QVBoxLayout(self.summary_frame)
        
#         summary_title = QLabel("📋 Récapitulatif de l'évaluation")
#         summary_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #0369a1;")
#         summary_layout.addWidget(summary_title)
        
#         self.summary_text = QLabel("Remplissez les champs pour voir le récapitulatif")
#         self.summary_text.setStyleSheet("color: #0369a1;")
#         summary_layout.addWidget(self.summary_text)
        
#         layout.addWidget(self.summary_frame)
        
#         # ============================================================
#         # BOUTONS
#         # ============================================================
#         btn_layout = QHBoxLayout()
#         btn_layout.addStretch()
        
#         self.btn_annuler = QPushButton("Annuler")
#         self.btn_annuler.setStyleSheet("""
#             QPushButton {
#                 padding: 10px 30px;
#                 border-radius: 8px;
#                 font-weight: bold;
#                 background-color: #f1f5f9;
#                 color: #64748b;
#             }
#             QPushButton:hover {
#                 background-color: #e2e8f0;
#             }
#         """)
#         self.btn_annuler.clicked.connect(self.reject)
#         btn_layout.addWidget(self.btn_annuler)
        
#         self.btn_creer = QPushButton("✅ Créer l'évaluation")
#         self.btn_creer.setStyleSheet("""
#             QPushButton {
#                 background-color: #1a73e8;
#                 color: white;
#                 padding: 10px 40px;
#                 border-radius: 8px;
#                 font-weight: bold;
#             }
#             QPushButton:hover {
#                 background-color: #1557b0;
#             }
#         """)
#         self.btn_creer.clicked.connect(self.creer_evaluation)
#         btn_layout.addWidget(self.btn_creer)
        
#         layout.addLayout(btn_layout)
        
#         # ============================================================
#         # CONNEXIONS
#         # ============================================================
#         self.input_type.currentIndexChanged.connect(self._update_summary)
#         self.input_categorie.textChanged.connect(self._update_summary)
#         self.input_montant_brut.valueChanged.connect(self._update_summary)
#         self.input_franchise.valueChanged.connect(self._update_summary)
#         self.input_taux.valueChanged.connect(self._update_summary)
#         self.input_details.textChanged.connect(self._update_summary)

#     def load_data(self):
#         """Charge les données initiales"""
#         self.calculer_net()
#         self._update_summary()
    
#     def calculer_net(self):
#         """Calcule le montant net automatiquement"""
#         brut = self.input_montant_brut.value()
#         franchise = self.input_franchise.value()
#         taux = self.input_taux.value() / 100
#         net = brut - franchise
#         self.lbl_net.setText(f"Montant net: {net:,.0f} FCFA")
#         self._net_calcule = net
#         return net
    
#     def _update_summary(self):
#         """Met à jour le récapitulatif"""
#         lines = []
        
#         # Type
#         type_text = self.input_type.currentText()
#         if type_text:
#             lines.append(f"📌 Type: {type_text.replace('_', ' ').title()}")
        
#         # Catégorie
#         categorie = self.input_categorie.text().strip()
#         if categorie:
#             lines.append(f"📂 Catégorie: {categorie}")
        
#         # Montants
#         brut = self.input_montant_brut.value()
#         franchise = self.input_franchise.value()
#         taux = self.input_taux.value()
#         net = self.calculer_net()
        
#         if brut > 0:
#             lines.append(f"💰 Brut: {brut:,.0f} FCFA")
#             lines.append(f"📉 Franchise: {franchise:,.0f} FCFA")
#             lines.append(f"📊 Taux: {taux:.0f}%")
#             lines.append(f"✅ Net: {net:,.0f} FCFA")
#         else:
#             lines.append("⚠️ Montant brut non défini")
        
#         # Détails
#         details = self.input_details.toPlainText().strip()
#         if details:
#             lines.append(f"📝 Détails: {details[:50]}...")
        
#         self.summary_text.setText("\n".join(lines))

#     def _filtrer_beneficiaires(self):
#         """Filtre les bénéficiaires selon le type."""
#         type_filtre = self.input_type.currentData()
#         current = self.input_type.currentData()
        
#         self.input_type.blockSignals(True)
#         self.input_type.clear()
#         self.input_type.addItem("-- Sélectionner un bénéficiaire --", None)
        
#         for b in getattr(self, '_tous_beneficiaires', []):
#             source = b.get('source', '')
#             type_b = b.get('type_beneficiaire', 'AUTRE')
            
#             # ✅ Filtre par source
#             if type_filtre == 'BENEFICIAIRE':
#                 if source != 'BENEFICIAIRE':
#                     continue
#             elif type_filtre == 'TIERS':
#                 if source != 'TIERS':
#                     continue
#             elif type_filtre == 'EXPERT':
#                 if source != 'EXPERT':
#                     continue
#             elif type_filtre:
#                 # Filtre par type_beneficiaire exact
#                 if type_b != type_filtre:
#                     continue
            
#             display = self._format_beneficiaire_display(b)
#             icon = self._get_beneficiaire_icon(b)
#             self.input_type.addItem(icon, display, b)
        
#         self.input_type.blockSignals(False)
        
#         # Restaurer la sélection
#         if current:
#             for i in range(self.input_type.count()):
#                 if self.input_type.itemData(i) == current:
#                     self.input_type.setCurrentIndex(i)
#                     break
        
#         self._update_summary()

#     def _charger_beneficiaires(self):
#         """Charge TOUS les bénéficiaires possibles (bénéficiaires + tiers + experts)."""
#         try:
#             # ✅ Appel unifié (3 sources)
#             self._tous_beneficiaires = self.reglement_controller.get_beneficiaires()
            
#             # Statistiques
#             nb_benefs = sum(1 for b in self._tous_beneficiaires if b.get('source') == 'BENEFICIAIRE')
#             nb_tiers = sum(1 for b in self._tous_beneficiaires if b.get('source') == 'TIERS')
#             nb_experts = sum(1 for b in self._tous_beneficiaires if b.get('source') == 'EXPERT')
            
#             print(f"📋 {len(self._tous_beneficiaires)} bénéficiaire(s) : "
#                 f"{nb_benefs} bénéficiaires, {nb_tiers} tiers, {nb_experts} experts")
            
#             # Remplir le combo
#             self.input_type.blockSignals(True)
#             self.input_type.clear()
#             self.input_type.addItem(
#                 "-- Sélectionner un bénéficiaire --", None
#             )
            
#             for b in self._tous_beneficiaires:
#                 display = self._format_beneficiaire_display(b)
#                 icon = self._get_beneficiaire_icon(b)
#                 self.input_type.addItem(icon, display, b)
            
#             self.input_type.blockSignals(False)
        
#         except Exception as e:
#             print(f"❌ Erreur chargement bénéficiaires : {e}")
#             import traceback
#             traceback.print_exc()

#     def _format_beneficiaire_display(self, b: dict) -> str:
#         """Formate l'affichage d'un bénéficiaire."""
#         nom_complet = b.get('nom_complet') or 'Sans nom'
#         type_ben = b.get('type_beneficiaire') or 'AUTRE'
#         source = b.get('source', '')
#         is_benef = b.get('is_beneficiaire', False)
        
#         # ✅ Suffixe pour distinguer la source
#         if source == 'BENEFICIAIRE':
#             suffix = "  ✓"   # déjà enregistré
#         elif source == 'TIERS':
#             suffix = "  (tiers)"   # à créer si utilisé
#         elif source == 'EXPERT':
#             suffix = "  (expert)"
#         else:
#             suffix = ""
        
#         infos = []
#         if b.get('telephone'):
#             infos.append(b['telephone'])
#         elif b.get('portable'):
#             infos.append(b['portable'])
        
#         if b.get('agrement'):
#             infos.append(f"Agrément: {b['agrement']}")
        
#         info_str = f"  ·  {'  ·  '.join(infos)}" if infos else ""
        
#         return f"{nom_complet}  ({type_ben}){suffix}{info_str}"

#     def _get_beneficiaire_icon(self, b: dict):
#         """Icône FontAwesome selon la source."""
#         source = b.get('source', '')
#         type_ben = b.get('type_beneficiaire', '')
        
#         # Priorité : source d'abord
#         if source == 'BENEFICIAIRE':
#             return qta.icon('fa5s.check-circle', color='#16a34a')
#         elif source == 'TIERS':
#             return qta.icon('fa5s.user-friends', color='#2563eb')
#         elif source == 'EXPERT':
#             return qta.icon('fa5s.user-tie', color='#7c3aed')
        
#         # Fallback : type
#         icon_map = {
#             'ASSURE': 'fa5s.user',
#             'GARAGE': 'fa5s.wrench',
#             'AVOCAT': 'fa5s.gavel',
#             'HOPITAL': 'fa5s.hospital',
#         }
#         icon_name = icon_map.get(type_ben, 'fa5s.user-circle')
#         return qta.icon(icon_name, color='#64748b')
    
#     def creer_evaluation(self):
#         """Crée l'évaluation"""
#         try:
#             # ============================================================
#             # VALIDATION
#             # ============================================================
            
#             # Vérifier le type
#             if not self.input_type.currentText():
#                 QMessageBox.warning(self, "Validation", "Veuillez sélectionner un type d'évaluation")
#                 return
            
#             # Vérifier le montant brut
#             brut = self.input_montant_brut.value()
#             if brut <= 0:
#                 QMessageBox.warning(self, "Validation", "Veuillez saisir un montant brut valide")
#                 return
            
#             # Vérifier que le taux est valide
#             taux = self.input_taux.value()
#             if taux < 0 or taux > 100:
#                 QMessageBox.warning(self, "Validation", "Le taux de responsabilité doit être entre 0 et 100%")
#                 return
            
#             # ============================================================
#             # CONSTRUCTION DES DONNÉES
#             # ============================================================
#             data = {
#                 'sinistre_id': self.sinistre_id,
#                 'type_evaluation': self.input_type.currentText(),
#                 'categorie': self.input_categorie.text().strip() or None,
#                 'montant_brut': brut,
#                 'franchise': self.input_franchise.value(),
#                 'taux_responsabilite': taux / 100,
#                 'details': self.input_details.toPlainText().strip() or None,
#                 'created_by': self.user.id if self.user else None
#             }
            
#             # ============================================================
#             # ENVOI
#             # ============================================================
#             print(f"📝 Création évaluation avec les données: {data}")
            
#             result = self.evaluation_controller.creer_evaluation(data)
            
#             if result:
#                 self.evaluation_created.emit(result)
#                 QMessageBox.information(
#                     self,
#                     "Succès",
#                     f"✅ Évaluation créée avec succès !\n\n"
#                     f"📌 N° Évaluation: {result.get('numero_evaluation', 'N/A')}\n"
#                     f"💰 Montant brut: {brut:,.0f} FCFA\n"
#                     f"✅ Montant net: {self._net_calcule:,.0f} FCFA\n"
#                     f"📌 Type: {data['type_evaluation'].replace('_', ' ').title()}\n\n"
#                     f"💡 Une provision a été créée automatiquement."
#                 )
#                 self.accept()
            
#         except Exception as e:
#             print(f"❌ Erreur création évaluation: {e}")
#             import traceback
#             traceback.print_exc()
#             QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")


"""
Dialogue de création d'évaluation — Design v3.0
Source : mission d'expertise validée (expertise OU contre-expertise)
Formule : net = (montant_brut + montant_expert) − franchise
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QDoubleSpinBox, QPushButton, QMessageBox,
    QWidget, QFrame, QScrollArea, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor

from datetime import datetime
import qtawesome as qta


# ═══════════════════════════════════════════════════════════════════
# STYLES
# ═══════════════════════════════════════════════════════════════════

STYLE = """
    QDialog { background: #f4f4f5; }
    QFrame#Card { background: #ffffff; border-radius: 12px; }
    QLabel { background: transparent; }
    QLabel#Title { font-size: 18px; font-weight: 700; color: #18181b; }
    QLabel#Subtitle { font-size: 13px; color: #71717a; }
    QLabel#SectionLabel {
        font-size: 11px; font-weight: 700; color: #3f3f46;
        letter-spacing: 0.5px;
    }

    QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit {
        background: #ffffff;
        border: 1px solid #d4d4d8;
        border-radius: 8px;
        padding: 9px 12px;
        font-size: 13px;
        color: #18181b;
    }
    QLineEdit:focus, QComboBox:focus,
    QDoubleSpinBox:focus, QTextEdit:focus {
        border: 1px solid #2563eb;
    }
    QComboBox::drop-down { border: none; width: 28px; }
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #71717a;
        margin-right: 10px;
    }
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
        width: 0; border: none;
    }

    QPushButton#BtnCancel {
        background: #ffffff; border: 1px solid #d4d4d8;
        border-radius: 8px; padding: 8px 18px;
        font-size: 13px; font-weight: 500; color: #18181b;
    }
    QPushButton#BtnCancel:hover { background: #fafafa; }

    QPushButton#BtnPrimary {
        background: #1d4ed8; border: none;
        border-radius: 8px; padding: 8px 20px;
        font-size: 13px; font-weight: 600; color: #ffffff;
    }
    QPushButton#BtnPrimary:hover { background: #1e40af; }

    QPushButton#BtnClose {
        background: transparent; border: none;
    }
    QPushButton#BtnClose:hover { background: #f4f4f5; border-radius: 6px; }
"""


def _section(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("SectionLabel")
    return lbl


def _field_label(icon_name: str, text: str, required: bool = False) -> QWidget:
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(6)
    ic = QLabel()
    ic.setPixmap(qta.icon(icon_name, color='#71717a').pixmap(QSize(12, 12)))
    ic.setFixedSize(14, 14)
    h.addWidget(ic)
    lbl = QLabel(text + (" *" if required else ""))
    lbl.setStyleSheet("color: #3f3f46; font-size: 12px; font-weight: 500;")
    h.addWidget(lbl)
    h.addStretch()
    return w


# ═══════════════════════════════════════════════════════════════════
# DIALOGUE
# ═══════════════════════════════════════════════════════════════════

class EvaluationDialog(QDialog):
    evaluation_created = Signal(dict)

    def __init__(self, sinistre_id, evaluation_controller, user,
                 sinistre_info=None, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.evaluation_controller = evaluation_controller
        self.user = user
        self.sinistre_info = sinistre_info or {}
        self._net_calcule = 0
        self._missions_validees = []

        self.setWindowTitle("Créer une évaluation")
        self.setModal(True)
        self.setMinimumSize(720, 760)
        self.setStyleSheet(STYLE)

        self.setup_ui()
        self._load_missions_validees()
        self.load_data()

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
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: #f4f4f5; }
            QScrollBar:vertical { background: transparent; width: 8px; }
            QScrollBar::handle:vertical {
                background: #d4d4d8; border-radius: 4px; min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #a1a1aa; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        container = QWidget()
        container.setStyleSheet("background: #f4f4f5;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(24, 24, 24, 24)
        container_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.card = QFrame()
        self.card.setObjectName("Card")
        self.card.setFixedWidth(660)
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        self.card.setGraphicsEffect(shadow)

        cl = QVBoxLayout(self.card)
        cl.setContentsMargins(32, 28, 32, 24)
        cl.setSpacing(18)

        cl.addLayout(self._build_header())
        cl.addWidget(self._separator())

        # ─── MISSION SOURCE ───
        cl.addWidget(_section("MISSION D'EXPERTISE VALIDÉE"))
        self.input_mission = QComboBox()
        self.input_mission.setMinimumHeight(38)
        self.input_mission.currentIndexChanged.connect(self._on_mission_changed)
        cl.addWidget(self.input_mission)

        # Détail mission (affiché sous le combo)
        self.mission_detail = QLabel("")
        self.mission_detail.setWordWrap(True)
        self.mission_detail.setStyleSheet(
            "background: #f0f9ff; border: 1px solid #dbeafe; "
            "border-radius: 8px; padding: 10px; "
            "font-size: 12px; color: #1e40af;"
        )
        self.mission_detail.setVisible(False)
        cl.addWidget(self.mission_detail)

        cl.addWidget(self._separator())

        # ─── TYPE D'ÉVALUATION ───
        cl.addWidget(_section("TYPE D'ÉVALUATION"))
        self.input_type = QComboBox()
        self.input_type.addItems([
            "auto_materiel", "auto_corporel", "incendie", "vol",
            "degats_eau", "rc_generale", "defense_recours",
            "transport_marchandises", "transport_conteneurs"
        ])
        cl.addWidget(self.input_type)

        # ─── CATÉGORIE ───
        cl.addWidget(_section("CATÉGORIE"))
        self.input_categorie = QLineEdit()
        self.input_categorie.setPlaceholderText("Ex : Véhicule, Bâtiment, Marchandise…")
        cl.addWidget(self.input_categorie)

        cl.addWidget(self._separator())

        # ─── MONTANTS ───
        cl.addWidget(_section("MONTANTS"))

        # Montant brut (lecture seule, vient de la mission)
        cl.addWidget(_field_label('fa5s.coins', "Montant brut (issu de la mission)", required=True))
        self.input_montant_brut = QDoubleSpinBox()
        self.input_montant_brut.setRange(0, 999999999)
        self.input_montant_brut.setDecimals(0)
        self.input_montant_brut.setGroupSeparatorShown(True)
        self.input_montant_brut.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.input_montant_brut.setSuffix("  FCFA")
        self.input_montant_brut.setReadOnly(True)
        self.input_montant_brut.setStyleSheet("""
            QDoubleSpinBox {
                background: #f4f4f5;
                border: 1px solid #d4d4d8;
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
                color: #52525b;
            }
        """)
        cl.addWidget(self.input_montant_brut)

        # Montant expert (libre)
        cl.addWidget(_field_label('fa5s.user-tie', "Montant de l'expert"))
        self.input_montant_expert = QDoubleSpinBox()
        self.input_montant_expert.setRange(0, 999999999)
        self.input_montant_expert.setDecimals(0)
        self.input_montant_expert.setSingleStep(10000)
        self.input_montant_expert.setGroupSeparatorShown(True)
        self.input_montant_expert.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.input_montant_expert.setSuffix("  FCFA")
        self.input_montant_expert.valueChanged.connect(self.calculer_net)
        cl.addWidget(self.input_montant_expert)

        # Franchise + Taux
        row = QHBoxLayout()
        row.setSpacing(12)

        col1 = QVBoxLayout()
        col1.setSpacing(4)
        col1.addWidget(_field_label('fa5s.minus-circle', "Franchise"))
        self.input_franchise = QDoubleSpinBox()
        self.input_franchise.setRange(0, 999999999)
        self.input_franchise.setDecimals(0)
        self.input_franchise.setSingleStep(5000)
        self.input_franchise.setGroupSeparatorShown(True)
        self.input_franchise.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.input_franchise.setSuffix("  FCFA")
        self.input_franchise.valueChanged.connect(self.calculer_net)
        col1.addWidget(self.input_franchise)
        row.addLayout(col1, 1)

        col2 = QVBoxLayout()
        col2.setSpacing(4)
        col2.addWidget(_field_label('fa5s.percent', "Taux responsabilité", required=True))
        self.input_taux = QDoubleSpinBox()
        self.input_taux.setRange(0, 100)
        self.input_taux.setSuffix("  %")
        self.input_taux.setValue(100)
        self.input_taux.setSingleStep(5)
        self.input_taux.setButtonSymbols(QDoubleSpinBox.NoButtons)
        # ⚠️ PAS de connexion valueChanged → le taux ne déclenche aucun calcul
        col2.addWidget(self.input_taux)
        row.addLayout(col2, 1)

        cl.addLayout(row)

        # ─── RÉSULTAT ───
        result_card = QFrame()
        result_card.setStyleSheet("""
            QFrame {
                background: #eff6ff;
                border: 1px solid #dbeafe;
                border-radius: 10px;
            }
        """)
        rl = QVBoxLayout(result_card)
        rl.setContentsMargins(16, 14, 16, 14)
        rl.setSpacing(4)

        result_title = QLabel("MONTANT NET")
        result_title.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #2563eb; letter-spacing: 1px;"
        )
        result_title.setAlignment(Qt.AlignCenter)
        rl.addWidget(result_title)

        self.lbl_net = QLabel("0 FCFA")
        self.lbl_net.setStyleSheet(
            "font-size: 22px; font-weight: 800; color: #1e40af;"
        )
        self.lbl_net.setAlignment(Qt.AlignCenter)
        rl.addWidget(self.lbl_net)

        self.lbl_formule = QLabel("Formule : (Brut + Expert) − Franchise")
        self.lbl_formule.setStyleSheet("font-size: 11px; color: #60a5fa;")
        self.lbl_formule.setAlignment(Qt.AlignCenter)
        rl.addWidget(self.lbl_formule)

        cl.addWidget(result_card)

        cl.addWidget(self._separator())

        # ─── DÉTAILS ───
        cl.addWidget(_section("DÉTAILS"))
        self.input_details = QTextEdit()
        self.input_details.setPlaceholderText(
            "Justifications, éléments pris en compte, pièces jointes…"
        )
        self.input_details.setFixedHeight(80)
        cl.addWidget(self.input_details)

        # ─── RÉCAP ───
        summary_card = QFrame()
        summary_card.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        sl = QVBoxLayout(summary_card)
        sl.setContentsMargins(16, 12, 16, 12)

        summary_head = QHBoxLayout()
        summary_head.setSpacing(8)
        ic = QLabel()
        ic.setPixmap(qta.icon('fa5s.clipboard-list', color='#64748b').pixmap(QSize(12, 12)))
        summary_head.addWidget(ic)
        summary_title = QLabel("RÉCAPITULATIF")
        summary_title.setStyleSheet(
            "font-size: 11px; font-weight: 700; color: #3f3f46; letter-spacing: 0.5px;"
        )
        summary_head.addWidget(summary_title)
        summary_head.addStretch()
        sl.addLayout(summary_head)

        self.summary_text = QLabel("—")
        self.summary_text.setWordWrap(True)
        self.summary_text.setStyleSheet("font-size: 12px; color: #52525b;")
        sl.addWidget(self.summary_text)

        cl.addWidget(summary_card)

        # ─── FOOTER ───
        cl.addWidget(self._separator())
        footer = QHBoxLayout()
        footer.addStretch()

        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setObjectName("BtnCancel")
        self.btn_annuler.setCursor(Qt.PointingHandCursor)
        self.btn_annuler.clicked.connect(self.reject)
        footer.addWidget(self.btn_annuler)

        self.btn_creer = QPushButton("Créer l'évaluation")
        self.btn_creer.setObjectName("BtnPrimary")
        self.btn_creer.setCursor(Qt.PointingHandCursor)
        self.btn_creer.clicked.connect(self.creer_evaluation)
        footer.addWidget(self.btn_creer)
        cl.addLayout(footer)

        container_layout.addWidget(self.card)
        scroll.setWidget(container)
        root.addWidget(scroll)

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        block = QVBoxLayout()
        block.setSpacing(2)
        num = self.sinistre_info.get('numero_sinistre', 'N/A')
        title = QLabel(f"Évaluation — Sinistre {num}")
        title.setObjectName("Title")
        block.addWidget(title)
        subtitle = QLabel("Basée sur une mission d'expertise validée")
        subtitle.setObjectName("Subtitle")
        block.addWidget(subtitle)
        row.addLayout(block, 1)

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

    # ═══════════════════════════════════════════════════════════════
    # CHARGEMENT DES MISSIONS VALIDÉES
    # ═══════════════════════════════════════════════════════════════
    def _load_missions_validees(self):
        """Charge les missions validées (expertise + contre-expertise) du sinistre"""
        try:
            missions = self.evaluation_controller.get_missions_validees(self.sinistre_id) or []
            self._missions_validees = missions

            self.input_mission.blockSignals(True)
            self.input_mission.clear()
            self.input_mission.addItem("— Sélectionner une mission validée —", None)

            if not missions:
                self.input_mission.addItem(
                    "⚠️ Aucune mission validée sur ce sinistre", None
                )
                self.input_mission.setEnabled(False)
                self.btn_creer.setEnabled(False)
            else:
                for m in missions:
                    num = m.get('numero_mission', 'N/A')
                    typ = m.get('type_mission_libelle') or m.get('type_mission_code', '')
                    expert = m.get('expert_nom') or 'N/A'
                    montant = float(m.get('montant_estime') or 0)
                    label = (
                        f"{num}  ·  {typ}  ·  {expert}  ·  "
                        f"{montant:,.0f} FCFA".replace(',', ' ')
                    )
                    self.input_mission.addItem(label, m)

            self.input_mission.blockSignals(False)
        except Exception as e:
            print(f"[EvaluationDialog] load_missions_validees: {e}")

    def _on_mission_changed(self, index):
        """Quand une mission est choisie, on remplit le montant brut + type d'évaluation"""
        mission = self.input_mission.currentData()
        if not mission:
            self.mission_detail.setVisible(False)
            self.input_montant_brut.setValue(0)
            self._recalc()
            return

        # Remplir le montant brut
        montant = float(mission.get('montant_estime') or 0)
        self.input_montant_brut.setValue(montant)

        # Auto-sélection du type d'évaluation selon le type d'expertise
        type_exp = (mission.get('type_expertise') or '').lower()
        if type_exp in [self.input_type.itemText(i) for i in range(self.input_type.count())]:
            self.input_type.setCurrentText(type_exp)

        # Afficher le détail
        num = mission.get('numero_mission', 'N/A')
        typ = mission.get('type_mission_libelle') or 'N/A'
        expert = mission.get('expert_nom') or 'N/A'
        parent = mission.get('mission_parente_numero')
        parent_line = f"\n↳ Contre-expertise de {parent}" if parent else ""
        date_val = str(mission.get('date_validation', ''))[:10] or 'N/A'

        self.mission_detail.setText(
            f"<b>Mission :</b> {num}{parent_line}<br>"
            f"<b>Type :</b> {typ}<br>"
            f"<b>Expert :</b> {expert}<br>"
            f"<b>Montant :</b> {montant:,.0f} FCFA<br>"
            f"<b>Validée le :</b> {date_val}".replace(',', ' ')
        )
        self.mission_detail.setVisible(True)

        self._recalc()

    # ═══════════════════════════════════════════════════════════════
    # CALCUL (sans boucle de signaux)
    # ═══════════════════════════════════════════════════════════════
    def load_data(self):
        self._recalc()

    def _recalc(self):
        """
        Recalcule le net SANS déclencher de boucle :
        - Aucun signal n'est émis vers les champs modifiés
        - On met à jour directement l'affichage
        """
        brut = self.input_montant_brut.value()
        expert_amt = self.input_montant_expert.value()
        franchise = self.input_franchise.value()

        net = max(0, (brut + expert_amt) - franchise)
        self._net_calcule = net
        self.lbl_net.setText(f"{net:,.0f} FCFA".replace(',', ' '))
        self._update_summary()

    def calculer_net(self):
        """Alias conservé pour compatibilité (déclenché par valueChanged)"""
        self._recalc()

    def _update_summary(self):
        parts = []

        mission = self.input_mission.currentData()
        if mission:
            num = mission.get('numero_mission', 'N/A')
            parts.append(f"Mission : <b>{num}</b>")

        type_text = self.input_type.currentText()
        if type_text:
            parts.append(f"Type : <b>{type_text.replace('_', ' ').title()}</b>")

        cat = self.input_categorie.text().strip()
        if cat:
            parts.append(f"Catégorie : {cat}")

        brut = self.input_montant_brut.value()
        expert_amt = self.input_montant_expert.value()
        franchise = self.input_franchise.value()
        taux = self.input_taux.value()

        if brut > 0:
            parts.append(f"Brut : {brut:,.0f} FCFA".replace(',', ' '))
        if expert_amt > 0:
            parts.append(f"Expert : {expert_amt:,.0f} FCFA".replace(',', ' '))
        if franchise > 0:
            parts.append(f"Franchise : {franchise:,.0f} FCFA".replace(',', ' '))
        if taux > 0:
            parts.append(f"Taux (info) : {taux:.0f} %")

        if brut > 0:
            net = max(0, (brut + expert_amt) - franchise)
            parts.append(f"Net : <b>{net:,.0f} FCFA</b>".replace(',', ' '))

        self.summary_text.setText("<br>".join(parts) if parts else "—")

    # ═══════════════════════════════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════════════════════════════
    def creer_evaluation(self):
        try:
            mission = self.input_mission.currentData()
            if not mission:
                QMessageBox.warning(
                    self, "Validation",
                    "Sélectionnez une mission validée pour baser l'évaluation"
                )
                return

            brut = self.input_montant_brut.value()
            if brut <= 0:
                QMessageBox.warning(
                    self, "Validation",
                    "La mission sélectionnée ne contient pas de montant valide"
                )
                return

            taux = self.input_taux.value()
            if taux < 0 or taux > 100:
                QMessageBox.warning(
                    self, "Validation", "Le taux doit être entre 0 et 100 %"
                )
                return

            data = {
                'sinistre_id': self.sinistre_id,
                'mission_id': mission.get('id'),
                'type_evaluation': self.input_type.currentText(),
                'categorie': self.input_categorie.text().strip() or None,
                'montant_brut': brut,
                'montant_expert': self.input_montant_expert.value() or None,
                'franchise': self.input_franchise.value(),
                'taux_responsabilite': taux / 100,
                'details': self.input_details.toPlainText().strip() or None,
                'created_by': self._get_user_id(),
            }

            result = self.evaluation_controller.creer_evaluation(data)
            if result:
                self.evaluation_created.emit(result)
                QMessageBox.information(
                    self, "Succès",
                    f"Évaluation {result.get('numero_evaluation')} créée\n"
                    f"Montant net : {self._net_calcule:,.0f} FCFA".replace(',', ' ')
                )
                self.accept()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", str(e))