import pygame
import random
import particles
import math
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


class MeleeEnemy(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('enemy1.png', -1)
        self.rect = self.image.get_rect()
        self.rect.center = (10, 10)
        self.angle = 0
        self.game = game
        self.game.all_sprites.add(self)
        self.game.enemies_mel.add(self)

    def update(self):
        n1 = random.randint(-2, 2)
        n2 = random.randint(-2, 2)

        player_pos = self.game.player.rect.center
        
        delta_x = player_pos[0] - self.rect.center[0]
        delta_y = player_pos[1] - self.rect.center[1]

        if delta_x != 0:
            n1 += delta_x // abs(delta_x)
        if delta_y != 0:
            n2 += delta_y // abs(delta_y)
        
        cr = (self.rect.center[0] + n1, self.rect.center[1] + n2)
        
        self.angle = 45 - int(math.atan2(delta_y, delta_x) * 180 / math.pi)
        self.image = load_image('enemy1.png', -1)
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = cr


class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, start_pos, end_pos):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.hyp = 0
        self.image = load_image('bullet.png', -1)
        self.dx = end_pos[0] - start_pos[0]
        self.dy = end_pos[1] - start_pos[1]
        self.angle = 180 - int(math.atan2(self.dy, self.dx) * 180 / math.pi)
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = start_pos
        self.game.all_sprites.add(self)
        self.game.platforms.add(self)
        self.start = (start_pos[0], start_pos[1])
        self.end = end_pos

    def update(self):
        if self.rect.center == self.end:
            self.game.particles.append(particles.Explosion(self.rect.center, 10, 10, self.game.screen))
            self.kill()
        else:
            self.hyp += 5
            x = - int(self.hyp * math.cos(self.angle))
            y = - int(self.hyp * math.sin(self.angle))
            self.rect.center = x + self.start[0], self.start[1] - y


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
        self.health = 100
        self.maxHealth = 100
        self.dead = False

    def update(self):
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if not hits:
            self.acc.y = 2
        else:
            self.acc.y = 0
            self.vel.y = 0
            self.pos.y = hits[0].rect.top + 2
            self.world_pos[1] = self.pos.y + 2
        self.acc.x = 0
        
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

        
        self.acc.x += self.vel.x * (-0.25)
        self.vel += self.acc
        self.world_pos[0] += self.vel.x + 0.5 * self.acc.x
        if not ((self.pos.x <= 200 and self.direction == 1) or (self.pos.x >= WIDTH - 200 and self.direction == -1)):
            self.pos.x += self.vel.x + 0.5 * self.acc.x
        else:
            for tile in self.game.platforms.sprites():
                newx = tile.rect.midbottom[0] - self.vel.x - 0.5 * self.acc.x
                tile.rect.midbottom = newx, tile.rect.midbottom[1]

            for tile in self.game.enemies_mel.sprites():
                newx = tile.rect.midbottom[0] - self.vel.x - 0.5 * self.acc.x
                tile.rect.midbottom = newx, tile.rect.midbottom[1]

            for particle in self.game.particles:
                newx = particle.pos[0] - self.vel.x - 0.5 * self.acc.x
                particle.pos = int(newx), particle.pos[1]
                if isinstance(particle, particles.Lightning):
                    newx = particle.pos2[0] - self.vel.x - 0.5 * self.acc.x
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
        
        enhits = pygame.sprite.spritecollide(self, self.game.enemies_mel, False)
        if enhits:
            self.health -= 10
            self.game.particles.append(particles.Explosion(enhits[0].rect.center, 100, 100, self.game.screen))
            enhits[0].kill()
            en = MeleeEnemy(self.game)
        
        self.world_pos = [int(i) for i in self.world_pos]
        
        if self.pos.y >= HEIGHT + 60:
            self.health -= 5
            self.pos.y = - 120
        
        self.rect.midbottom = self.pos
        self.image = pygame.transform.scale(self.image, ((55, 60)))
        if self.health > self.maxHealth:
            self.health = self.maxHealth
        if self.health <= 0:
            if not self.dead:
                self.dead = True
            self.health = 0
        self.image = load_image(f'run{self.frame}.png', -1)
        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)

    def jump(self):
        self.rect.x += 1
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 1
        if hits:
            pygame.mixer.Sound('data/jump-sound.wav').play()
            self.vel.y = -50

    def shoot(self, pos):
        b = Bullet(self.game, self.pos, pos)