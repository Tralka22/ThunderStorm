import pygame
import random

class Particle:
    def __init__(self, pos, age, screen):
        self.age = 1
        self.active = True
        self.screen = screen
        self.death = age
        self.pos = pos

    def update(self):
        if self.age > self.death:
            self.active = False
        else:
            self.perform()
            self.age += 1

    def perform(self):
        pass


class Lightning(Particle):
    def __init__(self, pos1, pos2, age, screen):
        self.age = 0
        self.active = True
        self.screen = screen
        self.death = age
        self.pos1 = pos1
        self.pos2 = pos2

    def perform(self):
        tc = []
        random.seed()
        p3 = (self.pos1[0] + int(((self.pos2[0] - self.pos1[0] + 5) // 2) * random.uniform(1, 1.5)),
              self.pos1[1] + int(((self.pos2[1] - self.pos1[1] + 5) // 2) * random.uniform(1, 1.5)))
        tc.append(self.pos1)
        tc.append(p3)
        tc.append(self.pos2)
        for i in range(len(tc) - 1):
            pygame.draw.line(screen, (0, 255, 255), tc[i], tc[i + 1], random.randint(1, 5))
            random.seed()


class Explosion(Particle):
    def __init__(self, pos, diameter, age, screen):
        self.age = 1
        self.active = True
        self.screen = screen
        self.death = age
        self.pos = pos
        self.diameter = diameter
    
    def perform(self):
        alpha = 255 - int(255 * (self.age / self.death))
        pygame.draw.circle(screen, (alpha, alpha, 0), self.pos, int(self.diameter * (self.age / self.death)))
        pygame.draw.circle(screen, (alpha, alpha // 2, 0), self.pos, int(self.diameter * (self.age / self.death)), int(self.diameter * (self.age / self.death) * 0.5))

pygame.init()
size = width, height = 1200, 900
screen = pygame.display.set_mode(size)
fps = 120
clock = pygame.time.Clock()
particles = []

running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for i in range(2):
                    particles.append(Lightning((0, 0), event.pos, 10, screen))
                    particles.append(Lightning((width, height), event.pos, 10, screen))
                    particles.append(Lightning((width, 0), event.pos, 10, screen))
                    particles.append(Lightning((0, height), event.pos, 10, screen))
                particles.append(Explosion(event.pos, random.randint(1, 5) * 10, random.randint(1, 5) * 10, screen))
    for i in particles:
        i.update()
        if not i.active:
            particles.remove(i)
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
