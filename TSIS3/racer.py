import pygame
import random
import math

# Load images and sound
player_img = pygame.image.load("assets/Player.png")
enemy_img = pygame.image.load("assets/Enemy.png")
background_img = pygame.image.load("assets/AnimatedStreet.png")
crash_sound = None
try:
    crash_sound = pygame.mixer.Sound("assets/crash.wav")
except:
    pass

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Coin colors by weight
COIN_COLORS = {
    1: (255, 215, 0),   # gold
    2: (192, 192, 192), # silver
    3: (205, 127, 50)   # bronze
}

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)

    def move(self, dx):
        self.rect.x += dx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

class Enemy(pygame.sprite.Sprite):
    """Traffic car – avoid it!"""
    def __init__(self, speed):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-200, -50))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def reset(self):
        self.rect.y = random.randint(-200, -50)
        self.rect.x = random.randint(40, SCREEN_WIDTH - 40)

class Obstacle(pygame.sprite.Sprite):
    """Road obstacle (brown barrier, black oil, gray pothole). These will end the game if you hit them."""
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.type = random.choice(['barrier', 'oil', 'pothole'])
        if self.type == 'barrier':
            self.image.fill((139, 69, 19))   # brown
        elif self.type == 'oil':
            self.image.fill((0, 0, 0))       # black
        else:
            self.image.fill((105, 105, 105)) # gray pothole
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-300, -50))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def reset(self):
        self.rect.y = random.randint(-300, -50)
        self.rect.x = random.randint(40, SCREEN_WIDTH - 40)

class Coin(pygame.sprite.Sprite):
    """Weighted coin – collect for points!"""
    def __init__(self, speed):
        super().__init__()
        self.weight = random.randint(1, 3)
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COIN_COLORS[self.weight], (12, 12), 12)
        font = pygame.font.SysFont("Verdana", 12, bold=True)
        w_text = font.render(str(self.weight), True, BLACK)
        self.image.blit(w_text, (7, 4))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-200, -30))
        self.speed = speed // 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def reset(self):
        self.rect.y = random.randint(-200, -30)
        self.rect.x = random.randint(40, SCREEN_WIDTH - 40)
        self.weight = random.randint(1, 3)
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, COIN_COLORS[self.weight], (12, 12), 12)
        font = pygame.font.SysFont("Verdana", 12, bold=True)
        w_text = font.render(str(self.weight), True, BLACK)
        self.image.blit(w_text, (7, 4))

class PowerUp(pygame.sprite.Sprite):
    """Power‑up: Nitro (cyan N), Shield (blue S), Repair (yellow R). Collect them!"""
    TYPES = {
        'nitro': (0, 255, 255),
        'shield': (0, 0, 255),
        'repair': (255, 255, 0)
    }

    def __init__(self, speed):
        super().__init__()
        self.type = random.choice(list(self.TYPES.keys()))
        self.color = self.TYPES[self.type]
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (15, 15), 15)
        font = pygame.font.SysFont("Verdana", 14, bold=True)
        letter = font.render(self.type[0].upper(), True, BLACK)
        self.image.blit(letter, (8, 5))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-300, -50))
        self.speed = speed // 3
        self.timer = 0

    def update(self):
        self.rect.y += self.speed
        self.timer += 1
        if self.timer > 600:       # disappear after ~10 sec
            self.reset()
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def reset(self):
        self.rect.y = random.randint(-300, -50)
        self.rect.x = random.randint(40, SCREEN_WIDTH - 40)
        self.type = random.choice(list(self.TYPES.keys()))
        self.color = self.TYPES[self.type]
        self.timer = 0
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, self.color, (15, 15), 15)
        font = pygame.font.SysFont("Verdana", 14, bold=True)
        letter = font.render(self.type[0].upper(), True, BLACK)
        self.image.blit(letter, (8, 5))

