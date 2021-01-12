from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import key_notifier
import map
import game_engine
import player
import pos
import enemy


from multiprocessing import Lock
from threading import Thread
from time import sleep

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 960

P1_INIT_COORDINATE = pos.Coordinate(14,1)
P2_INIT_COORDINATE = pos.Coordinate(14,14)
ENEMY_INIT_COORDIATE = pos.Coordinate(5,7)
mutex = Lock()

class GameWindow(QMainWindow):

    win_change_signal = QtCore.pyqtSignal()

    def __init__(self, list_of_names):
        super().__init__()

        # p1 = green
        # p2 = blue

        # Create map and game engine       
        self.map = map.Map()
        self.gameEngine = game_engine.GameEngine(self.map)
        

        # Add key notifier thread for player movment
        self.key_notifier = key_notifier.KeyNotifier()
        self.key_notifier.key_signal.connect(self.keyPressListener)
        self.key_notifier.start()

        # Add threads for player's movment
        self.player1_move_thread = None
        self.player2_move_thread = None
        self.enemies_thread = None

        # Create and sutup players
        self.player1 = player.Player(list_of_names[0], 1)
        self.player2 = player.Player(list_of_names[1], 2)
        self.player1.setupPlayer()
        self.player2.setupPlayer()

        self.running = True

        # Setup initial level number and number of enemies
        self.level = 1
        self.numOfEnemies = 3
        self.thinkTime = 0.4

        # Move player to their initial positions
        self.gameEngine.move(P1_INIT_COORDINATE, self.player1)
        self.gameEngine.move(P2_INIT_COORDINATE, self.player2)

        self.init_ui()

    def init_ui(self):        
        # Setup window and centar widget
        self.setWindowTitle('Try to win, if u can :P')
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.center_window()
        self.setCentralWidget(self.map)
        # Start level        
        self.startLevel(self.numOfEnemies)

        self.canMove = True
            
    def startLevel(self, numOfEnemies):
        self.enemies = []
        if self.level < 3:
            enemy_name = "benzo"
        elif self.level >= 3 and self.level < 6:
            enemy_name = "bonnie"
        elif self.level >= 6 and self.level < 9:
            enemy_name = "bonner"
        elif self.level >= 9 and self.level < 12:
            enemy_name = "boris"
        else:
            enemy_name = "boa"
        
        for i in range(numOfEnemies):
            e = enemy.Enemy(enemy_name + "_" + str(i+1))
            print("Created enemy with name: ", e.name)
            e.setupEnemy()
            self.enemies.append(e)

        #Comment out this if u don't want to start enemies
        self.initEnemies()

    def initEnemies(self):
        for enemy in self.enemies: 
            self.gameEngine.move(ENEMY_INIT_COORDIATE, enemy)
            self.enemies_thread = Thread(None,self.startAI,args=[enemy], name="EnemiesThread", daemon=True)
            self.enemies_thread.start()
            # This should give us enough time to move enemy that was spawned here and to move here second enemy
            ENEMY_INIT_COORDIATE.column += 1


    def startAI(self, enemy):        
        while(self.running):
            # Find which player is closer. If distance is same, attack player 1 :P
            id = self.getCloserPlayer(enemy)
            #print("Goten id: ", id)

            # Execute step to move closer to player which is closer
            desiredCoordinate = None
            if id == 1:
                desiredCoordinate = pos.Coordinate(self.player1.coordinate.row, self.player1.coordinate.column)
            else:
                desiredCoordinate = pos.Coordinate(self.player2.coordinate.row, self.player2.coordinate.column)

            # Try to move to same column as player, so either gravity will move you to player,
            # or jump can move you to the player
            if desiredCoordinate.column < enemy.coordinate.column:
                enemy.action = "move_left"
                self.gameEngine.move(pos.Coordinate(enemy.coordinate.row, enemy.coordinate.column - 1), enemy)
            elif desiredCoordinate.column > enemy.coordinate.column:
                enemy.action = "move_right"
                self.gameEngine.move(pos.Coordinate(enemy.coordinate.row, enemy.coordinate.column + 1), enemy)
            else:
                if desiredCoordinate.row > enemy.coordinate.row:
                    print("Fuck it, i am confused, just go right, as real patriot")
                    enemy.action = "move_right"
                    self.gameEngine.move(pos.Coordinate(enemy.coordinate.row, enemy.coordinate.column + 1), enemy)
                else:
                    enemy.action = "jump"
                    self.gameEngine.move(pos.Coordinate(enemy.coordinate.row-1 , enemy.coordinate.column), enemy)

            sleep(self.thinkTime)
    # Finding which player is closer to this enemy. Findig is done by checking diff in
    # list of available positions
    def getCloserPlayer(self, enemy):
        p1Coordinate = pos.Coordinate(self.player1.coordinate.row, self.player1.coordinate.column)
        p2Coordinate = pos.Coordinate(self.player2.coordinate.row, self.player2.coordinate.column)
        enemyCoordinate = pos.Coordinate(enemy.coordinate.row, enemy.coordinate.column)

        p1Value = 16 * p1Coordinate.row + p1Coordinate.column
        p2Value = 16 * p2Coordinate.row + p2Coordinate.column
        enemyValue = 16 * enemyCoordinate.row + enemyCoordinate.column

        p1Diff = abs(enemyValue - p1Value)
        p2Diff = abs(enemyValue - p2Value)

        chase = min(p1Diff, p2Diff)

        if chase == p1Diff:
            return 1
        else:
            return 2

    def move_player(self, player, coordinate):
        if player.canMove:
            player.canMove = False
            current_coordinate = player.coordinate
        
            if coordinate.column > current_coordinate.column:
                player.action = "move_right"
                self.gameEngine.move(coordinate, player)
            elif coordinate.column < current_coordinate.column:
                player.action = "move_left"
                self.gameEngine.move(coordinate, player)
            else:
                if coordinate.row < current_coordinate.row:
                    player.action = "jump"
                    self.gameEngine.move(coordinate, player)
            player.canMove = True

    def center_window(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)
    
    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        self.key_notifier.add_key(event.key())
    
    def closeEvent(self, evet):
        self.running = False
        self.key_notifier.die()

    def keyPressListener(self, key):
        if key == Qt.Key_A or key == Qt.Key_W or key == Qt.Key_D or key == Qt.Key_Space:

            current_row = self.player1.coordinate.row
            current_column = self.player1.coordinate.column
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
            self.player1_move_thread = Thread(None,self.move_player,args=[self.player1, desiredCoordinate], name="Player1Thread")
            self.player1_move_thread.start()

        elif key == Qt.Key_Left or Qt.Key_Right or Qt.Key_Up or Qt.Key_0:
            
            current_row = self.player2.coordinate.row
            current_column = self.player2.coordinate.column
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
            self.player2_move_thread = Thread(None,self.move_player,args=[self.player2, desiredCoordinate], name="Player2Thread")
            self.player2_move_thread.start()


    
