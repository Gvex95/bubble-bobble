
class Position():
    def __init__(self):
        self.coordinate = Coordinate(-1, -1)
        self.entity = None
        self.wall = False

    def setPosition(self, coordinate, entity, wall):
        self.coordinate = coordinate
        self.entity = entity
        self.wall = wall

    def setCoordinate(self, coordinate):
        self.coordinate = coordinate

    def setWall(self, isWall):
        self.wall = isWall

    def print(self):
        print(self.coordinate, self.entity)

    def __str__(self):
        s = "Entity: " + str(self.entity) + " at coordinate" + str(self.coordinate)
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