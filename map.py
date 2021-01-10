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
        self.initFreeCoordinates()

    def initPositions(self):
        available = False
        player = None
        index = 0        
        for row in range(16):
            for column in range(16):
                if self.board[row][column] == 1:
                    available = True
                else:
                    available = False
                p = pos.Position()
                p.coordinate = pos.Coordinate(row,column)
                p.player = player
                p.available = available
                p.enemy = False
                
                index = 16*row + column
                #print("Inserting at pos:", index)
                self.allPositions.insert(index, p)

    def initFreeCoordinates(self):
        for position in self.allPositions:
            if position.available == True:
                self.freeCoordinates.append(position.coordinate)

    def getFreeCoordinates(self):
        return self.freeCoordinates

    def updateAllPositions(self, entity, oldCoordinate, newPosition):
        for p in self.allPositions:
            if p.coordinate == newPosition.coordinate:
                if isinstance(entity, player.Player):
                    print("Player: ", entity, " have landed on coordinate: ", newPosition.coordinate)
                    p.player = entity
                    print("MJAU: ", p.player)
                    print(p)
                    #self.test()
            
            if p.coordinate == oldCoordinate:
                if isinstance(entity, player.Player):
                    print("Player: ", entity, " have removed coordinate: ", oldCoordinate)
                    p.player = None


    def updateFreeCoordinates(self, oldCoordinate, newPosition):
        # We have moved to some new position. Need to remove that coordinates from list
        for cordinate in self.freeCoordinates:
            if cordinate == newPosition.coordinate:
                #print("Removing newPosition coordinate: ", newPosition.coordinate)
                self.freeCoordinates.remove(newPosition.coordinate)
        
        # We have moved from some coordinate. If it is not init coordinates(-1,-1), we need to add
        # them to list of free coordinates
        #print("Old coordinate is: ", oldCoordinate)
        if oldCoordinate == pos.Coordinate(-1,-1):
            #print("Initial moving of players...")
            return
        # If not initial, than add coordinate in list of free, if not already there
        for freeCoordinate in self.freeCoordinates:
            if freeCoordinate == oldCoordinate:
                    # Is this really needed?
                    #print("Old coordinate already in list of free")
                    return
        #print("Apending old coordinate: ", oldCoordinate)
        self.freeCoordinates.append(oldCoordinate)
    
    # This method will update list of free positions, but also will update
    # list of all positions, because we draw map based on that list
    def updateMap(self, oldCoordinate, newPosition, entity):
        self.updateFreeCoordinates(oldCoordinate, newPosition)
        self.updateAllPositions(entity, oldCoordinate, newPosition)
    
    def test(self):
        for p in self.allPositions:
            if p.player is not None:
                print(p.player)

    def paintEvent(self, event):
        #print("Event is: ", event)
        painter = QPainter(self)
        for p in self.allPositions:
            if p.player is not None:
                self.drawPlayer(p, painter)
            else:
                if p.available == False:
                    self.drawWall(p, painter)
                else:
                    self.drawMapBlock(p, painter)
        
        self.drawLifes(painter)

    def drawPlayer(self, position, painter):
        # When drawing painter first need to draw block of map
        print("drawPlayer called!")
        self.drawMapBlock(position, painter)
        if position.player.player_id == 1:
            dir = None
            if position.player.player_direction == "right":
                dir = position.player.player_label_right
            else:
                dir = position.player.player_label_left
            print(dir)
            painter.drawPixmap(
                position.coordinate.column * self.block_w, 
                position.coordinate.row*self.block_h,
                self.block_w,
                self.block_h,
                QPixmap(dir))
        else:
            painter.drawPixmap(
                position.coordinate.column * self.block_w, 
                position.coordinate.row*self.block_h,
                self.block_w,
                self.block_h,
                QPixmap(position.player.player_label_left))


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

    def drawLifes(self, painter):
        painter.drawPixmap(P1_LIFE1_POS[0], P1_LIFE1_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bub_right.png'))
        painter.drawPixmap(P1_LIFE2_POS[0]*self.block_w, P1_LIFE2_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bub_right.png'))
        painter.drawPixmap(P1_LIFE3_POS[0]*self.block_w, P1_LIFE3_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bub_right.png'))

        painter.drawPixmap(P2_LIFE1_POS[0]*self.block_w, P2_LIFE1_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bob_left.png'))
        painter.drawPixmap(P2_LIFE2_POS[0]*self.block_w, P2_LIFE2_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bob_left.png'))
        painter.drawPixmap(P2_LIFE3_POS[0]*self.block_w, P2_LIFE3_POS[1]*self.block_h, self.block_w, self.block_h, QPixmap('characters/bob_left.png'))
        #sleep(1)
        self.update()