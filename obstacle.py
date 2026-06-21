import random
import pygame
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, OBSTACLES_PATH
from pygame.locals import RLEACCEL

OBSTACLE_FILES = ['crab.png', 'seagull.png', 'seaweed.png']

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surface = pygame.image.load(OBSTACLES_PATH + random.choice(OBSTACLE_FILES))
        self.surface = pygame.transform.scale(self.surface, (int(SCREEN_WIDTH / 9), int(SCREEN_HEIGHT / 8)))
        self.surface.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surface.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(4, 10)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
