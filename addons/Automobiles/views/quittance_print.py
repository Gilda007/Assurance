
# addons/Automobiles/reports/quittance_print.py
"""
Générateur de Quittance d'Assurance Automobile
Style professionnel - Version compacte (1 page)
"""

import os
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtCore import Qt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    KeepTogether, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.fonts import addMapping
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF
import tempfile


class QuittanceGenerator:
    """Générateur de quittance professionnelle (Conditions Particulières) - Version 1 page"""
    
    # Palette de couleurs professionnelle
    COLORS = {
        'primary': '#1a365d',
        'primary_light': '#2b6cb0',
        'secondary': '#2d3748',
        'accent': '#c53030',
        'gray_light': '#f7fafc',
        'gray_medium': '#e2e8f0',
        'gray_dark': '#4a5568',
        'white': '#ffffff',
        'black': '#1a202c',
        'border': '#cbd5e0',
        'success': '#38a169',
        'warning': '#dd6b20',
        'amount': '#2b6cb0',
        'total': '#c53030',
    }
    
    def __init__(self, contract_data, vehicle_data, owner_data, company_data):
        self.contract = contract_data or {}
        self.vehicle = vehicle_data or {}
        self.owner = owner_data or {}
        self.company = company_data or {}
        
        self.styles = {}
        self._init_styles()
    
    def _init_styles(self):
        """Initialise les styles pour le PDF - Version compacte"""
        styles = getSampleStyleSheet()
        
        # --- STYLES PRINCIPAUX (taille réduite) ---
        
        # Titre principal
        self.styles['main_title'] = ParagraphStyle(
            'MainTitle',
            parent=styles['Title'],
            fontSize=14,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            textColor=colors.HexColor(self.COLORS['primary']),
            spaceAfter=4,
            spaceBefore=2
        )
        
        # Sous-titre
        self.styles['subtitle'] = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            alignment=TA_CENTER,
            textColor=colors.HexColor(self.COLORS['gray_dark']),
            spaceAfter=4
        )
        
        # En-tête de section
        self.styles['section_title'] = ParagraphStyle(
            'SectionTitle',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor(self.COLORS['primary']),
            spaceAfter=3,
            spaceBefore=4
        )
        
        # Titre de section avec fond
        self.styles['section_header'] = ParagraphStyle(
            'SectionHeader',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor(self.COLORS['white']),
            alignment=TA_CENTER,
            backColor=colors.HexColor(self.COLORS['primary']),
            spaceAfter=2,
            borderPadding=4
        )
        
        # Label (gras)
        self.styles['label'] = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=7.5,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor(self.COLORS['secondary']),
            alignment=TA_LEFT
        )

        self.styles['center'] = ParagraphStyle(
            'CenterStyle',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica',
            alignment=TA_CENTER
        )
        
        # Valeur normale
        self.styles['value'] = ParagraphStyle(
            'Value',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica',
            textColor=colors.HexColor(self.COLORS['black']),
            alignment=TA_LEFT
        )
        
        # Valeur en gras
        self.styles['value_bold'] = ParagraphStyle(
            'ValueBold',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor(self.COLORS['black']),
            alignment=TA_LEFT
        )
        
        # Valeur centrée
        self.styles['value_center'] = ParagraphStyle(
            'ValueCenter',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica',
            alignment=TA_CENTER
        )
        
        # Cellules de tableau
        self.styles['cell_center'] = ParagraphStyle(
            'CellCenter',
            parent=styles['Normal'],
            fontSize=7,
            fontName='Helvetica',
            alignment=TA_CENTER,
            textColor=colors.HexColor(self.COLORS['black'])
        )
        
        self.styles['cell_left'] = ParagraphStyle(
            'CellLeft',
            parent=styles['Normal'],
            fontSize=7,
            fontName='Helvetica',
            alignment=TA_LEFT,
            textColor=colors.HexColor(self.COLORS['black'])
        )
        
        self.styles['cell_right'] = ParagraphStyle(
            'CellRight',
            parent=styles['Normal'],
            fontSize=7,
            fontName='Helvetica',
            alignment=TA_RIGHT,
            textColor=colors.HexColor(self.COLORS['black'])
        )
        
        self.styles['cell_bold'] = ParagraphStyle(
            'CellBold',
            parent=styles['Normal'],
            fontSize=7,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            textColor=colors.HexColor(self.COLORS['white'])
        )
        
        # Montants
        self.styles['amount'] = ParagraphStyle(
            'Amount',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor(self.COLORS['amount']),
            alignment=TA_RIGHT
        )
        
        # Pied de page
        self.styles['footer'] = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=6.5,
            fontName='Helvetica',
            textColor=colors.HexColor(self.COLORS['gray_dark']),
            alignment=TA_CENTER
        )
        
        # Signature
        self.styles['signature'] = ParagraphStyle(
            'Signature',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor(self.COLORS['primary']),
            alignment=TA_CENTER
        )
        
        # Texte normal
        self.styles['normal'] = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica',
            textColor=colors.HexColor(self.COLORS['black'])
        )

        self.styles['right'] = ParagraphStyle(
            'RightStyle',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica',
            alignment=TA_RIGHT,
            textColor=colors.HexColor(self.COLORS['black'])
        )

        self.styles['left'] = ParagraphStyle(
            'LeftStyle',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica',
            alignment=TA_LEFT,
            textColor=colors.HexColor(self.COLORS['black'])
        )
    
    def generate(self, output_path=None):
        """Génère le PDF de la quittance - Version 1 page"""
        if output_path is None:
            output_path = os.path.join(
                tempfile.gettempdir(),
                f"quittance_{self.contract.get('numero_police', 'temp')}.pdf"
            )
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=12*mm,
            leftMargin=12*mm,
            topMargin=10*mm,
            bottomMargin=10*mm,
            title=f"Quittance - {self.vehicle.get('immatriculation', '')}",
            author="Automobiles ASAC"
        )
        
        elements = []
        
        # === 1. EN-TÊTE ===
        elements.extend(self._build_company_header())
        elements.append(Spacer(1, 2*mm))
        
        # === 2. TITRE ===
        elements.extend(self._build_title())
        elements.append(Spacer(1, 2*mm))
        
        # # === 3. INFORMATIONS DU CONTRAT ===
        elements.extend(self._build_insured_info_combined())
        elements.append(Spacer(1, 3*mm))
        
        # === 4. GARANTIES + FINANCIER (ZONE UNIQUE) ===
        elements.extend(self._build_guarantees_and_financial())  # ou _build_guarantees_and_financial_vertical()
        elements.append(Spacer(1, 2*mm))
        
        # === 5. PIED DE PAGE ===
        elements.extend(self._build_footer())
        elements.append(Spacer(2, 8*mm))
        
        doc.build(elements)
        return output_path
    
    # def _build_company_header(self):
    #     """Construit l'en-tête avec les informations de la compagnie - Compact"""
    #     elements = []
        
    #     company_name = self.company.get('nom', 'AMS INSURANCES')
    #     company_address = self.company.get('adresse', 'BP 3073 DLA')
    #     company_phone = self.company.get('telephone', '98 76 85 43')
        
    #     header_data = [
    #         [
    #             Paragraph(f"<font size=14 color='#1a365d'><b>{company_name}</b></font>", self.styles['center']),
    #             Paragraph(f"<font size=9 color='#4a5568'>Agence: {self.company.get('agence', 'Yaoundé')}</font>", self.styles['center']),
    #             Paragraph(f"<font size=9 color='#4a5568'>Apporteur: {self.contract.get('apporteur', 'TH')}</font>", self.styles['center'])
    #         ],
    #         [
    #             Paragraph(f"<font size=8 color='#4a5568'>{company_address}</font>", self.styles['center']),
    #             Paragraph(f"<font size=8 color='#4a5568'>Tél: {company_phone}</font>", self.styles['center']),
    #             Paragraph(f"<font size=8 color='#4a5568'>Code: {self.company.get('code_agence', '1020')}</font>", self.styles['center'])
    #         ]
    #     ]
        
    #     header_table = Table(header_data, colWidths=[6*cm, 6*cm, 6*cm])
    #     header_table.setStyle(TableStyle([
    #         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    #         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    #         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    #         ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.HexColor(self.COLORS['primary'])),
    #         ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor(self.COLORS['border'])),
    #     ]))
    #     elements.append(header_table)
        
    #     return elements
    
    def _build_company_header(self):
        """Construit l'en-tête avec les informations de la compagnie - Textbox alignée à droite"""
        elements = []
        
        # Récupérer les données
        company_name = self.company.get('nom', 'AMS INSURANCES')
        company_address = self.company.get('adresse', 'BP 3073 DLA')
        company_phone = self.company.get('telephone', '98 76 85 43')
        code_agence = self.company.get('code_agence', '1020')
        apporteur = self.contract.get('apporteur', 'TH')
        produit = self.contract.get('produit', '201 CAT 01')
        duree = self.contract.get('duree', '365 Jours')
        
        # ✅ Style pour la textbox alignée à droite
        text_style = ParagraphStyle(
            'TextBoxStyle',
            parent=self.styles['normal'],
            fontSize=9,
            fontName='Helvetica',
            alignment=TA_RIGHT,  # ✅ Texte aligné à droite
            leading=14
        )
        
        # ✅ Texte formaté aligné à droite
        header_text = f"""
        <font size=14 color='#1a365d'><b>{company_name}</b></font><br/>
        <font size=8 color='#4a5568'><b>Bureau Direct:</b> {code_agence} &nbsp;&nbsp;&nbsp; <b>Apporteur:</b> {apporteur}</font><br/>
        <font size=8 color='#4a5568'>Adresse: {company_address} &nbsp;&nbsp;&nbsp; Tél: {company_phone}</font><br/>
        <font size=8 color='#4a5568'>Produit: {produit} &nbsp;&nbsp;&nbsp; Durée: {duree}</font>
        """
        
        # ✅ Créer la textbox avec bordure et fond
        textbox_data = [[Paragraph(header_text, text_style)]]
        
        textbox_table = Table(textbox_data, colWidths=[18*cm])
        textbox_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # ✅ Tableau aligné à droite
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # ✅ Bordure
            # ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(self.COLORS['border'])),
            # # ✅ Fond gris clair
            # ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(self.COLORS['gray_light'])),
            # ✅ Padding
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ]))
        elements.append(textbox_table)
        
        return elements

    def _build_title(self):
        """Construit le titre du document - Compact"""
        elements = []
        
        title_data = [
            [
                Paragraph(
                    "<font size=14 color='#1a365d'><b>CONDITIONS PARTICULIÈRES</b></font>",
                    self.styles['center']
                )
            ],
            [
                Paragraph(
                    f"<font size=9 color='#4a5568'>Contrat n° {self.contract.get('numero_police', '')}</font>",
                    self.styles['center']
                )
            ]
        ]
        
        title_table = Table(title_data, colWidths=[18*cm])
        title_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['gray_light'])),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor(self.COLORS['border'])),
        ]))
        elements.append(title_table)
        
        return elements
       

    def _build_contract_info(self):
        """Construit la zone d'informations du contrat - Style zone unique"""
        elements = []
        
        date_debut = self.contract.get('date_debut')
        date_fin = self.contract.get('date_fin')
        
        if isinstance(date_debut, datetime):
            date_debut_str = date_debut.strftime("%d/%m/%Y")
        else:
            date_debut_str = str(date_debut) if date_debut else ""
        
        if isinstance(date_fin, datetime):
            date_fin_str = date_fin.strftime("%d/%m/%Y")
        else:
            date_fin_str = str(date_fin) if date_fin else ""
        
        duree = self.contract.get('duree', '365 Jours')
        produit = self.contract.get('produit', '201 CAT 01')
        tacite = self.contract.get('tacite_reconduction', 'Sans Tacite Reconduction')
        
        # ✅ Zone 1: Dates du contrat
        contract_data = [
            [
                Paragraph(f"<b>Effet:</b> {date_debut_str}", self.styles['value']),
                Paragraph(f"<b>Expiration:</b> {date_fin_str}", self.styles['value']),
                Paragraph(f"<b>Durée:</b> {duree}", self.styles['value'])
            ]
        ]
        
        contract_table = Table(contract_data, colWidths=[6*cm, 6*cm, 6*cm])
        contract_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(contract_table)
        
        return elements


    def _build_insured_info(self):
        """Construit la zone des informations de l'assuré - Style zone unique"""
        elements = []
        
        # ✅ Récupérer les données du propriétaire
        nom_complet = self.vehicle.get('owner', '') or f"{self.owner.get('nom', '')} {self.owner.get('prenom', '')}".strip()
        phone = self.vehicle.get('owner_phone', '') or self.owner.get('telephone', '')
        email = self.vehicle.get('owner_email', '') or self.owner.get('email', '')
        address = self.vehicle.get('owner_address', '') or self.owner.get('adresse', '')
        city = self.vehicle.get('owner_city', '') or self.owner.get('ville', '')
        
        adresse = f"{address} {city}".strip() if address or city else ''
        
        # ✅ Zone 2: Informations de l'assuré
        insured_data = [
            [
                Paragraph(f"<b>Assuré:</b> {nom_complet or '—'}", self.styles['value']),
                Paragraph(f"<b>Adresse:</b> {adresse or '—'}", self.styles['value'])
            ],
            [
                Paragraph(f"<b>Tél:</b> {phone or '—'}", self.styles['value']),
                Paragraph(f"<b>Email:</b> {email or '—'}", self.styles['value'])
            ]
        ]
        
        insured_table = Table(insured_data, colWidths=[9*cm, 9*cm])
        insured_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(insured_table)
        
        return elements


    def _build_insured_info_combined(self):
        """
        Construit une zone unique contenant les 3 sections:
        1. Dates du contrat
        2. Informations de l'assuré
        3. Informations du véhicule
        """
        elements = []
        
        # === Récupérer les données ===
        
        # Dates
        date_debut = self.contract.get('date_debut')
        date_fin = self.contract.get('date_fin')
        
        if isinstance(date_debut, datetime):
            date_debut_str = date_debut.strftime("%d/%m/%Y")
        else:
            date_debut_str = str(date_debut) if date_debut else ""
        
        if isinstance(date_fin, datetime):
            date_fin_str = date_fin.strftime("%d/%m/%Y")
        else:
            date_fin_str = str(date_fin) if date_fin else ""
        
        duree = self.contract.get('duree', '365 Jours')
        
        # Assuré
        nom_complet = self.vehicle.get('owner', '') or f"{self.owner.get('nom', '')} {self.owner.get('prenom', '')}".strip()
        phone = self.vehicle.get('owner_phone', '') or self.owner.get('telephone', '')
        email = self.vehicle.get('owner_email', '') or self.owner.get('email', '')
        address = self.vehicle.get('owner_address', '') or self.owner.get('adresse', '')
        city = self.vehicle.get('owner_city', '') or self.owner.get('ville', '')
        adresse = f"{address} {city}".strip() if address or city else ''
        
        # Véhicule
        immatriculation = self.vehicle.get('immatriculation', '')
        marque = self.vehicle.get('marque', '')
        modele = self.vehicle.get('modele', '')
        usage = self.vehicle.get('usage', '')
        places = self.vehicle.get('places', '')
        date_mec = self.vehicle.get('date_mise_circulation', '')
        puissance = self.vehicle.get('puissance_fiscale', '')
        chassis = self.vehicle.get('chassis', '')
        vehicle_text = f"{marque} {modele}".strip() or '—'
        
        # ✅ Zone unique avec les 3 sections
        combined_data = [
            # === SECTION 1: Dates ===
            [
                Paragraph(f"<b>Effet:</b> {date_debut_str}", self.styles['value']),
                Paragraph(f"<b>Expiration:</b> {date_fin_str}", self.styles['value']),
                Paragraph(f"<b>Durée:</b> {duree}", self.styles['value'])
            ],
            # === SECTION 2: Assuré ===
            [
                Paragraph(f"<b>Assuré:</b> {nom_complet or '—'}", self.styles['value']),
                Paragraph(f"<b>Adresse:</b> {adresse or '—'}", self.styles['value']),
                "",
            ],
            [
                Paragraph(f"<b>Tél:</b> {phone or '—'}", self.styles['value']),
                Paragraph(f"<b>Email:</b> {email or '—'}", self.styles['value']),
                "",
            ],
            # === SECTION 3: Véhicule ===
            [
                Paragraph(f"<b>Véhicule:</b> {vehicle_text} - {immatriculation or '—'}", self.styles['value']),
                Paragraph(f"<b>Usage:</b> {usage or '—'}", self.styles['value']),
                Paragraph(f"<b>MEC:</b> {date_mec or '—'}", self.styles['value'])
            ],
            [
                Paragraph(f"<b>Places:</b> {places or '—'}", self.styles['value']),
                Paragraph(f"<b>Puissance:</b> {puissance or '—'} CV", self.styles['value']),
                Paragraph(f"<b>Châssis:</b> {chassis or '—'}", self.styles['value'])
            ]
        ]
        
        combined_table = Table(combined_data, colWidths=[6*cm, 6*cm, 6*cm])
        combined_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            # ✅ Fond alterné pour les sections
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f7fafc')),  # Dates
            ('BACKGROUND', (0, 1), (-1, 2), colors.HexColor('#ffffff')),  # Assuré
            ('BACKGROUND', (0, 3), (-1, 4), colors.HexColor('#f7fafc')),  # Véhicule
            # ✅ Bordures
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            # ✅ Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            # ✅ Fusion des cellules pour les lignes vides
            ('SPAN', (2, 1), (2, 2)),  # Fusion de la colonne 3 pour l'adresse
            ('SPAN', (2, 3), (2, 4)),  # Fusion de la colonne 3 pour le véhicule
        ]))
        elements.append(combined_table)
        
        return elements

    def _build_vehicle_info(self):
        """Construit la zone des informations du véhicule - Style zone unique"""
        elements = []
        
        immatriculation = self.vehicle.get('immatriculation', '')
        marque = self.vehicle.get('marque', '')
        modele = self.vehicle.get('modele', '')
        usage = self.vehicle.get('usage', '')
        places = self.vehicle.get('places', '')
        date_mec = self.vehicle.get('date_mise_circulation', '')
        puissance = self.vehicle.get('puissance_fiscale', '')
        chassis = self.vehicle.get('chassis', '')
        
        vehicle_text = f"{marque} {modele}".strip() or '—'
        
        # ✅ Zone 3: Informations du véhicule
        vehicle_data = [
            [
                Paragraph(f"<b>Véhicule:</b> {vehicle_text} - {immatriculation or '—'}", self.styles['value']),
                Paragraph(f"<b>Usage:</b> {usage or '—'}", self.styles['value']),
                Paragraph(f"<b>MEC:</b> {date_mec or '—'}", self.styles['value'])
            ],
            [
                Paragraph(f"<b>Places:</b> {places or '—'}", self.styles['value']),
                Paragraph(f"<b>Puissance:</b> {puissance or '—'} CV", self.styles['value']),
                Paragraph(f"<b>Châssis:</b> {chassis or '—'}", self.styles['value'])
            ]
        ]
        
        vehicle_table = Table(vehicle_data, colWidths=[6*cm, 6*cm, 6*cm])
        vehicle_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(vehicle_table)
        
        return elements

    def _build_guarantees_and_financial(self):
        """
        Construit une zone unique contenant les garanties et le décompte de prime
        """
        elements = []
        
        # ============================================================
        # 1. TABLEAU DES GARANTIES
        # ============================================================
        guarantees = self.contract.get('guarantees', [])
        
        if not guarantees:
            guarantees = [
                {"name": "RESPONSABILITE CIVILE", "prime": "-"},
                {"name": "DEFENSE RECOURS", "prime": "-"},
                {"name": "INDIVIDUELLE PERSONNES TRANSPORTÉES", "prime": "-"},
                {"name": "INDIVIDUELLE ACCIDENT CHAUFFEUR", "prime": "-"},
                {"name": "VOL / INCENDIE", "prime": "-"},
                {"name": "BRIS DE GLACE", "prime": "-"},
                {"name": "ASSISTANCE RÉPARATION", "prime": "-"},
                {"name": "DOMMAGES", "prime": "-"},
            ]
        
        # ✅ Titre du tableau des garanties
        guar_title = Paragraph(
            "<b><font size=9 color='#1a365d'>Caractéristiques VEHICULE</font></b>",
            self.styles['center']
        )
        
        # En-têtes
        guar_headers = ["Garanties", "Prime Période"]
        guar_table_data = []
        guar_table_data.append([Paragraph(h, self.styles['cell_bold']) for h in guar_headers])
        
        total_prime = 0
        for g in guarantees:
            prime_text = str(g.get('prime', '0'))
            prime_clean = prime_text.replace(' ', '').replace(',', '')
            try:
                total_prime += float(prime_clean) if prime_clean and prime_clean != '-' else 0
            except:
                pass
            
            guar_table_data.append([
                Paragraph(g.get('name', ''), self.styles['cell_left']),
                Paragraph(str(g.get('prime', '')), self.styles['cell_right'])
            ])
        
        guar_table_data.append([
            Paragraph("<b>TOTAL GARANTIES</b>", self.styles['cell_left']),
            Paragraph(f"<b>{total_prime:,.0f}</b>".replace(',', ' '), self.styles['cell_right'])
        ])
        
        guar_table = Table(guar_table_data, colWidths=[5*cm, 3*cm])
        guar_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(self.COLORS['white'])),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor(self.COLORS['border'])),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(self.COLORS['gray_light'])),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor(self.COLORS['primary'])),
        ]))
        
        # ============================================================
        # 2. TABLEAU FINANCIER
        # ============================================================
        prime_nette = self.contract.get('prime_nette', 0)
        accessoires = self.contract.get('accessoires', 0)
        asac = self.contract.get('asac', 0)
        tva = self.contract.get('tva', 0)
        carte_rose = self.contract.get('carte_rose', 0)
        vignette = self.contract.get('vignette', 0)
        prime_totale = prime_nette + accessoires + asac + tva + carte_rose + vignette
        
        # ✅ Titre du tableau financier
        fin_title = Paragraph(
            "<b><font size=9 color='#1a365d'>Décompte de prime</font></b>",
            self.styles['center']
        )
        
        financial_data = [
            ["Prime Nette", f"{prime_nette:,.0f}".replace(',', ' ')],
            ["Accessoires", f"{accessoires:,.0f}".replace(',', ' ')],
            ["ASAC", f"{asac:,.0f}".replace(',', ' ')],
            ["TVA (19.25%)", f"{tva:,.0f}".replace(',', ' ')],
            ["Carte Rose", f"{carte_rose:,.0f}".replace(',', ' ')],
            ["Vignette (CP)", f"{vignette:,.0f}".replace(',', ' ')],
            ["", ""],
            ["TOTAL À PAYER", f"{prime_totale:,.0f}".replace(',', ' ')]
        ]
        
        fin_table = Table(financial_data, colWidths=[5*cm, 3*cm])
        fin_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor(self.COLORS['border'])),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['gray_light'])),
            ('LINEABOVE', (0, 6), (-1, 6), 1, colors.HexColor(self.COLORS['border'])),
            ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor(self.COLORS['gray_light'])),
            ('LINEABOVE', (0, 7), (-1, 7), 1.5, colors.HexColor(self.COLORS['primary'])),
            ('LINEBELOW', (0, 7), (-1, 7), 1.5, colors.HexColor(self.COLORS['primary'])),
            ('FONTNAME', (0, 7), (-1, 7), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 7), (-1, 7), 10),
        ]))
        
        # ============================================================
        # 3. ASSEMBLAGE AVEC LES TITRES
        # ============================================================
        combined_data = [
            [guar_title, fin_title],
            [guar_table, fin_table]
        ]
        
        combined_table = Table(combined_data, colWidths=[8*cm, 10*cm])
        combined_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # ✅ Padding
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            # ✅ Ligne de séparation sous les titres
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor(self.COLORS['border'])),
        ]))
        elements.append(combined_table)
        
        return elements

    def _build_financial_summary(self):
        """Construit le décompte de prime - Compact"""
        elements = []
        
        prime_nette = self.contract.get('prime_nette', 0)
        accessoires = self.contract.get('accessoires', 0)
        asac = self.contract.get('asac', 0)
        tva = self.contract.get('tva', 0)
        carte_rose = self.contract.get('carte_rose', 0)
        vignette = self.contract.get('vignette', 0)
        prime_totale = prime_nette + accessoires + asac + tva + carte_rose + vignette
        
        financial_data = [
            ["Prime Nette", f"{prime_nette:,.0f}".replace(',', ' ')],
            ["Accessoires", f"{accessoires:,.0f}".replace(',', ' ')],
            ["ASAC", f"{asac:,.0f}".replace(',', ' ')],
            ["TVA (19.25%)", f"{tva:,.0f}".replace(',', ' ')],
            ["Carte Rose", f"{carte_rose:,.0f}".replace(',', ' ')],
            ["Vignette (CP)", f"{vignette:,.0f}".replace(',', ' ')],
            ["", ""],
            ["TOTAL À PAYER", f"{prime_totale:,.0f}".replace(',', ' ')]
        ]
        
        financial_table = Table(financial_data, colWidths=[12*cm, 6*cm])
        financial_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor(self.COLORS['border'])),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['gray_light'])),
            ('LINEABOVE', (0, 6), (-1, 6), 1, colors.HexColor(self.COLORS['border'])),
            ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor(self.COLORS['gray_light'])),
            ('LINEABOVE', (0, 7), (-1, 7), 1.5, colors.HexColor(self.COLORS['primary'])),
            ('LINEBELOW', (0, 7), (-1, 7), 1.5, colors.HexColor(self.COLORS['primary'])),
            ('FONTNAME', (0, 7), (-1, 7), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 7), (-1, 7), 10),
        ]))
        elements.append(financial_table)
        
        return elements
    
    def _build_footer(self):
        """Construit le pied de page avec signatures - Compact"""
        elements = []
        
        apporteur = self.contract.get('apporteur', 'TH')
        ville = self.company.get('ville', 'Yaoundé')
        date_signature = datetime.now().strftime("%d/%m/%Y")
        compagnie_nom = self.company.get('nom', 'AMS INSURANCES')
        
        footer_data = [
            [
                Paragraph(f"Contrat produit par {apporteur}", self.styles['center']),
                "",
                Paragraph(f"Charge de clientèle: {apporteur}", self.styles['center']),
                ""
            ],
            [
                Paragraph(f"Fait à {ville}, le {date_signature}", self.styles['center']),
                "",
                "",
                Paragraph(date_signature, self.styles['center'])
            ],
            [
                Paragraph("<b>Pour l'Assuré</b>", self.styles['signature']),
                "",
                "",
                Paragraph(f"<b>Pour {compagnie_nom}</b>", self.styles['signature'])
            ],
            [
                Paragraph("_________________________", self.styles['center']),
                "",
                "",
                Paragraph("_________________________", self.styles['center'])
            ]
        ]
        
        footer_table = Table(footer_data, colWidths=[4*cm, 2.5*cm, 2.5*cm, 4*cm])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('SPAN', (0, 0), (1, 0)),
            ('SPAN', (2, 0), (3, 0)),
            ('SPAN', (0, 1), (2, 1)),
            ('SPAN', (0, 2), (1, 2)),
            ('SPAN', (2, 2), (3, 2)),
        ]))
        elements.append(footer_table)
        
        elements.append(Paragraph(
            f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            self.styles['footer']
        ))
        
        return elements


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def generate_quittance(contract_data, vehicle_data, owner_data, company_data, output_path=None):
    generator = QuittanceGenerator(contract_data, vehicle_data, owner_data, company_data)
    return generator.generate(output_path)


