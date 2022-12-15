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
        self.map_placeholder_home.deleteLater()
        self.map_placeholder_route.deleteLater()
        self.map_placeholder_map.deleteLater()

        # Initiate HTML elements for maps
        # Home
        self.browser_home = QWebEngineView(self.map_box_home)
        self.browser_home.load(QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0] + r'\web\home\index-home.html'))
        self.map_layout_home.addWidget(self.browser_home)
        self.browser_home.loadFinished.connect(self.onLoadFinishedHome) # Once loaded, connect buttons
        # Route edit
        self.browser_route = QWebEngineView(self.map_box_route)
        self.browser_route.load(QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0] + r'\web\route\index-route.html'))
        self.map_layout_route.addWidget(self.browser_route)
        self.browser_route.loadFinished.connect(self.onLoadFinishedRoute) # Once loaded, connect buttons
        # Map edit
        self.browser_map = QWebEngineView(self.map_box_map)
        self.browser_map.load(QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0] + r'\web\map\index-map.html'))
        self.map_layout_map.addWidget(self.browser_map)
        self.browser_map.loadFinished.connect(self.onLoadFinishedMap) # Once loaded, connect buttons


    def onLoadFinishedHome(self):
        print("Home map ready!")

        # Once map is loaded, connect buttons to functions
        self.stop_all.clicked.connect(self.stopAllClick)

        # Draw sheep, herding and monitor drones
        self.drawTestHome()

    def onLoadFinishedRoute(self):
        print("Route edit map ready!")

        # Once map is loaded, connect buttons to functions
        #self.stop_all.clicked.connect(self.buttonClick)

    def onLoadFinishedMap(self):
        print("Map edit map ready!")

        # Once map is loaded, connect buttons to functions
        self.add_wall.clicked.connect(self.addWall)
        self.remove_wall.clicked.connect(self.removeWall)
        self.add_gate.clicked.connect(self.addGate)
        self.remove_gate.clicked.connect(self.removeGate)
        self.add_no_fly.clicked.connect(self.addNoFly)
        self.remove_no_fly.clicked.connect(self.removeNoFly)



    # Home tab
    def stopAllClick(self):
        print("Mmm, clickeroo")


    def drawTestHome(self):
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
        self.browser_home.page().runJavaScript("addMarkers(" + str(locations) + ", 'sheep');")

    def drawHerdingDrones(self, locations):
        self.browser_home.page().runJavaScript("addMarkers(" + str(locations) + ", 'herding_drones');")

    def drawMonitorDrones(self, locations):
        self.browser_home.page().runJavaScript("addMarkers(" + str(locations) + ", 'monitor_drones');")


    # Map edit tab
    def addWall(self):
        print("Omg let's make a new wall!")

        self.walls_list_widget.addItem("Wall " + str(self.walls_list_widget.count()))

    def removeWall(self):
        print("Omg let's remove a wall!")

        selected_items = self.walls_list_widget.selectedItems()
        
        for item in selected_items:
            index = self.walls_list_widget.row(item)

            self.walls_list_widget.takeItem(index)

            print(index)

    def addGate(self):
        print("Omg let's make a new gate!")

        self.gates_list_widget.addItem("Gate " + str(self.gates_list_widget.count()))

    def removeGate(self):
        print("Omg let's remove a gate!")

        selected_items = self.gates_list_widget.selectedItems()
        
        for item in selected_items:
            index = self.gates_list_widget.row(item)

            self.gates_list_widget.takeItem(index)

            print(index)

    def addNoFly(self):
        print("Omg let's make a new no fly zone!")

        self.no_fly_list_widget.addItem("No fly zone " + str(self.no_fly_list_widget.count()))

    def removeNoFly(self):
        print("Omg let's remove a no fly zone!")

        selected_items = self.no_fly_list_widget.selectedItems()
        
        for item in selected_items:
            index = self.no_fly_list_widget.row(item)

            self.no_fly_list_widget.takeItem(index)

            print(index)


app = QApplication(sys.argv)

window = Ui()

app.exec()