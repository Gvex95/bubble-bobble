import pos
from time import sleep
class Player():
    def __init__(self, name, id):
        super().__init__()
        self.id = id
        self.name = name
        self.label_left = None
        self.label_right = None
        self.label = None
        self.speed = 1
        self.action = None
        self.switchLabelForced = False
        self.canMove = False
        self.coordinate = pos.Coordinate(-1, -1)
        self.lifes = 3

    def switch_label(self):
        self.switchLabelForced = True
        if self.label == self.label_left:
            self.label = self.label_right
        else:
            self.label = self.label_left

    def setupPlayer(self):
        if self.id == 1:
            self.label_left = "characters/bub_left.png"
            self.label_right = "characters/bub_right.png"
            self.action = "init"
            self.canMove = True
        else:
            self.label_left = "characters/bob_left.png"
            self.label_right = "characters/bob_right.png"
            self.action = "init"
            self.canMove = True
    
    def getCurrentCoordinate(self):        
        return self.coordinate
            
    def __str__(self):
        return " Player: name[" + self.name + "]" + ", coordinate[" + str(self.coordinate) + "]"
