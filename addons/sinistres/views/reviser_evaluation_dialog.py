"""
Dialogue de révision d'évaluation avec historisation
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from datetime import datetime


class ReviserEvaluationDialog(QDialog):
    """Dialogue de révision d'évaluation avec historisation"""
    
    evaluation_revised = Signal(dict)  # Émis quand l'évaluation est révisée
    
    def __init__(self, evaluation_id, evaluation_info, evaluation_controller, user, parent=None):
        super().__init__(parent)
        self.evaluation_id = evaluation_id
        self.evaluation_info = evaluation_info or {}
        self.evaluation_controller = evaluation_controller
        self.user = user
        
        self.setWindowTitle("Réviser une évaluation")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # ============================================================
        # EN-TÊTE AVEC INFOS ÉVALUATION
        # ============================================================
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #e2e8f0;
            }
            QLabel {
                color: #1e293b;
                font-size: 12px;
            }
            QLabel.title {
                font-weight: bold;
                font-size: 14px;
                color: #1a73e8;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("✏️ Révision d'évaluation")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        
        self.lbl_evaluation = QLabel(f"Évaluation: {self.evaluation_info.get('numero_evaluation', 'N/A')}")
        info_layout.addWidget(self.lbl_evaluation)
        
        self.lbl_type = QLabel(f"Type: {self.evaluation_info.get('type_evaluation', 'N/A')}")
        info_layout.addWidget(self.lbl_type)
        
        self.lbl_statut = QLabel(f"Statut: {'✅ Validée' if self.evaluation_info.get('est_validee') else '⏳ Non validée'}")
        statut_color = "#22c55e" if self.evaluation_info.get('est_validee') else "#f59e0b"
        self.lbl_statut.setStyleSheet(f"color: {statut_color}; font-weight: bold;")
        info_layout.addWidget(self.lbl_statut)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        layout.addWidget(header_frame)
        
        # ============================================================
        # SECTION 1: VALEURS ACTUELLES
        # ============================================================
        current_group = QGroupBox("Valeurs actuelles")
        current_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        current_layout = QFormLayout(current_group)
        current_layout.setSpacing(10)
        
        self.lbl_brut_actuel = QLabel(f"{self.evaluation_info.get('montant_brut', 0):,.0f} FCFA")
        self.lbl_brut_actuel.setStyleSheet("font-weight: bold; color: #64748b;")
        current_layout.addRow("Montant brut actuel:", self.lbl_brut_actuel)
        
        self.lbl_franchise_actuel = QLabel(f"{self.evaluation_info.get('franchise', 0):,.0f} FCFA")
        self.lbl_franchise_actuel.setStyleSheet("font-weight: bold; color: #64748b;")
        current_layout.addRow("Franchise actuelle:", self.lbl_franchise_actuel)
        
        self.lbl_taux_actuel = QLabel(f"{self.evaluation_info.get('taux_responsabilite', 1) * 100:.0f}%")
        self.lbl_taux_actuel.setStyleSheet("font-weight: bold; color: #64748b;")
        current_layout.addRow("Taux actuel:", self.lbl_taux_actuel)
        
        self.lbl_net_actuel = QLabel(f"{self.evaluation_info.get('montant_net', 0):,.0f} FCFA")
        self.lbl_net_actuel.setStyleSheet("font-weight: bold; color: #1a73e8; font-size: 14px;")
        current_layout.addRow("Montant net actuel:", self.lbl_net_actuel)
        
        layout.addWidget(current_group)
        
        # ============================================================
        # SECTION 2: NOUVELLES VALEURS
        # ============================================================
        new_group = QGroupBox("Nouvelles valeurs")
        new_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #1a73e8;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #1a73e8;
            }
        """)
        new_layout = QFormLayout(new_group)
        new_layout.setSpacing(12)
        
        # Nouveau montant brut
        self.input_nouveau_brut = QDoubleSpinBox()
        self.input_nouveau_brut.setRange(0, 999999999)
        self.input_nouveau_brut.setPrefix("FCFA ")
        self.input_nouveau_brut.setDecimals(0)
        self.input_nouveau_brut.setSingleStep(10000)
        self.input_nouveau_brut.setValue(self.evaluation_info.get('montant_brut', 0))
        self.input_nouveau_brut.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        self.input_nouveau_brut.valueChanged.connect(self.calculer_nouveau_net)
        new_layout.addRow("Nouveau montant brut *:", self.input_nouveau_brut)
        
        # Nouvelle franchise
        self.input_nouvelle_franchise = QDoubleSpinBox()
        self.input_nouvelle_franchise.setRange(0, 999999999)
        self.input_nouvelle_franchise.setPrefix("FCFA ")
        self.input_nouvelle_franchise.setDecimals(0)
        self.input_nouvelle_franchise.setSingleStep(5000)
        self.input_nouvelle_franchise.setValue(self.evaluation_info.get('franchise', 0))
        self.input_nouvelle_franchise.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_nouvelle_franchise.valueChanged.connect(self.calculer_nouveau_net)
        new_layout.addRow("Nouvelle franchise:", self.input_nouvelle_franchise)
        
        # Nouveau taux
        self.input_nouveau_taux = QDoubleSpinBox()
        self.input_nouveau_taux.setRange(0, 100)
        self.input_nouveau_taux.setSuffix("%")
        self.input_nouveau_taux.setValue(self.evaluation_info.get('taux_responsabilite', 1) * 100)
        self.input_nouveau_taux.setSingleStep(5)
        self.input_nouveau_taux.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_nouveau_taux.valueChanged.connect(self.calculer_nouveau_net)
        new_layout.addRow("Nouveau taux:", self.input_nouveau_taux)
        
        # Résultat
        result_frame = QFrame()
        result_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 6px;
                padding: 10px;
            }
            QLabel {
                color: #0369a1;
                font-size: 14px;
            }
            QLabel.value {
                font-weight: bold;
                font-size: 18px;
                color: #1a73e8;
            }
        """)
        result_layout = QVBoxLayout(result_frame)
        
        self.lbl_nouveau_net = QLabel("Nouveau montant net: 0 FCFA")
        self.lbl_nouveau_net.setStyleSheet("font-weight: bold; font-size: 18px; color: #1a73e8;")
        self.lbl_nouveau_net.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(self.lbl_nouveau_net)
        
        # Différence
        self.lbl_difference = QLabel("Variation: 0 FCFA (0%)")
        self.lbl_difference.setStyleSheet("color: #64748b; font-size: 12px;")
        self.lbl_difference.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(self.lbl_difference)
        
        new_layout.addRow("", result_frame)
        
        layout.addWidget(new_group)
        
        # ============================================================
        # SECTION 3: MOTIF DE LA RÉVISION
        # ============================================================
        self.input_motif = QTextEdit()
        self.input_motif.setPlaceholderText("""
Motif de la révision:

- Nouveau dommage découvert
- Expertise complémentaire
- Décision judiciaire
- Erreur de calcul
- Autre...
        """.strip())
        self.input_motif.setMaximumHeight(80)
        self.input_motif.setStyleSheet("""
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 8px;
            font-family: monospace;
            font-size: 12px;
        """)
        layout.addWidget(QLabel("Motif de la révision *:"))
        layout.addWidget(self.input_motif)
        
        # ============================================================
        # SECTION 4: RÉCAPITULATIF
        # ============================================================
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 8px;
                padding: 12px;
            }
            QLabel {
                color: #0369a1;
                font-size: 12px;
            }
            QLabel.title {
                font-weight: bold;
                font-size: 13px;
            }
        """)
        summary_layout = QVBoxLayout(self.summary_frame)
        
        summary_title = QLabel("📋 Récapitulatif de la révision")
        summary_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #0369a1;")
        summary_layout.addWidget(summary_title)
        
        self.summary_text = QLabel("Remplissez les champs pour voir le récapitulatif")
        self.summary_text.setStyleSheet("color: #0369a1;")
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(self.summary_frame)
        
        # ============================================================
        # BOUTONS
        # ============================================================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                border-radius: 8px;
                font-weight: bold;
                background-color: #f1f5f9;
                color: #64748b;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_annuler.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_annuler)
        
        self.btn_reviser = QPushButton("✅ Valider la révision")
        self.btn_reviser.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 10px 40px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_reviser.clicked.connect(self.reviser_evaluation)
        btn_layout.addWidget(self.btn_reviser)
        
        layout.addLayout(btn_layout)
        
        # ============================================================
        # CONNEXIONS
        # ============================================================
        self.input_nouveau_brut.valueChanged.connect(self._update_summary)
        self.input_nouvelle_franchise.valueChanged.connect(self._update_summary)
        self.input_nouveau_taux.valueChanged.connect(self._update_summary)
        self.input_motif.textChanged.connect(self._update_summary)
        
        # Calcul initial
        self.calculer_nouveau_net()
        self._update_summary()
    
    def calculer_nouveau_net(self):
        """Calcule le nouveau montant net"""
        brut = self.input_nouveau_brut.value()
        franchise = self.input_nouvelle_franchise.value()
        taux = self.input_nouveau_taux.value() / 100
        nouveau_net = (brut - franchise) * taux
        
        # Récupérer l'ancien net
        ancien_net = self.evaluation_info.get('montant_net', 0)
        variation = nouveau_net - ancien_net
        variation_pct = (variation / ancien_net * 100) if ancien_net > 0 else 0
        
        # Mettre à jour l'affichage
        self.lbl_nouveau_net.setText(f"Nouveau montant net: {nouveau_net:,.0f} FCFA")
        
        # Couleur de la variation
        if variation > 0:
            color = "#22c55e"  # Vert
            signe = "+"
        elif variation < 0:
            color = "#ef4444"  # Rouge
            signe = ""
        else:
            color = "#64748b"  # Gris
            signe = ""
        
        self.lbl_difference.setText(
            f"Variation: {signe}{variation:,.0f} FCFA ({signe}{variation_pct:.1f}%)"
        )
        self.lbl_difference.setStyleSheet(f"color: {color}; font-size: 12px;")
        
        self._nouveau_net = nouveau_net
        return nouveau_net
    
    def _update_summary(self):
        """Met à jour le récapitulatif"""
        lines = []
        
        # Anciennes valeurs
        ancien_brut = self.evaluation_info.get('montant_brut', 0)
        ancien_net = self.evaluation_info.get('montant_net', 0)
        lines.append(f"📊 Ancien brut: {ancien_brut:,.0f} FCFA")
        lines.append(f"📊 Ancien net: {ancien_net:,.0f} FCFA")
        lines.append("")
        
        # Nouvelles valeurs
        nouveau_brut = self.input_nouveau_brut.value()
        nouveau_net = self.calculer_nouveau_net()
        lines.append(f"🔄 Nouveau brut: {nouveau_brut:,.0f} FCFA")
        lines.append(f"🔄 Nouveau net: {nouveau_net:,.0f} FCFA")
        lines.append("")
        
        # Différence
        variation = nouveau_net - ancien_net
        if variation > 0:
            lines.append(f"📈 Augmentation: +{variation:,.0f} FCFA")
        elif variation < 0:
            lines.append(f"📉 Diminution: {variation:,.0f} FCFA")
        else:
            lines.append("➖ Aucune variation")
        
        # Motif
        motif = self.input_motif.toPlainText().strip()
        if motif:
            lines.append("")
            lines.append(f"📝 Motif: {motif[:50]}...")
        else:
            lines.append("⚠️ Motif non saisi")
        
        self.summary_text.setText("\n".join(lines))
    
    def reviser_evaluation(self):
        """Valide la révision"""
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
            # Vérifier le motif
            motif = self.input_motif.toPlainText().strip()
            if not motif:
                QMessageBox.warning(self, "Validation", "Veuillez saisir un motif pour la révision")
                return
            
            if len(motif) < 5:
                QMessageBox.warning(
                    self, 
                    "Validation", 
                    "Le motif est trop court (minimum 5 caractères)"
                )
                return
            
            # Vérifier le montant brut
            brut = self.input_nouveau_brut.value()
            if brut <= 0:
                QMessageBox.warning(self, "Validation", "Veuillez saisir un montant brut valide")
                return
            
            # Vérifier que l'évaluation n'est pas validée
            if self.evaluation_info.get('est_validee'):
                QMessageBox.warning(
                    self,
                    "Attention",
                    "Cette évaluation est déjà validée et ne peut plus être révisée."
                )
                return
            
            # ============================================================
            # CONSTRUCTION DES DONNÉES
            # ============================================================
            data = {
                'montant_brut': brut,
                'franchise': self.input_nouvelle_franchise.value(),
                'taux_responsabilite': self.input_nouveau_taux.value() / 100,
                'motif': motif,
                'updated_by': self.user.id if self.user else None
            }
            
            # ============================================================
            # ENVOI
            # ============================================================
            print(f"📝 Révision évaluation avec les données: {data}")
            
            result = self.evaluation_controller.reviser_evaluation(
                self.evaluation_id,
                data
            )
            
            if result:
                self.evaluation_revised.emit({
                    'evaluation_id': self.evaluation_id,
                    'ancien_brut': self.evaluation_info.get('montant_brut', 0),
                    'nouveau_brut': brut,
                    'ancien_net': self.evaluation_info.get('montant_net', 0),
                    'nouveau_net': self._nouveau_net,
                    'motif': motif
                })
                
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Évaluation révisée avec succès !\n\n"
                    f"📌 N° Évaluation: {self.evaluation_info.get('numero_evaluation', 'N/A')}\n"
                    f"💰 Ancien montant: {self.evaluation_info.get('montant_net', 0):,.0f} FCFA\n"
                    f"💰 Nouveau montant: {self._nouveau_net:,.0f} FCFA\n"
                    f"📝 Motif: {motif[:50]}{'...' if len(motif) > 50 else ''}\n\n"
                    f"💡 Une nouvelle provision a été créée automatiquement."
                )
                self.accept()
            
        except Exception as e:
            print(f"❌ Erreur révision évaluation: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la révision: {str(e)}")