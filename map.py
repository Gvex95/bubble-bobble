from PyQt5.QtWidgets import (QMainWindow, QLabel, QDesktopWidget, QFrame, QPushButton)
from PyQt5.QtGui import (QPainter, QPixmap, QIcon, QMovie, QTextDocument)
from PyQt5.QtCore import Qt, QThreadPool, pyqtSlot, QCoreApplication
import pos
import player
import enemy
from time import sleep

P1_LIFE1 = pos.Coordinate(15, 0)
P1_LIFE2 = pos.Coordinate(15, 1)
P1_LIFE3 = pos.Coordinate(15, 2)

P2_LIFE1 = pos.Coordinate(15, 13)
P2_LIFE2 = pos.Coordinate(15, 14)
P2_LIFE3 = pos.Coordinate(15, 15)

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
        #print("map init done")

    def updateAllPositions(self, entity, oldCoordinate, newCoordinate):
        for p in self.allPositions:
            if p.coordinate == newCoordinate:
                #print("Entity: ", entity, " have landed on coordinate: ", newCoordinate)
                if isinstance(entity, player.Player):
                    p.player = entity
                elif isinstance(entity, enemy.Enemy):
                    p.enemy = entity
            
            if p.coordinate == oldCoordinate:
                #print("Entity: ", entity, " have been removed from coordinate: ", oldCoordinate)
                if isinstance(entity, player.Player):
                    p.player = None
                elif isinstance(entity, enemy.Enemy):
                    p.enemy = None


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

    # Refactor!!!
    def isCoordinateAvailable(self, checkCoordinate, entity):
        if entity.action == "jump":
            if self.isInMap(checkCoordinate):
                if isinstance (entity, player.Player):
                    return not self.isPlayerOn(checkCoordinate)
                elif isinstance (entity, enemy.Enemy):
                    return not self.isEnemyOn(checkCoordinate)
        else:
            return checkCoordinate in self.freeCoordinates
    
    # Refactor, move to utils
    def isEnemyOn(self, coordinate):
        for p in self.allPositions:
            if p.coordinate == coordinate:
                if p.enemy is not None:
                    return True
                else:
                    return False
    
    # Refactor, move to utils
    def isPlayerOn(self, coordinate):
        for p in self.allPositions:
            if p.coordinate == coordinate:
                if p.player is not None:
                    return True
                else:
                    return False
    
    # Refactor, move to utils
    def isWallOrPlayer(self, coordinate):
        for pos in self.allPositions:
            if pos.coordinate == coordinate:
                if pos.player is not None:
                    return True
                else:
                    return pos.wall
    
    
    def paintEvent(self, event):
        #print("painting event called!")
        painter = QPainter(self)
        for p in self.allPositions:
            if isinstance(p.player,player.Player):
                if p.wall:
                    self.drawPlayer(p, painter, True)
                else:
                    #print("Drawing player")
                    self.drawPlayer(p, painter, False)
            
            elif isinstance(p.enemy,enemy.Enemy):
                if p.wall:
                    #print("drawing enemy 1")
                    self.drawEnemy(p, painter, True)
                else:
                    #print("drawing enemy 2")
                    self.drawEnemy(p, painter, False)
            else:
                if p.wall:
                    self.drawWall(p, painter)
                else:
                    self.drawMapBlock(p, painter)
        #self.drawNames(painter)
        self.drawLifes(painter)

    
    def drawEnemy(self, position, painter, inWall):
        self.drawMapBlock(position, painter)
        if inWall:
            self.drawWall(position, painter)
        if position.enemy.action == "move_left" or position.enemy.action == "init" or position.enemy.action == "gravity":
            position.enemy.label = position.enemy.label_left
        elif position.enemy.action == "move_right":
            position.enemy.label = position.enemy.label_right
        #print("drawing enemy: ", position.enemy, " at coordinate: ", position.coordinate, " with label: ", position.enemy.label)
        self.drawPixmap(painter, position.coordinate, position.enemy.label)
    
    def drawPlayer(self, position, painter, inWall):
        # When drawing painter first need to draw block of map
        self.drawMapBlock(position, painter)
        if inWall:
            self.drawWall(position, painter)
        if position.player.id == 1:
            if position.player.action == "move_right" or position.player.action == "init":
                position.player.label = position.player.label_right
            elif position.player.action == "move_left":
                position.player.label = position.player.label_left            
            self.drawPixmap(painter, position.coordinate, position.player.label)
        else:
            if not position.player.switchLabelForced:
                if position.player.action == "move_left" or position.player.action == "init":
                    position.player.label = position.player.label_left
                elif position.player.action == "move_right":
                    position.player.label = position.player.label_right
            self.drawPixmap(painter, position.coordinate, position.player.label)
        
    def drawWall(self, position, painter):
        self.drawPixmap(painter, position.coordinate, 'map/map_block.png')
        
    def drawMapBlock(self, position, painter):
        painter.fillRect(position.coordinate.column * self.block_w, 
            position.coordinate.row*self.block_h,
            self.block_w,
            self.block_h,
            Qt.black)

    def drawNames(self, painter):
        pass
        #painter.drawText(P1_LIFE1_POS[0], 0*self.block_h, "Hello")

    def drawLifes(self, painter):
        self.drawPixmap(painter, P1_LIFE1, 'characters/bub_right.png')
        self.drawPixmap(painter, P1_LIFE2, 'characters/bub_right.png')
        self.drawPixmap(painter, P1_LIFE3, 'characters/bub_right.png')
        
        self.drawPixmap(painter, P2_LIFE1, 'characters/bob_left.png')
        self.drawPixmap(painter, P2_LIFE2, 'characters/bob_left.png')
        self.drawPixmap(painter, P2_LIFE3, 'characters/bob_left.png')

    def drawPixmap(self, painter, coordinate, image):
        painter.drawPixmap(coordinate.column * self.block_w, coordinate.row * self.block_h, self.block_w, self.block_h, QPixmap(image))
        self.update()