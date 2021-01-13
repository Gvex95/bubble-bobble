import pos
from time import sleep
class Player():
    def __init__(self, name, id):
        super().__init__()
        self.id = id
        self.name = name
        self.label_left = None
        self.label_left_imuned = None
        self.label_right = None
        self.label_right_imuned = None
        self.label = None
        self.action = None
        self.canMove = False
        self.coordinate = pos.Coordinate(-1, -1)
        self.initCoordinate = pos.Coordinate( -1, -1)
        self.lifes = 3
        self.imune = False
        self.spawned = False

    def switch_label(self):
        self.switchLabelForced = True
        if self.label == self.label_left:
            self.label = self.label_right
        else:
            self.label = self.label_left

    def setupPlayer(self, initCoordinate):
        self.action = "init"
        self.canMove = True
        self.spawned = True
        self.initCoordinate = pos.Coordinate(initCoordinate.row, initCoordinate.column)
        if self.id == 1:
            self.label_left = "characters/bub_left.png"
            self.label_left_imuned = "characters/bub_left_imuned.png"
            self.label_right = "characters/bub_right.png"
            self.label_right_imuned = "characters/bub_right_imuned.png"
        else:
            self.label_left = "characters/bob_left.png"
            self.label_left_imuned = "characters/bob_left_imuned.png"
            self.label_right = "characters/bob_right.png"
            self.label_right_imuned = "characters/bob_right_imuned.png"
    
    def getCurrentCoordinate(self):        
        return self.coordinate
            
    def __str__(self):
        return " Player: name[" + self.name + "]" + ", coordinate[" + str(self.coordinate) + "]" + " imuned: " + str(self.imune)
