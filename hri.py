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

        # Initiate HTML elements for maps
        self.browser = QWebEngineView(self.map_box)
        self.browser.load(QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0] + r'\map.html'))
        self.map_layout.addWidget(self.browser)
        self.browser.loadFinished.connect(self.onLoadFinished) # Once loaded, connect buttons


    def onLoadFinished(self):
        # Once map is loaded, connect buttons to functions
        self.stop_all.clicked.connect(self.buttonClick)

        print("Ready!")


    def buttonClick(self):        
        print("Mmm, clickeroo")

        self.drawTest()


    def drawTest(self):
        sheep_locations = [
            [51.6255863, -2.5121819],
            [51.626060, -2.512327],
            [51.626045, -2.512716],
            [51.626151, -2.511915],
            [51.625848, -2.512039],
            [51.625616, -2.512513],
            [51.625737, -2.512117]
        ]

        herding_drone_locations = [
            [51.626360, -2.513160],
            [51.626485, -2.512436],
            [51.626504, -2.511712]
        ]

        monitor_drone_locations = [
            [51.625987, -2.512303]
        ]

        self.drawSheep(sheep_locations)
        self.drawHerdingDrones(herding_drone_locations)
        self.drawMonitorDrones(monitor_drone_locations)

    def drawSheep(self, locations):
        self.browser.page().runJavaScript("addMarkers(" + str(locations) + ", 'sheep');")

    def drawHerdingDrones(self, locations):
        self.browser.page().runJavaScript("addMarkers(" + str(locations) + ", 'herding_drones');")

    def drawMonitorDrones(self, locations):
        self.browser.page().runJavaScript("addMarkers(" + str(locations) + ", 'monitor_drones');")


app = QApplication(sys.argv)

window = Ui()

app.exec()