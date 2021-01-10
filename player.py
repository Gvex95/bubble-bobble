from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPixmap, QGuiApplication
import pos
import map

class Player(QLabel):
    def __init__(self, name, id):
        super().__init__()
        self.player_id = id
        self.player_name = name
        self.player_label_left = None
        self.player_label_right = None
        self.player_direction = None
        self.player_speed = 1
        self.player_coordinate = pos.Coordinate(-1, -1)
        self.map = None

    def move(self, position, action):
        if action == "jump":
            print("jump!")
        else:
            if self.isCoordinateAvailable(position.coordinate) == True:
                self.move_success(action, position)
            else:
                self.move_failed(action, position)

    def isCoordinateAvailable(self, desired):
        free_coordinates = self.map.getFreeCoordinates()
        for coordinate in free_coordinates:
            if coordinate == desired:
                return True
        return False

    def move_success(self, action, position):
        old_coordinate = self.player_coordinate
        print("old coordinates: ", old_coordinate)
        self.player_coordinate = position.coordinate
        self.map.updateMap(old_coordinate, position, self)
        print("Player: ", self.player_name, " direction: ", self.player_direction,  " executed action: ", action, " from: ", old_coordinate, " to: ", position.coordinate)
    
    def move_failed(self, action, position):
        print("Player: ", self.player_name, " can not execute action: ", action, " from: ", self.player_coordinate, " to: ", position.coordinate)
    
    
    def getCurrentCoordinate(self):        
        return self.player_coordinate
    
    def setPlayerLabelAndDirection(self):
        if self.player_id == 1:
            self.player_label_left = "characters/bub_left.png"
            self.player_label_right = "characters/bub_right.png"
            self.player_direction = "right"
        else:
            self.player_label_left = "characters/bob_left.png"
            self.player_label_right = "characters/bob_right.png"
            self.player_direction = "left"
    
    def setMap(self, map):
        self.map = map
    
    def __str__(self):
        return self.player_name