import random
import pygame
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, TRASH_PATH
from pygame.locals import RLEACCEL

TRASH_FILES = ['can.png', 'cigarette.png', 'paper_wad.png', 'water_bottle.png']

class Trash(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surface = pygame.image.load(TRASH_PATH + random.choice(TRASH_FILES))
        self.surface = pygame.transform.scale(self.surface, (int(SCREEN_WIDTH / 10), int(SCREEN_HEIGHT / 10)))
        self.surface.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surface.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(4, 8)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
