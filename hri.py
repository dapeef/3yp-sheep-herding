from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys


class Ui(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI
        uic.loadUi("hri.ui", self)
        self.show()

        # Tether buttons to functions
        self.stop_all.clicked.connect(self.button_click)


    def button_click(self):
        print("Mmm, clickeroo")


app = QApplication(sys.argv)

window = Ui()

app.exec()