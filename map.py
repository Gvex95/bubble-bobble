from PyQt5.QtWidgets import (QMainWindow, QLabel, QDesktopWidget, QFrame, QPushButton)
from PyQt5.QtGui import (QPainter, QPixmap, QIcon, QMovie, QTextDocument)
from PyQt5.QtCore import Qt, QThreadPool, pyqtSlot, QCoreApplication
import pos
import player
import enemy
import bubble
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
    # Needs refactoring
    def isCoordinateAvailable(self, checkCoordinate, entity):
        if entity.action == "anti_gravity":
            if self.isBubble(entity):
                return self._canBubbleGoUp(bubble, checkCoordinate)
        else:
            if self.isPlayer(entity):
                return self._canPlayerMoveOrJump(entity, checkCoordinate)
            elif self.isEnemy(entity):
                return self._canEnemyMoveOrJump(entity, checkCoordinate)
            elif self.isBubble(entity):
                return self._canBubbleMove(entity, checkCoordinate)
    # Scenarios:
    # 1. Bubble - Empty bubble,  enemy inside bubble or full bubble - can move/jump, full is taking life
    # 2. Enemy - Can move/jump - if not imuned, we are loosing life
    # 3. Player - Can NOT move/jump
    # 4. Empty block - Can move/jump if it is in list of free coordinates
    def _canPlayerMoveOrJump(self, player, coordinate):
        if not self.isInMap(coordinate):
            return False
        
        atCoordinate = self.getEntityAtCoordinate(coordinate)
        if self.isBubble(atCoordinate):
            # If it is a full bubble, loose a life. We will never be able to jump or move to our own full bubble
            if atCoordinate.mode == 1:
                player.takeAwayLife()
                return True
            else:
                return True

        elif self.isEnemy(atCoordinate):
            if not player.imune:
                self.playerLostLife(player)
            return True
        
        elif self.isPlayer(atCoordinate):
            return False
        
        else:
            return coordinate in self.freeCoordinates


    # Scenarios:
    # 1. Bubble - Empty bubble,  enemy inside bubble or full bubble - can move/jump, full is taking life
    # 2. Player - Can move/jump - if not imuned, we are taking his life
    # 3. Enemy - Can NOT move/jump
    # 4. Empty block - Can move/jump if it is in list of free coordinates
    def _canEnemyMoveOrJump(self, enemy, coordinate):
        atCoordinate = self.getEntityAtCoordinate(coordinate)
        if self.isBubble(atCoordinate):
            if atCoordinate.mode == 1:
                enemy.destroyEnemy()
                return True
            else:
                return True

        elif self.isPlayer(atCoordinate):
            if not atCoordinate.imune:
                self.playerLostLife(atCoordinate)
            return True

        elif self.isEnemy(atCoordinate):
            return False

        else:
            return coordinate in self.freeCoordinates

    # Scenarios:
    # 1. Enemy - Can move, in case we are full bubble, we are killing enemy
    # 2. Player - Can move/jump - if not imuned, we are loosing life
    # 3. Bubble - Can NOT move/jump
    # 4. Empty block - Can move/jump if it is in list of free coordinates
    def _canBubbleMove(self, bubble, coordinate):
        atCoordinate = self.getEntityAtCoordinate(coordinate)
        if self.isEnemy(atCoordinate):
            if bubble.mode == 1:
                atCoordinate.destroyEnemy()
                bubble.mode = 2
            return True
        
        elif self.isPlayer(atCoordinate):
            if bubble.mode == 1:
                atCoordinate.takeAwayLife()
            return True

        elif self.isBubble(atCoordinate):
            self.destroyEntity(bubble)
            self.destroyEntity(atCoordinate)
            return False
        
        else:
            return coordinate in self.freeCoordinates
    
    # So far keep it as sideways bubble movment. Not sure if it stay the same?
    def _canBubbleGoUp(self, bubble, coordinate):
        atCoordinate = self.getEntityAtCoordinate(coordinate)
        if self.isEnemy(atCoordinate):
            if bubble.mode == 1:
                atCoordinate.destroyEnemy()
                bubble.mode = 2
            return True
        
        elif self.isPlayer(atCoordinate):
            if bubble.mode == 1:
                atCoordinate.takeAwayLife()
            return True

        elif self.isBubble(atCoordinate):
            bubble.destroyBubble()
            atCoordinate.destroyBubble()
            return True
        
        else:
            return coordinate in self.freeCoordinates


    # Method for checking if we should apply coordinate on passed entity, by checking what is
    # bellow us
    def isGravityNeeded(self, entity):
        coordinateBellow = pos.Coordinate(entity.coordinate.row + 1, entity.coordinate.column)
        atCoordinate = self.getEntityAtCoordinate(coordinateBellow)
        
        if self.isPlayer(entity):
            # Player can land on:
            # 1. Wall
            # 2. Another player
            # 3. On bubble -> TODO    
            if self._isWall(coordinateBellow) or self.isPlayer(atCoordinate):
                return False
            elif self.isBubble(atCoordinate):
                if atCoordinate.mode == 1:
                    self.playerLostLife(entity)
                    # Killed, return false, not really need to drop down
                    return False
                else:
                    # For now when we fall, and encounter bubble which is not full, call foundBubble
                    # For NOW we DON'T WANT on bubble which is going up.
                    # TODO: If it is empty bubble - land on bubble, so return false here
                    # TODO: If it is bubble which have enemy iside it - take points, destroy bubble and keep faling (return True) 
                    entity.foundBubble(atCoordinate)
                    return True
            elif self.isEnemy(atCoordinate):
                self.playerLostLife(entity)
                return False
            else:
                return True

        elif self.isEnemy(entity):
            # Enemy can land on
            # 1. On wall
            # 2. On another enemy
            if self._isWall(coordinateBellow) or self.isEnemy(atCoordinate):
                return False
            elif self.isBubble(atCoordinate):
                if atCoordinate.mode == 1:
                    # If it is full bubble, we are dead
                    self.destroyEntity(entity)
                    return False
                else:
                    return True
            elif self.isPlayer(atCoordinate):
                self.playerLostLife(atCoordinate)
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
                if self.isPlayer(entity) or self.isBubble(entity) or self.isEnemy(entity):
                    entity.coordinate = pos.Coordinate(-1,-1)
                    pos.entity = None
                        
                if pos.coordinate not in self.freeCoordinates:
                        self.freeCoordinates.append(pos.coordinate)
    
    def _isWall(self, coordinate):
        for pos in self.allPositions:
            if pos.coordinate == coordinate:
                return pos.wall

    
    def playerLostLife(self, player):
        if player.id == 1:
            self.p1_lives -= 1
        else:
            self.p2_lives -= 1
        
        player.takeAwayLife()
        # If it was last life, remove it from map
        if not player.isAlive():
            self.destroyEntity(player)
        else:
            # Remove it from coordinate
            self.destroyEntity(player)
            player.afterLifeLoss()       
    
    # Maybe move this 3 methods to some util?
    def isPlayer(self, entity):
        return isinstance(entity, player.Player)
    
    def isEnemy(self, entity):
        return isinstance(entity, enemy.Enemy)
    
    def isBubble(self, entity):
        return isinstance(entity, bubble.Bubble)
    
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
        # Draw bubble
        elif self.isBubble(position.entity):
            self._drawBubble(position, painter)

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

    def _drawBubble(self, position, painter):
        if position.entity.mode == 1:
            self._drawPixmap(painter, position.coordinate, position.entity.label_mode_1)
        elif position.entity.mode == 2:
            self._drawPixmap(painter, position.coordinate, position.entity.label_mode_2)
        else:
            self._drawPixmap(painter, position.coordinate, position.entity.label_mode_3)
    
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
            self._drawPixmap(painter, pos.Coordinate(LIVES_ROW_POS, i), 'characters/heart.png')
    
    def _drawP2Lives(self, painter, numOfLives):
        for i in range(numOfLives):
            self._drawPixmap(painter, pos.Coordinate(LIVES_ROW_POS, P2_LIFE_1_COLUMN + i), 'characters/heart.png')
        
    def _drawPixmap(self, painter, coordinate, image):
        painter.drawPixmap(coordinate.column * self.block_w, coordinate.row * self.block_h, self.block_w, self.block_h, QPixmap(image))
        self.update()