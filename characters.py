import pygame
import random
import particles
import math
import sys
import os

vector = pygame.math.Vector2
MORTAL = True
FPS = 60
WIDTH = 800
HEIGHT = 600
CLASSES = {'warrior': [100, 25, 15, 1.5, 1.5],
           'magician': [70, 50, 50, 1, 1.2],
           'dev': [400, 100, 1000, 3, 4]}

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
        self.rect.center = (random.choice([10, WIDTH - 10]), random.choice([10, HEIGHT - 10]))
        self.angle = 0
        self.game = game
        self.game.all_sprites.add(self)
        self.game.enemies_mel.add(self)

    def update(self):
        n1 = 1 + random.uniform(-0.2, 0.2)
        n2 = 1 + random.uniform(-0.2, 0.2)

        player_pos = self.game.player.rect.center
        
        delta_x = player_pos[0] - self.rect.center[0]
        delta_y = player_pos[1] - self.rect.center[1]

        if delta_x != 0:
            n1 *= self.game.lvl * delta_x // abs(delta_x)
        if delta_y != 0:
            n2 *= self.game.lvl * delta_y // abs(delta_y)
        
        cr = (self.rect.center[0] + n1, self.rect.center[1] + n2)
        
        self.angle = 45 - int(math.atan2(delta_y, delta_x) * 180 / math.pi)
        self.image = load_image('enemy1.png', -1)
        
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = cr
        hitts = pygame.sprite.spritecollide(self, self.game.bullets, False)
        if hitts:
            self.game.particles.append(particles.Explosion(self.rect.center, 10, 10, self.game.screen))
            for i in range(2):
                en = MeleeEnemy(self.game)
            self.game.player.coins += 10
            self.game.lvl += 1
            hitts[0].kill()
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, start_pos, end_pos):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.hyp = 0
        self.image = load_image('bullet.png', -1)
        self.dx = end_pos[0] - start_pos[0]
        self.dy = end_pos[1] - start_pos[1]
        self.angle = int(math.atan2(self.dy, self.dx) * 180 / math.pi)
        self.image = pygame.transform.rotate(self.image, - self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = start_pos
        self.game.all_sprites.add(self)
        self.game.platforms.add(self)
        self.game.bullets.add(self)
        self.start = (start_pos[0], start_pos[1])
        self.end = end_pos

    def update(self):
        if not ((0 <= self.rect.center[0] <= WIDTH) and (0 <= self.rect.center[1] <= HEIGHT)):
            self.game.particles.append(particles.Explosion(self.rect.center, 10, 10, self.game.screen))
            self.kill()
        else:
            self.hyp += 1
            x = int(self.hyp * self.dx / 20)#- (self.hyp * math.cos(self.angle))
            y = int(self.hyp * self.dy / 20)#- (self.hyp * math.sin(self.angle))
            self.rect.center = x + self.start[0], self.start[1] + y


class Character(pygame.sprite.Sprite):
    def __init__(self, game, character_class):
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
        self.clas = character_class
        self.coins = CLASSES[self.clas][2]
        self.maxHealth = CLASSES[self.clas][0]
        self.health = self.maxHealth
        self.dmg = CLASSES[self.clas][1]
        self.walk = CLASSES[self.clas][3]
        self.sprint = CLASSES[self.clas][4]
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
            self.acc.x = self.walk
            self.direction = -1
            if pygame.sprite.spritecollide(self, self.game.platforms, False):
                self.frame += 1

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.acc.x = - self.walk
            self.direction = 1
            if pygame.sprite.spritecollide(self, self.game.platforms, False):
                self.frame += 1

        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            self.jump()
        
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.acc.x *= self.sprint
            self.acc.y /= self.sprint
            self.frame += 1
        self.frame = self.frame % 6
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
            en = MeleeEnemy(self.game)
            enhits[0].kill()
        
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
                self.dead = MORTAL
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