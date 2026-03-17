

class AboutUsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        logo = QLabel("AMS AUTO")
        logo.setStyleSheet("font-size: 32px; font-weight: bold; color: #1e3a8a;")
        desc = QLabel("v1.1.0\nSystème de Gestion d'Assurance Automobile\n© 2026 Fearless Software")
        desc.setAlignment(Qt.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(logo)
        layout.addWidget(desc)
        layout.addStretch()