# test_minimal.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

class MinimalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Minimal")
        self.setCentralWidget(QLabel("L'application fonctionne !"))
        self.resize(400, 300)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinimalWindow()
    window.show()
    sys.exit(app.exec())