class Game:
    def __init__(self, settings):
        self.settings = settings
        self.difficulty = settings.get('difficulty', 'normal')
        self.sound_on = settings.get('sound', True)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Racer - TSIS 3")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 20)

        self.score = 0
        self.distance = 0.0
        self.coin_score = 0
        self.coins_collected = 0
        self.goal_distance = 1000
        self.speed = 5
        self.base_speed = 5
        self.max_speed = 15
        self.active_powerup = None
        self.powerup_time_left = 0
        self.shield_active = False

        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        # Spawn 3 coins immediately so you see them right away
        for _ in range(3):
            c = Coin(self.speed)
            self.coins.add(c)
            self.all_sprites.add(c)

        # Timers
        self.enemy_timer = 0
        self.obstacle_timer = 0
        self.coin_timer = 0
        self.powerup_timer = 0

    def spawn_enemy(self):
        if len(self.enemies) < 3 + (self.difficulty == 'hard') * 3:
            e = Enemy(self.speed)
            while pygame.sprite.collide_rect(e, self.player) or pygame.sprite.spritecollideany(e, self.enemies):
                e.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-200, -50))
            self.enemies.add(e)
            self.all_sprites.add(e)

    def spawn_obstacle(self):
        if len(self.obstacles) < 2 + (self.difficulty == 'hard') * 2:
            o = Obstacle(self.speed)
            while pygame.sprite.collide_rect(o, self.player) or pygame.sprite.spritecollideany(o, self.obstacles):
                o.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-300, -50))
            self.obstacles.add(o)
            self.all_sprites.add(o)

    def spawn_coin(self):
        if len(self.coins) < 4:   # keep around 4 coins on screen
            c = Coin(self.speed)
            while pygame.sprite.collide_rect(c, self.player):
                c.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-200, -30))
            self.coins.add(c)
            self.all_sprites.add(c)

    def spawn_powerup(self):
        if len(self.powerups) == 0:   # only one power‑up at a time
            p = PowerUp(self.speed)
            while pygame.sprite.collide_rect(p, self.player):
                p.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-300, -50))
            self.powerups.add(p)
            self.all_sprites.add(p)

    def apply_powerup(self, powerup_type):
        if powerup_type == 'nitro':
            self.active_powerup = 'nitro'
            self.powerup_time_left = 180   # 3 seconds at 60fps
            self.speed = min(self.max_speed, self.base_speed + 5)
        elif powerup_type == 'shield':
            self.shield_active = True
        elif powerup_type == 'repair':
            zone_rect = pygame.Rect(self.player.rect.x - 50, self.player.rect.y - 200, 100, 200)
            for obs in list(self.obstacles):
                if zone_rect.colliderect(obs.rect):
                    obs.reset()
                    break
            else:
                for en in list(self.enemies):
                    if zone_rect.colliderect(en.rect):
                        en.reset()
                        break

    def handle_collisions(self):
        # Player vs enemy
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            if self.shield_active:
                self.shield_active = False
                for e in self.enemies:
                    if self.player.rect.colliderect(e.rect):
                        e.reset()
                return False
            else:
                if self.sound_on and crash_sound:
                    crash_sound.play()
                return True

        # Player vs obstacle
        hit_obs = pygame.sprite.spritecollide(self.player, self.obstacles, False)
        if hit_obs:
            if self.shield_active:
                self.shield_active = False
                for o in hit_obs:
                    o.reset()
                return False
            else:
                if self.sound_on and crash_sound:
                    crash_sound.play()
                return True

        # Player vs coin
        hit_coins = pygame.sprite.spritecollide(self.player, self.coins, False)
        for coin in hit_coins:
            self.coin_score += coin.weight
            self.coins_collected += 1
            self.score += coin.weight * 10
            coin.reset()

        # Player vs powerup
        hit_powers = pygame.sprite.spritecollide(self.player, self.powerups, False)
        for pup in hit_powers:
            if self.active_powerup is None or pup.type != self.active_powerup:
                self.apply_powerup(pup.type)
            pup.reset()

        return False

    def update_hud(self):
        lines = []
        lines.append(self.font.render(f"Score: {self.score}  Coins: {self.coin_score}", True, BLACK))
        lines.append(self.font.render(f"Distance: {int(self.distance)} / {self.goal_distance}", True, BLACK))
        if self.active_powerup == 'nitro':
            lines.append(self.font.render(f"NITRO: {self.powerup_time_left // 60}s", True, RED))
        if self.shield_active:
            lines.append(self.font.render("SHIELD ACTIVE", True, BLUE))
        return lines

    def run(self):
        running = True
        while running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Player movement
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT]:
                dx = -5
            if keys[pygame.K_RIGHT]:
                dx = 5
            self.player.move(dx)

            # Distance and scoring
            self.distance += self.speed * 0.1
            self.score = int(self.distance) + self.coin_score * 10

            # Difficulty scaling
            progress = self.distance / self.goal_distance
            if self.difficulty == 'easy':
                self.speed = self.base_speed + int(progress * 2)
            elif self.difficulty == 'normal':
                self.speed = self.base_speed + int(progress * 4)
            else:
                self.speed = self.base_speed + int(progress * 6)
            self.speed = min(self.max_speed, self.speed)

            # Nitro timer
            if self.active_powerup == 'nitro':
                self.powerup_time_left -= 1
                if self.powerup_time_left <= 0:
                    self.speed = min(self.max_speed, self.base_speed + int(progress * 4 if self.difficulty != 'hard' else progress * 6))
                    self.active_powerup = None

            # Spawn timers
            self.enemy_timer += 1
            if self.enemy_timer > max(30, 60 - int(progress * 20)):
                self.enemy_timer = 0
                self.spawn_enemy()

            self.obstacle_timer += 1
            if self.obstacle_timer > max(50, 90 - int(progress * 30)):
                self.obstacle_timer = 0
                self.spawn_obstacle()

            self.coin_timer += 1
            if self.coin_timer > 40:   # new coin roughly every 0.7 seconds
                self.coin_timer = 0
                self.spawn_coin()

            self.powerup_timer += 1
            if self.powerup_timer > 150:   # a power‑up appears roughly every 2.5 seconds
                self.powerup_timer = 0
                self.spawn_powerup()

            # Update all sprites
            for e in self.enemies:
                e.speed = self.speed
                e.update()
            for o in self.obstacles:
                o.speed = self.speed
                o.update()
            for c in self.coins:
                c.speed = self.speed // 2
                c.update()
            for p in self.powerups:
                p.speed = self.speed // 3
                p.update()

            # Collisions
            if self.handle_collisions():
                return {
                    'score': self.score,
                    'distance': int(self.distance),
                    'coins': self.coin_score
                }

            # Finish line
            if self.distance >= self.goal_distance:
                return {
                    'score': self.score + 100,
                    'distance': int(self.distance),
                    'coins': self.coin_score
                }

            # Draw everything
            self.screen.blit(background_img, (0, 0))
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)

            # Draw HUD
            y = 10
            for line in self.update_hud():
                self.screen.blit(line, (10, y))
                y += 25

            pygame.display.flip()

        return None