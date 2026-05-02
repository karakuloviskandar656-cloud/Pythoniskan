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
RED   = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE  = (50, 100, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 165, 0)
CYAN  = (0, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (128, 128, 128)
DARK_GRAY = (80, 80, 80)

# Coin colors by weight
COIN_COLORS = {
    1: (255, 215, 0),   # gold
    2: (192, 192, 192), # silver
    3: (205, 127, 50)   # bronze
}

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

class Particle:
    """Simple particle effect for explosions and power-ups."""
    def __init__(self, x, y, color, speed, size):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-speed, speed)
        self.vy = random.uniform(-speed, speed)
        self.size = size
        self.life = 255
        self.decay = random.randint(3, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size = max(0, self.size - 0.2)

    def draw(self, screen):
        if self.life > 0 and self.size > 0:
            surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, self.life), (int(self.size), int(self.size)), int(self.size))
            screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

    def is_alive(self):
        return self.life > 0

class Road:
    """Scrolling road with lane markings."""
    def __init__(self):
        self.offset = 0
        self.lane_width = SCREEN_WIDTH // 3

    def update(self, speed):
        self.offset = (self.offset + speed) % 80

    def draw(self, screen):
        # Asphalt
        screen.fill(DARK_GRAY)

        # Side lines
        pygame.draw.rect(screen, WHITE, (0, 0, 8, SCREEN_HEIGHT))
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - 8, 0, 8, SCREEN_HEIGHT))

        # Lane markings
        for y in range(-80, SCREEN_HEIGHT, 80):
            draw_y = y + self.offset
            if 0 <= draw_y < SCREEN_HEIGHT:
                # Center line
                pygame.draw.rect(screen, YELLOW, (SCREEN_WIDTH//2 - 3, draw_y, 6, 40))
                # Side lane markings
                pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//3 - 2, draw_y, 4, 30))
                pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH*2//3 - 2, draw_y, 4, 30))

class Player(pygame.sprite.Sprite):
    def __init__(self, car_color="red"):
        super().__init__()
        self.base_image = player_img.copy()
        self.apply_car_color(car_color)
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.tilt = 0

    def apply_car_color(self, color_name):
        color_map = {
            "red": (255, 50, 50),
            "blue": (50, 100, 255),
            "green": (50, 255, 50),
            "yellow": (255, 255, 50)
        }
        target_color = color_map.get(color_name, (255, 50, 50))

        # Simple color replacement for the car body
        for x in range(self.base_image.get_width()):
            for y in range(self.base_image.get_height()):
                pixel = self.base_image.get_at((x, y))
                # If pixel is close to red (original car color), replace it
                if pixel.r > 150 and pixel.g < 100 and pixel.b < 100:
                    ratio = pixel.r / 255.0
                    new_r = min(255, int(target_color[0] * ratio + 50))
                    new_g = min(255, int(target_color[1] * ratio + 50))
                    new_b = min(255, int(target_color[2] * ratio + 50))
                    self.base_image.set_at((x, y), (new_r, new_g, new_b, pixel.a))

    def move(self, dx):
        self.rect.x += dx
        # Tilt effect when turning
        if dx < 0:
            self.tilt = min(15, self.tilt + 2)
        elif dx > 0:
            self.tilt = max(-15, self.tilt - 2)
        else:
            self.tilt = self.tilt * 0.8

        if self.rect.left < 10:
            self.rect.left = 10
        if self.rect.right > SCREEN_WIDTH - 10:
            self.rect.right = SCREEN_WIDTH - 10

        # Apply rotation for tilt effect
        if abs(self.tilt) > 1:
            self.image = pygame.transform.rotate(self.base_image, self.tilt)
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.image = self.base_image

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-200, -50))
        self.speed = speed
        self.wobble = random.uniform(-1, 1)

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.wobble
        if abs(self.wobble) > 2:
            self.wobble *= -0.5
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def reset(self):
        self.rect.y = random.randint(-200, -50)
        self.rect.x = random.randint(40, SCREEN_WIDTH - 40)
        self.wobble = random.uniform(-1, 1)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.type = random.choice(['barrier', 'oil', 'pothole'])
        if self.type == 'barrier':
            self.image = pygame.Surface((35, 25))
            self.image.fill((139, 69, 19))
            pygame.draw.rect(self.image, (100, 50, 10), (0, 0, 35, 5))
            pygame.draw.rect(self.image, (100, 50, 10), (0, 20, 35, 5))
        elif self.type == 'oil':
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (0, 0, 0, 200), (0, 0, 30, 30))
            pygame.draw.ellipse(self.image, (20, 20, 20, 150), (5, 5, 20, 20))
        else:
            self.image = pygame.Surface((25, 20))
            self.image.fill((105, 105, 105))
            pygame.draw.circle(self.image, (80, 80, 80), (12, 10), 8)
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
    def __init__(self, speed):
        super().__init__()
        self.weight = random.randint(1, 3)
        self.angle = 0
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.draw_coin()
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-200, -30))
        self.speed = speed // 2

    def draw_coin(self):
        self.image.fill((0,0,0,0))
        color = COIN_COLORS[self.weight]
        # Outer ring
        pygame.draw.circle(self.image, (255, 255, 200), (15, 15), 14)
        pygame.draw.circle(self.image, color, (15, 15), 12)
        pygame.draw.circle(self.image, (255, 255, 255, 100), (12, 12), 5)
        font = pygame.font.SysFont("Arial", 14, bold=True)
        w_text = font.render(str(self.weight), True, BLACK)
        self.image.blit(w_text, (10, 8))

    def update(self):
        self.rect.y += self.speed
        self.angle += 2
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def reset(self):
        self.rect.y = random.randint(-200, -30)
        self.rect.x = random.randint(40, SCREEN_WIDTH - 40)
        self.weight = random.randint(1, 3)
        self.draw_coin()

