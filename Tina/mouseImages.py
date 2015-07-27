""" MouseImages.py
    create a sprite with a given image file,
    and have it follow the mouse"""
    
import pygame

screen = pygame.display.set_mode((640, 480))

class MousePlane(pygame.sprite.Sprite):
    def __init__(self, planeImage):
        pygame.sprite.Sprite.__init__(self)
        self.image =  pygame.image.load(planeImage)
        self.rect = self.image.get_rect()
        print "width is %d, height is %d" %(self.rect.width, self.rect.height)
        # self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height)) 
        

    def update(self):
        self.rect.center = pygame.mouse.get_pos()


class MovingImage(pygame.sprite.Sprite):
    def __init__(self, theImage):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(theImage)
        self.image = pygame.transform.scale(self.image,(50,50))
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.centerx = 0
        self.rect.centery = 200
        self.dx = 2
        
    def update(self):
        self.rect.centerx += self.dx
        if self.rect.right > screen.get_width():
            self.rect.left = 0       

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


