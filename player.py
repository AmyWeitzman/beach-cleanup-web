import pygame
from utils import SCREEN_WIDTH, SCREEN_HEIGHT
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, RLEACCEL

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surface = pygame.image.load('./imgs/players/stick_figure.png').convert()
        self.surface = pygame.transform.scale(self.surface, (int(SCREEN_WIDTH / 8), int(SCREEN_HEIGHT / 4)))
        self.surface.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surface.get_rect()
        self.speed = 5
        self.points = 0

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -self.speed)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, self.speed)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def getPts(self):
        return self.points

    def incPts(self, numPts):
        self.points += numPts
