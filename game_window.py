from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import key_notifier
import map
import player
import pos
from multiprocessing import Lock
from threading import Thread
from time import sleep

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 960

P1_INIT_COORDINATES = pos.Coordinate(14,1)
P2_INIT_COORDINATES = pos.Coordinate(14,14)

mutex = Lock()

class GameWindow(QMainWindow):

    win_change_signal = QtCore.pyqtSignal()

    def __init__(self, list_of_names):
        super().__init__()

        # p1 = green
        # p2 = blue
       
        self.map = map.Map()
        
        self.player1 = player.Player(list_of_names[0], 1)
        self.player2 = player.Player(list_of_names[1], 2)

        self.player1.setupPlayer(P1_INIT_COORDINATES, self.map)
        self.player2.setupPlayer(P2_INIT_COORDINATES, self.map)

        self.key_notifier = key_notifier.KeyNotifier()
        self.key_notifier.key_signal.connect(self.keyPressListener)
        self.key_notifier.start()

        self.player1_thread = None
        self.player2_thread = None

        self.init_ui()

    def init_ui(self):        
        self.setWindowTitle('Try to win, if u can :P')
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.center_window()
        self.setCentralWidget(self.map)
        
    def move_player(self, player, coordinate):
        current_coordinate = player.getCurrentCoordinate()
        moved = False
        action = None
        with mutex:
            if coordinate.column > current_coordinate.column:
                action = "move_right"
                moved = player.move(coordinate, action)
            elif coordinate.column < current_coordinate.column:
                action = "move_left"
                moved = player.move(coordinate, action)
            else:
                if coordinate.row < current_coordinate.row:
                    action = "jump"
                    moved = player.move(coordinate, action)

    def center_window(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)
    
    def keyPressEvent(self, event):
        self.key_notifier.add_key(event.key())
    
    def closeEvent(self, evet):
        self.key_notifier.die()

    def keyPressListener(self, key):
        if key == Qt.Key_A or key == Qt.Key_W or key == Qt.Key_D or key == Qt.Key_Space:

            current_row = self.player1.player_coordinate.row
            current_column = self.player1.player_coordinate.column
            desiredCoordinate = pos.Coordinate(current_row,current_column)
            
            if key == Qt.Key_A:
                desiredCoordinate.column -= 1
            elif key == Qt.Key_D:
                desiredCoordinate.column += 1
            elif key == Qt.Key_W:
                desiredCoordinate.row -= 1
            else:
                # Puca
                pass
                #desiredCoordinate.row += 1
            self.player1_thread = Thread(None,self.move_player,args=[self.player1, desiredCoordinate], name="Player1Thread")
            self.player1_thread.start()

        elif key == Qt.Key_Left or Qt.Key_Right or Qt.Key_Up or Qt.Key_0:
            
            current_row = self.player2.player_coordinate.row
            current_column = self.player2.player_coordinate.column
            desiredCoordinate = pos.Coordinate(current_row,current_column)

            if key == Qt.Key_Left :
                desiredCoordinate.column -= 1
            elif key == Qt.Key_Right:
                desiredCoordinate.column += 1
            elif key == Qt.Key_Up:
                desiredCoordinate.row -= 1
            else:
                # Puca
                pass
                #desiredCoordinate.row += 1
            self.player2_thread = Thread(None,self.move_player,args=[self.player2, desiredCoordinate], name="Player2Thread")
            self.player2_thread.start()


    
