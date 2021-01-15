import pos
class Bubble():
    def __init__(self, id):
        self.coordinate = pos.Coordinate(-1, -1)
        self.id = id
        self.action = None
        self.label_mode_1 = None
        self.label_mode_2 = None
        self.label_mode_3 = None
        self.mode = -1

    def __str__(self):
        return "Bubble[id: " + str(self.id) + ", cor: " + str(self.coordinate) + "]"

    def setupBubble(self):
        self.mode = 1
        if self.id == 1:
            self.label_mode_1 = "characters/green_bubble_1.png"
            self.label_mode_2 = "characters/green_bubble_2.png"
        else:
            self.label_mode_1 = "characters/blue_bubble_1.png"
            self.label_mode_2 = "characters/blue_bubble_2.png"
