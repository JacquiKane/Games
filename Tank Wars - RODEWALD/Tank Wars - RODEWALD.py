
""" Tank Wars - RODEWALD.py

    N451 - Web Game Development
    Final Project
    Keith Rodewald
    05/02/2010

    Directions:
    Use the left and right arrow keys to move the white tank left or right.
    Use the up and down arrow keys to rotate the turret.
    Hold down the space bar to increase the shot power, release the space bar to fire
    Hit the black tank to increase the score (number of hits).

    Tank engine sound was public domain sound clip downloaded from
    http://www.pdsounds.org/sounds/compressor_motor
    
"""

import pygame, math, random
pygame.init()
pygame.mixer.init()

#global variable
GOOD_TANK_HIT_HILL = False
ENEMY_TANK_HIT_HILL = False
screen = pygame.display.set_mode((640,480))


#######################  Label Class Below  #######################

class Label(pygame.sprite.Sprite):
    """ Label Class for displaying tank and turret information """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("None", 22)
        self.text = ""
        self.center = (320, 240)

    def update(self):
        self.image = self.font.render(self.text, 1, (0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        

#######################  Sound Class Below  #######################

class Sound(pygame.sprite.Sprite):
    """ Class for game sounds """
    def __init__(self):
        if not pygame.mixer:
            print ("problem with sound")
        else:
            pygame.mixer.init()
            self.sndEngine = pygame.mixer.Sound("engine.ogg")
            self.sndEngine.play(-1) # -1 means sound repeats continuously
            self.sndEngine.set_volume(.75) # sets the sound volume (0-off, .5-half, 1-full)
            self.sndHit = pygame.mixer.Sound("hit.ogg")
            self.sndHit.set_volume(.5) # sets the sound volume (0-off, .5-half, 1-full)
            self.sndExplode = pygame.mixer.Sound("explode.ogg")
            

#######################  Good Tank Code Below  #######################
       
class GoodTank(pygame.sprite.Sprite):
    """ Good Tank Class.  Handles tank movement controlled by left / right
        arrow keys. Also handles tank wheel rotation"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("tank000.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (120,291)
        self.dx = 3 
        self.delay = 4 #delay the tank wheel rotation animation
        self.pause = 0 #pause the game frame animation
        screenEdge = False
        self.Dead = False
                
       #images used for wheel rotation
        self.wheelMoveList = ["tank000.gif", "tank001.gif", "tank002.gif"]
        self.frame = len(self.wheelMoveList)-1
        
    def update(self):
        if not self.Dead:
            self.moveTank()
            self.pause += 3
            
    # check keys for tank forward/reverse movement
    def moveTank(self):
        
        #checks collision with screen
        if self.rect.left <= 0:
            screenEdge = True
        else:
            screenEdge = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and screenEdge:
            self.dx = 0
        elif keys[pygame.K_LEFT]:
            self.dx = 4
            self.rect.centerx = self.rect.centerx - self.dx
            self.moveWheels("counterclockwise")
            
        # checks collision with hill
        if keys[pygame.K_RIGHT] and GOOD_TANK_HIT_HILL:
            self.dx = 0
        elif keys[pygame.K_RIGHT]:
            #self.frame = 0
            self.dx = 4
            self.rect.centerx = self.rect.centerx + self.dx
            self.moveWheels("clockwise")

    # frame animation for wheel rotation
    def moveWheels(self, rotation):
        if rotation == "counterclockwise":
            if self.pause >= self.delay:
                self.pause = 0
                self.frame -= 1
            if self.frame <= 0:
                self.frame = len(self.wheelMoveList)-1
            self.image = pygame.image.load(self.wheelMoveList[self.frame])
        if rotation == "clockwise":
            if self.pause >= self.delay:
                self.pause = 0
                self.frame += 1
            if self.frame >= len(self.wheelMoveList):
                self.frame = 0
            self.image = pygame.image.load(self.wheelMoveList[self.frame])


class Turret(pygame.sprite.Sprite):
    """ Turret for good tank.  Turret rotation controlled by up/down arrow keys"""
    def __init__(self, goodShell, goodTank):
        self.shell = goodShell
        self.goodTank = goodTank
        pygame.sprite.Sprite.__init__(self)
        self.imageMaster = pygame.image.load("turret.gif")
        self.rect = self.imageMaster.get_rect()
        self.imagemaster = self.imageMaster.convert()
        #tranColor = self.imageMaster.get_at((1, 1))
        #self.imageMaster.set_colorkey(tranColor)
        self.rect.center = (goodTank.rect.centerx, goodTank.rect.centery-17)
        self.shotCount = 0         # counts number of shots fired
        self.incrShotCount = False # used to specify when to increment shot count
        self.turnRate = 10         # rate of turret rotation
        self.dir = 0               # direction
        self.charge = 0            # shot power value
        self.saveCharge = 0        # saves the shot power value from the previous shot

    def update(self):
        if not self.goodTank.Dead:
            self.checkKeys()
            self.rotate()
            self.rect.center = (self.goodTank.rect.centerx, self.goodTank.rect.centery-17)
        else:
            self.rect.center = (-100,-100)
            
    # check keys for turret rotation
    def checkKeys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.dir += self.turnRate
            if self.dir > 360:
                self.dir = self.turnRate
        if keys[pygame.K_DOWN]:
            self.dir -= self.turnRate
            if self.dir < 0:
                self.dir = 360 - self.turnRate
        if keys[pygame.K_SPACE]:
            self.charge += 1
            self.shell.x = self.rect.centerx
            self.shell.y = self.rect.centery
            self.shell.speed = self.charge
            self.shell.dir = self.dir
            self.shell.calcVector()
            self.saveCharge = self.charge
            if not self.incrShotCount:
                self.shotCount += 1
                self.incrShotCount = True
        else:
            self.charge = 0
            self.incrShotCount = False


    def rotate(self):
        oldCenter = self.rect.center
        self.image = pygame.transform.rotate(self.imageMaster, self.dir)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter

        
#######################  Enemy Tank Code Below  #######################

class EnemyTank(pygame.sprite.Sprite):
    """ Enemy Tank Class.  Tank programmed to move randomly.
    Class also handles tank wheel rotation"""
    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.image = pygame.image.load("enemyTank000.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (550,288)
        self.dx = 3
        self.old_dx = 0
        self.frameCounter = 0
        self.wheelRotation = ""
        self.randomDirection()
        self.delay = 4 #delay the tank wheel rotation animation
        self.pause = 0 #pause the game frame animation
        self.Dead = False

        #images used for wheel rotation
        self.wheelMoveList = ["enemyTank000.gif", "enemyTank001.gif", "enemyTank002.gif"]
        self.frame = len(self.wheelMoveList)-1

    def update(self):
        if not self.Dead: 
            self.moveTank()
            self.pause += 3

    def moveTank(self):
        """ move tank laterally"""
        self.frameCounter += 1
        self.rect.centerx = self.rect.centerx + (self.dx * self.tankDirection)
        if self.frameCounter > 40:  #randomly changes direction at 40 frames
            self.randomDirection()
            self.frameCounter = 0

        #checks tank boundary collision
        if self.rect.right >= self.screen.get_width():
            #screenEdge = True
            self.tankDirection = -1
            self.moveTank()

        # checks collision with hill
        if ENEMY_TANK_HIT_HILL:
            self.tankDirection = 1

        #determines direction of wheel rotation
        if self.tankDirection == -1:
            self.moveWheels("counterclockwise")
        if self.tankDirection == 1:
            self.moveWheels("clockwise")
 
    def randomDirection(self):
        """ramdomly selects tank to go forward or reverse"""
        self.directionList = [1,-1,0,0,0] # multiple zeros increase the odds of a stationary tank
        self.number = random.randrange(0, int(len(self.directionList)))
        self.tankDirection = self.directionList[self.number]

    # frame animation for wheel rotation
    def moveWheels(self, rotation):
        if rotation == "counterclockwise":
            self.frame -= 1
            if self.frame <= 0:
                self.frame = len(self.wheelMoveList)-1
            self.image = pygame.image.load(self.wheelMoveList[self.frame])
        if rotation == "clockwise":
            self.frame += 1
            if self.frame >= len(self.wheelMoveList):
                self.frame = 0
            self.image = pygame.image.load(self.wheelMoveList[self.frame])


class EnemyTurret(pygame.sprite.Sprite):
    """ Turret for enemy tank.  Turret rotation programmed for random rotation and shot power"""
    def __init__(self, enemyShell, enemyTank):
        self.shell = enemyShell
        self.enemyTank = enemyTank
        pygame.sprite.Sprite.__init__(self)
        self.imageMaster = pygame.image.load("enemyTurret.gif")
        self.rect = self.imageMaster.get_rect()
        self.imagemaster = self.imageMaster.convert()
        self.rect.center = (self.enemyTank.rect.centerx, self.enemyTank.rect.centery-17)
        self.turnRate = 10
        self.dir = 180
        self.charge = 0
        self.frameCounter = 0
        self.getDelay() #initialze delay for turret movement
        #self.getDirection() #initialize direction for turret movement"""
        self.getLimit() #initialize limit for turret movement

    def update(self):
        if not self.enemyTank.Dead:
            self.rotate()
            self.rect.center = (self.enemyTank.rect.centerx, self.enemyTank.rect.centery-17)
            self.frameCounter += 1
        else:
            self.rect.center = (-100,-100)

    def rotate(self):
        oldCenter = self.rect.center
        self.image = pygame.transform.rotate(self.imageMaster, self.dir)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter

        if self.frameCounter > self.randomDelay:
            if self.dir >= self.randomTurretLimit:
                self.rotateClockwise()
                if self.dir <= self.randomTurretLimit:
                    self.initShell() #initializes the shell
                    self.getLimit() #gets new turret rotate limit
                    self.getDelay() #gets new turret delay value
                    self.frameCounter = 0
            if self.dir <= self.randomTurretLimit:
                self.rotateCounterclockwise()
                if self.dir >= self.randomTurretLimit:
                    self.initShell() #initializes the shell
                    self.getLimit()  #gets new turret rotate limit
                    self.getDelay()  #gets new turret delay value
                    self.frameCounter = 0


    def getDelay(self): #random turrent time delay between movements
            self.randomDelay = random.randrange(50,150) 

    def getLimit(self): #random limit for turret movement
            self.randomTurretLimit = random.randrange(120,150)

    def rotateClockwise(self):
            self.dir -= self.turnRate

    def rotateCounterclockwise(self):
            self.dir += self.turnRate

    def initShell(self): #initializes the shell and charge
            self.randomCharge = random.randrange(13,18)
            self.shell.x = self.rect.centerx
            self.shell.y = self.rect.centery
            self.shell.speed = self.randomCharge
            self.shell.dir = self.dir
            self.shell.calcVector()

#######################  SHELL CLASS BELOW  #######################

class Shell(pygame.sprite.Sprite):
    def __init__(self, screen, background, enemyTank, goodTank, lifeMeterGood, lifeMeterEnemy):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.background = background
        self.enemyTank = enemyTank
        self.lifeMeterGood = lifeMeterGood
        self.lifeMeterEnemy = lifeMeterEnemy
        self.image = pygame.Surface((10,10))
        self.image.fill((0xff, 0xff, 0xff))
        self.image.set_colorkey((0xff, 0xff, 0xff))
        pygame.draw.circle(self.image, (0,0,0), (5,5), 5)
        self.image = pygame.transform.scale(self.image, (5, 5))

        #initialize shell off the stage
        self.rect = self.image.get_rect()
        self.rect.center = (-100, -100)

        self.x = -100       # initial x position
        self.y = -100       # initial y position
        self.dx = 0         # initial x velocity
        self.dy = 0         # initial y velocity
        self.speed = 0      # initial speed
        self.dir = 0        # initial direction 
        self.gravity = .5   # gravity strength

    def update(self):
        self.calcPos()
        self.checkBounds()
        self.rect.center = (self.x, self.y)

    def calcVector(self):
        radians = self.dir * math.pi / 180
        self.dx = self.speed * math.cos(radians)
        self.dy = self.speed * math.sin(radians)
        self.dy *= -1

    def calcPos(self):
        self.dy += self.gravity      
        self.x += self.dx
        self.y += self.dy

    def checkBounds(self):
        screen = self.screen
        if self.x > screen.get_width():
            self.reset()
        if self.x < 0:
            self.reset()
        if self.y > screen.get_height():
            self.reset()
        if self.y < 0:
            self.reset()

    def reset(self):
        """move off stage and stop"""
        self.x = -100
        self.y = -100
        self.speed = 0
        
        self.image = pygame.Surface((10,10))
        self.image.fill((0xff, 0xff, 0xff))
        self.image.set_colorkey((0xff, 0xff, 0xff))
        pygame.draw.circle(self.image, (0,0,0), (5,5), 5)
        self.image = pygame.transform.scale(self.image, (5, 5))


###########  Code to handle Ground (Flat1, Flat2, Hill) below
###########  Hill Collider is transparent Gif used to control
###########  boundaries for shell collisions.
        
class Flat1(pygame.sprite.Sprite):
    """flat ground area on left side of screen """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("flat1.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (117,328)

class Flat2(pygame.sprite.Sprite):
    """flat ground area on left side of screen """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("flat2.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()        
        self.rect.center = (521,326)

class Hill(pygame.sprite.Sprite):
    """hill in the center of the screen """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("hill.gif")
        self.rect = self.image.get_rect()
        self.rect.center = (318,302)
        self.image = self.image.convert()

class HillCollider(pygame.sprite.Sprite):
    def __init__(self):
        #placed behind the hill to manage collisions
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("hill_collider.gif")
        self.rect = self.image.get_rect()
        self.rect.center = (318,295)
        self.image = self.image.convert()



#######################  LIFE METER CLASS BELOW  #######################

class LifeMeter(pygame.sprite.Sprite):
    """ changes life meter and plays sounds for tank hits
        Meter Number is number of hits until dead.  Initialized to 8 """
    
    def __init__(self, sound):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("life_meter_1.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.center = (320, 240)
        self.meterNumber = 1
        self.enemyHit = False
        self.goodHit = False
        self.tankDead = False
        self.enemyIsHit = False

        self.sound = sound

    def update(self):
        self.rect = self.image.get_rect()
        self.rect.center = self.center

    def hitTank(self, whichTank):
        self.whichTank = whichTank
        if not self.tankDead:
            if  self.whichTank == "enemy" and not self.enemyIsHit:
                self.meterNumber += 1
                self.image = pygame.image.load("life_meter_%s.gif" % str(self.meterNumber))
                self.enemyIsHit = True
                if self.meterNumber >= 8:
                    self.tankDead = True
                    self.sound.sndExplode.play()
                else:
                    self.tankDead = False
                    self.sound.sndHit.play()
            if  self.whichTank == "good" and not self.goodIsHit:
                self.meterNumber += 1
                self.image = pygame.image.load("life_meter_%s.gif" % str(self.meterNumber))
                self.goodIsHit = True
                if self.meterNumber >= 8:
                    self.tankDead = True
                    self.sound.sndExplode.play()
                else:
                    self.tankDead = False
                    self.sound.sndHit.play()


                    

#######################  Intro Screen Code Below  #######################

def introScreen():
    background = pygame.image.load("intro-screen.jpg")
    background = background.convert()

    keepGoing = True
    clock = pygame.time.Clock()
    while keepGoing:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  #escape key to exit
                    keepGoing = False
                if event.key == pygame.K_RETURN:  #RETURN/ENTER to start game
                    keepGoing = False
            
        screen.blit(background, (0, 0))
        pygame.display.flip()

        

#######################  Game Code Below  #######################

def game():
    pygame.display.set_caption("Tank Wars")
    background = pygame.image.load("background.jpg")
    background = background.convert()
    screen.blit(background, (0, 0))

    goodTank = GoodTank()
    enemyTank = EnemyTank(screen)
    sound = Sound()
    lifeMeterGood = LifeMeter(sound)
    lifeMeterEnemy = LifeMeter(sound)
    goodShell = Shell(screen, background, enemyTank, goodTank, lifeMeterGood, lifeMeterEnemy)
    enemyShell = Shell(screen, background, enemyTank, goodTank, lifeMeterGood, lifeMeterEnemy)
    turret = Turret(goodShell, goodTank)
    enemyTurret = EnemyTurret(enemyShell, enemyTank)
    flat1 = Flat1()
    flat2 = Flat2()
    hill = Hill()
    hillCollider = HillCollider()

    lblAngle = Label()
    lblPower = Label()
    lblShotCount = Label()
    lblGameStatus1 = Label()
    lblGameStatus2 = Label()
    lblAngle.center = (100, 400)
    lblPower.center = (100, 420)
    lblShotCount.center = (100, 440)
    lblGameStatus1.center = (320,440)
    lblGameStatus2.center = (320,455)
    lifeMeterGood.center = (125,375)
    lifeMeterEnemy.center = (550,375)

    allSprites = pygame.sprite.Group(
                                    flat1,
                                    flat2,
                                    hill,
                                    hillCollider,
                                    goodShell,
                                    enemyShell,
                                    turret,
                                    enemyTurret,
                                    lifeMeterGood,
                                    lifeMeterEnemy,
                                    lblAngle,
                                    lblPower,
                                    lblShotCount,
                                    lblGameStatus1,
                                    lblGameStatus2,
                                    goodTank,
                                    enemyTank
                                    )

    goodTankSprite = pygame.sprite.Group(goodTank)
    enemyTankSprite = pygame.sprite.Group(enemyTank)
    groundSprite = pygame.sprite.Group(flat1, flat2, hillCollider)
    hillSprite = pygame.sprite.Group(hill)
    hillCollider = pygame.sprite.Group(hillCollider)
    shellSprite = pygame.sprite.Group(goodShell, enemyShell)

    
    clock = pygame.time.Clock()
    keepGoing = True
    while keepGoing:
        clock.tick(30)
        for event in  pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False

        #check for Shell/Tank Collisions
        enemyHitTank = pygame.sprite.spritecollide(goodShell, enemyTankSprite, False)
        goodHitTank = pygame.sprite.spritecollide(enemyShell, goodTankSprite, False)

        #check for Shell / Ground Collisions
        shellHitGroundGood = pygame.sprite.spritecollide(goodShell, groundSprite, False)
        shellHitGroundEnemy = pygame.sprite.spritecollide(enemyShell, groundSprite, False)

        # check for Tank / Ground or Hill collisions
        global GOOD_TANK_HIT_HILL
        global ENEMY_TANK_HIT_HILL
        GOOD_TANK_HIT_HILL = pygame.sprite.spritecollide(goodTank, hillSprite, False)
        ENEMY_TANK_HIT_HILL = pygame.sprite.spritecollide(enemyTank, hillSprite, False)

        #Tank is hit by shell
        if enemyHitTank and not lifeMeterEnemy.tankDead:  
                lifeMeterEnemy.hitTank("enemy")
                lifeMeterEnemy.enemyIsHit = True
        else:
            lifeMeterEnemy.enemyIsHit = False
        if goodHitTank:  
            lifeMeterGood.hitTank("good")
            lifeMeterGood.goodIsHit = True
        else:
            lifeMeterGood.goodIsHit = False
            

        #if enemy tank is dead
        if lifeMeterEnemy.tankDead:
            enemyTank.image = pygame.image.load("dead_tank.gif")
            enemyTank.Dead = True
            lblGameStatus1.text = "        You Win!        "
            lblGameStatus2.text = "(return key to play again)"
            if enemyTank.Dead:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]: #return to start new game
                    turret.shotCount = 0
                    lblGameStatus1.text = ""
                    lblGameStatus2.text = ""

                    #reset enemy tank labels, tank image, and life meter
                    enemyTank.image = pygame.image.load("enemyTank000.gif")
                    lifeMeterEnemy.enemyHit = False
                    lifeMeterEnemy.tankDead = False
                    lifeMeterEnemy.enemyIsHit = False
                    enemyTank.Dead = False
                    lifeMeterEnemy.image = pygame.image.load("life_meter_1.gif")
                    lifeMeterEnemy.meterNumber = 1

                    #reset good tank and life meter
                    lifeMeterGood.image = pygame.image.load("life_meter_1.gif")
                    lifeMeterGood.meterNumber = 1
                    
        #if good tank is dead
        if lifeMeterGood.tankDead:
            goodTank.image = pygame.image.load("dead_tank.gif")
            goodTank.Dead = True
            lblGameStatus1.text = "        You Lose!        "
            lblGameStatus2.text = "(return key to play again)"
            if goodTank.Dead:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]: #return to start new game

                    #reset good tank labels, tank image, and life meter
                    turret.shotCount = 0
                    lblGameStatus1.text = ""
                    lblGameStatus2.text = ""
                    goodTank.image = pygame.image.load("tank000.gif")
                    lifeMeterGood.goodHit = False
                    lifeMeterGood.tankDead = False
                    lifeMeterGood.goodIsHit = False
                    goodTank.Dead = False
                    lifeMeterGood.image = pygame.image.load("life_meter_1.gif")
                    lifeMeterGood.meterNumber = 1

                    #reset enemy tank and life meter
                    lifeMeterEnemy.image = pygame.image.load("life_meter_1.gif")
                    lifeMeterEnemy.meterNumber = 1



        #if shell hits ground, move off-screen
        if shellHitGroundGood:
            goodShell.reset()
        else:
            shellHitGroundGood = False
        if shellHitGroundEnemy:
            enemyShell.reset()
        else:
            shellHitGroundEnemy = False          


        #update labels
        lblAngle.text = "angle: %d" % turret.dir
        lblPower.text = "power: %d" % turret.saveCharge
        lblShotCount.text = "shots fired: %d" % turret.shotCount


        allSprites.clear(screen, background)
        allSprites.update()
        allSprites.draw(screen)
        pygame.display.flip()



#######################  Program Main Below  #######################
     
def main():
    introScreen()
    game()
    
    pygame.quit()

if __name__ == "__main__":
        main()
