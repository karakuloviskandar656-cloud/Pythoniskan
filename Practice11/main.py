import pygame, sys, random, time
from pygame.locals import *

# Initialise pygame
pygame.init()

# Frames per second
FPS = 60
FramePerSec = pygame.time.Clock()

# Colours
RED   = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
# Coin colours by weight
COIN_COLORS = {
    1: (218, 165, 32),   # gold
    2: (192, 192, 192),  # silver
    3: (205, 127, 50)    # bronze
}

# Screen settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COIN_SCORE = 0
COINS_COLLECTED = 0    # total coins picked up (used for speed increase)
SPEED_INCREASE_EVERY = 5  # increase enemy speed after this many coins

# Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Load background and images
background = pygame.image.load("AnimatedStreet.png")
player_img = pygame.image.load("Player.png")
enemy_img = pygame.image.load("Enemy.png")

# Create display
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer with Weighted Coins")

# ---------- Player class ----------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

# ---------- Enemy class ----------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

# ---------- Coin class (weighted) ----------
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # randomly assign weight 1, 2 or 3
        self.weight = random.randint(1, 3)
        # draw a circle with the appropriate color
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COIN_COLORS[self.weight], (15, 15), 15)
        # optionally add a small number to show weight
        weight_font = pygame.font.SysFont("Verdana", 14, bold=True)
        weight_text = weight_font.render(str(self.weight), True, BLACK)
        self.image.blit(weight_text, (10, 6))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        self.rect.move_ip(0, SPEED // 2)  # coins fall slower than enemies
        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position()

    def reset_position(self):
        self.rect.top = 0
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)
        # also give a new random weight
        self.weight = random.randint(1, 3)
        # redraw the circle with new color
        self.image.fill((0,0,0,0))  # clear alpha
        pygame.draw.circle(self.image, COIN_COLORS[self.weight], (15, 15), 15)
        weight_font = pygame.font.SysFont("Verdana", 14, bold=True)
        weight_text = weight_font.render(str(self.weight), True, BLACK)
        self.image.blit(weight_text, (10, 6))

# ---------- Setup sprites ----------
P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies = pygame.sprite.Group()
enemies.add(E1)
coins = pygame.sprite.Group()
coins.add(C1)
all_sprites = pygame.sprite.Group()
all_sprites.add(P1, E1, C1)

# Speed increase event (increases enemy speed gradually over time)
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# ---------- Game loop ----------
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw background
    DISPLAYSURF.blit(background, (0, 0))

    # Show scores and stats
    scores_text = font_small.render(f"Score: {SCORE}", True, BLACK)
    coin_text = font_small.render(f"Coins: {COIN_SCORE} (next speed at {SPEED_INCREASE_EVERY - (COINS_COLLECTED % SPEED_INCREASE_EVERY)} more)", True, BLACK)
    speed_text = font_small.render(f"Enemy speed: {SPEED:.1f}", True, BLACK)
    DISPLAYSURF.blit(scores_text, (10, 10))
    DISPLAYSURF.blit(coin_text, (10, 35))
    DISPLAYSURF.blit(speed_text, (10, 60))

    # Move and redraw all sprites
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Collision: Player vs Enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound('crash.wav').play()
        time.sleep(0.5)
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()
        for entity in all_sprites:
            entity.kill()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    # Collision: Player vs Coin
    if pygame.sprite.spritecollideany(P1, coins):
        COIN_SCORE += C1.weight          # add weight to coin score
        COINS_COLLECTED += 1
        # Increase enemy speed after every SPEED_INCREASE_EVERY coins
        if COINS_COLLECTED % SPEED_INCREASE_EVERY == 0:
            SPEED += 2   # permanent speed boost for enemy
        C1.reset_position()

    pygame.display.update()
    FramePerSec.tick(FPS)