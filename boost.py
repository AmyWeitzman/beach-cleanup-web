import random
import pygame
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, BOOSTS_PATH
from pygame.locals import RLEACCEL

BOOST_FILES = ['seashell1.png', 'seashell2.png', 'seashell3.png']

class Boost(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surface = pygame.image.load(BOOSTS_PATH + random.choice(BOOST_FILES))
        self.surface = pygame.transform.scale(self.surface, (int(SCREEN_WIDTH / 10), int(SCREEN_HEIGHT / 10)))
        self.surface.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surface.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    def update(self):
        self.rect.move_ip(-3, 0)
        if self.rect.right < 0:
            self.kill()