class PowerUp(pygame.sprite.Sprite):
    TYPES = {
        'nitro': (CYAN, 'N'),
        'shield': (BLUE, 'S'),
        'repair': (YELLOW, 'R')
    }

    def __init__(self, speed):
        super().__init__()
        self.type = random.choice(list(self.TYPES.keys()))
        self.color, self.letter = self.TYPES[self.type]
        self.image = pygame.Surface((35, 35), pygame.SRCALPHA)
        self.draw_powerup()
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-300, -50))
        self.speed = speed // 3
        self.pulse = 0

    def draw_powerup(self):
        self.image.fill((0,0,0,0))
        # Glow
        glow_surf = pygame.Surface((35, 35), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 100), (17, 17), 17)
        self.image.blit(glow_surf, (0, 0))
        # Main circle
        pygame.draw.circle(self.image, self.color, (17, 17), 14)
        pygame.draw.circle(self.image, WHITE, (17, 17), 14, 2)
        # Letter
        font = pygame.font.SysFont("Arial", 16, bold=True)
        letter = font.render(self.letter, True, BLACK)
        self.image.blit(letter, (12, 8))

    def update(self):
        self.rect.y += self.speed
        self.pulse += 0.1
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def reset(self):
        self.rect.y = random.randint(-300, -50)
        self.rect.x = random.randint(40, SCREEN_WIDTH - 40)
        self.type = random.choice(list(self.TYPES.keys()))
        self.color, self.letter = self.TYPES[self.type]
        self.draw_powerup()

