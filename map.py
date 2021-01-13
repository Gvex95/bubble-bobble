from PyQt5.QtWidgets import (QMainWindow, QLabel, QDesktopWidget, QFrame, QPushButton)
from PyQt5.QtGui import (QPainter, QPixmap, QIcon, QMovie, QTextDocument)
from PyQt5.QtCore import Qt, QThreadPool, pyqtSlot, QCoreApplication
import pos
import player
import enemy
import bullet
from time import sleep

LIVES_ROW_POS = 15
P2_LIFE_1_COLUMN = 13

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

        # Number of lives for players. For drawing lives on map
        self.p1_lives = 3
        self.p2_lives = 3

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

        self._initPositions()

    def _initPositions(self):
        index = 0        
        for row in range(16):
            for column in range(16):
                p = pos.Position()
                p.setPosition(pos.Coordinate(row, column), None, False)
                if self.board[row][column] == 1:
                    self.freeCoordinates.append(p.coordinate)
                else:
                    p.setWall(True)
                index = 16 * row + column
                self.allPositions.insert(index, p)

    def _updateAllPositions(self, entity, oldCoordinate, newCoordinate):
        for p in self.allPositions:
            if p.coordinate == newCoordinate:
                #print("Entity: ", entity, " have landed on coordinate: ", newCoordinate)
                p.entity = entity
            
            if p.coordinate == oldCoordinate:
                #print("Entity: ", entity, " have been removed from coordinate: ", oldCoordinate)
                p.entity = None


    def _updateFreeCoordinates(self, oldCoordinate, newCoordinate):
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
        self._updateAllPositions(entity, oldCoordinate, newCoordinate)
        self._updateFreeCoordinates(oldCoordinate, newCoordinate)
        
    def isInMap(self, coordinate):
        if coordinate.row > 0 and coordinate.row < 15 and coordinate.column > 0 and coordinate.column < 15:
            return True
        else:
            print("Coordinate not in map: ", coordinate)
            return False

    # Method for checking if cordinate is available when jump or move is performed
    def isCoordinateAvailable(self, checkCoordinate, entity):
        if entity.action == "jump":
            if self.isInMap(checkCoordinate):
                entityAt = self.getEntityAtCoordinate(checkCoordinate)
                if self.isPlayer(entity):
                    # If we are player, and we are imune, we can go through enemy and through player
                    if entity.imune:
                        return True
                    else:
                        return not self.isPlayer(entityAt)
                elif self.isEnemy(entity):
                    # TODO: Check if enemy can get through player if player is imuned??
                    return not self.isEnemy(entityAt)
        else:
            # If player is imuned, it can go through enemy, fuck yeaaah
            if self.isPlayer(entity):
                if not entity.imune:
                    return checkCoordinate in self.freeCoordinates
                else:
                    atCoordinate = self.getEntityAtCoordinate(checkCoordinate)
                    if self.isEnemy(atCoordinate):
                        return True
                    else:
                        return checkCoordinate in self.freeCoordinates
            else:
                return checkCoordinate in self.freeCoordinates
    
    # Method for checking if we should apply coordinate on passed entity, by checking what is
    # bellow us
    def isGravityNeeded(self, entity):
        coordinateBellow = pos.Coordinate(entity.coordinate.row + 1, entity.coordinate.column)
        entityAtCoordinate = self.getEntityAtCoordinate(coordinateBellow)
        
        if self.isPlayer(entity):
            # Player can land on:
            # 1. Wall
            # 2. Another player
            # 3. On bubble -> TODO    
            if self._isWall(coordinateBellow) or self.isPlayer(entityAtCoordinate):
                return False
            else:
                return True

        elif self.isEnemy(entity):
            # Enemy can land on
            # 1. On wall
            # 2. On another enemy
            if self._isWall(coordinateBellow) or self.isEnemy(entityAtCoordinate):
                return False
            else:
                return True

    def getEntityAtCoordinate(self, coordinate):
        for p in self.allPositions:
            if p.coordinate == coordinate:
                return p.entity
                
    # Destroy entitity from coordinates he was on
    # Add that coordinates to list of free coordinates
    def destroyEntity(self, entity):
        for pos in self.allPositions:
            if pos.coordinate == entity.coordinate:
                if self.isPlayer(entity):
                    if entity.id == 1:
                        if self.p1_lives is not 0:
                            self.p1_lives -= 1
                    else:
                        if self.p2_lives is not 0:
                            self.p2_lives -= 1
                    pos.entity = None
                    if pos.coordinate not in self.freeCoordinates:
                        self.freeCoordinates.append(pos.coordinate)
    
    def _isWall(self, coordinate):
        for pos in self.allPositions:
            if pos.coordinate == coordinate:
                return pos.wall

    # Maybe move this 3 methods to some util?
    def isPlayer(self, entity):
        return isinstance(entity, player.Player)
    
    def isEnemy(self, entity):
        return isinstance(entity, enemy.Enemy)
    
    def isBullet(self, entity):
        return isinstance(entity, bullet.Bullet)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        for p in self.allPositions:
            if p.entity is not None:
                self._drawEntity(p, painter)
            else:
                if p.wall:
                    self._drawWall(p, painter)
                else:
                    self._drawMapBlock(p, painter)
        self._drawP1Lives(painter, self.p1_lives)
        self._drawP2Lives(painter, self.p2_lives)

    def _drawEntity(self, position, painter):
        self._drawMapBlock(position, painter)
        if position.wall:
            self._drawWall(position, painter)

        # Draw player
        if self.isPlayer(position.entity):
            if position.entity.id == 1:
                self._drawPlayer1(position, painter)
            else:
                self._drawPlayer2(position, painter)
        # Draw enemy
        elif self.isEnemy(position.entity):
            self._drawEnemy(position, painter)

    def _drawPlayer1(self, position, painter):
        if position.entity.action == "move_right" or position.entity.action == "init":
            if position.entity.imune:
                position.entity.label = position.entity.label_right_imuned
            else:
                position.entity.label = position.entity.label_right
        elif position.entity.action == "move_left":
            if position.entity.imune:
                position.entity.label = position.entity.label_left_imuned
            else:
                position.entity.label = position.entity.label_left            

        self._drawPixmap(painter, position.coordinate, position.entity.label)

    def _drawPlayer2(self, position, painter):
        if position.entity.action == "move_left" or position.entity.action == "init":
            if position.entity.imune:
                position.entity.label = position.entity.label_left_imuned
            else:
                position.entity.label = position.entity.label_left
        elif position.entity.action == "move_right":
            if position.entity.imune:
                position.entity.label = position.entity.label_right_imuned
            else:
                position.entity.label = position.entity.label_right
        
        self._drawPixmap(painter, position.coordinate, position.entity.label)


    def _drawEnemy(self, position, painter):
        if position.entity.action == "move_left" or position.entity.action == "init" or position.entity.action == "gravity":
            position.entity.label = position.entity.label_left
        elif position.entity.action == "move_right":
            position.entity.label = position.entity.label_right
        
        self._drawPixmap(painter, position.coordinate, position.entity.label)

    
    def _drawWall(self, position, painter):
        self._drawPixmap(painter, position.coordinate, 'map/map_block.png')
        
    def _drawMapBlock(self, position, painter):
        painter.fillRect(position.coordinate.column * self.block_w, 
            position.coordinate.row*self.block_h,
            self.block_w,
            self.block_h,
            Qt.black)

    def _drawP1Lives(self, painter, numOfLives):
        for i in range(numOfLives):
            self._drawPixmap(painter, pos.Coordinate(LIVES_ROW_POS, i), 'characters/bub_right.png')
    
    def _drawP2Lives(self, painter, numOfLives):
        for i in range(numOfLives):
            self._drawPixmap(painter, pos.Coordinate(LIVES_ROW_POS, P2_LIFE_1_COLUMN + i), 'characters/bob_left.png')
        
    def _drawPixmap(self, painter, coordinate, image):
        painter.drawPixmap(coordinate.column * self.block_w, coordinate.row * self.block_h, self.block_w, self.block_h, QPixmap(image))
        self.update()