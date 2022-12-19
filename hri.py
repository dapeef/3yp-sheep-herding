from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys
import os
import json


class Ui(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI
        uic.loadUi("hri.ui", self)

        # Get data from json file
        self.data = self.readInfData()

        # Remove placeholders
        self.map_placeholder_home.deleteLater()
        self.map_placeholder_route.deleteLater()
        self.map_placeholder_map.deleteLater()

        # Hide buttons in map edit tab
        self.save_wall.setHidden(True)
        self.cancel_wall.setHidden(True)
        self.save_gate.setHidden(True)
        self.cancel_gate.setHidden(True)
        self.save_no_fly.setHidden(True)
        self.cancel_no_fly.setHidden(True)

        # Disable buttons until maps are loaded
        self.toggleButtonsEnabledHome(False)
        self.toggleButtonsEnabledRoute(False)
        self.toggleButtonsEnabledMap(False)

        # Initiate HTML elements for maps
        # Home
        self.browser_home = QWebEngineView(self.map_box_home)
        self.browser_home.load(QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0] + r'\web\home-index.html'))
        self.map_layout_home.addWidget(self.browser_home)
        self.browser_home.loadFinished.connect(self.onLoadFinishedHome) # Once loaded, connect buttons
        # Route edit
        self.browser_route = QWebEngineView(self.map_box_route)
        self.browser_route.load(QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0] + r'\web\route-index.html'))
        self.map_layout_route.addWidget(self.browser_route)
        self.browser_route.loadFinished.connect(self.onLoadFinishedRoute) # Once loaded, connect buttons
        # Map edit
        self.browser_map = QWebEngineView(self.map_box_map)
        self.browser_map.load(QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0] + r'\web\map-index.html'))
        self.map_layout_map.addWidget(self.browser_map)
        self.browser_map.loadFinished.connect(self.onLoadFinishedMap) # Once loaded, connect buttons


    # On map load
    def onLoadFinishedHome(self):
        print("Home map ready!")

        # Once map is loaded, connect buttons to functions
        self.stop_all.clicked.connect(self.stopAllClick)

        # Draw infrastructure
        self.drawInfrastructure()

        # Enable all buttons
        self.toggleButtonsEnabledHome(True)

        # Draw sheep, herding and monitor drones
        self.drawTestHome()

    def onLoadFinishedRoute(self):
        print("Route edit map ready!")

        # Once map is loaded, connect buttons to functions
        #self.stop_all.clicked.connect(self.buttonClick)
        
        # Draw infrastructure
        self.drawInfrastructure()

        # Enable all buttons
        self.toggleButtonsEnabledRoute(True)

    def onLoadFinishedMap(self):
        print("Map edit map ready!")

        # Populate lists from data
        for wall in self.data["walls"]: self.walls_list_widget.addItem(wall["name"])
        for gate in self.data["gates"]: self.gates_list_widget.addItem(gate["name"])
        for no_fly in self.data["no_fly"]: self.no_fly_list_widget.addItem(no_fly["name"])

        # Draw infrastructure
        self.drawInfrastructure()

        # Once map is loaded, connect buttons to functions
        # Walls
        self.add_wall.clicked.connect(self.addWall)
        self.remove_wall.clicked.connect(self.removeWall)
        self.save_wall.clicked.connect(self.saveWall)
        self.cancel_wall.clicked.connect(self.cancelWall)
        # Gates
        self.add_gate.clicked.connect(self.addGate)
        self.remove_gate.clicked.connect(self.removeGate)
        self.save_gate.clicked.connect(self.saveGate)
        self.cancel_gate.clicked.connect(self.cancelGate)
        # No fly zones
        self.add_no_fly.clicked.connect(self.addNoFly)
        self.remove_no_fly.clicked.connect(self.removeNoFly)

        # Enable all buttons
        self.toggleButtonsEnabledMap(True)

        # Change instruction
        self.instructions_label.setText("Press a button to begin")


    # Draw infrastructure on all maps
    def drawInfrastructure(self, data=None):
        if data == None: data = self.data

        self.browser_home.page().runJavaScript("drawInfrastructure(" + str(data) + ");")
        self.browser_route.page().runJavaScript("drawInfrastructure(" + str(data) + ");")
        self.browser_map.page().runJavaScript("drawInfrastructure(" + str(data) + ");")


    # Home tab
    def stopAllClick(self):
        print("Mmm, clickeroo")

        self.drawTestHome()

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

    def toggleButtonsEnabledHome(self, value):
        self.land_button1.setEnabled(value)
        self.land_button2.setEnabled(value)
        self.land_button3.setEnabled(value)
        self.land_button4.setEnabled(value)
        self.come_by.setEnabled(value)
        self.movement2.setEnabled(value)
        self.movement3.setEnabled(value)
        self.collect.setEnabled(value)
        self.stop_all.setEnabled(value)


    # Route tab
    def toggleButtonsEnabledRoute(self, value):
        self.pushButton_18.setEnabled(value)
        self.pushButton_19.setEnabled(value)


    # Map edit tab
    # Walls
    def addWall(self):
        # Change wall button options
        self.save_wall.setHidden(False)
        self.cancel_wall.setHidden(False)
        self.add_wall.setHidden(True)
        self.edit_wall.setHidden(True)
        self.remove_wall.setHidden(True)

        # Disable other buttons
        self.toggleButtonsEnabledMap(False)

        # Change instructions
        self.instructions_label.setText("Click 2 points to start the wall. When you're finished editing, press Save")

        # Call javascript
        self.browser_map.page().runJavaScript("makeWall();")

    def removeWall(self):
        selected_items = self.walls_list_widget.selectedItems()
        
        for item in selected_items:
            index = self.walls_list_widget.row(item)
            name = self.data["walls"][index]["name"]
            self.walls_list_widget.takeItem(index)
            self.data["walls"].pop(index)
            self.writeInfData()
        
        self.drawInfrastructure()

        # Change instructions
        self.instructions_label.setText("Successfully removed " + name)

    def saveWall(self):
        self.browser_map.page().runJavaScript("saveWall();", self.saveWallCallback)

    def saveWallCallback(self, points):
        # Revert button states
        self.resetAllButtonsMap()

        name = "Wall " + str(self.walls_list_widget.count())
        self.walls_list_widget.addItem(name)
        self.data["walls"].append({
            "name": name,
            "points": points
        })
        self.writeInfData()
        
        self.instructions_label.setText("Successfully added " + name)
        
        # Redraw infrastructure
        self.drawInfrastructure()

    def cancelWall(self):
        self.browser_map.page().runJavaScript("cancelWall();")

        # Revert button states
        self.resetAllButtonsMap()

    # Gates
    def addGate(self):
        # Change gate button options
        self.save_gate.setHidden(False)
        self.cancel_gate.setHidden(False)
        self.add_gate.setHidden(True)
        self.edit_gate.setHidden(True)
        self.remove_gate.setHidden(True)

        # Disable other buttons
        self.toggleButtonsEnabledMap(False)

        # Change instructions
        self.instructions_label.setText("Click 2 points on either side of the gate, starting with the hinge end, then press Save")

        # Call javascript
        self.browser_map.page().runJavaScript("makeGate();")
    
    def removeGate(self):
        selected_items = self.gates_list_widget.selectedItems()
        
        for item in selected_items:
            index = self.gates_list_widget.row(item)
            name = self.data["gates"][index]["name"]
            self.gates_list_widget.takeItem(index)
            self.data["gates"].pop(index)
            self.writeInfData()
        
        self.drawInfrastructure()

        # Change instructions
        self.instructions_label.setText("Successfully removed " + name)

    def saveGate(self):
        self.browser_map.page().runJavaScript("saveGate();", self.saveGateCallback)

    def saveGateCallback(self, points):
        # Revert button states
        self.resetAllButtonsMap()

        if len(points) == 2:
            name = "Gate " + str(self.gates_list_widget.count())
            self.gates_list_widget.addItem(name)
            self.data["gates"].append({
                "name": name,
                "points": points
            })
            self.writeInfData()
            
            self.instructions_label.setText("Successfully added " + name)
        
        else:
            self.instructions_label.setText("Wrong number of points selected; 2 required, " + str(len(points)) + " selected")
        
        # Redraw infrastructure
        self.drawInfrastructure()

    def cancelGate(self):
        self.browser_map.page().runJavaScript("saveGate();")

        # Revert button states
        self.resetAllButtonsMap()

    # No fly
    def addNoFly(self):
        name = "No fly zone " + str(self.no_fly_list_widget.count())
        self.no_fly_list_widget.addItem(name)
        self.data["no_fly"].append({"name": name})
        self.writeInfData()

    def removeNoFly(self):
        selected_items = self.no_fly_list_widget.selectedItems()
        
        for item in selected_items:
            index = self.no_fly_list_widget.row(item)
            name = self.data["no_fly"][index]["name"]
            self.no_fly_list_widget.takeItem(index)
            self.data["no_fly"].pop(index)
            self.writeInfData()

        # Change instructions
        self.instructions_label.setText("Successfully removed " + name)

    # Read and write infrastructure-data.json
    def readInfData(self):
        return json.load(open('infrastructure-data.json'))

    def writeInfData(self, data=None):
        if data == None: data = self.data

        with open('infrastructure-data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    # Handle buttons enabled
    def toggleButtonsEnabledMap(self, value):
        self.add_wall.setEnabled(value)
        self.edit_wall.setEnabled(value)
        self.remove_wall.setEnabled(value)
        self.add_gate.setEnabled(value)
        self.edit_gate.setEnabled(value)
        self.remove_gate.setEnabled(value)
        self.add_no_fly.setEnabled(value)
        self.edit_no_fly.setEnabled(value)
        self.remove_no_fly.setEnabled(value)
    
    def resetAllButtonsMap(self):
        # Wall
        self.save_wall.setHidden(True)
        self.cancel_wall.setHidden(True)
        self.add_wall.setHidden(False)
        self.edit_wall.setHidden(False)
        self.remove_wall.setHidden(False)
        # Gate
        self.save_gate.setHidden(True)
        self.cancel_gate.setHidden(True)
        self.add_gate.setHidden(False)
        self.edit_gate.setHidden(False)
        self.remove_gate.setHidden(False)
        # No fly
        self.save_no_fly.setHidden(True)
        self.cancel_no_fly.setHidden(True)
        self.add_no_fly.setHidden(False)
        self.edit_no_fly.setHidden(False)
        self.remove_no_fly.setHidden(False)

        # Enable other buttons
        self.toggleButtonsEnabledMap(True)

        # Reset instructions
        self.instructions_label.setText("Click a button to start")


app = QApplication(sys.argv)

window = Ui()
window.show()

app.exec()