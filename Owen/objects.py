""" Navigation.py (for CSCI N451)
    bounce,wrap,slide at will
    Use Ball as the parent class and then override
    checkBounds and update.
    J.Kane Jan 11th 2010
"""

import pygame
pygame.init()

""" Parent class, Ball. Sprite, filled with circle
    and positioned in center of screen."""
class BaseObject(pygame.sprite.Sprite):
    def __init__(self, screen, background, imageFile, centerPoint):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.background = background
        
        self.image = pygame.image.load(imageFile)
        self.rect = self.image.get_rect()

        self.rect.center = centerPoint
        
        self.dx = 5
        self.dy = 5

""" BouncingBall class. Ball bounces off extremities.
    inherits from Ball class."""
class BouncingObject(BaseObject):
    def __init__(self, screen, background, bouncingImage, centerPoint):
        BaseObject.__init__(self, screen, background, bouncingImage, centerPoint)
    
    def update(self):
        oldCenter = self.rect.center
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        # Do this to see line drawn
        # pygame.draw.line(self.background, (0, 0, 0), oldCenter, self.rect.center)       
        self.checkBounds()        
    
    def checkBounds(self):
        """ bounce on encountering any screen boundary -
            multiply by -1 to change direction."""
        if self.rect.right >= self.screen.get_width():
            self.dx *= -1
        if self.rect.left <= 0:
            self.dx *= -1
        if self.rect.bottom >= self.screen.get_height():
            self.dy *= -1
        if self.rect.top  <= 0:
            self.dy *= -1
            
""" SlidingBall class. Ball slides along extremities.
    inherits from Ball class."""
class SlidingObject(BaseObject):
    def __init__(self, screen, background, slidingImage, centerPoint):
        # Parent class constructor
        BaseObject.__init__(self, screen, background, slidingImage, centerPoint)
    
    def update(self):
        oldCenter = self.rect.center
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        pygame.draw.line(self.background,
                         (0, 0, 0),
                         oldCenter,
                         self.rect.center)
        
        self.checkBounds()        
            
    def checkBounds(self):
        """ begin slide on encountering any screen boundary """
        """ Decide on which direction you want the object to slide."""
        
        if self.rect.right >= self.screen.get_width():
            self.dx = 0
        if self.rect.left <= 0:
            self.dx = 0

        # Now focus on the top and bottom.
        # No need to look left/right
        if self.rect.bottom >= self.screen.get_height():
            self.dy = 0
            if self.rect.right >= self.screen.get_width():
                self.dy = -3
                self.dx = 0
            if self.rect.left <= 0:
                self.dx = 3
        if self.rect.top <= 0:
            self.dy = 0
            if self.rect.right >= self.screen.get_width():
                self.dx = -3
            elif self.rect.left <= 0:
                self.dx = 0
                self.dy = 3

""" WrappingBall class. Ball wraps around the screen.
    Inherits from Ball class."""
class WrappingObject(BaseObject):
    def __init__(self, screen, background, wrappingImage, centerPoint):
        BaseObject.__init__(self, screen, background, wrappingImage, centerPoint)
        self.rect.centerx = 320
        self.rect.centery = 240
        self.dy = 0
        self.dx = 2
    
    def update(self):
        oldCenter = self.rect.center
        self.rect.centerx += self.dx
        self.rect.centery -= self.dy
        
        self.checkBounds()        
    
    def checkBounds(self):
        """ wrap around screen boundary """
        if self.rect.right > self.screen.get_width():
            self.rect.right = 25
        if self.rect.right < 0:
            self.rect.right = self.screen.get_width() + self.dx
        if self.rect.bottom > self.screen.get_height():
            self.rect.top = 25
        if self.rect.top  < 0:
            self.rect.bottom = self.screen.get_height()
    

        
def main():
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("B: Bouncing, W: Wrapping, S: Sliding")
    
    background = pygame.Surface(screen.get_size())
    background.fill((255, 255, 255))
    screen.blit(background, (0, 0))

    # Create a stationary Ball to start with    
    ball = BaseObject(screen, background,"riverrock.gif", (320,240))
    allSprites = pygame.sprite.Group(ball)
    
    clock = pygame.time.Clock()
    keepGoing = True
    
    while keepGoing:
        # Frame rate - 30 frames per second
        clock.tick(30)
        # Event checking
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            if (event.type == pygame.KEYDOWN):
                # User pressed a key
                # Check to see if the user pressed
                # a valid key.
                noChange = False
                if event.key == pygame.K_b:
                    ballClass = BouncingObject
                elif event.key == pygame.K_w:
                    ballClass = WrappingObject
                elif event.key == pygame.K_s:
                    ballClass = SlidingObject
                else:
                    # No valid key was pressed.
                    noChange = True
                if not(noChange):
                    # Trick to change ball class.
                    # Remove from sprites group
                    objectCoordinates = ball.rect.center
                    ball.remove(allSprites)
                    # Instantiate new Ball object
                    ball = ballClass(screen, background, "riverrock.gif", objectCoordinates)
                    # Add back in to the group for display.
                    allSprites.add(ball)
                                 
        allSprites.clear(screen, background)
        allSprites.update()
        allSprites.draw(screen)
        
        pygame.display.flip()

    # Windows 'gem'    
    pygame.quit()

if __name__ == "__main__":
    main()
