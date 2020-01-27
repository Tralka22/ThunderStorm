import pygame
import random
import particles
import sys
import os

vector = pygame.math.Vector2
FPS = 60
WIDTH = 800
HEIGHT = 600

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Character(pygame.sprite.Sprite):
    def __init__(self, game):
            pygame.sprite.Sprite.__init__(self)
            self.frame = 0
            self.image = load_image(f'run{self.frame}.png', -1)
            self.image = pygame.transform.scale(self.image, ((55, 60)))
            self.rect = self.image.get_rect()
            self.rect.center = (WIDTH / 2, HEIGHT / 2)
            self.world_pos = [WIDTH / 2, HEIGHT / 2]
            self.pos = vector(WIDTH / 2, HEIGHT / 2)
            self.vel = vector(0, 0)
            self.acc = vector(0, 0)
            self.game = game
            self.direction = -1
            self.coins = 15

    def update(self):
        self.acc = vector(0, 2)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.acc.x = 1.5
            self.direction = -1
            if pygame.sprite.spritecollide(self, self.game.platforms, False):
                self.frame += 1

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.acc.x = -1.5
            self.direction = 1
            if pygame.sprite.spritecollide(self, self.game.platforms, False):
                self.frame += 1
        self.frame = self.frame % 6

        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            self.jump()

        self.image = load_image(f'run{self.frame}.png', -1)
        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
        
        self.acc.x += self.vel.x * (-0.2)
        self.vel += self.acc
        if not ((self.pos.x <= 200 and self.direction == 1) or (self.pos.x >= WIDTH - 200 and self.direction == -1)):
            self.pos.x += self.vel.x + 0.5 * self.acc.x
        else:
            for tile in self.game.platforms.sprites():
                newx = tile.rect.midbottom[0] - self.vel.x + 0.5 * self.acc.x
                tile.rect.midbottom = newx, tile.rect.midbottom[1]
            for particle in self.game.particles:
                newx = particle.pos[0] - self.vel.x + 0.5 * self.acc.x
                particle.pos = int(newx), particle.pos[1]
                if isinstance(particle, particles.Lightning):
                    newx = particle.pos2[0] - self.vel.x + 0.5 * self.acc.x
                    particle.pos2 = int(newx), particle.pos2[1]
        
        self.pos.y += self.vel.y + 5 * self.acc.y
        self.world_pos[1] += self.vel.y + 5 * self.acc.y
        if self.vel.y > 0:
            hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
            if hits:
                self.pos.y = hits[0].rect.top
                self.world_pos[1] = self.pos.y
                self.vel.y = 0
            self.hits = hits
        
        self.world_pos[0] += self.vel.x + 0.5 * self.acc.x
        
        self.world_pos = [int(i) for i in self.world_pos]
        self.rect.midbottom = self.pos
        self.image = pygame.transform.scale(self.image, ((55, 60)))

    def jump(self):
        self.rect.x += 1
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 1
        if hits:
            self.vel.y = -50
            self.game.particles.append(particles.Explosion(self.rect.midbottom, 100, 100, self.game.screen))
            self.game.particles.append(particles.Lightning(self.rect.midbottom, (0, 0), 100, self.game.screen))
            self.coins += 1
