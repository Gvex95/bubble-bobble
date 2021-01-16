import pos
from time import sleep
from time import monotonic as timer
from threading import Thread


PLAYER_IMUNE_TIME = 10
PLAYER_RESPAWN_TIME_SEC = 2

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
        self.dir = None
        self.imuneTimerThread = None
        self.movePlayerAfterLifeLossThread = None
        self.game_engine = None

    def setupPlayer(self, initCoordinate, game_engine):
        self.action = "init"
        self.canMove = True
        self.spawned = True
        self.game_engine = game_engine
        self.initCoordinate = pos.Coordinate(initCoordinate.row, initCoordinate.column)
        if self.id == 1:
            self.label_left = "characters/bub_left.png"
            self.label_left_imuned = "characters/bub_left_imuned.png"
            self.label_right = "characters/bub_right.png"
            self.label_right_imuned = "characters/bub_right_imuned.png"
            self.dir = "right"
        else:
            self.label_left = "characters/bob_left.png"
            self.label_left_imuned = "characters/bob_left_imuned.png"
            self.label_right = "characters/bob_right.png"
            self.label_right_imuned = "characters/bob_right_imuned.png"
            self.dir = "left"

    def takeAwayLife(self):
        self.lifes -= 1
        print("Player: ", self, " have lost a life. Remaining: ", self.lifes)
    
    def afterLifeLoss(self):
        
        # Reset coordinates and set player to be imuned, so enemy is not interested in us anymore!
        self.coordinate = pos.Coordinate(-1, -1)
        self.imune = True
        # Disable pressing buttons untill player is not again spawned on map
        self.spawned = False
        
        # Create imune time thread, which will start when we return to our init pos
        # Try to move player to init pos, after life loss
             
        self.imuneTimerThread = Thread(None,self.startImuneTimer, name="imuneTimerThread")
        self.movePlayerAfterLifeLossThread = Thread(None,self.movePlayerAfterLifeLoss, name="moveAfterLifeLossThread")
        self.movePlayerAfterLifeLossThread.start()
       
    # Timer which run for PLAYER_IMUNE_TIME seconds. After that player is not imune anymore
    def startImuneTimer(self):
        endtime = timer() + PLAYER_IMUNE_TIME
        while timer() < endtime:
            pass
        self.imune = False
        print("Timer have expired, player: ", self, " is becoming pussy again")

    # Try to move player to his init coordinate
    # If someone is on his init coordinate,
    # wait 2 seconds and try again.
    def movePlayerAfterLifeLoss(self):
        self.action = "init"
        sleep(PLAYER_RESPAWN_TIME_SEC)
        moved = self.game_engine.move(self.initCoordinate, self)
        if moved:
            print("Player is moved to init position in first attempt")
            self.imuneTimerThread.start()
            self.spawned = True
            return
        while (not moved):
            moved = self.game_engine.move(self.initCoordinate, self)
            if not moved:
                print("Can't move: ", self, " to init pos")
                sleep(PLAYER_RESPAWN_TIME_SEC)

        print("Manage to put player at init position after some time")
        self.imuneTimerThread.start()
        self.spawned = True

    def isAlive(self):
        return not self.lifes is 0
    
    def getCurrentCoordinate(self):        
        return self.coordinate
            
    def __str__(self):
        return "Player:[name: " + self.name + ", cor: " + str(self.coordinate) + ", imuned: " + str(self.imune) + "]"
