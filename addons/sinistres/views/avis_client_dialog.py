"""
Dialog pour enregistrer l'avis du client (acceptation / refus)
avec pièce jointe (PDF ou photo).
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QTextEdit, QFileDialog,
    QMessageBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
import qtawesome as qta
import os


class AvisClientDialog(QDialog):
    """Dialog de dépôt d'avis client."""

    def __init__(self, evaluation: dict, controller, parent=None):
        super().__init__(parent)
        self.evaluation = evaluation
        self.controller = controller
        self.document_path = None
        self.document_nom = None

        self.setWindowTitle(
            f"Avis du client — {evaluation.get('numero_evaluation', '')}"
        )
        self.setMinimumWidth(560)
        self.setStyleSheet("""
            QDialog { background: white; }
            QLabel { color: #1e293b; }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # ─── En-tête ───
        header = QHBoxLayout()
        header.setSpacing(10)

        icon = QLabel()
        icon.setPixmap(qta.icon('fa5s.user-check', color='#2563eb').pixmap(QSize(24, 24)))
        header.addWidget(icon)

        title = QLabel("Avis du client sur la proposition")
        title.setStyleSheet("font-size: 17px; font-weight: 700; color: #0f172a;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # ─── Détails évaluation ───
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(14, 12, 14, 12)
        info_layout.setSpacing(4)

        info_layout.addWidget(QLabel(
            f"<b>Montant proposé :</b> "
            f"{float(self.evaluation.get('montant_net', 0)):,.0f} FCFA".replace(",", " ")
        ))
        info_layout.addWidget(QLabel(
            f"<b>Référence :</b> {self.evaluation.get('numero_evaluation', 'N/A')}"
        ))
        layout.addWidget(info_frame)

        # ─── Choix accepte / refuse ───
        decision_lbl = QLabel("<b>Décision du client :</b>")
        layout.addWidget(decision_lbl)

        self.radio_accepte = QRadioButton("  ✅ Accepter la proposition")
        self.radio_refuse = QRadioButton("  ❌ Refuser la proposition")
        self.radio_accepte.setStyleSheet("font-size: 13px; padding: 6px;")
        self.radio_refuse.setStyleSheet("font-size: 13px; padding: 6px;")
        self.radio_accepte.setChecked(True)

        grp = QButtonGroup(self)
        grp.addButton(self.radio_accepte)
        grp.addButton(self.radio_refuse)

        layout.addWidget(self.radio_accepte)
        layout.addWidget(self.radio_refuse)

        # ─── Pièce jointe ───
        pj_lbl = QLabel("<b>Pièce jointe (obligatoire) :</b>")
        layout.addWidget(pj_lbl)

        self.lbl_fichier = QLabel("Aucun fichier sélectionné")
        self.lbl_fichier.setStyleSheet(
            "color: #94a3b8; font-size: 12px; padding: 6px;"
        )
        layout.addWidget(self.lbl_fichier)

        btn_row = QHBoxLayout()
        self.btn_choisir = QPushButton("  Choisir un fichier")
        self.btn_choisir.setIcon(qta.icon('fa5s.paperclip', color='white'))
        self.btn_choisir.setIconSize(QSize(12, 12))
        self.btn_choisir.setStyleSheet("""
            QPushButton {
                background: #2563eb; color: white;
                border: none; border-radius: 8px;
                padding: 8px 16px; font-weight: 600;
                text-align: left;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        self.btn_choisir.clicked.connect(self._choisir_fichier)
        btn_row.addWidget(self.btn_choisir)

        self.lbl_apercu = QLabel()
        self.lbl_apercu.setFixedHeight(60)
        btn_row.addWidget(self.lbl_apercu, 1)

        layout.addLayout(btn_row)

        # ─── Commentaire ───
        comment_lbl = QLabel("<b>Commentaire (optionnel) :</b>")
        layout.addWidget(comment_lbl)

        self.txt_commentaire = QTextEdit()
        self.txt_commentaire.setPlaceholderText(
            "Motif du refus, précisions, etc."
        )
        self.txt_commentaire.setMaximumHeight(80)
        self.txt_commentaire.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
            }
            QTextEdit:focus { border-color: #3b82f6; }
        """)
        layout.addWidget(self.txt_commentaire)

        layout.addStretch()

        # ─── Boutons ───
        btn_row2 = QHBoxLayout()
        btn_row2.addStretch()

        btn_annuler = QPushButton("Annuler")
        btn_annuler.setStyleSheet("""
            QPushButton {
                background: white; color: #64748b;
                border: 1px solid #e2e8f0; border-radius: 8px;
                padding: 8px 16px; font-weight: 600;
            }
            QPushButton:hover { background: #f8fafc; }
        """)
        btn_annuler.clicked.connect(self.reject)
        btn_row2.addWidget(btn_annuler)

        btn_valider = QPushButton("  Enregistrer l'avis")
        btn_valider.setIcon(qta.icon('fa5s.check', color='white'))
        btn_valider.setIconSize(QSize(12, 12))
        btn_valider.setStyleSheet("""
            QPushButton {
                background: #16a34a; color: white;
                border: none; border-radius: 8px;
                padding: 8px 20px; font-weight: 700;
                text-align: left;
            }
            QPushButton:hover { background: #15803d; }
        """)
        btn_valider.clicked.connect(self._valider)
        btn_row2.addWidget(btn_valider)

        layout.addLayout(btn_row2)

    def _choisir_fichier(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner la pièce jointe de l'avis client",
            "",
            "Documents (*.pdf *.jpg *.jpeg *.png *.webp);;Tous (*.*)"
        )
        if not path:
            return

        # Vérifier extension
        ext = os.path.splitext(path)[1].lower()
        if ext not in ('.pdf', '.jpg', '.jpeg', '.png', '.webp'):
            QMessageBox.warning(
                self, "Format non supporté",
                "Formats acceptés : PDF, JPG, JPEG, PNG, WEBP"
            )
            return

        self.document_path = path
        self.document_nom = os.path.basename(path)
        self.lbl_fichier.setText(f"📎 {self.document_nom}")
        self.lbl_fichier.setStyleSheet("color: #16a34a; font-size: 12px; padding: 6px;")

        # Aperçu image
        if ext != '.pdf':
            pix = QPixmap(path).scaledToHeight(60, Qt.SmoothTransformation)
            self.lbl_apercu.setPixmap(pix)
        else:
            self.lbl_apercu.setPixmap(
                qta.icon('fa5s.file-pdf', color='#dc2626').pixmap(48, 48)
            )

    # def _valider(self):
    #     if not self.document_path:
    #         QMessageBox.warning(
    #             self, "Pièce jointe requise",
    #             "Veuillez joindre le document de l'avis du client."
    #         )
    #         return

    #     avis = "ACCEPTE" if self.radio_accepte.isChecked() else "REFUSE"
    #     commentaire = self.txt_commentaire.toPlainText().strip()

    #     success = self.controller.enregistrer_avis_client(
    #         evaluation_id=self.evaluation['id'],
    #         avis=avis,
    #         document_path=self.document_path,
    #         document_nom=self.document_nom,
    #         commentaire=commentaire,
    #     )

    #     if success:
    #         QMessageBox.information(
    #             self, "Avis enregistré",
    #             f"L'avis ({'accepté' if avis == 'ACCEPTE' else 'refusé'}) "
    #             f"a bien été enregistré."
    #         )
    #         self.accept()
    #     else:
    #         QMessageBox.critical(
    #             self, "Erreur",
    #             "L'enregistrement de l'avis a échoué. Consultez le journal."
    #         )

    def _valider(self):
        if not self.document_path:
            QMessageBox.warning(
                self, "Pièce jointe requise",
                "Veuillez joindre le document de l'avis du client."
            )
            return

        avis = "ACCEPTE" if self.radio_accepte.isChecked() else "REFUSE"
        commentaire = self.txt_commentaire.toPlainText().strip()

        # ✅ Noms alignés sur le service
        success = self.controller.enregistrer_avis_client(
            evaluation_id=self.evaluation['id'],
            avis=avis,
            piece_jointe_path=self.document_path,
            piece_jointe_nom=self.document_nom,
            piece_jointe_type=self._detecter_type(),
            commentaire=commentaire,
        )

        if success:
            QMessageBox.information(
                self, "Avis enregistré",
                f"L'avis ({'accepté' if avis == 'ACCEPTE' else 'refusé'}) "
                f"a bien été enregistré."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self, "Erreur",
                "L'enregistrement de l'avis a échoué. Consultez le journal."
            )

    def _detecter_type(self) -> str:
        """Détecte le MIME type approximatif à partir de l'extension."""
        import os
        ext = os.path.splitext(self.document_path or '')[1].lower()
        mapping = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
        }
        return mapping.get(ext, 'application/octet-stream')

        