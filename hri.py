from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QProcess
from PyQt5.QtGui import QPixmap
import sys
import os
import json
import image_processing as ip
import transform as tf
import pygame as pg


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

        # Hide no fly zone menu entirely - decided not to implement this
        self.no_fly_box.setHidden(True)

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


        # Add items to live view dropdown menu
        self.live_view_menu.addItems(["RGB", "Infrared"])
        self.live_view_menu.currentTextChanged.connect(self.liveViewTextChange)

        # Pixmap to hold live view image
        self.rgb_image_file = "images\chapel-cottage.jpg"
        self.live_view_pix = QPixmap(self.rgb_image_file)
        self.live_view_tab.resizeEvent = self.resizeLiveViewImage

    # On map load
    def onLoadFinishedHome(self):
        print("Home map ready!")

        # Create pipe and boids
        self.p_boids = QProcess()
        self.p_boids.readyReadStandardOutput.connect(self.timeStepHome)
        self.p_boids.start("python", ['boids.py'])

        # Once map is loaded, connect buttons to functions
        self.stop_all.clicked.connect(self.stopAllClick)

        # Draw infrastructure
        self.drawInfrastructure()

        # Enable all buttons
        self.toggleButtonsEnabledHome(True)

        # Draw sheep, herding and monitor drones
        self.timeStepHome()

    def onLoadFinishedRoute(self):
        print("Route edit map ready!")
        
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

        # Connect buttons to functions
        # Walls
        self.walls_list_widget.keyPressEvent = self.wallKeyPress
        self.add_wall.clicked.connect(self.addWall)
        self.edit_wall.clicked.connect(self.editWall)
        self.remove_wall.clicked.connect(self.removeWall)
        self.save_wall.clicked.connect(self.saveWall)
        self.cancel_wall.clicked.connect(self.cancelWall)
        # Gates
        self.gates_list_widget.keyPressEvent = self.gateKeyPress
        self.add_gate.clicked.connect(self.addGate)
        self.edit_gate.clicked.connect(self.editGate)
        self.remove_gate.clicked.connect(self.removeGate)
        self.save_gate.clicked.connect(self.saveGate)
        self.cancel_gate.clicked.connect(self.cancelGate)
        # No fly zones
        self.no_fly_list_widget.keyPressEvent = self.noFlyKeyPress
        self.add_no_fly.clicked.connect(self.addNoFly)
        self.edit_no_fly.clicked.connect(self.editNoFly)
        self.remove_no_fly.clicked.connect(self.removeNoFly)

        # Connect on-change for list widgets
        self.walls_list_widget.currentItemChanged.connect(self.selectWall)
        self.gates_list_widget.currentItemChanged.connect(self.selectGate)
        self.no_fly_list_widget.currentItemChanged.connect(self.selectNoFly)

        # Enable all buttons
        self.toggleButtonsEnabledMap(True)

        # Change instruction
        self.instructions_label.setText("Press a button to begin")

        # Mode
        self.mode = None


    # Draw infrastructure on all maps
    def drawInfrastructure(self, data=None):
        if data == None: data = self.data

        self.browser_home.page().runJavaScript("drawInfrastructure(" + str(data) + ");")
        self.browser_route.page().runJavaScript("drawInfrastructure(" + str(data) + ");")
        self.browser_map.page().runJavaScript("drawInfrastructure(" + str(data) + ");")


    # Home tab
    def stopAllClick(self):
        print("Mmm, clickeroo")

        self.timeStepHome()

    def timeStepHome(self):
        # try:

        # Receive data from boids stdout
        data = self.p_boids.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")

        # Parse JSON
        try:
            json_data = json.loads(stdout)
        
        except json.decoder.JSONDecodeError:
            json_data = {
                "sheep": [],
                "drones": [],
                "monitoring": [[51.623510, -2.512716]],
                "window_size": {
                    "width": 1200,
                    "height": 800
                }
            }

        sheep_locations = json_data["sheep"]
        herding_drone_locations = json_data["drones"]
        monitor_drone_locations = json_data["monitoring"]
        
        if os.path.exists("temp\\boids.png"):
            # Update image in "live view" tab
            if self.live_view_menu.currentText() == "RGB":
                self.rgb_image_file = "temp\\boids.png"
                self.live_view_pix = QPixmap("temp\\boids.png")
                self.resizeLiveViewImage()
            
            # Run Qianyi's algorithm on image to get sheep positions
            local_sheep_locations = ip.getCoordinates("temp\\boids.png")

            sheep_locations = []
            camera_pos = tf.TransformLP(pg.Vector2(monitor_drone_locations[0]))
            camera_pos -= pg.Vector2(json_data["window_size"]["width"], json_data["window_size"]["height"]) / 2

            # print(camera_pos)

            for local_location in local_sheep_locations:
                local_location += camera_pos
                global_location = tf.TransformPL(pg.Vector2(local_location))

                sheep_locations.append([global_location.x, global_location.y])
        
        # except Exception as e:
        #     # If something goes wrong with the data transfer/processing
        #     sheep_locations = []
        #     herding_drone_locations = []
        #     monitor_drone_locations = []

        # Draw markers
        self.drawSheep(sheep_locations)
        self.drawHerdingDrones(herding_drone_locations)
        self.drawMonitorDrones(monitor_drone_locations)

    def drawSheep(self, locations):
        self.browser_home.page().runJavaScript("addDots(" + str(locations) + ", 'sheep');")

    def drawHerdingDrones(self, locations):
        self.browser_home.page().runJavaScript("addDots(" + str(locations) + ", 'herding_drones');")

    def drawMonitorDrones(self, locations):
        self.browser_home.page().runJavaScript("addDots(" + str(locations) + ", 'monitor_drones');")

    def toggleButtonsEnabledHome(self, value):
        self.land_button1.setEnabled(value)
        self.land_button2.setEnabled(value)
        self.land_button3.setEnabled(value)
        self.land_button4.setEnabled(value)
        self.start_route.setEnabled(value)
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
        
    def editWall(self):
        # Get selected index
        index = self.getSelectedIndex(self.walls_list_widget)

        # If something is selected
        if index != None:
            self.mode = "edit_wall"

            # Change wall button options
            self.walls_list_widget.setEnabled(False)
            self.save_wall.setHidden(False)
            self.cancel_wall.setHidden(False)
            self.add_wall.setHidden(True)
            self.edit_wall.setHidden(True)
            self.remove_wall.setHidden(True)

            # Disable other buttons
            self.toggleButtonsEnabledMap(False)

            # Change instructions
            self.instructions_label.setText("Drag the markers to edit. When you're finished editing, press Save")

            # Call javascript
            self.browser_map.page().runJavaScript("editWall(" + str(index) + ");")

    def removeWall(self):
        index = self.getSelectedIndex(self.walls_list_widget)
        
        if index != None:
            name = self.data["walls"][index]["name"]
            self.walls_list_widget.takeItem(index)
            self.data["walls"].pop(index)
            self.writeInfData()
        
            self.drawInfrastructure()

            # Change instructions
            self.instructions_label.setText("Successfully removed " + name)

    def saveWall(self):
        if self.mode == "edit_wall":
            index = self.getSelectedIndex(self.walls_list_widget)

            self.browser_map.page().runJavaScript("saveWall(" + str(index) + ");", self.saveWallCallback)

        else:
            self.browser_map.page().runJavaScript("saveWall();", self.saveWallCallback)

    def saveWallCallback(self, points):
        if self.mode == "edit_wall":
            index = self.getSelectedIndex(self.walls_list_widget)

            self.data["walls"][index]["points"] = points
            
            self.instructions_label.setText("Successfully edited " + self.data["walls"][index]["name"])

        else:
            if points != None:
                name = "Wall " + str(self.walls_list_widget.count())
                self.walls_list_widget.addItem(name)
                self.data["walls"].append({
                    "name": name,
                    "points": points
                })
                
                self.instructions_label.setText("Successfully added " + name)
            
            else:
                self.instructions_label.setText("Save failed; not enough points selected")

        self.writeInfData()

        # Revert button states
        self.resetAllButtonsMap()
        
        # Redraw infrastructure
        self.drawInfrastructure()

    def cancelWall(self):
        self.browser_map.page().runJavaScript("cancelWall();")

        self.instructions_label.setText("Press a button to begin")

        # Revert button states
        self.resetAllButtonsMap()

        self.drawInfrastructure()

    def selectWall(self, item):
        self.edit_wall.setEnabled(True)
        self.remove_wall.setEnabled(True)

        index = self.walls_list_widget.row(item)

        self.browser_map.page().runJavaScript("selectWall(" + str(self.data["walls"][index]["points"]) + ");")

    def deselectWall(self):
        self.walls_list_widget.clearSelection()
            
        self.edit_wall.setEnabled(False)
        self.remove_wall.setEnabled(False)

        self.browser_map.page().runJavaScript("deselectWall()")

    def wallKeyPress(self, event):
        key = event.key()

        if key in [Qt.Key_Delete, Qt.Key_Backspace]:
            self.removeWall()
        
            self.deselectWall()

        elif key == Qt.Key_Escape:
            self.deselectWall()

        elif key == Qt.Key_Up:
            self.moveInListWidget(self.walls_list_widget, -1)

        elif key == Qt.Key_Down:
            self.moveInListWidget(self.walls_list_widget, +1)

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
        self.instructions_label.setText("Click 2 points on either side of the gate, starting with the hinge end. These markers are draggable. When finished, press Save.")

        # Call javascript
        self.browser_map.page().runJavaScript("makeGate();")

    def editGate(self):
        # Get selected index
        index = self.getSelectedIndex(self.gates_list_widget)

        # If something is selected
        if index != None:
            self.mode = "edit_gate"

            # Change gate button options
            self.gates_list_widget.setEnabled(False)
            self.save_gate.setHidden(False)
            self.cancel_gate.setHidden(False)
            self.add_gate.setHidden(True)
            self.edit_gate.setHidden(True)
            self.remove_gate.setHidden(True)

            # Disable other buttons
            self.toggleButtonsEnabledMap(False)

            # Change instructions
            self.instructions_label.setText("Click 2 points on either side of the gate, starting with the hinge end. These markers are draggable. When finished, press Save.")

            # Call javascript
            self.browser_map.page().runJavaScript("editGate(" + str(index) + ");")
    
    def removeGate(self):
        index = self.getSelectedIndex(self.gates_list_widget)
        
        if index != None:
            name = self.data["gates"][index]["name"]
            self.gates_list_widget.takeItem(index)
            self.data["gates"].pop(index)
            self.writeInfData()
        
        self.drawInfrastructure()

        # Change instructions
        self.instructions_label.setText("Successfully removed " + name)

    def saveGate(self):
        if self.mode == "edit_gate":
            index = self.getSelectedIndex(self.gates_list_widget)

            self.browser_map.page().runJavaScript("saveGate(" + str(index) + ");", self.saveGateCallback)

        else:
            self.browser_map.page().runJavaScript("saveGate();", self.saveGateCallback)

    def saveGateCallback(self, points):
        if self.mode == "edit_gate":
            index = self.getSelectedIndex(self.gates_list_widget)

            self.data["gates"][index]["points"] = points
            
            self.instructions_label.setText("Successfully edited " + self.data["gates"][index]["name"])

        else:
            if len(points) == 2:
                name = "Gate " + str(self.gates_list_widget.count())
                self.gates_list_widget.addItem(name)
                self.data["gates"].append({
                    "name": name,
                    "points": points
                })
                
                self.instructions_label.setText("Successfully added " + name)
            
            else:
                self.instructions_label.setText("Wrong number of points selected; 2 required, " + str(len(points)) + " selected")
        
        self.writeInfData()

        # Revert button states
        self.resetAllButtonsMap()

        # Redraw infrastructure
        self.drawInfrastructure()

    def cancelGate(self):
        self.browser_map.page().runJavaScript("cancelGate();")

        # Revert button states
        self.resetAllButtonsMap()

        self.drawInfrastructure()

    def selectGate(self, item):
        self.edit_gate.setEnabled(True)
        self.remove_gate.setEnabled(True)

        index = self.gates_list_widget.row(item)

        self.browser_map.page().runJavaScript("selectGate(" + str(self.data["gates"][index]["points"]) + ");")

    def deselectGate(self):
        self.gates_list_widget.clearSelection()
            
        self.edit_gate.setEnabled(False)
        self.remove_gate.setEnabled(False)

        self.browser_map.page().runJavaScript("deselectGate()")

    def gateKeyPress(self, event):
        key = event.key()

        if key in [Qt.Key_Delete, Qt.Key_Backspace]:
            self.removeGate()
        
            self.deselectGate()

        elif key == Qt.Key_Escape:
            self.deselectGate()

        elif key == Qt.Key_Up:
            self.moveInListWidget(self.gates_list_widget, -1)

        elif key == Qt.Key_Down:
            self.moveInListWidget(self.gates_list_widget, +1)

    # No fly
    def addNoFly(self):
        name = "No fly zone " + str(self.no_fly_list_widget.count())
        self.no_fly_list_widget.addItem(name)
        self.data["no_fly"].append({"name": name})
        self.writeInfData()
        
    def editNoFly(self):
        name = "No fly zone " + str(self.no_fly_list_widget.count())
        self.no_fly_list_widget.addItem(name)
        self.data["no_fly"].append({"name": name})
        self.writeInfData()

    def removeNoFly(self):
        index = self.getSelectedIndex(self.no_fly_list_widget)
        
        if index != None:
            name = self.data["no_fly"][index]["name"]
            self.no_fly_list_widget.takeItem(index)
            self.data["no_fly"].pop(index)
            self.writeInfData()

        # Change instructions
        self.instructions_label.setText("Successfully removed " + name)

    def saveNoFly(self):
        if self.mode == "edit_no_fly":
            index = self.getSelectedIndex(self.no_fly_list_widget)

            self.browser_map.page().runJavaScript("saveNoFly(" + str(index) + ");", self.saveNoFlyCallback)

        else:
            self.browser_map.page().runJavaScript("saveNoFly();", self.saveNoFlyCallback)

    def saveNoFlyCallback(self, points):
        if self.mode == "edit_no_fly":
            index = self.getSelectedIndex(self.no_fly_list_widget)

            self.data["no_fly"][index]["points"] = points
            
            self.instructions_label.setText("Successfully edited " + self.data["no_fly"][index]["name"])

        else:
            if points != None:
                name = "No fly zone " + str(self.no_Fly_list_widget.count())
                self.no_fly_list_widget.addItem(name)
                self.data["no_fly"].append({
                    "name": name,
                    "points": points
                })
                
                self.instructions_label.setText("Successfully added " + name)
            
            else:
                self.instructions_label.setText("Save failed; not enough points selected")
        
        self.writeInfData()

        # Revert button states
        self.resetAllButtonsMap()

        # Redraw infrastructure
        self.drawInfrastructure()

    def selectNoFly(self, item):
        self.edit_no_fly.setEnabled(True)
        self.remove_no_fly.setEnabled(True)

        print("No fly zone selected")

    def deselectNoFly(self):
        self.no_fly_list_widget.clearSelection()
            
        self.edit_no_fly.setEnabled(False)
        self.remove_no_fly.setEnabled(False)

        self.browser_map.page().runJavaScript("deselectNoFly()")

    def noFlyKeyPress(self, event):
        key = event.key()

        if key in [Qt.Key_Delete, Qt.Key_Backspace]:
            self.removeNoFly()
        
            self.deselectNoFly()

        elif key == Qt.Key_Escape:
            self.deselectNoFly()

        elif key == Qt.Key_Up:
            self.moveInListWidget(self.no_fly_list_widget, -1)

        elif key == Qt.Key_Down:
            self.moveInListWidget(self.no_fly_list_widget, +1)

    # Read and write infrastructure-data.json
    def readInfData(self):
        return json.load(open('infrastructure-data.json'))

    def writeInfData(self, data=None):
        if data == None: data = self.data

        with open('infrastructure-data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    # Handle buttons enabled
    def toggleButtonsEnabledMap(self, value):
        # Walls
        self.add_wall.setEnabled(value)
        if self.getSelectedIndex(self.walls_list_widget) == None or value == False:
            self.edit_wall.setEnabled(False)
            self.remove_wall.setEnabled(False)
        else:
            self.edit_wall.setEnabled(True)
            self.remove_wall.setEnabled(True)

        # Gates
        self.add_gate.setEnabled(value)
        if self.getSelectedIndex(self.gates_list_widget) == None or value == False:
            self.edit_gate.setEnabled(False)
            self.remove_gate.setEnabled(False)
        else:
            self.edit_gate.setEnabled(True)
            self.remove_gate.setEnabled(True)

        # No fly
        self.add_no_fly.setEnabled(value)
        if self.getSelectedIndex(self.no_fly_list_widget) == None or value == False:
            self.edit_no_fly.setEnabled(False)
            self.remove_no_fly.setEnabled(False)
        else:
            self.edit_no_fly.setEnabled(True)
            self.remove_no_fly.setEnabled(True)
    
    def resetAllButtonsMap(self):
        self.mode = None

        # Wall
        self.walls_list_widget.setEnabled(True)
        self.save_wall.setHidden(True)
        self.cancel_wall.setHidden(True)
        self.add_wall.setHidden(False)
        self.edit_wall.setHidden(False)
        self.remove_wall.setHidden(False)
        # Gate
        self.gates_list_widget.setEnabled(True)
        self.save_gate.setHidden(True)
        self.cancel_gate.setHidden(True)
        self.add_gate.setHidden(False)
        self.edit_gate.setHidden(False)
        self.remove_gate.setHidden(False)
        # No fly
        self.no_fly_list_widget.setEnabled(True)
        self.save_no_fly.setHidden(True)
        self.cancel_no_fly.setHidden(True)
        self.add_no_fly.setHidden(False)
        self.edit_no_fly.setHidden(False)
        self.remove_no_fly.setHidden(False)

        # Enable other buttons
        self.toggleButtonsEnabledMap(True)

    def moveInListWidget(self, widget, row_diff):
        row = self.getSelectedIndex(widget)

        if row != None:
            new_row = min(max(0, row + row_diff), widget.count()-1)

            widget.setCurrentRow(new_row)

    def getSelectedIndex(self, list_widget):
        selected_items = list_widget.selectedItems()

        if len(selected_items) == 1:
            return list_widget.row(selected_items[0])
        
        else:
            return None


    # Live view tab
    # Update image dimensions
    def resizeLiveViewImage(self, *args, **kwargs):
        width = self.live_view_image_label.width()
        height = self.live_view_image_label.height() - 1
        
        self.live_view_image_label.setPixmap(self.live_view_pix.scaled(width, height, aspectRatioMode=1))

    def liveViewTextChange(self, value):
        if value == "RGB":
            self.live_view_pix = QPixmap(self.rgb_image_file)
        
        elif value == "Infrared":
            self.live_view_pix = QPixmap("images\chapel-cottage-inverted.jpg")
        
        self.resizeLiveViewImage()


class Hri():
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.window = Ui()
        self.window.show()

    def mainloop(self):
        self.app.exec()


if __name__ == "__main__":
    hri = Hri()

    hri.mainloop()
