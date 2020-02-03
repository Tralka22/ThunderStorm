import pygame
import characters
import random
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

cl = 'dev'

FPS = 60
WIDTH = 800
HEIGHT = 600
PLATFORMS = [(0, HEIGHT - 40, WIDTH, 40),
             (1000, 400, 50, 50),
             (1200, 300, WIDTH // 2, 20)]


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pygame.sprite.Sprite.__init__(self)
        self.image = characters.load_image('platform.png', -1)
        self.image = pygame.transform.scale(self.image, ((w, h)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption('Thunderstorm')
        pygame.display.set_icon(characters.load_image('game-icon.png', -1))
        self.clock = pygame.time.Clock()
        pygame.mixer.music.load('data/theme-2.wav')
        self.cursor_active = pygame.mouse.get_focused()
        self.mouse_pos = pygame.mouse.get_pos()
        self.cursor_active = True
        pygame.mouse.set_visible(False)
        self.running = True

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.player = characters.Character(self, cl)
        self.platforms = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        for x, y, w, h in PLATFORMS:
            p1 = Platform(x, y, w, h)
            self.all_sprites.add(p1)
            self.platforms.add(p1)
        self.particles = []
        self.enemies_mel = pygame.sprite.Group()
        e = characters.MeleeEnemy(self, 1)
        self.paused = False
        self.fs = False
        self.player.dead = False
        self.lvl = 1
        pygame.mixer.music.play(-1)
        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.clock.tick(FPS)
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()
        if self.player.dead:
            self.new()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == 27:
                    self.paused = not self.paused
                if event.key == 292:
                    self.fs = not self.fs
                    if self.fs:
                        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
            if event.type == pygame.MOUSEMOTION:
                self.cursor_active = pygame.mouse.get_focused()
                if self.cursor_active:
                    self.mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.player.shoot(event.pos)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.transform.scale(characters.load_image("sky.png"), (WIDTH, HEIGHT)), (0, 0))
        self.all_sprites.draw(self.screen)
        
        hat = characters.load_image(f'{self.player.clas}.png', -1)
        self.screen.blit(hat, (self.player.rect.topleft[0], self.player.rect.topleft[1] - 25))
        
        if not self.paused:
            for i in self.particles:
                i.update()
                if not i.active:
                    self.particles.remove(i)
        
        pygame.draw.rect(self.screen, (0, 0, 0), (WIDTH - self.player.maxHealth * 2, 0, self.player.maxHealth * 2, 30))
        pygame.draw.rect(self.screen, (255, 0, 0), (WIDTH - self.player.health * 2, 0, self.player.health * 2, 30))
        
        text = pygame.font.Font('data/joker.ttf', 80).render(f'{self.player.health}', 1, (255, 255, 255))
        text = pygame.transform.scale(text, (self.player.maxHealth * 2, 30))
        self.screen.blit(text, (WIDTH - self.player.maxHealth * 2, 0))
        
        text = pygame.font.Font('data/joker.ttf', 30).render(f'{self.player.coins}$', 1, (255, 255, 0))
        self.screen.blit(text, (5, 5))
        
        if self.paused:
            psm = pygame.Surface((WIDTH, HEIGHT))
            psm.fill((0, 0, 0))
            psm.set_colorkey((0, 255, 0))
            psm.set_alpha(128)
            self.screen.blit(psm, (0, 0))
            text = pygame.font.Font('data/joker.ttf', 100).render('GAME PAUSED', 1, (255, 255, 255))
            text = pygame.transform.scale(text, (WIDTH // 2, 50))
            self.screen.blit(text, (0, HEIGHT - 100))
        
        if self.cursor_active:
            cursor = characters.load_image('cursor.png', -1)
            self.screen.blit(cursor, self.mouse_pos)
        pygame.display.flip()

g = Game()
while g.running:
    g.new()
pygame.quit()
