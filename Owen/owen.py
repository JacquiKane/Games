""" RiverMonster.py (Owen Vs RiverMonster) 
    Example interaction using animated  sprite
    and graphics from reiner's tile set.

    The motion relies on the file setup in
    Reiner's Tilesets.

    * Owen walks around a river patrolled by a River Monster.
    * If Owen jumps over the river he collects points. 
    * If Owen collides with the River Monster he loses a life.
    * If Owen collides with the floating River Skull he loses
    10 points.
    * If Owen collides with the bushes he loses points.

    The objective is to build up as many points as possible
    by jumping across the river.

    Techniques:
    1) Using States and transitions
    2) Using a Games Controller class (non-pygame)
    3) Reusing classes
    4) Partial scrolling
    
"""

import pygame, objects
pygame.init()

#direction constants
EAST = 0
NORTHEAST = 1
NORTH = 2
NORTHWEST = 3
WEST = 4
SOUTHWEST = 5
SOUTH = 6
SOUTHEAST = 7

# State Constants
WALKING = "Walking"
ATTACKED = "Attacked"
STOPPED = "Stopped"
DAZED = "Dazed"
JUMPING = "Jumping"
ATTACKING = "Attacking"


""" A Game Controller class is useful if you want to share
    object information between objects in the application.
    Technique - Pass the game controller object to the
    application object. The application object can then
    access information from other psrites/objects.
    No need to inherit from Sprite etc"""
class GameController:
        
    def __init__(self, score, monster, boy):
        self.monster = monster
        self.boy = boy
        self.score = score


""" The 'hero' sprite.
    The hero sprite has 2 sequences of images, one for
    the WALKING state, and the other for the JUMPING state.
    The JUMPING state is hi-jacked for the ATTACKED state,
    and for the DAZED state. """
