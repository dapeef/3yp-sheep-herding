from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys


class Ui(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI
        uic.loadUi("hri.ui", self)
        self.show()

        # Remove placeholders
        self.map_placeholder.deleteLater()
        self.map_placeholder_2.deleteLater()
        self.map_placeholder_3.deleteLater()

        # Tether buttons to functions
        self.stop_all.clicked.connect(self.button_click)


    def button_click(self):
        print("Mmm, clickeroo")


app = QApplication(sys.argv)

window = Ui()

app.exec()