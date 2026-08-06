# addons/Automobiles/reports/utils.py
import os
def create_default_logo(output_path=None):
    """
    Crée un logo simple pour l'application si aucun logo n'existe.
    """
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    
    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'static', 
            'logo.png'
        )
    
    # Créer le dossier si nécessaire
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Créer un canvas PDF temporaire
    temp_pdf = output_path.replace('.png', '_temp.pdf')
    c = canvas.Canvas(temp_pdf, pagesize=(200, 80))
    
    # Dessiner un rectangle avec dégradé
    c.setFillColor(colors.HexColor('#1a56db'))
    c.rect(0, 0, 200, 80, fill=1)
    
    # Texte
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 24)
    c.drawString(20, 25, "AMS")
    c.setFont('Helvetica', 12)
    c.drawString(80, 30, "ASSURANCES")
    
    c.save()
    
    # Convertir PDF en PNG nécessite des outils supplémentaires
    # Pour simplifier, on garde juste le nom de l'entreprise
    print(f"⚠️ Logo simple créé en PDF: {temp_pdf}")
    print(f"📌 Pour un logo PNG, veuillez ajouter {output_path}")
    
    return output_path