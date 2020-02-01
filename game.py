import pygame
import characters

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
        self.clock = pygame.time.Clock()
        pygame.mixer.music.load('data/theme-1.wav')
        self.running = True

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.player = characters.Character(self)
        self.platforms = pygame.sprite.Group()
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

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.transform.scale(characters.load_image("sky.png"), (WIDTH, HEIGHT)), (0, 0))
        self.all_sprites.draw(self.screen)
        
        if not self.paused:
            for i in self.particles:
                i.update()
                if not i.active:
                    self.particles.remove(i)
        
        text = pygame.font.Font('data/joker.ttf', 30).render(f'{self.player.coins}$', 1, (255, 255, 0))
        self.screen.blit(text, (5, 5))
        
        pygame.draw.rect(self.screen, (0, 0, 0), (WIDTH - self.player.maxHealth * 2, 0, self.player.maxHealth * 2, 30))
        pygame.draw.rect(self.screen, (255, 0, 0), (WIDTH - self.player.health * 2, 0, self.player.health * 2, 30))
        
        text = pygame.font.Font('data/joker.ttf', 80).render(f'{self.player.health}', 1, (255, 255, 255))
        text = pygame.transform.scale(text, (self.player.maxHealth * 2, 30))
        self.screen.blit(text, (WIDTH - self.player.maxHealth * 2, 0))

        if self.paused:
            psm = pygame.Surface((WIDTH, HEIGHT))
            psm.fill((0, 0, 0))
            psm.set_colorkey((0, 255, 0))
            psm.set_alpha(128)
            self.screen.blit(psm, (0, 0))
            text = pygame.font.Font('data/joker.ttf', 100).render('GAME PAUSED', 1, (255, 255, 255))
            text = pygame.transform.scale(text, (WIDTH // 2, 50))
            self.screen.blit(text, (0, HEIGHT - 100))
        pygame.display.flip()

g = Game()
while g.running:
    g.new()
pygame.quit()
