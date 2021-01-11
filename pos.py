
class Position():
    def __init__(self):
        self.coordinate = Coordinate(-1, -1)
        self.available = False
        self.player = None
        self.enemy = None
        self.wall = False

    def setPosition(self, coordinate, player, enemy, wall):
        self.coordinate = coordinate
        self.player = player
        self.enemy = enemy
        self.wall = wall

    def setCoordinate(self, coordinate):
        self.coordinate = coordinate

    def setWall(self, isWall):
        self.wall = isWall

    def print(self):
        print(self.coordinate, self.player, self.enemy)

    def __str__(self):
        s = " Cor: " + str(self.coordinate) + " player: " + str(self.player)
        return s 


class Coordinate():
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def setCoordinate(self, row, column):
        self.row = row
        self.column = column

    def isInit(self):
        if self.row == -1:
            return True
        else:
            return False

    def __str__(self):
        t = (self.row, self.column)
        return str(t)
    
    def __eq__(self, c1):
        if self.row == c1.row and self.column == c1.column:
            return True
        else:
            return False