class Game:
    def __init__(self, settings):
        self.settings = settings
        self.difficulty = settings.get('difficulty', 'normal')
        self.sound_on = settings.get('sound', True)
        self.car_color = settings.get('car_color', 'red')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Racer - TSIS 3")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.road = Road()

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

        self.particles = []

        self.player = Player(self.car_color)
        self.enemies = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        for _ in range(3):
            c = Coin(self.speed)
            self.coins.add(c)
            self.all_sprites.add(c)

        self.enemy_timer = 0
        self.obstacle_timer = 0
        self.coin_timer = 0
        self.powerup_timer = 0

        self.music_loaded = False
        if self.sound_on:
            try:
                pygame.mixer.music.load("assets/background.wav")
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
                self.music_loaded = True
            except:
                pass

    def spawn_enemy(self):
        max_enemies = {'easy': 2, 'normal': 3, 'hard': 4}
        if len(self.enemies) < max_enemies.get(self.difficulty, 3):
            e = Enemy(self.speed)
            while pygame.sprite.collide_rect(e, self.player) or pygame.sprite.spritecollideany(e, self.enemies):
                e.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-200, -50))
            self.enemies.add(e)
            self.all_sprites.add(e)

    def spawn_obstacle(self):
        max_obs = {'easy': 1, 'normal': 2, 'hard': 3}
        if len(self.obstacles) < max_obs.get(self.difficulty, 2):
            o = Obstacle(self.speed)
            while pygame.sprite.collide_rect(o, self.player) or pygame.sprite.spritecollideany(o, self.obstacles):
                o.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-300, -50))
            self.obstacles.add(o)
            self.all_sprites.add(o)

    def spawn_coin(self):
        if len(self.coins) < 4:
            c = Coin(self.speed)
            while pygame.sprite.collide_rect(c, self.player):
                c.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-200, -30))
            self.coins.add(c)
            self.all_sprites.add(c)

    def spawn_powerup(self):
        if len(self.powerups) == 0:
            p = PowerUp(self.speed)
            while pygame.sprite.collide_rect(p, self.player):
                p.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-300, -50))
            self.powerups.add(p)
            self.all_sprites.add(p)

    def add_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, 3, random.randint(3, 8)))

    def apply_powerup(self, ptype):
        if ptype == 'nitro':
            self.active_powerup = 'nitro'
            self.powerup_time_left = 180
            self.speed = min(self.max_speed, self.base_speed + 5)
            self.add_particles(self.player.rect.centerx, self.player.rect.centery, CYAN, 20)
        elif ptype == 'shield':
            self.shield_active = True
            self.add_particles(self.player.rect.centerx, self.player.rect.centery, BLUE, 15)
        elif ptype == 'repair':
            self.add_particles(self.player.rect.centerx, self.player.rect.centery, YELLOW, 15)
            zone = pygame.Rect(self.player.rect.x - 50, self.player.rect.y - 200, 100, 200)
            for obs in list(self.obstacles):
                if zone.colliderect(obs.rect):
                    obs.reset()
                    break
            else:
                for en in list(self.enemies):
                    if zone.colliderect(en.rect):
                        en.reset()
                        break

    def handle_collisions(self):
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            if self.shield_active:
                self.shield_active = False
                for e in self.enemies:
                    if self.player.rect.colliderect(e.rect):
                        self.add_particles(e.rect.centerx, e.rect.centery, RED, 15)
                        e.reset()
                return False
            else:
                if self.sound_on and crash_sound:
                    crash_sound.play()
                self.add_particles(self.player.rect.centerx, self.player.rect.centery, RED, 30)
                return True

        hit_obs = pygame.sprite.spritecollide(self.player, self.obstacles, False)
        if hit_obs:
            if self.shield_active:
                self.shield_active = False
                for o in hit_obs:
                    self.add_particles(o.rect.centerx, o.rect.centery, ORANGE, 10)
                    o.reset()
                return False
            else:
                if self.sound_on and crash_sound:
                    crash_sound.play()
                self.add_particles(self.player.rect.centerx, self.player.rect.centery, RED, 30)
                return True

        for coin in pygame.sprite.spritecollide(self.player, self.coins, False):
            self.coin_score += coin.weight
            self.coins_collected += 1
            self.score += coin.weight * 10
            self.add_particles(coin.rect.centerx, coin.rect.centery, COIN_COLORS[coin.weight], 10)
            coin.reset()

        for pup in pygame.sprite.spritecollide(self.player, self.powerups, False):
            if self.active_powerup is None or pup.type != self.active_powerup:
                self.apply_powerup(pup.type)
            pup.reset()

        return False

    def update_hud(self):
        lines = []
        lines.append((self.font.render(f"Score: {self.score}", True, WHITE), 10))
        lines.append((self.font.render(f"Coins: {self.coin_score}", True, YELLOW), 35))
        lines.append((self.font.render(f"Dist: {int(self.distance)}m", True, GREEN), 60))
        if self.active_powerup == 'nitro':
            lines.append((self.font.render(f"NITRO: {self.powerup_time_left // 60}s", True, CYAN), 85))
        if self.shield_active:
            lines.append((self.font.render("SHIELD ON", True, BLUE), 85 if self.active_powerup != 'nitro' else 110))
        return lines

    def run(self):
        running = True
        while running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT]:
                dx = -5
            if keys[pygame.K_RIGHT]:
                dx = 5
            self.player.move(dx)

            self.distance += self.speed * 0.1
            self.score = int(self.distance) + self.coin_score * 10

            progress = self.distance / self.goal_distance
            if self.difficulty == 'easy':
                self.speed = self.base_speed + int(progress * 1.5)
            elif self.difficulty == 'normal':
                self.speed = self.base_speed + int(progress * 3)
            else:
                self.speed = self.base_speed + int(progress * 5)
            self.speed = min(self.max_speed, self.speed)

            if self.active_powerup == 'nitro':
                self.powerup_time_left -= 1
                if self.powerup_time_left <= 0:
                    if self.difficulty == 'easy':
                        self.speed = self.base_speed + int(progress * 1.5)
                    elif self.difficulty == 'normal':
                        self.speed = self.base_speed + int(progress * 3)
                    else:
                        self.speed = self.base_speed + int(progress * 5)
                    self.speed = min(self.max_speed, self.speed)
                    self.active_powerup = None

            enemy_delays = {'easy': 80, 'normal': 60, 'hard': 40}
            obstacle_delays = {'easy': 100, 'normal': 70, 'hard': 50}
            self.enemy_timer += 1
            if self.enemy_timer > enemy_delays.get(self.difficulty, 60):
                self.enemy_timer = 0
                self.spawn_enemy()

            self.obstacle_timer += 1
            if self.obstacle_timer > obstacle_delays.get(self.difficulty, 70):
                self.obstacle_timer = 0
                self.spawn_obstacle()

            self.coin_timer += 1
            if self.coin_timer > 40:
                self.coin_timer = 0
                self.spawn_coin()

            self.powerup_timer += 1
            if self.powerup_timer > 180:
                self.powerup_timer = 0
                self.spawn_powerup()

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

            # Update particles
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.is_alive()]

            if self.handle_collisions():
                if self.music_loaded:
                    pygame.mixer.music.stop()
                return {
                    'score': self.score,
                    'distance': int(self.distance),
                    'coins': self.coin_score
                }

            if self.distance >= self.goal_distance:
                if self.music_loaded:
                    pygame.mixer.music.stop()
                return {
                    'score': self.score + 100,
                    'distance': int(self.distance),
                    'coins': self.coin_score
                }

            # Draw
            self.road.update(self.speed)
            self.road.draw(self.screen)

            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)

            # Draw shield effect
            if self.shield_active:
                shield_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(shield_surf, (0, 100, 255, 100), (30, 30), 30)
                pygame.draw.circle(shield_surf, (100, 200, 255, 150), (30, 30), 30, 3)
                self.screen.blit(shield_surf, 
                    (self.player.rect.centerx - 30, self.player.rect.centery - 30))

            # Draw particles
            for p in self.particles:
                p.draw(self.screen)

            # HUD background
            hud_bg = pygame.Surface((200, 120), pygame.SRCALPHA)
            hud_bg.fill((0, 0, 0, 100))
            self.screen.blit(hud_bg, (5, 5))

            # HUD text
            for line, y in self.update_hud():
                self.screen.blit(line, (10, y))

            # Progress bar
            bar_width = 200
            bar_height = 10
            progress = min(1.0, self.distance / self.goal_distance)
            pygame.draw.rect(self.screen, GRAY, (5, SCREEN_HEIGHT - 20, bar_width, bar_height))
            pygame.draw.rect(self.screen, GREEN, (5, SCREEN_HEIGHT - 20, int(bar_width * progress), bar_height))
            pygame.draw.rect(self.screen, WHITE, (5, SCREEN_HEIGHT - 20, bar_width, bar_height), 1)

            pygame.display.flip()

        return None
