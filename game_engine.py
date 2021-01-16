import player
import enemy
import bubble
import pos
from time import sleep
from time import monotonic as timer
from threading import Thread

JUMP_SLEEP_DURATION = 0.0300
GRAVITY_SLEEP_DURATION = 0.0600
BUBBLE_SPEED = 0.2

BUBBLE_TOP_ROW = 1
BUBBLE_TOP_TIME = 6
BUBBLE_ANTI_GRAVITY_SLEEP = 0.5
class GameEngine():
    def __init__(self, map):
        self.map = map
        self.entity = None

        self.bubbleStayOnMapTimerThread = None
        self.bubbleAntiGravityThread = None
        
    def move(self, coordinate, entity):
        #if entity.action == "jump":
            #checkCoordinate = pos.Coordinate(coordinate.row-2, coordinate.column)
        #else:
            #checkCoordinate = coordinate
        
        if self.map.isCoordinateAvailable(coordinate, entity):
            if entity.action == "jump":
                self.jump(coordinate, entity)
            
            elif entity.action == "shoot_r" or entity.action == "shoot_l":
                self.shoot(coordinate, entity)

            else:
                self.move_success(coordinate, entity)
                self.gravity(entity)
                return True
        else:
            self.move_failed(coordinate, entity)
            return False
                    

    def shoot(self, coordinate, bubble):
        print("Bubble shoot called for bubble: ", bubble, " with coordinate: ", coordinate)
        cor = pos.Coordinate(coordinate.row, coordinate.column)
        for i in range(3):
            sleep(BUBBLE_SPEED)
            if self.map.isCoordinateAvailable(cor, bubble) and bubble.isAlive():
                self.move_success(cor, bubble)
                if bubble.action == "shoot_r":
                    cor.column += 1
                elif bubble.action == "shoot_l":
                    cor.column -= 1
            else:
                break
        
        print("Bubble shoot ended for bubble: ", bubble, " now coordinate is: ", bubble.coordinate)
        # After shoot is done, we need to start moving bubble on top
        cor = pos.Coordinate(bubble.coordinate.row - 1, bubble.coordinate.column)
        self.bubbleAntiGravityThread = Thread(None, self.bubbleAntiGravity, args=[bubble, cor], name="BubbleAGThread")
        self.bubbleAntiGravityThread.start()


    def jump(self, coordinate, entity):
        cor = pos.Coordinate(coordinate.row, coordinate.column)
        for i in range(3):
            sleep(JUMP_SLEEP_DURATION)
            if self.map.isCoordinateAvailable(cor, entity):
                self.move_success(cor, entity)
                cor.row = cor.row - 1
            else:
                break
                
        # when we finish jump we need to check for gravity
        self.gravity(entity)

    def move_success(self, coordinate, entity):
        oldCoordinate = pos.Coordinate(entity.coordinate.row, entity.coordinate.column)        
        entity.coordinate.setCoordinate(coordinate.row, coordinate.column)
        #print("Entity: ", entity, " executed action: ", entity.action, " from: ", oldCoordinate, " to: ", coordinate)
        self.map.updateMap(oldCoordinate, coordinate, entity)

    def move_failed(self, coordinate, entity):
        onCoordinate = self.map.getEntityAtCoordinate(coordinate)
        if onCoordinate == None:
            onCoordinate = " wall"
    
        #print("Entity:", entity, " can not execute action: ", entity.action, " from: ", entity.coordinate, " to: ", coordinate
        #, ", it have colided with:", onCoordinate)
    
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

    def bubbleAntiGravity(self, bubble, coordinate):
        bubble.action = "anti_gravity"
        bubble.mode = 2
        while(coordinate.row is not BUBBLE_TOP_ROW):
            sleep(BUBBLE_ANTI_GRAVITY_SLEEP)
            # At this point, we don't want to check entities above us as we go up
            # TODO: Implement this
            self.move_success(coordinate, bubble)
            coordinate.row -= 1
            
                        
        # After it have been moved to row = 2, start timer which will destroy it after n seconds
        self.bubbleStayOnMapTimerThread = Thread(None,self.startBubbleTimer,args=[bubble, BUBBLE_TOP_TIME], name="bubbleAliveTimerThread")
        self.bubbleStayOnMapTimerThread.start()

    def startBubbleTimer(self, bubble, seconds):
        endtime = timer() + seconds
        while timer() < endtime:
            pass
        self.map.destroyEntity(bubble)
            
