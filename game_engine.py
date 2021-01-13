import player
import enemy
import bullet
import pos
from time import sleep
from time import monotonic as timer
from threading import Thread

JUMP_SLEEP_DURATION = 0.0300
GRAVITY_SLEEP_DURATION = 0.0600
PLAYER_IMUNE_TIME = 4
PLAYER_RESPAWN_TIME_SEC = 2
class GameEngine():
    def __init__(self, map):
        self.map = map
        self.entity = None
        self.imuneTimerThreadP1 = None
        self.movePlayerAfterLifeLossThreadP1 = None
        self.imuneTimerThreadP2 = None
        self.movePlayerAfterLifeLossThreadP2 = None
        
    def move(self, coordinate, entity):
        if entity.action == "jump":
            checkCoordinate = pos.Coordinate(coordinate.row-2, coordinate.column)
        else:
            checkCoordinate = coordinate
        
        if self.map.isCoordinateAvailable(checkCoordinate, entity):
            if entity.action == "jump":
                self.jump(coordinate, entity)
            else:
                self.move_success(coordinate, entity)
                self.gravity(entity)
                return True
        else:
            self.move_failed(coordinate, entity)
            return False
                    
    def jump(self, coordinate, entity):
        for i in range(3):
            sleep(JUMP_SLEEP_DURATION)
            self.move_success(coordinate, entity)
            coordinate.row = coordinate.row - 1
                
        # when we finish jump we need to check for gravity
        self.gravity(entity)

    def move_success(self, coordinate, entity):
        oldCoordinate = pos.Coordinate(entity.coordinate.row, entity.coordinate.column)        
        entity.coordinate.setCoordinate(coordinate.row, coordinate.column)
        print("Entity: ", entity.name, " executed action: ", entity.action, " from: ", oldCoordinate, " to: ", coordinate)
        self.map.updateMap(oldCoordinate, coordinate, entity)

    def move_failed(self, coordinate, entity):
        onCoordinate = self.map.getEntityAtCoordinate(coordinate)
        if onCoordinate == None:
            onCoordinate = " wall"
        
        if self.map.isPlayer(entity):
            if self.map.isEnemy(onCoordinate):
                # Player have crashed with enemy
                if not entity.imune:
                    self.takeAwayLife(entity)
        elif self.map.isEnemy(entity):
            if self.map.isPlayer(onCoordinate):
                # Enemy have crashed with player
                if not onCoordinate.imune:
                    self.takeAwayLife(onCoordinate)

        print("Entity:", entity.name, " can not execute action: ", entity.action, " from: ", entity.coordinate, " to: ", coordinate
        , ", it have colided with:", onCoordinate)
    
    def takeAwayLife(self, player):
        player.lifes -= 1
        print("Player: ", player, " have lost a life. Remaining: ", player.lifes)
        
        # Check if this was last life, destroy player
        if not self.isAlive(player):
            print("ALL LIFES WASTED, KILLING PLAYER!!!")
            self.destroyEntity(player)
            return

        # Should remove player from this position
        self.destroyEntity(player)
        print("Player ", player, " removed from map")

        # Reset coordinates and set player to be imuned, so enemy is not interested in us anymore!
        player.coordinate = pos.Coordinate(-1, -1)
        player.imune = True
        # Disable pressing buttons untill player is not again spawned on map
        player.spawned = False
        
        # Create imune time thread, which will start when we return to our init pos
        # Try to move player to init pos, after life loss
        if player.id == 1:        
            self.imuneTimerThreadP1 = Thread(None,self.startImuneTimer,args=[player, PLAYER_IMUNE_TIME], name="imuneTimerThread")
            self.movePlayerAfterLifeLossThreadP1 = Thread(None,self.movePlayerAfterLifeLoss,args=[player], name="moveAfterLifeLossThread")
            self.movePlayerAfterLifeLossThreadP1.start()
        else:
            self.imuneTimerThreadP2 = Thread(None,self.startImuneTimer,args=[player, PLAYER_IMUNE_TIME], name="imuneTimerThread")
            self.movePlayerAfterLifeLossThreadP2 = Thread(None,self.movePlayerAfterLifeLoss,args=[player], name="moveAfterLifeLossThread")
            self.movePlayerAfterLifeLossThreadP2.start()
   
    # Timer which run for N[passed] seconds. After that player is not imune anymore
    def startImuneTimer(self, player, seconds):
        endtime = timer() + seconds
        while timer() < endtime:
            pass
        player.imune = False
        print("Timer have expired, player: ", player, " is becoming pussy again")

    # Try to move player to his init coordinate
    # If someone is on his init coordinate,
    # wait 2 seconds and try again.
    def movePlayerAfterLifeLoss(self, player):
        player.action = "init"
        sleep(PLAYER_RESPAWN_TIME_SEC)
        moved = self.move(player.initCoordinate, player)
        if moved:
            print("Player is moved to init position in first attempt")
            if player.id == 1:
                self.imuneTimerThreadP1.start()
            else:
                self.imuneTimerThreadP2.start()
            player.spawned = True
            return
        while (not moved):
            moved = self.move(player.initCoordinate, player)
            if not moved:
                print("Can't move player: ", player, " to init pos")
                sleep(PLAYER_RESPAWN_TIME_SEC)
            else:
                # If we can move, check if on his init coordiate is enemy
                # If it is than we don't want to move, instead we need to wait
                # Maybe move it to init position, because we will be imuned?
                e = self.map.getEntityAtCoordinate(player.initCoordinate)
                if self.map.isEnemy(e):
                    moved = False
                    sleep(PLAYER_RESPAWN_TIME_SEC)
                else:
                    print("Can't move player ", player, " to init pos, there is enemy there: ", e)

        print("Manage to put player at init position after some time")
        if player.id == 1:
            self.imuneTimerThreadP1.start()
        else:
            self.imuneTimerThreadP2.start()
        player.spawned = True

    
    
    
    
    
    
    
    
    
    # Invoked when
    # 1. Player lost life
    # 2. TODO: Enemy is killed
    # 3. TODO: Bullet disapear
    def destroyEntity(self, entity):
        print("DESTROYING ENTITY: ", entity)
        if self.map.isPlayer(entity):
            self.map.destroyEntity(entity)


    def gravity(self, entity):
        if not self.map.isGravityNeeded(entity):
            return
        coordinateBellow = pos.Coordinate(entity.coordinate.row + 1, entity.coordinate.column)        
        gravity = True
        while(gravity):
            sleep(GRAVITY_SLEEP_DURATION)
            if not self.map.isGravityNeeded(entity):
                gravity = False
            else:
                entity.action = "gravity"
                self.move_success(coordinateBellow, entity)
                coordinateBellow.row += 1

    def isAlive(self, entitity):
        return not entitity.lifes is 0
            