class Boy(pygame.sprite.Sprite):
    
    def __init__(self, screen, score):
        self.screen = screen
        # Call the parent init
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("boy/running se0001.bmp")
        self.image = self.image.convert()
        tranColor = self.image.get_at((1, 1))
        self.image.set_colorkey(tranColor)
        self.rect = self.image.get_rect()
        self.rect.center = (300, 100)
        # Reduce the rectangular container to minimize collisions
        self.rect.inflate_ip(-20, -20)
        # Keep the score
        self.score = score

        # Image lists to use depending on the state 
        self.imgList = []
        self.jumpingImgList=[]
        self.walkingImgList = []
        #self.dazedImage = 0

        # Load the images here, so they are ready for use
        self.loadPics()

        # Initialize sprite for display
        self.dir = EAST
        self.frame = 0
        self.delay = 3
        self.pause = self.delay
        self.speed = 4       

        # Directional increments
        self.dxVals = (1,  .7,  0, -.7, -1, -.7, 0, .7)
        self.dyVals = (0, -.7, -1, -.7,  0,  .7, 1, .7)

        # Set the state to WALKING
        self.state = WALKING

        # Timers, for use to interrupt a state
        self.jumpTimer = 0
        self.dazedTimer = 0
        self.attackedTimer = 0

        # Placeholder
        self.gameController = []

    """ checkBounds - Method to keep sprite within
        display area.
    """
    def checkBounds(self):
        if self.rect.centerx > self.screen.get_width():
            self.rect.centerx = 0
        if self.rect.centerx < 0:
            self.rect.centerx = self.screen.get_width()
        if self.rect.centery > self.screen.get_height():
            self.rect.centery = 0
        if self.rect.centery < 0:
            self.rect.centery = self.screen.get_height()

            
    """ loadPics - Method to prepare image animation
        sequences."""
    def loadPics(self):
        fileBase = [
            "boy/running e000",
            "boy/running ne000",
            "boy/running n000",
            "boy/running nw000",
            "boy/running w000",
            "boy/running sw000",
            "boy/running s000",
            "boy/running se000"]


        jumpingFileBase = [
            "boy/cheering e000",
            "boy/cheering ne000",
            "boy/cheering n000",
            "boy/cheering nw000",
            "boy/cheering w000",
            "boy/cheering sw000",
            "boy/cheering s000",
            "boy/cheering se000"]
        
        for dir in range(8):
            tempList = []
            tempJumpingList = []
            tempFile = fileBase[dir]
            jumpingTempFile = jumpingFileBase[dir]
            for frame in range(8):
                imgName = "%s%d.bmp" % (tempFile, frame)
                jumpingImgFile = "%s%d.bmp" %(jumpingTempFile, frame)
                
                tmpImg = pygame.image.load(imgName)
                tmpImg.convert()
                tranColor = tmpImg.get_at((0, 0))
                tmpImg.set_colorkey(tranColor)
                tempList.append(tmpImg)
                
                tmpJumpingImg = pygame.image.load(jumpingImgFile)
                tmpJumpingImg.convert()
                tranColor = tmpJumpingImg.get_at((0, 0))
                tmpJumpingImg.set_colorkey(tranColor)
                tempJumpingList.append(tmpJumpingImg)
                
            self.imgList.append(tempList)
            self.walkingImgList.append(tempList)
            self.jumpingImgList.append(tempJumpingList)

    """ update - Method called at the frame rate. Here, screen
        updates are made. The states are checked here. """
    def update(self):
        
        # Implement the delay between animation frames
        self.pause -= 1
        
        if self.pause <= 0:
            self.pause = self.delay
        
            self.frame += 1
            if self.frame > 7:
                self.frame = 0
            
            self.calcVector()
            if not self.state == STOPPED:
                self.image =\
                           self.imgList[self.dir][self.frame]

            self.rect.centerx += self.dx
            self.rect.centery += self.dy

            self.checkBounds()

        # If the boy is jumping, time the jumping action.
        if self.state == JUMPING:
            self.jumpTimer +=1
            if self.jumpTimer > 45:
                # Reset the state and images to walking
                self.state = WALKING
                self.imgList = self.walkingImgList
        # If the state is DAZED (bushes), reset after 1 second
        elif self.state == DAZED:
            self.dazedTimer += 1
            if self.dazedTimer > 30:
                self.dazedTimer = 0
                self.reset()
        # If under attack by the monster, allow 2/3 of a second
        elif self.state == ATTACKED:
            self.attackedTimer += 1
            if self.attackedTimer > 20:
                self.attackedTimer = 0
                self.reset()


    """ faceTheMonster - the monster is walking EAST, so
        on collision, the boy should face the monster.
        SOUTHWEST looks best, also WEST."""
    def faceTheMonster(self):
        self.dir = SOUTHWEST
        self.rect.center = \
            (self.gameController.monster.rect.centerx + 10,
             self.gameController.monster.rect.centery + 10)

    """ giveController - A method to allow passing the
        gameController to this object, if created after
        the object is instantiated."""
    def giveController(self, gameController):
        self.gameController = gameController

    """calcVector - Method that uses positional parameters
        and increments to 'move' the sprite. Called from
        update"""
    def calcVector(self):
        self.dx = self.dxVals[self.dir]
        self.dy = self.dyVals[self.dir]

        if self.state == JUMPING:
            # Temporarily raise the sprite
            # by changing increments
            if self.jumpTimer < 5 :
                if self.dir == NORTH:
                    self.dy -=30
                elif self.dir == SOUTH:
                    self.dy += 30
            elif self.jumpTimer > 20:
                self.score.score += 50
                self.score.message = "Congratulations - Good Jump!"
                self.state = WALKING
                self.imgList = self.walkingImgList
        
        self.dx *= self.speed
        self.dy *= self.speed
    
    def turnLeft(self):
        self.dir += 1
        if self.dir > SOUTHEAST:
            self.dir = EAST

    def turnRight(self):
        self.dir -= 1
        if self.dir < EAST:
            self.dir = SOUTHEAST

    def jump(self):
        self.speed = 4
        self.jumpTimer = 0
        self.state = JUMPING
        self.imgList = self.jumpingImgList

    def stop(self):
        self.state = STOPPED
        self.speed = 0

    def reset(self):
        self.rect.centerx, self.rect.centery = (40,40)
        self.speed = 4
        self.state = WALKING
        self.imgList = self.walkingImgList

    def dazedAndConfused(self):
        self.state = DAZED
        self.dazedTimer = 0
        self.speed = 0
        self.imgList = self.jumpingImgList

    def underAttack(self):
        self.state = ATTACKED
        self.faceTheMonster()

