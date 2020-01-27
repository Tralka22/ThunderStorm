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
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Thunderstorm')
        self.clock = pygame.time.Clock()
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
        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                exit()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.transform.scale(characters.load_image("sky.png"), (WIDTH, HEIGHT)), (0, 0))
        self.all_sprites.draw(self.screen)
        
        for i in self.particles:
            i.update()
            if not i.active:
                self.particles.remove(i)
        
        text = pygame.font.Font(None, 30).render(f'Coordinates: {self.player.world_pos}', 1, (255, 0, 0))
        self.screen.blit(text, (0, 0))
        
        text = pygame.font.Font(None, 30).render(f'{self.player.coins}$', 1, (255, 255, 0))
        self.screen.blit(text, (0, 30))
        
        pygame.display.flip()

g = Game()
while g.running:
    g.new()
pygame.quit()
