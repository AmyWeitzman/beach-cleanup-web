import pygame
from player import Player
from obstacle import Obstacle
from trash import Trash
from boost import Boost
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, AUDIO_PATH, LOGO_PATH
from random import randint, choices
import time

from pygame.locals import K_ESCAPE, KEYDOWN, QUIT


class Button:
    def __init__(self, x, y, w, h, text, color=(30, 159, 199), hover=(20, 120, 160)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = hover

    def draw(self, surface):
        col = self.hover if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=8)
        font = pygame.font.SysFont('Arial', 28)
        txt = font.render(self.text, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class Toggle:
    def __init__(self, label, x, y, value=True):
        self.label = label
        self.x = x
        self.y = y
        self.value = value
        self.rect = pygame.Rect(x + 280, y - 5, 70, 32)

    def draw(self, surface):
        font = pygame.font.SysFont('Arial', 26)
        surface.blit(font.render(self.label + ':', True, (0, 0, 0)), (self.x, self.y))
        col = (50, 200, 100) if self.value else (180, 60, 60)
        pygame.draw.rect(surface, col, self.rect, border_radius=16)
        val = font.render('ON' if self.value else 'OFF', True, (255, 255, 255))
        surface.blit(val, val.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.value = not self.value


class Game:
    SETTINGS = 'settings'
    PLAYING = 'playing'
    GAME_OVER = 'game_over'

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.logo = pygame.image.load(LOGO_PATH)
        pygame.display.set_caption('Beach Cleanup')
        pygame.display.set_icon(self.logo)
        self.bg = pygame.transform.scale(
            pygame.image.load('./imgs/sand_bg.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        cx = SCREEN_WIDTH // 2
        self.music_toggle = Toggle('Background Music', cx - 175, SCREEN_HEIGHT // 2 - 10)
        self.sounds_toggle = Toggle('Sound Effects', cx - 175, SCREEN_HEIGHT // 2 + 50)
        self.play_btn = Button(cx - 80, SCREEN_HEIGHT // 2 + 120, 160, 48, 'Play')
        self.play_again_btn = Button(cx - 100, SCREEN_HEIGHT // 2 + 120, 200, 48, 'Play Again')

        self.state = self.SETTINGS
        self.sounds = {}
        self.player = None
        self.obstacles = self.trash = self.boosts = None
        self.startTime = self.totalTime = 0
        self.ADD_OBSTACLE = self.ADD_TRASH = self.ADD_BOOST = None
        self.POINTS_TRASH = 20
        self.POINTS_BOOST = 100
        self.COLLISION_DELTA = 30

    def _init_round(self):
        self.ADD_OBSTACLE = pygame.USEREVENT + 1
        self.ADD_TRASH = pygame.USEREVENT + 2
        self.ADD_BOOST = pygame.USEREVENT + 3
        pygame.time.set_timer(self.ADD_OBSTACLE, randint(1000, 3000))
        pygame.time.set_timer(self.ADD_TRASH, randint(1000, 3000))
        pygame.time.set_timer(self.ADD_BOOST, randint(5000, 10000))

        self.player = Player()
        self.obstacles = pygame.sprite.Group()
        self.trash = pygame.sprite.Group()
        self.boosts = pygame.sprite.Group()
        self.startTime = time.time()
        self.totalTime = 0

        pygame.mixer.music.load(AUDIO_PATH + 'waves.ogg')
        pygame.mixer.music.set_volume(1)
        if self.music_toggle.value:
            pygame.mixer.music.play(loops=-1)

        collect_trash = pygame.mixer.Sound(AUDIO_PATH + 'collect_trash.ogg')
        collect_trash.set_volume(0.8)
        self.sounds['trash'] = collect_trash

        collect_boost = pygame.mixer.Sound(AUDIO_PATH + 'collect_boost.ogg')
        collect_boost.set_volume(0.8)
        self.sounds['boost'] = collect_boost

        game_over = pygame.mixer.Sound(AUDIO_PATH + 'game_over.ogg')
        game_over.set_volume(0.2)
        self.sounds['game_over'] = game_over

        self.state = self.PLAYING

    # ── Settings screen ──────────────────────────────────────────────

    def _draw_settings(self):
        self.screen.fill((240, 220, 160))
        logo_scaled = pygame.transform.scale(self.logo, (220, 110))
        self.screen.blit(logo_scaled, logo_scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))
        font = pygame.font.SysFont('Arial', 38, bold=True)
        title = font.render('Settings', True, (0, 0, 0))
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 65)))
        self.music_toggle.draw(self.screen)
        self.sounds_toggle.draw(self.screen)
        self.play_btn.draw(self.screen)

    def _handle_settings(self, event):
        self.music_toggle.handle(event)
        self.sounds_toggle.handle(event)
        if self.play_btn.clicked(event):
            self._init_round()

    # ── Playing screen ───────────────────────────────────────────────

    def _collision(self, a, b):
        x_ok = (a.rect.right > b.rect.left) and ((a.rect.right - b.rect.left) >= self.COLLISION_DELTA)
        top = (a.rect.bottom > b.rect.top) and (self.COLLISION_DELTA <= (a.rect.bottom - b.rect.top) <= (a.rect.height - self.COLLISION_DELTA))
        bot = (b.rect.bottom > a.rect.top) and (self.COLLISION_DELTA <= (b.rect.bottom - a.rect.top) <= (a.rect.height - self.COLLISION_DELTA))
        return x_ok and (top or bot)

    def _check_collisions(self):
        for obs in self.obstacles:
            if self._collision(self.player, obs):
                if self.sounds_toggle.value:
                    self.sounds['game_over'].play()
                pygame.mixer.music.stop()
                self.state = self.GAME_OVER
                return

        collected_trash = pygame.sprite.spritecollide(self.player, self.trash, True)
        if collected_trash:
            self.player.incPts(self.POINTS_TRASH * len(collected_trash))
            if self.sounds_toggle.value:
                self.sounds['trash'].play()

        collected_boosts = pygame.sprite.spritecollide(self.player, self.boosts, True)
        if collected_boosts:
            self.player.incPts(self.POINTS_BOOST * len(collected_boosts))
            if self.sounds_toggle.value:
                self.sounds['boost'].play()

    def _draw_game(self):
        self.screen.blit(self.bg, (0, 0))
        for sprite in list(self.obstacles) + list(self.trash) + list(self.boosts) + [self.player]:
            self.screen.blit(sprite.surface, sprite.rect)
        font = pygame.font.SysFont('Arial', 50)
        score = font.render('Score: ' + str(self.player.getPts()), True, (0, 0, 0))
        self.screen.blit(score, score.get_rect(topright=(SCREEN_WIDTH - 10, 15)))
        timer = font.render('Time: ' + str(self.totalTime) + 's', True, (0, 0, 0))
        self.screen.blit(timer, timer.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)))

    def _handle_game(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.mixer.music.stop()
            self.state = self.GAME_OVER
        elif event.type == self.ADD_OBSTACLE:
            obj = Obstacle()
            self.obstacles.add(obj)
        elif event.type == self.ADD_TRASH:
            obj = Trash()
            self.trash.add(obj)
        elif event.type == self.ADD_BOOST:
            if choices([0, 1], weights=[70, 30])[0]:
                self.boosts.add(Boost())

    def _update_game(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.obstacles.update()
        self.trash.update()
        self.boosts.update()
        self.totalTime = int(time.time() - self.startTime)
        self._check_collisions()

    # ── Game over screen ─────────────────────────────────────────────

    def _draw_game_over(self):
        self.screen.blit(self.bg, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        big = pygame.font.SysFont('Arial', 60, bold=True)
        med = pygame.font.SysFont('Arial', 36)

        title = big.render('GAME OVER', True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(cx, SCREEN_HEIGHT // 2 - 90)))
        score = med.render('Score: ' + str(self.player.getPts()), True, (255, 255, 255))
        self.screen.blit(score, score.get_rect(center=(cx, SCREEN_HEIGHT // 2 - 10)))
        t = med.render('Time: ' + str(self.totalTime) + 's', True, (255, 255, 255))
        self.screen.blit(t, t.get_rect(center=(cx, SCREEN_HEIGHT // 2 + 45)))
        self.play_again_btn.draw(self.screen)

    def _handle_game_over(self, event):
        if self.play_again_btn.clicked(event):
            self.state = self.SETTINGS

    # ── Main tick (called every frame from run.py) ───────────────────

    def tick(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if self.state == self.SETTINGS:
                self._handle_settings(event)
            elif self.state == self.PLAYING:
                self._handle_game(event)
            elif self.state == self.GAME_OVER:
                self._handle_game_over(event)

        if self.state == self.PLAYING:
            self._update_game()

        if self.state == self.SETTINGS:
            self._draw_settings()
        elif self.state == self.PLAYING:
            self._draw_game()
        elif self.state == self.GAME_OVER:
            self._draw_game_over()

        pygame.display.flip()
        self.clock.tick(30)
        return True