class RiverMonster(pygame.sprite.Sprite):

    # Placeholder ! (N,S,E,W,NE,NW,SE,SW)
    # Direction
    EAST = 0
    
    def __init__(self, screen):
        self.screen = screen
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load("swampthing/stopped0002.bmp")
        self.image = self.image.convert()
 
        tranColor = self.image.get_at((1, 1))
        self.image.set_colorkey(tranColor)
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-20, -40)
        
        # (1) Screen Coordinates
        self.rect.center = (50,260)
        self.img = []
        self.walkingImg = self.img
        self.attackingImg = []
        
        self.loadPics()
        self.frame = 0
        self.delay = 3
        self.pause = self.delay

        # Displacement and Direction
        self.dx = 4

        # State
        self.state = WALKING

        self.attackTimer = 0


    def update(self):
        # Delay
        self.pause -= 1

        if self.pause <= 0:
            self.pause = self.delay
            
            self.frame += 1
            if self.frame > 7:
                self.frame = 0

            self.image = self.img[self.frame]

            # Coordinates and Displacement, only if WALKING
            if self.state == WALKING:
                self.rect.centerx += self.dx
                if self.rect.centerx > self.screen.get_width():
                    self.rect.centerx = 0

        if self.state == ATTACKING:
            self.attackTimer +=1
            # Check the timer
            if self.attackTimer > 30:
                self.attackTimer = 0
                self.rect.centerx += self.dx*3
                self.normalize()
            
    
    def loadPics(self):
        for i in range(8):
            imgName = "swampthing/walking e000%d.bmp" % i
            attackImgName = "swampthing/attack e000%d.bmp" % i
            tmpImg = pygame.image.load(imgName)
            tmpAttackImg = pygame.image.load(attackImgName)
            tmpImg.convert()
            tmpAttackImg.convert()
            tranColor = tmpImg.get_at((0, 0))
            tmpImg.set_colorkey(tranColor)
            tmpAttackImg.set_colorkey(tranColor)
            self.img.append(tmpImg)
            self.attackingImg.append(tmpAttackImg)

    def attack(self):
        self.vandalize()

    def normalize(self):
        self.img = self.walkingImg
        self.state = WALKING
        self.speed = 4

    def vandalize(self):
        self.img = self.attackingImg
        self.speed = 0
        self.state = ATTACKING

""" Class River uses scrolling techniques to animate the
    river"""
class River(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("river.gif")
        self.image = pygame.transform.scale(self.image,(1920, 50))
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-20, -40)
        # Position
        self.rect.top = 220
        self.dx = -5
        self.reset()
        
    def update(self):
        # Scroll left to right or vice versa
        self.rect.right += self.dx
        if self.rect.left <= -640:
            self.reset() 
    
    def reset(self):
        # Reset so scrolling works
        self.rect.left = 0

