""" Tina.py 
    Use vector projection
    to simulate Tina the Dart Throwing Monkey"""
    
import pygame, math
pygame.init()
pygame.mixer.init()




class Label(pygame.sprite.Sprite):
    """ Label Class (simplest version) 
        Properties:
            font: any pygame font object
            text: text to display
            center: desired position of label center (x, y)
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("None", 30)
        self.text = ""
        self.center = (320, 240)
                
    def update(self):
        self.image = self.font.render(self.text, 1, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.center

class MonkeyArm(pygame.sprite.Sprite):
    def __init__(self, shell):
        self.shell = shell
        pygame.sprite.Sprite.__init__(self)
        self.imageMaster = pygame.image.load("monkeyArm.gif")
        self.imageMaster = self.imageMaster.convert()
        self.rect = self.imageMaster.get_rect()
        self.rect.center = (20, 450)
        self.TURNRATE = 5
        self.dir = 45
        
        # Changed this from 5 to 15 for Tina the Dart Throwing Monkey
        self.charge = 15

        
    def update(self):
        self.checkKeys()
        self.rotate()
    
    def checkKeys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.dir += self.TURNRATE
            if self.dir > 360:
                self.dir = self.TURNRATE
        if keys[pygame.K_RIGHT]:
            self.dir -= self.TURNRATE
            if self.dir < 0:
                self.dir = 360 - self.TURNRATE
        if keys[pygame.K_UP]:
            self.charge += 1
            if self.charge > 20:
                self.charge = 20
        if keys[pygame.K_DOWN]:
            self.charge -= 1
            if self.charge < 0:
                self.charge = 0
            
        if keys[pygame.K_SPACE]:
            self.shell.x = self.rect.centerx
            self.shell.y = self.rect.centery
            self.shell.speed = self.charge
            self.shell.dir = self.dir
            self.shell.calcVector()
    
    def rotate(self):
        oldCenter = self.rect.center
        self.image = pygame.transform.rotate(self.imageMaster, self.dir)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter

class Dart(pygame.sprite.Sprite):
    def __init__(self, screen, background, balloonSprites):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.background = background
        
        self.image = pygame.Surface((10, 10))
        self.image.fill((0xff, 0xff, 0xff))
        self.image.set_colorkey((0xff, 0xff, 0xff))
        pygame.draw.circle(self.image, (0, 0, 0), (5, 5), 5)
        self.image = pygame.transform.scale(self.image, (5, 5))
        self.rect = self.image.get_rect()
        self.rect.center = (-100, -100)
        
        self.x = -100
        self.y = -100
        self.dx = 0
        self.dy = 0

        # Set speed
        self.speed = 10
        self.dir = 0
        self.gravity = .5

        # Add balloons and sound effect(pop)
        self.balloonSprites = balloonSprites
        self.sndPop = pygame.mixer.Sound("pop.wav")


        # Number of balloons burst
        self.balloonsDown = 0
        
    def update(self):
        self.calcPos()
        self.checkBounds()
        self.rect.center = (self.x, self.y)

        # On collision, remove the sprite from the sprite balloon group
        if pygame.sprite.spritecollide(self, self.balloonSprites, True):
            self.balloonsDown += 1
            self.sndPop.play()
            if self.balloonsDown >= 8:
                print("All gone")

        
   
    def calcVector(self):
        radians = self.dir * math.pi / 180
        
        self.dx = self.speed * math.cos(radians)
        self.dy = self.speed * math.sin(radians)
        self.dy *= -1
        
        #clear the background
        self.background.fill((0x00, 0xCC, 0x00))
    
    def calcPos(self):
        #compensate for gravity
        self.dy += self.gravity
        
        #get old position for drawing
        oldx = self.x
        oldy = self.y
        
        self.x += self.dx
        self.y += self.dy
    
        pygame.draw.line(self.background, (0,0,0), (oldx, oldy), (self.x, self.y))
    
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
        """ move off stage and stop"""
        self.x = -100
        self.y = -100
        self.speed = 0

class StationaryImage(pygame.sprite.Sprite):
    def __init__(self, theImage, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40,40))
        self.image = pygame.image.load(theImage)
        # self.image = pygame.transform.scale(self.image,(20,20))
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y


def main():
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption ("Firing a Shell")
    
    background = pygame.Surface(screen.get_size())
    background.fill((0x00, 0xCC, 0x00))
    screen.blit(background, (0, 0))

    # Add as many layers of balloons as you want ..... (just adding 1 here)
    balloonSprites = pygame.sprite.Group()
    for balloon in range(0,10):
        balloon = StationaryImage("redBalloon.gif",50+50*balloon, 240)
        balloonSprites.add(balloon)

    # The monkey image
    tina = StationaryImage("monkey.gif", 20, 440)
    
    dart = Dart(screen, background, balloonSprites)
    monkeyArm = MonkeyArm(dart)
    lblOutput = Label()
    lblOutput.center = (100, 20)
    
    allSprites = pygame.sprite.OrderedUpdates(dart, lblOutput, tina, monkeyArm)

    clock = pygame.time.Clock()
    keepGoing = True
    while keepGoing:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            if event.type == pygame.KEYDOWN:
                print("Key down")
                
        
        #update label
        lblOutput.text = "dir: %d  speed %d" % (monkeyArm.dir, monkeyArm.charge)
        
        #blit the background for drawings
        screen.blit(background, (0, 0))
        
        #allSprites.clear(screen, background)
        allSprites.update()
        allSprites.draw(screen)
        balloonSprites.update()
        balloonSprites.draw(screen)
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
    
