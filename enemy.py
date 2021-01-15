import pos
class Enemy():
    def __init__(self, name):
        self.name = name
        self.label_right = None
        self.label_left = None
        self.label = None
        self.action = None
        self.coordinate = pos.Coordinate(-1, -1)
        self.speed = 1

    def setupEnemy(self):
        self.label_left = "characters/benzo_left.png"
        self.label_right = "characters/benzo_right.png"
        self.action = "init"

    def getCoordinate(self):
        return self.coordinate

    def destroyEnemy(self):
        pass

    def __str__(self):
        return "Enemy: [name: " + self.name + ", cor: " + str(self.coordinate) + "]"