class Scoreboard(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.lives = 5
        self.score = 0
        self.message = "Beware ..."
        self.font = pygame.font.SysFont("None", 25)
        
    def update(self):
        self.text = "Monster leaves: %d lives, Owen: %d, and %s" \
                    % (self.lives, self.score, self.message)
        self.image = self.font.render(self.text, 1, (255, 255, 0))
        self.rect = self.image.get_rect()

    

def main():
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Press Space to make Owen jump, r to reset - be careful")
    
    background = pygame.Surface(screen.get_size())
    background.fill((0, 0x66, 0))
    screen.blit(background, (0, 0))

    # Create the game objects
    # Scoreboard
    scoreboard = Scoreboard()    
    # Hero sprite
    boy = Boy(screen, scoreboard)
    # Monster sprite
    riverMonster = RiverMonster(screen)
    # River sprite
    river = River()
    # Rocky home base for hero sprite
    rockBase = objects.BaseObject(screen,
                                  background,
                                  "rockarea.gif",
                                  (10,10))
    # Sand banks by side of river.
    # Note use of objects (navigation)
    upperSandyBank = objects.BaseObject(screen,
                                        background,
                                        "sandyBankupper.gif",
                                        (320,200))
    lowerSandyBank = objects.BaseObject(screen,
                                        background,
                                        "sandyBanklower.gif",
                                        (320,280))
    # Bushes for hero sprite to collide with
    bush =  objects.BaseObject(screen,
                               background,
                               "bush.gif",
                               (220,80))
    # ... to minimize 'wide' collisions
    bush.rect.inflate_ip(-25, -25)
    
    weed =  objects.BaseObject(screen,
                               background,
                               "weed.gif",
                               (250,380))
    weed.rect.inflate_ip(-25, -25)

    weed2 = objects.BaseObject(screen,
                               background,
                               "weed.gif",
                               (450,40))
    weed2.rect.inflate_ip(-25, -25)


    # Create the game controller object, possible
    # solution to sharing information between sprites
    gameController = GameController(scoreboard,
                                    riverMonster,
                                    boy)
    # Pass the reference to the game controller
    boy.giveController(gameController)

    # Create the flowting skull, using WrappingObject class
    riverSkull = objects.WrappingObject(background,
                                   screen,
                                   "skull.gif",
                                   (0,240))

    # Display all sprites
    allSprites = pygame.sprite.OrderedUpdates(river,
                                              rockBase,
                                              upperSandyBank,
                                              lowerSandyBank,
                                              riverSkull,
                                              boy,
                                              riverMonster,
                                              scoreboard,
                                              bush,
                                              weed,
                                              weed2)
    
    # Differentiate sprites for collision detection
    skullSprites = pygame.sprite.Group(riverSkull)

    bushSprites = pygame.sprite.Group(bush, weed, weed2)
    
    clock = pygame.time.Clock()
    keepGoing = True
    while keepGoing:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    boy.turnLeft()
                elif event.key == pygame.K_RIGHT:
                    boy.turnRight()
                elif event.key == pygame.K_SPACE:
                    boy.jump()
                elif event.key == pygame.K_r:
                    boy.reset()

        # Add a new check, to see if the boy hit the river
        hitByRiver = pygame.sprite.collide_rect(boy,river)

        # Hit floating skull?
        hitByMissile = pygame.sprite.spritecollide(boy,
                                            skullSprites,
                                                    False)
        # Hit River Monster?
        hitByRiverMonster = \
            pygame.sprite.collide_rect(boy,
                                       riverMonster)

        # Hit bushes?
        hitByBushes = pygame.sprite.spritecollide(boy,
                                                bushSprites,
                                                False)
        # Hit river?
        if hitByRiver:
            scoreboard.message = "Owen is stuck in the sandbanks.."
            boy.stop()

        # Now handle the collisions
        if hitByMissile:
            scoreboard.message = "Ouch! Hit by a skeleton head .."

        # Check for attacked state to avoid constantly
        # reducing score.
        if hitByRiverMonster and not boy.state == ATTACKED:
            scoreboard.message = "Ouch! Hit by a River Monster..."
            scoreboard.lives -= 1
            scoreboard.score -= 10
            boy.stop()
            riverMonster.attack()
            boy.dazedAndConfused()
            boy.underAttack()

        # Again, check for dazed state to avoid constantly
        # reducing score
        if hitByBushes and not boy.state == DAZED:
            boy.state = DAZED
            scoreboard.message = "Watchout for the bushes!"
            scoreboard.score -= 10
            boy.stop()
            boy.dazedAndConfused()

        allSprites.clear(screen, background)
        allSprites.update()
        allSprites.draw(screen)
        
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main()
