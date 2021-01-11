from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPixmap, QGuiApplication
import pos
import map
from time import sleep


JUMP_SLEEP_DURATION = 0.05
GRAVITY_SLEEP_DURATION = 0.04

class Player(QLabel):
    def __init__(self, name, id):
        super().__init__()
        self.player_id = id
        self.player_name = name
        self.player_label_left = None
        self.player_label_right = None
        self.player_label = None
        self.player_speed = 1
        self.player_action = None
        self.canMove = True
        self.switchLabelForced = False
        self.player_coordinate = pos.Coordinate(-1, -1)
        self.map = None

    def move(self, coordinate, action):
        self.player_action = action
        if action == "jump":
            if self.isCoordinateAvailable(pos.Coordinate(coordinate.row-2, coordinate.column), self.player_action):
                if self.canMove:
                    self.canMove = False
                    for i in range(3):
                        sleep(JUMP_SLEEP_DURATION)
                        self.move_success(self.player_action, coordinate)
                        coordinate.row = coordinate.row - 1
                
                    # when we finish jump we need to check for gravity
                    self.gravity()
                    self.canMove = True
        else:
            if self.isCoordinateAvailable(coordinate, self.player_action):
                if self.canMove:
                    self.canMove = False
                    self.move_success(self.player_action, coordinate)
                    self.gravity()
                    self.canMove = True

            else:
                self.move_failed(self.player_action, coordinate)


    def gravity(self):
        coordinateBellow = pos.Coordinate(self.player_coordinate.row + 1, self.player_coordinate.column)
        if self.map.isWallOrPlayer(coordinateBellow):
            return
        
        gravity = True
        while(gravity):
            sleep(GRAVITY_SLEEP_DURATION)
            if self.map.isWallOrPlayer(coordinateBellow):
                gravity = False
            else:
                self.move_success("gravity", coordinateBellow)
                coordinateBellow.row += 1
           
    def isCoordinateAvailable(self,coordinate, action):
        if action == "jump":
            if self.map.isInMap(coordinate):
                return not self.map.isPlayerOn(coordinate)
        else:
            return coordinate in self.map.freeCoordinates

    def move_success(self, action, coordinate):
        self.switchLabelForced = False
        oldCoordinate = pos.Coordinate(self.player_coordinate.row, self.player_coordinate.column)        
        self.player_coordinate.setCoordinate(coordinate.row, coordinate.column)
        self.map.updateMap(oldCoordinate, coordinate, self)
        #print("Player: ", self.player_name, " executed action: ", action, " from: ", oldCoordinate, " to: ", coordinate)
    def move_failed(self, action, coordinate):
        entity = None
        for p in self.map.allPositions:
            if p.coordinate == coordinate:
                if p.player is not None:
                    entity = p.player
                elif p.enemy is not None:
                    entity = p.enemy
                else:
                    entity = " wall"
    
        if entity == " wall":
            #print("Switching label")
            self.switch_label()
            pass
        
        print("Player:", self.player_name, " can not execute action: ", action, " from: ", self.player_coordinate, " to: ", coordinate
        , ", it have colided with:", entity)
    
    def switch_label(self):
        self.switchLabelForced = True
        if self.player_label == self.player_label_left:
            self.player_label = self.player_label_right
        else:
            self.player_label = self.player_label_left

    def setupPlayer(self, initCoordinate, map):
        self.map = map
        if self.player_id == 1:
            self.player_label_left = "characters/bub_left.png"
            self.player_label_right = "characters/bub_right.png"
            self.move(initCoordinate, "init")
        else:
            self.player_label_left = "characters/bob_left.png"
            self.player_label_right = "characters/bob_right.png"
            self.move(initCoordinate, "init")
    
    # Return a copy coordinate, so no one from outside can change it.t
    def getCurrentCoordinate(self):        
        return self.player_coordinate
    
    def testBefore(self):
        print("BEFORE RETURN CURRENT COORDINATE IS: ", self.player_coordinate)

    def testAfter(self):
        print("AFTER RETURN CURRENT COORDINATE IS: ", self.player_coordinate)
    
    def setMap(self, map):
        self.map = map
    
    def __str__(self):
        return " Player: name[" + self.player_name + "]" + ", coordinate[" + str(self.player_coordinate) + "]"