def generate_quittance_from_vehicle(vehicle, parent=None):
    """Génère une quittance à partir d'un véhicule"""
    try:
        if isinstance(vehicle, dict):
            vehicle_dict = vehicle
        else:
            # Si c'est un objet Vehicle
            vehicle_dict = {
                'immatriculation': getattr(vehicle, 'immatriculation', ''),
                'marque': getattr(vehicle, 'marque', ''),
                'modele': getattr(vehicle, 'modele', ''),
                'usage': getattr(vehicle, 'usage', ''),
                'places': getattr(vehicle, 'places', 5),
                'date_mise_circulation': getattr(vehicle, 'date_mise_circulation', ''),
                'chassis': getattr(vehicle, 'chassis', ''),
                'puissance_fiscale': getattr(vehicle, 'puissance_fiscale', ''),
                'categorie': getattr(vehicle, 'categorie', '201 CAT 01'),
                'numero_police': getattr(vehicle, 'numero_police', ''),
                'date_debut': getattr(vehicle, 'date_debut', datetime.now()),
                'date_fin': getattr(vehicle, 'date_fin', datetime.now()),
                'prime_nette': getattr(vehicle, 'prime_nette', 0),
                'accessoires': getattr(vehicle, 'accessoires', 0),
                'fichier_asac': getattr(vehicle, 'fichier_asac', 0),
                'tva': getattr(vehicle, 'tva', 0),
                'carte_rose': getattr(vehicle, 'carte_rose', 0),
                'vignette': getattr(vehicle, 'vignette', 0),
                'amt_rc': getattr(vehicle, 'amt_rc', 0),
                'amt_dr': getattr(vehicle, 'amt_dr', 0),
                'amt_ipt': getattr(vehicle, 'amt_ipt', 0),
                'amt_vol': getattr(vehicle, 'amt_vol', 0),
                'amt_vb': getattr(vehicle, 'amt_vb', 0),
                'amt_bris': getattr(vehicle, 'amt_bris', 0),
                'amt_ar': getattr(vehicle, 'amt_ar', 0),
                'amt_dta': getattr(vehicle, 'amt_dta', 0),
                'amt_in': getattr(vehicle, 'amt_in', 0),
                'owner': getattr(vehicle.owner, 'nom', '') + ' ' + getattr(vehicle.owner, 'prenom', '') if hasattr(vehicle, 'owner') and vehicle.owner else '',
                'owner_phone': getattr(vehicle.owner, 'telephone', '') if hasattr(vehicle, 'owner') and vehicle.owner else '',
                'owner_email': getattr(vehicle.owner, 'email', '') if hasattr(vehicle, 'owner') and vehicle.owner else '',
                'owner_address': getattr(vehicle.owner, 'adresse', '') if hasattr(vehicle, 'owner') and vehicle.owner else '',
                'owner_city': getattr(vehicle.owner, 'ville', '') if hasattr(vehicle, 'owner') and vehicle.owner else '',
            }
        
        # Préparer les données
        contract_data = {...}  # Même code que précédemment
        vehicle_data = {...}   # Même code que précédemment
        owner_data = {...}     # Même code que précédemment
        company_data = {...}   # Même code que précédemment
        
        if parent:
            output_path, _ = QFileDialog.getSaveFileName(
                parent,
                "Enregistrer la quittance",
                f"quittance_{vehicle_dict.get('immatriculation', 'temp')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                "PDF Files (*.pdf)"
            )
            if not output_path:
                return False
        else:
            output_path = None
        
        generator = QuittanceGenerator(contract_data, vehicle_data, owner_data, company_data)
        file_path = generator.generate(output_path)
        
        if parent:
            QMessageBox.information(
                parent,
                "Succès",
                f"✅ La quittance a été générée avec succès !\n\n📄 {file_path}"
            )
        
        return True
        
    except Exception as e:
        if parent:
            QMessageBox.critical(
                parent,
                "Erreur",
                f"❌ Erreur lors de la génération de la quittance :\n\n{str(e)}"
            )
        import traceback
        traceback.print_exc()
        return False