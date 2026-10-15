"""
Dialogue de répartition d'un recours encaissé entre les parties prenantes.
Règle CDC Tome 6 §8 (REC-020) : Σ répartitions = montant encaissé.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QDoubleSpinBox, QPushButton, QMessageBox,
    QFrame, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from typing import Dict


class RepartitionRecoursDialog(QDialog):
    """Dialogue de saisie de la répartition d'un recours"""
    
    repartition_validee = Signal(list)  # Liste des répartitions créées
    
    def __init__(self, recours_id, recours_info, recours_controller, user, parent=None):
        super().__init__(parent)
        self.recours_id = recours_id
        self.recours_info = recours_info or {}
        self.recours_controller = recours_controller
        self.user = user
        
        self.setWindowTitle("Répartition du recours")
        self.setModal(True)
        self.setMinimumWidth(700)
        
        self.inputs = {}  # {type_beneficiaire: QDoubleSpinBox}
        self.labels_montant = {}  # {type_beneficiaire: QLabel}
        
        self.setup_ui()
        self.charger_quoteparts_defaut()
        self._update_totaux()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ============================================================
        # EN-TÊTE
        # ============================================================
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 10px;
                padding: 14px;
                border: 1px solid #e2e8f0;
            }
        """)
        header_layout = QVBoxLayout(header)
        
        title = QLabel("📊 Répartition du recours")
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        self.lbl_recours = QLabel(f"Recours: {self.recours_info.get('numero_recours', 'N/A')}")
        info_layout.addWidget(self.lbl_recours)
        
        self.lbl_debiteur = QLabel(f"Débiteur: {self.recours_info.get('debiteur_nom', 'N/A')}")
        info_layout.addWidget(self.lbl_debiteur)
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        # Montant encaissé en gros
        montant_encaisse = float(self.recours_info.get('montant_encaisse', 0) or 0)
        self.lbl_montant_encaisse = QLabel(
            f"💰 Montant encaissé : {montant_encaisse:,.0f} FCFA"
        )
        self.lbl_montant_encaisse.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #22c55e; margin-top: 8px;"
        )
        header_layout.addWidget(self.lbl_montant_encaisse)
        
        layout.addWidget(header)
        
        # ============================================================
        # FORMULAIRE DE RÉPARTITION
        # ============================================================
        form_group = QGroupBox("Répartition par bénéficiaire")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 10px;
                color: #1a73e8;
            }
        """)
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(12)
        
        # Colonnes : Type | Quote-part (%) | Montant calculé
        row_header = QHBoxLayout()
        lbl_type = QLabel("Type de bénéficiaire")
        lbl_type.setStyleSheet("font-size: 11px; color: #64748b; font-weight: bold;")
        row_header.addWidget(lbl_type, 3)
        
        lbl_quote = QLabel("Quote-part (%)")
        lbl_quote.setStyleSheet("font-size: 11px; color: #64748b; font-weight: bold;")
        row_header.addWidget(lbl_quote, 2)
        
        lbl_montant = QLabel("Montant")
        lbl_montant.setStyleSheet("font-size: 11px; color: #64748b; font-weight: bold;")
        row_header.addWidget(lbl_montant, 3)
        
        form_layout.addRow(row_header)
        
        # 4 lignes : CLIENT, COMPAGNIE, HONORAIRES, COASSUREUR
        for type_ben, libelle, color in [
            ('CLIENT', '👤 Client', '#22c55e'),
            ('COMPAGNIE', '🏢 Compagnie', '#1a73e8'),
            ('HONORAIRES', '💼 Honoraires', '#f59e0b'),
            ('COASSUREUR', '🤝 Coassureurs', '#8b5cf6'),
        ]:
            form_layout.addRow(self._make_ligne(type_ben, libelle, color))
        
        layout.addWidget(form_group)
        
        # ============================================================
        # TOTAUX
        # ============================================================
        total_frame = QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        total_layout = QHBoxLayout(total_frame)
        
        self.lbl_total_quote = QLabel("Σ Quote-parts : 0.00 %")
        self.lbl_total_quote.setStyleSheet("font-size: 13px; font-weight: bold;")
        total_layout.addWidget(self.lbl_total_quote)
        
        total_layout.addStretch()
        
        self.lbl_total_montant = QLabel("Σ Montants : 0 FCFA")
        self.lbl_total_montant.setStyleSheet("font-size: 13px; font-weight: bold; color: #1a73e8;")
        total_layout.addWidget(self.lbl_total_montant)
        
        layout.addWidget(total_frame)
        
        # Indicateur de validation
        self.lbl_validation = QLabel("")
        self.lbl_validation.setStyleSheet("font-size: 12px; padding: 8px;")
        self.lbl_validation.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_validation)
        
        # ============================================================
        # BOUTONS
        # ============================================================
        btn_layout = QHBoxLayout()
        
        # Bouton réinitialiser
        self.btn_reinit = QPushButton("🔄 Réinitialiser")
        self.btn_reinit.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                background-color: #f1f5f9;
                color: #64748b;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        self.btn_reinit.clicked.connect(self.charger_quoteparts_defaut)
        btn_layout.addWidget(self.btn_reinit)
        
        btn_layout.addStretch()
        
        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                border-radius: 8px;
                font-weight: bold;
                background-color: #f1f5f9;
                color: #64748b;
                border: none;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        self.btn_annuler.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_annuler)
        
        self.btn_valider = QPushButton("✅ Valider la répartition")
        self.btn_valider.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 10px 40px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #1557b0; }
            QPushButton:disabled {
                background-color: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self.btn_valider.clicked.connect(self.valider_repartition)
        btn_layout.addWidget(self.btn_valider)
        
        layout.addLayout(btn_layout)
    
    def _make_ligne(self, type_ben: str, libelle: str, color: str) -> QWidget:
        """Crée une ligne de saisie pour un type de bénéficiaire"""
        widget = QWidget()
        row = QHBoxLayout(widget)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        
        # Icône + label
        lbl = QLabel(libelle)
        lbl.setStyleSheet(f"font-size: 13px; color: {color}; font-weight: bold;")
        row.addWidget(lbl, 3)
        
        # Spinbox pour quote-part
        spin = QDoubleSpinBox()
        spin.setRange(0, 100)
        spin.setDecimals(2)
        spin.setSuffix(" %")
        spin.setValue(0)
        spin.setStyleSheet("""
            QDoubleSpinBox {
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
                background-color: white;
            }
            QDoubleSpinBox:focus { border: 2px solid #1a73e8; }
        """)
        spin.valueChanged.connect(self._update_totaux)
        row.addWidget(spin, 2)
        
        self.inputs[type_ben] = spin
        
        # Label montant calculé
        lbl_montant = QLabel("—")
        lbl_montant.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #1a73e8;
            background-color: #f0f9ff;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #bae6fd;
        """)
        lbl_montant.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(lbl_montant, 3)
        
        self.labels_montant[type_ben] = lbl_montant
        
        return widget
    
    # ============================================================
    # LOGIQUE
    # ============================================================
    
    def charger_quoteparts_defaut(self):
        """Charge les quote-parts par défaut depuis les paramètres"""
        try:
            defaults = self.recours_controller.get_quoteparts_defaut()
            for type_ben, quote in defaults.items():
                if type_ben in self.inputs:
                    self.inputs[type_ben].setValue(quote)
            self._update_totaux()
        except Exception as e:
            print(f"❌ Erreur chargement quote-parts défaut: {e}")
    
    def _update_totaux(self):
        """Met à jour les totaux en temps réel"""
        total_quote = sum(inp.value() for inp in self.inputs.values())
        montant_encaisse = float(self.recours_info.get('montant_encaisse', 0) or 0)
        
        total_montant = 0
        for type_ben, spin in self.inputs.items():
            quote = spin.value()
            montant = round(montant_encaisse * quote / 100, 2)
            total_montant += montant
            self.labels_montant[type_ben].setText(f"{montant:,.0f} FCFA")
        
        # Mise à jour labels
        self.lbl_total_quote.setText(f"Σ Quote-parts : {total_quote:.2f} %")
        self.lbl_total_montant.setText(f"Σ Montants : {total_montant:,.0f} FCFA")
        
        # Validation
        ecart_quote = abs(total_quote - 100.0)
        ecart_montant = abs(total_montant - montant_encaisse)
        
        if ecart_quote < 0.01 and ecart_montant < 1:
            self.lbl_validation.setText("✅ Répartition valide (Σ = 100%)")
            self.lbl_validation.setStyleSheet("""
                color: #166534;
                background-color: #dcfce7;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            """)
            self.btn_valider.setEnabled(True)
        else:
            if ecart_quote >= 0.01:
                self.lbl_validation.setText(
                    f"⚠️ La somme des quote-parts doit être égale à 100% "
                    f"(actuel : {total_quote:.2f}%)"
                )
            else:
                self.lbl_validation.setText(
                    f"⚠️ La somme des montants ({total_montant:,.0f}) "
                    f"ne correspond pas au montant encaissé ({montant_encaisse:,.0f})"
                )
            self.lbl_validation.setStyleSheet("""
                color: #92400e;
                background-color: #fef3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            """)
            self.btn_valider.setEnabled(False)
    
    def valider_repartition(self):
        """Valide la répartition auprès du contrôleur"""
        try:
            quote_parts = {
                type_ben: spin.value()
                for type_ben, spin in self.inputs.items()
                if spin.value() > 0
            }
            
            if not quote_parts:
                QMessageBox.warning(self, "Validation", "Aucune quote-part saisie")
                return
            
            result = self.recours_controller.calculer_repartition(
                self.recours_id,
                quote_parts,
            )
            
            if result:
                self.repartition_validee.emit(result)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Répartition enregistrée avec succès !\n\n"
                    f"📊 {len(result)} part(s) créée(s)"
                )
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", "Échec de la répartition")
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur : {str(e)}")