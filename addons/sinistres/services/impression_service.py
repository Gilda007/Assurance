"""
Service de génération de documents PDF pour les sinistres
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, Any, Optional


class ImpressionService:
    """Service de génération de documents PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configure les styles personnalisés"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=20,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=10,
            spaceBefore=15,
        ))
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=9,
            textColor=colors.HexColor('#334155'),
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            name='CustomSmall',
            parent=self.styles['BodyText'],
            fontSize=8,
            textColor=colors.HexColor('#64748b'),
        ))
    
    # ============================================================
    # MÉTHODE PRINCIPALE
    # ============================================================
    
    def generer_document(
        self,
        sinistre_data: Dict[str, Any],
        type_document: str,
        filepath: str
    ) -> bool:
        """
        Génère un PDF selon le type de document demandé.
        
        Args:
            sinistre_data: données du sinistre (dict sérialisé)
            type_document: 'ACCUSE_RECEPTION', 'FICHE_DECLARATION', etc.
            filepath: chemin de sauvegarde
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Créer le document PDF
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=1.5*cm,
                leftMargin=1.5*cm,
                topMargin=2*cm,
                bottomMargin=2*cm,
                title=f"{type_document}_{sinistre_data.get('numero_sinistre', '')}",
                author="LOMETA",
            )
            
            # Construire le contenu selon le type
            story = []
            
            # En-tête commun
            story.extend(self._build_header(sinistre_data, type_document))
            
            # Corps selon le type
            if type_document == 'ACCUSE_RECEPTION':
                story.extend(self._build_accuse_reception(sinistre_data))
            elif type_document == 'FICHE_DECLARATION':
                story.extend(self._build_fiche_declaration(sinistre_data))
            elif type_document == 'FICHE_INSTRUCTION':
                story.extend(self._build_fiche_instruction(sinistre_data))
            elif type_document == 'FICHE_EXPERTISE':
                story.extend(self._build_fiche_expertise(sinistre_data))
            elif type_document == 'FICHE_EVALUATION':
                story.extend(self._build_fiche_evaluation(sinistre_data))
            elif type_document == 'FICHE_VALIDEE':
                story.extend(self._build_fiche_validee(sinistre_data))
            elif type_document == 'FICHE_REGLEMENT':
                story.extend(self._build_fiche_reglement(sinistre_data))
            elif type_document == 'FICHE_RECOURS':
                story.extend(self._build_fiche_recours(sinistre_data))
            elif type_document == 'FICHE_DEFINITIVE':
                story.extend(self._build_fiche_definitive(sinistre_data))
            elif type_document == 'ATTESTATION_CLOTURE':
                story.extend(self._build_attestation_cloture(sinistre_data))
            elif type_document == 'FICHE_REOUVERTURE':
                story.extend(self._build_fiche_reouverture(sinistre_data))
            else:
                story.append(Paragraph(
                    f"Type de document non supporté : {type_document}",
                    self.styles['CustomBody']
                ))
            
            # Pied de page
            story.append(Spacer(1, 1*cm))
            story.extend(self._build_footer(sinistre_data))
            
            # Générer le PDF
            doc.build(
                story,
                onFirstPage=self._add_page_footer,
                onLaterPages=self._add_page_footer,
            )
            
            return True
        
        except Exception as e:
            print(f"Erreur génération PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ============================================================
    # BLOCS COMMUNS
    # ============================================================
    
    def _build_header(self, s: dict, type_doc: str) -> list:
        """En-tête commun à tous les documents"""
        story = []
        
        # Titre
        titles = {
            'ACCUSE_RECEPTION': "ACCUSÉ DE RÉCEPTION",
            'FICHE_DECLARATION': "FICHE DE DÉCLARATION DE SINISTRE",
            'FICHE_INSTRUCTION': "FICHE D'INSTRUCTION",
            'FICHE_EXPERTISE': "FICHE D'EXPERTISE",
            'FICHE_EVALUATION': "FICHE D'ÉVALUATION",
            'FICHE_VALIDEE': "FICHE VALIDÉE",
            'FICHE_REGLEMENT': "FICHE DE RÈGLEMENT",
            'FICHE_RECOURS': "FICHE DE RECOURS",
            'FICHE_DEFINITIVE': "FICHE DÉFINITIVE",
            'ATTESTATION_CLOTURE': "ATTESTATION DE CLÔTURE",
            'FICHE_REOUVERTURE': "FICHE DE RÉOUVERTURE",
        }
        
        story.append(Paragraph("LOMETA", self.styles['CustomTitle']))
        story.append(Paragraph(
            titles.get(type_doc, type_doc),
            self.styles['Heading1']
        ))
        story.append(Spacer(1, 0.5*cm))
        
        # Bloc d'informations principales
        numero = s.get('numero_sinistre', 'N/A')
        date_decl = s.get('date_declaration', '')
        date_decl_str = str(date_decl)[:10] if date_decl else '—'
        
        info_data = [
            ['N° Sinistre', numero, 'Date de déclaration', date_decl_str],
            ['Branche', s.get('branche', '—'), 'Catégorie', s.get('categorie', '—')],
            ['Statut', s.get('statut', '—'), 'Taux responsabilité',
             f"{(s.get('taux_responsabilite') or 0) * 100:.0f}%"],
        ]
        
        info_table = Table(info_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.5*cm))
        
        return story
    
    def _build_footer(self, s: dict) -> list:
        """Pied de document commun"""
        story = []
        
        story.append(Paragraph(
            f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            self.styles['CustomSmall']
        ))
        story.append(Paragraph(
            f"LOMETA - Gestion des Sinistres - {s.get('numero_sinistre', '')}",
            self.styles['CustomSmall']
        ))
        
        return story
    
    def _add_page_footer(self, canvas, doc):
        """Ajoute un pied de page sur chaque page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#94a3b8'))
        canvas.drawString(
            1.5*cm, 1*cm,
            f"LOMETA - Page {doc.page}"
        )
        canvas.drawRightString(
            A4[0] - 1.5*cm, 1*cm,
            datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        canvas.restoreState()
    
    # ============================================================
    # BLOCS SPÉCIFIQUES
    # ============================================================
    
    def _section_title(self, text: str) -> Paragraph:
        return Paragraph(text, self.styles['CustomHeading'])
    
    def _key_value_table(self, data: list) -> Table:
        """Table clé/valeur générique"""
        table = Table(data, colWidths=[4*cm, 13*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        return table
    
    def _build_accuse_reception(self, s: dict) -> list:
        """Accusé de réception"""
        story = []
        story.append(self._section_title("1. Informations du client"))
        
        data = [
            ['Client', s.get('client_nom', '—')],
            ['Date de survenance', str(s.get('date_survenance', ''))[:10] or '—'],
            ['Circonstance principale', s.get('circonstance_principale', '—')],
            ['Description', s.get('description', '—') or '—'],
        ]
        story.append(self._key_value_table(data))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(self._section_title("2. Objet"))
        story.append(Paragraph(
            "Nous accusons réception de votre déclaration de sinistre. "
            "Votre dossier a été enregistré et sera traité dans les meilleurs délais. "
            "Un gestionnaire vous sera affecté prochainement.",
            self.styles['CustomBody']
        ))
        
        return story
    
    def _build_fiche_declaration(self, s: dict) -> list:
        """Fiche de déclaration"""
        story = []
        story.append(self._section_title("Informations générales"))
        data = [
            ['Numéro', s.get('numero_sinistre', '—')],
            ['Branche', s.get('branche', '—')],
            ['Catégorie', s.get('categorie', '—')],
            ['Sous-catégorie', s.get('sous_categorie', '—') or '—'],
            ['Date survenance', str(s.get('date_survenance', ''))[:10] or '—'],
            ['Date déclaration', str(s.get('date_declaration', ''))[:10] or '—'],
            ['Circonstance', s.get('circonstance_principale', '—')],
        ]
        story.append(self._key_value_table(data))
        
        if s.get('description'):
            story.append(Spacer(1, 0.5*cm))
            story.append(self._section_title("Description"))
            story.append(Paragraph(s['description'], self.styles['CustomBody']))
        
        return story
    
    def _build_fiche_instruction(self, s: dict) -> list:
        """Fiche d'instruction"""
        story = []
        story.append(self._section_title("État d'instruction"))
        data = [
            ['Statut', s.get('statut', '—')],
            ['Responsable', s.get('responsable_nom', '—') or '—'],
            ['Taux responsabilité',
             f"{(s.get('taux_responsabilite') or 0) * 100:.0f}%"],
            ['Date ouverture', str(s.get('date_ouverture', ''))[:10] or '—'],
        ]
        story.append(self._key_value_table(data))
        return story
    
    def _build_fiche_expertise(self, s: dict) -> list:
        """Fiche d'expertise"""
        story = []
        story.append(self._section_title("Missions d'expertise"))
        
        expertises = s.get('expertises', []) or []
        if not expertises:
            story.append(Paragraph("Aucune expertise enregistrée.", self.styles['CustomBody']))
        else:
            data = [['N° Mission', 'Expert', 'Type', 'Date', 'Statut']]
            for e in expertises:
                data.append([
                    e.get('numero_mission', '—'),
                    e.get('expert_nom', '—') or '—',
                    e.get('type_expertise', '—'),
                    str(e.get('date_mission', ''))[:10] if e.get('date_mission') else '—',
                    e.get('statut', '—'),
                ])
            
            table = Table(data, colWidths=[3*cm, 4*cm, 3.5*cm, 3*cm, 3.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(table)
        
        return story
    
    def _build_fiche_evaluation(self, s: dict) -> list:
        """Fiche d'évaluation"""
        story = []
        story.append(self._section_title("Évaluations"))
        
        evaluations = s.get('evaluations', []) or []
        if not evaluations:
            story.append(Paragraph("Aucune évaluation enregistrée.", self.styles['CustomBody']))
        else:
            data = [['N°', 'Type', 'Brut (FCFA)', 'Franchise', 'Net', 'Validée']]
            for e in evaluations:
                data.append([
                    e.get('numero_evaluation', '—'),
                    e.get('type_evaluation', '—'),
                    f"{e.get('montant_brut', 0):,.0f}",
                    f"{e.get('franchise', 0):,.0f}",
                    f"{e.get('montant_net', 0):,.0f}",
                    "Oui" if e.get('est_validee') else "Non",
                ])
            
            table = Table(data, colWidths=[2.5*cm, 3.5*cm, 3*cm, 2.5*cm, 3*cm, 2.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
            ]))
            story.append(table)
        
        return story
    
    def _build_fiche_validee(self, s: dict) -> list:
        """Fiche validée"""
        story = self._build_fiche_evaluation(s)
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(
            "Ce sinistre a été validé. Les règlements peuvent être déclenchés.",
            self.styles['CustomBody']
        ))
        return story
    
    def _build_fiche_reglement(self, s: dict) -> list:
        """Fiche de règlement"""
        story = []
        story.append(self._section_title("Règlements"))
        
        reglements = s.get('reglements', []) or []
        if not reglements:
            story.append(Paragraph("Aucun règlement enregistré.", self.styles['CustomBody']))
        else:
            data = [['N°', 'Bénéficiaire', 'Montant', 'Type', 'Statut']]
            for r in reglements:
                data.append([
                    r.get('numero_reglement', '—'),
                    r.get('beneficiaire_nom', '—') or '—',
                    f"{r.get('montant', 0):,.0f}",
                    r.get('type_paiement', '—'),
                    r.get('statut', '—'),
                ])
            
            table = Table(data, colWidths=[3*cm, 4.5*cm, 3*cm, 3*cm, 3.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ]))
            story.append(table)
        
        return story
    
    def _build_fiche_recours(self, s: dict) -> list:
        """Fiche de recours"""
        story = []
        story.append(self._section_title("Recours"))
        
        recours = s.get('recours', []) or []
        if not recours:
            story.append(Paragraph("Aucun recours enregistré.", self.styles['CustomBody']))
        else:
            data = [['N°', 'Débiteur', 'Réclamé', 'Encaissé', 'Statut']]
            for r in recours:
                data.append([
                    r.get('numero_recours', '—'),
                    r.get('debiteur_nom', '—') or '—',
                    f"{r.get('montant_reclame', 0):,.0f}",
                    f"{r.get('montant_encaisse', 0):,.0f}",
                    r.get('statut', '—'),
                ])
            
            table = Table(data, colWidths=[3*cm, 4.5*cm, 3*cm, 3*cm, 3.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(table)
        
        return story
    
    def _build_fiche_definitive(self, s: dict) -> list:
        """Fiche définitive (toutes les sections)"""
        story = []
        story.extend(self._build_fiche_declaration(s))
        story.append(Spacer(1, 0.3*cm))
        story.extend(self._build_fiche_expertise(s))
        story.append(Spacer(1, 0.3*cm))
        story.extend(self._build_fiche_evaluation(s))
        story.append(Spacer(1, 0.3*cm))
        story.extend(self._build_fiche_reglement(s))
        return story
    
    def _build_attestation_cloture(self, s: dict) -> list:
        """Attestation de clôture"""
        story = []
        story.append(Paragraph(
            "Nous attestons que le sinistre référencé ci-dessous a été traité "
            "et clôturé conformément aux conditions du contrat.",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 1*cm))
        
        data = [
            ['N° Sinistre', s.get('numero_sinistre', '—')],
            ['Date de clôture', str(s.get('date_cloture', ''))[:10] or '—'],
            ['Statut', s.get('statut', '—')],
        ]
        story.append(self._key_value_table(data))
        
        return story
    
    def _build_fiche_reouverture(self, s: dict) -> list:
        """Fiche de réouverture"""
        story = []
        story.append(self._section_title("Réouverture du dossier"))
        data = [
            ['N° Sinistre', s.get('numero_sinistre', '—')],
            ['Date de réexamen', str(s.get('date_reexamen', ''))[:10] or '—'],
            ['Statut actuel', s.get('statut', '—')],
        ]
        story.append(self._key_value_table(data))
        return story