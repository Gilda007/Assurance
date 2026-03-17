from PySide6.QtWidgets import QMessageBox
from core.logger import logger

class AlertManager:
    @staticmethod
    def show_error(parent, title, message, detailed_text=None):
        """Affiche une erreur critique et la logue."""
        logger.error(f"{title}: {message}")
        
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        if detailed_text:
            msg.setDetailedText(str(detailed_text))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    @staticmethod
    def show_info(parent, title, message):
        """Affiche une information de succès."""
        logger.info(message)
        QMessageBox.information(parent, title, message)