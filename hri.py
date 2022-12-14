from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys
import os


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

        # Initiate HTML elements for maps
        self.webEngineView = QWebEngineView(self.map_box)
        self.webEngineView.load(QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0] + r'\map.html'))
        self.map_layout.addWidget(self.webEngineView)


    def button_click(self):
        print("Mmm, clickeroo")

        self.webEngineView.page().runJavaScript("add_marker(51.6255863, -2.5121819);")


app = QApplication(sys.argv)

window = Ui()

app.exec()