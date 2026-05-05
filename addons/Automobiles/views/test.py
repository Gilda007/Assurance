def create_header(self, styles):
    """Crée l'en-tête du document avec logo et informations"""
    
    # 1. Préparation du logo
    # Remplacez 'logo_ams.png' par le chemin réel de l'image sur votre machine
    logo_path = "addons/Automobiles/static/logo.png" 
    try:
        # Ajustez la largeur (width) et la hauteur (height) selon vos besoins
        logo = Image(logo_path, width=25*mm, height=20*mm)
        logo.hAlign = 'RIGHT'
    except:
        logo = "LOGO NON TROUVÉ" # Sécurité si l'image est manquante

    # Ajouter un indicateur de statut dans l'en-tête
    status_indicator = "🔴" if not self.is_paid else "🟢"
    status_text = "PAYÉ" if self.is_paid else "IMPAYÉ"
    
    # 2. Structure des données - Logo à droite sur la même ligne
    header_data = [
        [f"N° Police: {self.data.get('numero_police', 'N/A')}", logo],
        ["Assureur agréé", f"{status_indicator} Statut: {status_text}"],
    ]
    
    header_table = Table(header_data, colWidths=[90*mm, 70*mm])
    header_table.setStyle(TableStyle([
        # Style du titre principal (colonne 0, ligne 0)
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 16),
        ('TEXTCOLOR', (0, 0), (0, 0), self.colors['primary']),
        
        # Logo à droite (colonne 1, ligne 0)
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 10),
        ('RIGHTPADDING', (1, 0), (1, 0), 0),
        ('TOPPADDING', (1, 0), (1, 0), 5),
        ('BOTTOMPADDING', (1, 0), (1, 0), 5),

        # Style du texte "Assureur agréé" (colonne 0, ligne 1)
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (0, 1), 9),
        ('TEXTCOLOR', (0, 1), (0, 1), self.colors['gray']),
        ('ALIGN', (0, 1), (0, 1), 'LEFT'),

        # Style du texte de droite (colonne 1, ligne 1)
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica'),
        ('FONTSIZE', (1, 1), (1, 1), 9),
        ('TEXTCOLOR', (1, 1), (1, 1), self.colors['gray']),
        ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
        
        # Style du statut (colonne 1, ligne 1)
        ('TEXTCOLOR', (1, 1), (1, 1), self.colors['success'] if self.is_paid else self.colors['danger']),
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
        
        # Alignement vertical général
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    return header_table