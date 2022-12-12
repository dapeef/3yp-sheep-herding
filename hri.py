from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize
import sys

app = QApplication(sys.argv)
app.setStyle("Fusion")

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sheep herding HRI")
        self.setMinimumSize(QSize(600, 400))

        # Tab object
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # Add tabs
        home_container = QWidget()
        tabs.addTab(home_container, "Home")
        edit_container = QWidget()
        tabs.addTab(edit_container, "Edit map")

        # Home tab layout
        home_layout = QVBoxLayout()
        home_container.setLayout(home_layout)

        # Home Buttons
        self.top_button = QPushButton('Top')
        self.top_button.setCheckable(True)
        self.top_button.clicked.connect(self.top_button_clicked)
        home_layout.addWidget(self.top_button)

        self.bottom_button = QPushButton('Bottom')
        self.bottom_button.clicked.connect(self.bottom_button_clicked)
        home_layout.addWidget(self.bottom_button)


        # Edit tab layout
        edit_layout = QVBoxLayout()
        edit_container.setLayout(edit_layout)

        # Edit Button
        self.edit_button = QPushButton('Edit')
        self.edit_button.setCheckable(True)
        self.edit_button.clicked.connect(self.edit_button_clicked)
        edit_layout.addWidget(self.edit_button)

        self.show()

    def edit_button_clicked(self, checked):
        print("EDIT", checked)

    def top_button_clicked(self, checked):
        print("TOP", checked)

    def bottom_button_clicked(self):
        print("BOTTOM")

window = Window()

app.exec()