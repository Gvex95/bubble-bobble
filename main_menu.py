from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_HOR_POSITION = 550
SCREEN_VER_POSITION = 200

class MainWindow(QMainWindow):

    win_change_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        # Background image and pallete for main window
        self.bImage = QImage("images/main_menu.jpg")
        self.palette = QPalette()
        
        # Main menu buttons
        self.enterNames = QPushButton('Select player', self)
        self.quitButton = QPushButton('Quit', self)

        # QWidget which stores buttons
        self.qWidget = QWidget()
        
        # Initialize main menu ui
        self.init_ui()

    def init_ui(self):        
        # Add background
        self.setWindowTitle('Bubble-Bobble game')
        self.setGeometry(SCREEN_HOR_POSITION, SCREEN_VER_POSITION, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.palette.setBrush(QPalette.Window, QBrush(self.bImage))
        self.setPalette(self.palette)
        
        # Modify buttons
        self.enterNames.setFixedSize(250, 50)
        self.enterNames.setStyleSheet("background-color: #33ffff;""font: 25pt Comic Sans MS;""color: black;""border-radius: 20px;")
        self.enterNames.clicked.connect(lambda : self.onEnterNames())

        self.quitButton.setFixedSize(250, 50)
        self.quitButton.setStyleSheet("background-color: #33ffff;""font: 25pt Comic Sans MS;""color: black;""border-radius: 20px;")
        self.quitButton.clicked.connect(lambda : self.onQuitPressed())

        # Add vertical layout
        horizonal_layout = QVBoxLayout()
        horizonal_layout.addWidget(self.enterNames)
        horizonal_layout.addWidget(self.quitButton)
        horizonal_layout.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        
        # Add layout inside widget
        self.qWidget.setLayout(horizonal_layout)

        # Add central widget which contains buttons
        self.setCentralWidget(self.qWidget)

    def onQuitPressed(self):
        print("onQuit pressed")
        self.close()

    def onEnterNames(self):
        print("onEnterNamePressed")
        self.win_change_signal.emit()