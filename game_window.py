from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import key_notifier
import map
import player
import pos
from threading import Thread
from time import sleep

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 960
JUMP_STEP = 3

class GameWindow(QMainWindow):

    win_change_signal = QtCore.pyqtSignal()

    def __init__(self, list_of_names):
        super().__init__()

        # p1 = green
        # p2 = blue
       
        self.player1 = player.Player(list_of_names[0], 1)
        self.player2 = player.Player(list_of_names[1], 2)

        self.player1.setPlayerLabelAndDirection()
        self.player2.setPlayerLabelAndDirection()

        self.player1_initPos = pos.Position()
        self.player2_initPos = pos.Position()

        self.player1_initPos.setPosition(pos.Coordinate(14,1), False, self.player1, False)
        self.player2_initPos.setPosition(pos.Coordinate(14,14), False, self.player2, False)
      
        self.map = map.Map()

        self.player1.setMap(self.map)
        self.player2.setMap(self.map)
        
        self.key_notifier = key_notifier.KeyNotifier()
        self.key_notifier.key_signal.connect(self.keyPressListener)
        self.key_notifier.start()

        self.player1_thread = None
        self.gravity_thread = None


        self.init_ui()

    def init_ui(self):        
        self.setWindowTitle('Try to win, if u can :P')
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.center_window()
        self.setCentralWidget(self.map)
        
        # Set position for player's
        self.move_player(self.player1, self.player1_initPos)
        self.move_player(self.player2, self.player2_initPos)

    def move_player(self, player, position):
        current_coordinate = player.getCurrentCoordinate()
        moved = False
        action = None
        if current_coordinate.isInit() == False:
            # If height is changing, do not change left/right
            if position.coordinate.row == current_coordinate.row:
                if position.coordinate.column > current_coordinate.column:
                    player.player_direction = "right"
                    action = "move_right"
                    moved = player.move(position, action)
                else:
                    player.player_direction = "left"
                    action = "move_left"
                    moved = player.move(position, action)
            else:
                if position.coordinate.row < current_coordinate.row:
                    action = "jump"
                    moved = player.move(position, action)
        else:
            print("Init case!")
            if player.player_id == 1:
                player.player_diraction = "right"
                moved = player.move(position, "move_right")
            else:
                player.player_direction = "left"
                moved = player.move(position, "move_left")


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
        if key == Qt.Key_Left or key == Qt.Key_Right or key == Qt.Key_Up or key == Qt.Key_Down:
            #Moving player to the left
            currenPlayerCoordinate = self.player1.getCurrentCoordinate()
            newPosition = pos.Position()
            
            if key == Qt.Key_Left:
                newPosition.setCoordinate(pos.Coordinate(currenPlayerCoordinate.row, currenPlayerCoordinate.column - 1))
            elif key == Qt.Key_Right:
                newPosition.setCoordinate(pos.Coordinate(currenPlayerCoordinate.row, currenPlayerCoordinate.column + 1))
            elif key == Qt.Key_Up:
                newPosition.setCoordinate(pos.Coordinate(currenPlayerCoordinate.row - 1, currenPlayerCoordinate.column))
            else:
                newPosition.setCoordinate(pos.Coordinate(currenPlayerCoordinate.row + 1, currenPlayerCoordinate.column))
            self.player1_thread = Thread(None,self.move_player,args=[self.player1, newPosition], name="Player1Thread")
            self.player1_thread.start()

    
