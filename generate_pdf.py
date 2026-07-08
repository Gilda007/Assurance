#!/usr/bin/env python3
"""
Générateur de PDF pour la présentation LOMETA
Convertit le fichier HTML en PDF professionnel
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def generate_pdf():
    """Génère le PDF à partir du fichier HTML"""
    
    # Vérifier les dépendances
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        print("❌ WeasyPrint non installé. Installation en cours...")
        os.system("pip install weasyprint")
        from weasyprint import HTML, CSS
    
    # Chemins
    html_file = Path(__file__).parent / "presentation_lometa.html"
    pdf_file = Path(__file__).parent / "LOMETA_Presentation.pdf"
    
    if not html_file.exists():
        print(f"❌ Fichier HTML introuvable: {html_file}")
        return False
    
    print(f"📄 Génération du PDF depuis: {html_file}")
    print(f"📁 Destination: {pdf_file}")
    
    try:
        # Générer le PDF
        HTML(filename=str(html_file)).write_pdf(
            str(pdf_file),
            stylesheets=[
                CSS(string='''
                    @page {
                        size: A4;
                        margin: 0.5cm;
                    }
                ''')
            ]
        )
        print(f"✅ PDF généré avec succès: {pdf_file}")
        print(f"📊 Taille: {pdf_file.stat().st_size / 1024:.1f} KB")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF: {e}")
        return False

def preview_pdf():
    """Ouvre le PDF généré"""
    pdf_file = Path(__file__).parent / "LOMETA_Presentation.pdf"
    
    if not pdf_file.exists():
        print("❌ PDF introuvable. Veuillez d'abord le générer.")
        return
    
    # Ouvrir selon le système d'exploitation
    if sys.platform == 'win32':
        os.startfile(str(pdf_file))
    elif sys.platform == 'darwin':
        os.system(f'open "{pdf_file}"')
    else:
        os.system(f'xdg-open "{pdf_file}"')

if __name__ == "__main__":
    print("=" * 60)
    print("📄 Générateur de présentation LOMETA")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        preview_pdf()
    else:
        generate_pdf()