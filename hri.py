from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys


class Ui(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("hri.ui", self)

        self.show()


app = QApplication(sys.argv)

window = Ui()

app.exec()