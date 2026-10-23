"""
Service de génération du PDF de proposition au client.
Conserve le fichier à vie dans DATA_DIR/evaluations/<id>/
"""
import os
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class EvaluationPDFService:
    """Génère et stocke les PDF de proposition d'évaluation."""

    def __init__(self, data_dir: str = None):
        # Dossier racine : <projet>/data/evaluations/
        self.data_dir = Path(
            data_dir or os.path.join(os.getcwd(), "data", "evaluations")
        )
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _dossier_evaluation(self, evaluation_id: int) -> Path:
        d = self.data_dir / f"eval_{evaluation_id:06d}"
        d.mkdir(parents=True, exist_ok=True)
        return d

    # ═══════════════════════════════════════════════════════════
    # PDF de proposition
    # ═══════════════════════════════════════════════════════════

    def generer_pdf_proposition(self, evaluation: dict, sinistre: dict,
                                client: dict, utilisateur: dict = None) -> str:
        """
        Génère le PDF de proposition et retourne son chemin absolu.
        Ne supprime jamais l'ancien (versionnage par timestamp).
        """
        dossier = self._dossier_evaluation(evaluation['id'])
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"proposition_{evaluation['numero_evaluation']}_{ts}.pdf"
        path = dossier / filename

        doc = SimpleDocTemplate(
            str(path), pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )
        styles = self._styles()
        story = []

        # ─── En-tête ───
        story.append(Paragraph(
            "<b>LOMETA ASSURANCE</b>", styles['H1']))
        story.append(Paragraph(
            "Gestion des sinistres — Proposition d'indemnisation",
            styles['Subtitle']))
        story.append(Spacer(1, 0.5*cm))
        story.append(self._ligne_separation())
        story.append(Spacer(1, 0.5*cm))

        # ─── Références ───
        story.append(Paragraph(
            f"<b>Référence évaluation :</b> {evaluation['numero_evaluation']}",
            styles['Normal']))
        story.append(Paragraph(
            f"<b>Sinistre :</b> {sinistre.get('numero_sinistre', 'N/A')}",
            styles['Normal']))
        story.append(Paragraph(
            f"<b>Date :</b> {datetime.now().strftime('%d/%m/%Y')}",
            styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # ─── Destinataire ───
        story.append(Paragraph(
            f"À l'attention de : <b>{client.get('nom', 'N/A')} "
            f"{client.get('prenom', '')}</b>", styles['Normal']))
        if client.get('adresse'):
            story.append(Paragraph(client['adresse'], styles['Normal']))
        story.append(Spacer(1, 1*cm))

        # ─── Objet ───
        story.append(Paragraph(
            "<b>Objet :</b> Proposition d'indemnisation suite à votre sinistre",
            styles['H2']))
        story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph(
            "Madame, Monsieur,", styles['Normal']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            "Suite à l'expertise réalisée concernant votre sinistre référencé "
            f"<b>{sinistre.get('numero_sinistre', 'N/A')}</b>, "
            "nous avons le plaisir de vous communiquer notre proposition "
            "d'indemnisation détaillée ci-dessous.",
            styles['Normal']))
        story.append(Spacer(1, 0.7*cm))

        # ─── Tableau détail ───
        story.append(Paragraph("<b>Détail de l'évaluation</b>", styles['H2']))
        story.append(Spacer(1, 0.3*cm))

        def _fmt(v):
            try:
                return f"{float(v or 0):,.0f} FCFA".replace(",", " ")
            except Exception:
                return "0 FCFA"

        data = [
            ["Désignation", "Montant"],
            ["Montant brut des réparations", _fmt(evaluation.get('montant_brut'))],
            ["Frais d'expertise", _fmt(evaluation.get('montant_expert'))],
            ["Franchise à déduire", f"- {_fmt(evaluation.get('franchise'))}"],
            ["Taux franchise",
             f"{float(evaluation.get('taux_responsabilite', 1) or 1) * 100:.0f} %"],
        ]

        # Montant expert validé (si mission liée)
        if evaluation.get('mission_id'):
            data.append([
                "Montant expertise validée",
                _fmt(evaluation.get('montant_expert_valide'))
            ])

        data.append([
            "MONTANT NET PROPOSÉ",
            _fmt(evaluation.get('montant_net'))
        ])

        table = Table(data, colWidths=[10*cm, 6*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#dbeafe")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(table)
        story.append(Spacer(1, 1*cm))

        # ─── Modalités ───
        story.append(Paragraph("<b>Modalités de réponse</b>", styles['H2']))
        story.append(Paragraph(
            "Merci de nous retourner votre avis dans un délai de 15 jours, "
            "en joignant :",
            styles['Normal']))
        story.append(Paragraph(
            "• soit votre acceptation signée de la présente proposition ;",
            styles['Normal']))
        story.append(Paragraph(
            "• soit votre refus motivé accompagné des pièces justificatives.",
            styles['Normal']))
        story.append(Spacer(1, 1.5*cm))

        # ─── Signature ───
        story.append(Paragraph(
            "Fait à ____________________, le "
            f"{datetime.now().strftime('%d/%m/%Y')}",
            styles['Normal']))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            "<b>Le Gestionnaire Sinistres</b>", styles['Normal']))
        if utilisateur:
            story.append(Paragraph(
                f"{utilisateur.get('nom', '')} {utilisateur.get('prenom', '')}",
                styles['Normal']))

        doc.build(story)
        return str(path)

    # ═══════════════════════════════════════════════════════════
    # Stockage du document d'avis client
    # ═══════════════════════════════════════════════════════════

    def stocker_avis_client(self, evaluation_id: int, source_path: str,
                            nom_original: str = None) -> dict:
        """
        Copie le document d'avis client dans le dossier de l'évaluation.
        Retourne un dict : {path, type, nom}
        """
        import shutil
        dossier = self._dossier_evaluation(evaluation_id)

        ext = Path(source_path).suffix.lower()
        type_map = {
            '.pdf': 'PDF',
            '.jpg': 'IMAGE', '.jpeg': 'IMAGE', '.png': 'IMAGE',
            '.gif': 'IMAGE', '.bmp': 'IMAGE', '.webp': 'IMAGE',
        }
        doc_type = type_map.get(ext, 'AUTRE')

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_final = f"avis_client_{ts}{ext}"
        dest = dossier / nom_final
        shutil.copy2(source_path, dest)

        return {
            'path': str(dest),
            'type': doc_type,
            'nom': nom_original or Path(source_path).name,
        }

    # ═══════════════════════════════════════════════════════════
    # Utilitaires
    # ═══════════════════════════════════════════════════════════

    def _styles(self):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            'H1', parent=styles['Heading1'], fontSize=18,
            textColor=colors.HexColor("#0f172a"), alignment=TA_CENTER,
            spaceAfter=6))
        styles.add(ParagraphStyle(
            'H2', parent=styles['Heading2'], fontSize=13,
            textColor=colors.HexColor("#1e40af"), spaceBefore=12,
            spaceAfter=6))
        styles.add(ParagraphStyle(
            'Subtitle', parent=styles['Normal'], fontSize=11,
            textColor=colors.HexColor("#64748b"), alignment=TA_CENTER))
        return styles

    def _ligne_separation(self):
        from reportlab.platypus import HRFlowable
        return HRFlowable(
            width="100%", thickness=1,
            color=colors.HexColor("#e2e8f0"),
            spaceBefore=4, spaceAfter=4)