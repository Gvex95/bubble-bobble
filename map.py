from PyQt5.QtWidgets import (QMainWindow, QLabel, QDesktopWidget, QFrame, QPushButton)
from PyQt5.QtGui import (QPainter, QPixmap, QIcon, QMovie, QTextDocument)
from PyQt5.QtCore import Qt, QThreadPool, pyqtSlot, QCoreApplication
import pos
import player
from time import sleep

P1_LIFE1_POS = (0, 15)
P1_LIFE2_POS = (1, 15)
P1_LIFE3_POS = (2, 15)

P2_LIFE1_POS = (13, 15)
P2_LIFE2_POS = (14, 15)
P2_LIFE3_POS = (15, 15)

class Map(QFrame):
    def __init__(self):
        super().__init__()
        
        # i = vertical, kolona 
        # j = horizonal, vrsta
       
        self.block_w = 75
        self.block_h = 60

        # List of free position objects
        self.freeCoordinates = []

        # List of all position
        self.allPositions = []

        self.board = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        self.initPositions()

    def initPositions(self):
        index = 0        
        for row in range(16):
            for column in range(16):
                p = pos.Position()
                p.setPosition(pos.Coordinate(row, column), None, None, False)
                if self.board[row][column] == 1:
                    self.freeCoordinates.append(p.coordinate)
                else:
                    p.setWall(True)
                index = 16 * row + column
                self.allPositions.insert(index, p)

    def updateAllPositions(self, entity, oldCoordinate, newCoordinate):
        for p in self.allPositions:
            if p.coordinate == newCoordinate:
                if isinstance(entity, player.Player):
                    #print("Player: ", entity, " have landed on coordinate: ", newCoordinate)
                    p.player = entity
            
            if p.coordinate == oldCoordinate:
                if isinstance(entity, player.Player):
                    #print("Player: ", entity, " have been removed from coordinate: ", oldCoordinate)
                    p.player = None


    def updateFreeCoordinates(self, oldCoordinate, newCoordinate):
        # We have moved to some new position. Need to remove that coordinates from list
        if newCoordinate in self.freeCoordinates:
            #print("Removing coordinate from list of free: ", newCoordinate)
            self.freeCoordinates.remove(newCoordinate)
        
        # We have moved from some coordinate. If it is not init coordinates(-1,-1), we need to add
        # them to list of free coordinates
        if oldCoordinate == pos.Coordinate(-1,-1):
            #print("Initial moving of players...")
            return
        if oldCoordinate not in self.freeCoordinates:
            #print("Adding old coordinate: ", oldCoordinate, " to the list of free coordinates!")
            self.freeCoordinates.append(oldCoordinate)

    # This method will update list of free positions, but also will update
    # list of all positions, because we draw map based on that list
    def updateMap(self, oldCoordinate, newCoordinate, entity):
        self.updateAllPositions(entity, oldCoordinate, newCoordinate)
        self.updateFreeCoordinates(oldCoordinate, newCoordinate)
        
    def isInMap(self, coordinate):
        if coordinate.row > 0 and coordinate.row < 15 and coordinate.column > 0 and coordinate.column < 15:
            return True
        else:
            print("Coordinate not in map: ", coordinate)
            return False

    def isPlayerOn(self, coordinate):
        for p in self.allPositions:
            if p.coordinate == coordinate:
                if p.player is not None:
                    return True
                else:
                    return False
    
    def isWallOrPlayer(self, coordinate):
        for pos in self.allPositions:
            if pos.coordinate == coordinate:
                if pos.player is not None:
                    return True
                else:
                    return pos.wall
    
    
    def paintEvent(self, event):
        painter = QPainter(self)
        for p in self.allPositions:
            if isinstance(p.player,player.Player):
                if p.wall:
                    self.drawPlayer(p, painter, True)
                else:
                    self.drawPlayer(p, painter, False)
            else:
                if p.wall:
                    self.drawWall(p, painter)
                else:
                    self.drawMapBlock(p, painter)
        self.drawNames(painter)
        self.drawLifes(painter)

    def drawPlayer(self, position, painter, inWall):
        # When drawing painter first need to draw block of map
        self.drawMapBlock(position, painter)
        if inWall:
            self.drawWall(position, painter)
        if position.player.player_id == 1:
            if not position.player.switchLabelForced:
                if position.player.player_action == "move_right" or position.player.player_action == "init":
                    position.player.player_label = position.player.player_label_right
                elif position.player.player_action == "move_left":
                    position.player.player_label = position.player.player_label_left
            painter.drawPixmap(
                position.coordinate.column * self.block_w, 
                position.coordinate.row*self.block_h,
                self.block_w,
                self.block_h,
                QPixmap(position.player.player_label))
        else:
            if not position.player.switchLabelForced:
                if position.player.player_action == "move_left" or position.player.player_action == "init":
                    position.player.player_label = position.player.player_label_left
                elif position.player.player_action == "move_right":
                    position.player.player_label = position.player.player_label_right
            painter.drawPixmap(
                position.coordinate.column * self.block_w, 
                position.coordinate.row*self.block_h,
                self.block_w,
                self.block_h,
                QPixmap(position.player.player_label))
    def drawWall(self, position, painter):
        painter.drawPixmap(position.coordinate.column * self.block_w,
            position.coordinate.row*self.block_h,
            self.block_w,
            self.block_h,
            QPixmap('map/map_block.png'))    

    def drawMapBlock(self, position, painter):
        painter.fillRect(position.coordinate.column * self.block_w, 
            position.coordinate.row*self.block_h,
            self.block_w,
            self.block_h,
            Qt.black)

    def drawNames(self, painter):
        painter.drawText(P1_LIFE1_POS[0], 0*self.block_h, "Hello")

    def drawLifes(self, painter):
        painter.drawPixmap(P1_LIFE1_POS[0], P1_LIFE1_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bub_right.png'))
        painter.drawPixmap(P1_LIFE2_POS[0]*self.block_w, P1_LIFE2_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bub_right.png'))
        painter.drawPixmap(P1_LIFE3_POS[0]*self.block_w, P1_LIFE3_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bub_right.png'))

        painter.drawPixmap(P2_LIFE1_POS[0]*self.block_w, P2_LIFE1_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bob_left.png'))
        painter.drawPixmap(P2_LIFE2_POS[0]*self.block_w, P2_LIFE2_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bob_left.png'))
        painter.drawPixmap(P2_LIFE3_POS[0]*self.block_w, P2_LIFE3_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bob_left.png'))
        self.update()