import pygame
import characters
import random
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

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
        file = open('data/intro.txt', 'rt')
        data = file.read().split('\n')
        file.close()
        for i in range(len(data)):
            text = pygame.font.Font('data/joker.ttf', 30).render(data[i], 1, (255, 255, 255))
            self.screen.blit(text, (5, i * 25 + 5))
        pygame.display.flip()
        watching = True
        while watching:
            for event in pygame.event.get():
                if event.type in [pygame.KEYUP, pygame.MOUSEBUTTONDOWN]:
                    watching = False
            self.clock.tick(120)
        pygame.mixer.music.load('data/theme-2.wav')
        self.cursor_active = pygame.mouse.get_focused()
        self.mouse_pos = pygame.mouse.get_pos()
        self.cursor_active = True
        pygame.mouse.set_visible(False)
        self.running = True

    def choose_hat(self):
        hat_chosen = False
        hat = 0
        hats = list(characters.CLASSES.keys())
        while not hat_chosen:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    self.cursor_active = pygame.mouse.get_focused()
                    if self.cursor_active:
                        self.mouse_pos = event.pos
                if event.type == pygame.KEYDOWN:
                    if event.key == 276:
                        hat -= 1
                    if event.key == 275:
                        hat += 1
                    else:
                        hat_chosen = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.pos[0] < WIDTH // 2:
                        hat -= 1
                    else:
                        hat += 1
            hat = hat % len(hats)
            
            self.screen.fill((0, 128, 0))
            
            text = pygame.font.Font('data/joker.ttf', 30).render('CHOOSE YOUR HAT!', 1, (255, 255, 255))
            self.screen.blit(text, (200, 5))
            
            text = pygame.font.Font('data/joker.ttf', 30).render(hats[hat].upper(), 1, (255, 255, 255))
            self.screen.blit(text, (220, 100))
            
            hat_image = characters.load_image(f'{hats[hat]}.png', -1)
            hat_image = pygame.transform.scale(hat_image, (200, 200))
            self.screen.blit(hat_image, (WIDTH // 2 - 100, HEIGHT // 2 - 100))
            
            if self.cursor_active:
                cursor = characters.load_image('cursor.png', -1)
                self.screen.blit(cursor, self.mouse_pos)
        
            pygame.display.flip()
            self.clock.tick(60)
        self.clac = hats[hat]

    def new(self):
        self.choose_hat()
        self.lvl = 1
        self.all_sprites = pygame.sprite.Group()
        self.player = characters.Character(self, self.clac)
        self.platforms = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        for x, y, w, h in PLATFORMS:
            p1 = Platform(x, y, w, h)
            self.all_sprites.add(p1)
            self.platforms.add(p1)
        self.particles = []
        self.enemies_mel = pygame.sprite.Group()
        e = characters.MeleeEnemy(self)
        self.paused = False
        self.fs = False
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
        file = open('highscore.txt', 'rt')
        heh = int(file.read())
        file.close()
        if self.player.coins >= heh:
            fil = open('highscore.txt', 'wt')
            print(self.player.coins, file=fil)

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
        
        for enemy in self.enemies_mel.sprites():
            posx = enemy.rect.topleft[0]
            posy = enemy.rect.midtop[1] - 20
            pygame.draw.rect(self.screen, (0, 0, 0), (posx, posy, 100, 20))
            pygame.draw.rect(self.screen, (0, 255, 0), (posx, posy, int(100 * enemy.hp / enemy.mhp), 20))
        
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
        
        file = open('highscore.txt', 'rt')
        heh = int(file.read())
        file.close()
        text = pygame.font.Font('data/joker.ttf', 30).render(f'Best score: {heh}$', 1, (255, 255, 0))
        self.screen.blit(text, (5, 40))
        
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
