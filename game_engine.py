import player
import enemy
import bullet
import pos
from time import sleep

JUMP_SLEEP_DURATION = 0.0300
GRAVITY_SLEEP_DURATION = 0.0600

class GameEngine():
    def __init__(self, map):
        self.map = map
        self.entity = None
        
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
        else:
            self.move_failed(coordinate, entity)
                    
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
        #print("Entity: ", entity.name, " executed action: ", entity.action, " from: ", oldCoordinate, " to: ", coordinate)
        self.map.updateMap(oldCoordinate, coordinate, entity)

    def move_failed(self, coordinate, entity):
        onCoordinate = None
        for p in self.map.allPositions:
            if p.coordinate == coordinate:
                if p.player is not None:
                    onCoordinate = p.player
                elif p.enemy is not None:
                    onCoordinate = p.enemy
                else:
                    onCoordinate = " wall"
    
        if self.isPlayer(entity):
            if self.isEnemy(onCoordinate):
                # Player have crashed with enemy
                print("Player: ", entity.name, " have lost a life!")
                entity.lifes -= 1
        elif self.isEnemy(entity):
            if self.isPlayer(onCoordinate):
                print("Player: ", onCoordinate.name, " have lost a life!")
        
        print("Entity:", entity.name, " can not execute action: ", entity.action, " from: ", entity.coordinate, " to: ", coordinate
        , ", it have colided with:", onCoordinate)
    

    def gravity(self, entity):
        coordinateBellow = pos.Coordinate(entity.coordinate.row + 1, entity.coordinate.column)
        if self.map.isWallOrPlayer(coordinateBellow):
            return
        
        gravity = True
        while(gravity):
            sleep(GRAVITY_SLEEP_DURATION)
            if self.map.isWallOrPlayer(coordinateBellow):
                gravity = False
            else:
                entity.action = "gravity"
                self.move_success(coordinateBellow, entity)
                coordinateBellow.row += 1
    # Move to util
    def isPlayer(self, entity):
        return isinstance(entity, player.Player)
    # Move to util
    def isEnemy(self, entity):
        return isinstance(entity, enemy.Enemy)
    # Move to util
    def isBullet(self, entity):
        return isinstance(entity, bullet.Bullet)
