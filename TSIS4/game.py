import pygame
import sys
import random
import json
import os
import math

# ---------- Safe database import ----------
try:
    from db import get_top_leaderboard, save_game_session, get_personal_best, get_or_create_player
    DB_AVAILABLE = True
except Exception as e:
    print(f"DB not available: {e}")
    DB_AVAILABLE = False

# ---------- Safe sound initialization ----------
SOUND_AVAILABLE = False
try:
    pygame.mixer.init(frequency=44100, size=-8, channels=1, buffer=512)
    SOUND_AVAILABLE = True
except:
    pass

def generate_sound(frequency, duration, volume=0.3):
    """Generate a simple beep sound."""
    if not SOUND_AVAILABLE:
        return None
    try:
        sample_rate = 44100
        samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(samples):
            t = i / sample_rate
            decay = max(0, 1 - (i / samples))
            value = int(127 + 127 * math.sin(2 * math.pi * frequency * t) * decay * volume)
            buf.append(value)
        return pygame.mixer.Sound(buffer=bytes(buf))
    except:
        return None

# Pre-generate sounds
eat_sound = generate_sound(800, 0.1, 0.3)
crash_sound = generate_sound(200, 0.3, 0.5)
powerup_sound = generate_sound(1200, 0.15, 0.4)
levelup_sound = generate_sound(600, 0.2, 0.3)

def play_sound(sound):
    """Safely play a sound if available."""
    if SOUND_AVAILABLE and sound:
        try:
            sound.play()
        except:
            pass

# ---------- Settings persistence ----------
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "snake_color": [0, 255, 0],
    "grid_on": True,
    "sound_on": True
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

# ---------- Initialize Pygame ----------
pygame.init()
WIDTH, HEIGHT = 600, 400
CELL = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 4 - Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)
small_font = pygame.font.SysFont("Arial", 14, bold=True)
big_font = pygame.font.SysFont("Arial", 40, bold=True)
title_font = pygame.font.SysFont("Arial", 50, bold=True)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE  = (50, 100, 255)
GRAY  = (120, 120, 120)
DARK_RED = (139, 0, 0)
CYAN  = (0, 255, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 165, 0)
PURPLE = (150, 50, 255)
DARK_BG = (20, 20, 30)
LIGHT_BG = (240, 240, 240)

# Directions
UP    = (0, -1)
DOWN  = (0, 1)
LEFT  = (-1, 0)
RIGHT = (1, 0)

# ---------- Particle effects ----------
class Particle:
    def __init__(self, x, y, color, speed=3, size=5):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-speed, speed)
        self.vy = random.uniform(-speed, speed)
        self.size = size
        self.life = 255
        self.decay = random.randint(5, 10)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size = max(0, self.size - 0.3)

    def draw(self, screen):
        if self.life > 0 and self.size > 0:
            surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, self.life), (int(self.size), int(self.size)), int(self.size))
            screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

    def is_alive(self):
        return self.life > 0

# ---------- Gradient & visual helpers ----------
def draw_gradient(screen, color1, color2, width, height):
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

class Button:
    """Modern button with hover and animation."""
    def __init__(self, x, y, w, h, text, color=(100,100,100), hover_color=(150,150,150), text_color=WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.scale = 1.0
        self.target_scale = 1.0

    def update(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        self.target_scale = 1.05 if self.hovered else 1.0
        self.scale += (self.target_scale - self.scale) * 0.2

    def draw(self, screen):
        scaled_w = int(self.rect.width * self.scale)
        scaled_h = int(self.rect.height * self.scale)
        scaled_x = self.rect.centerx - scaled_w // 2
        scaled_y = self.rect.centery - scaled_h // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_w, scaled_h)

        color = self.hover_color if self.hovered else self.color

        # Shadow
        shadow = scaled_rect.copy()
        shadow.move_ip(3, 3)
        pygame.draw.rect(screen, (0,0,0,100), shadow, border_radius=12)

        # Button
        pygame.draw.rect(screen, color, scaled_rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, scaled_rect, 2, border_radius=12)

        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# ---------- Food helpers ----------
FOOD_COLORS = {
    1: (255, 215, 0),
    2: (255, 165, 0),
    3: (255, 50, 50)
}

def get_random_food(snake_body, obstacles):
    while True:
        pos = (random.randint(0, (WIDTH//CELL)-1),
               random.randint(0, (HEIGHT//CELL)-1))
        if pos not in snake_body and pos not in obstacles:
            weight = random.randint(1, 3)
            return pos, weight

def get_random_poison(snake_body, obstacles, normal_food_pos):
    while True:
        pos = (random.randint(0, (WIDTH//CELL)-1),
               random.randint(0, (HEIGHT//CELL)-1))
        if pos not in snake_body and pos not in obstacles and pos != normal_food_pos:
            return pos

def get_random_obstacles(snake_body, food_pos, poison_pos, count):
    obs = set()
    while len(obs) < count:
        pos = (random.randint(0, (WIDTH//CELL)-1),
               random.randint(0, (HEIGHT//CELL)-1))
        if pos not in snake_body and pos != food_pos and pos != poison_pos and pos not in obs:
            head = snake_body[0]
            neighbors = [(head[0]+dx, head[1]+dy) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]]
            if all(n in obs for n in neighbors):
                continue
            obs.add(pos)
    return list(obs)

# ---------- Screens ----------
def input_username_screen():
    name = ""
    cursor_visible = True
    cursor_timer = 0

    while True:
        draw_gradient(screen, (20, 20, 30), (40, 40, 60), WIDTH, HEIGHT)

        title = title_font.render("PLAYER NAME", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        prompt = font.render("Enter your username:", True, (200, 200, 200))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 160))

        # Input box
        box_rect = pygame.Rect(WIDTH//2 - 120, 210, 240, 45)
        pygame.draw.rect(screen, WHITE, box_rect, border_radius=8)
        pygame.draw.rect(screen, CYAN, box_rect, 3, border_radius=8)

        name_surf = font.render(name, True, BLACK)
        screen.blit(name_surf, (box_rect.x + 10, box_rect.y + 10))

        # Blinking cursor
        cursor_timer += 1
        if cursor_timer % 30 < 15:
            cursor_x = box_rect.x + 15 + name_surf.get_width()
            pygame.draw.line(screen, BLACK, (cursor_x, box_rect.y + 10), (cursor_x, box_rect.y + 35), 2)

        ok_btn = Button(WIDTH//2 - 60, 290, 120, 45, "START", (50, 150, 50), (80, 200, 80))
        mouse_pos = pygame.mouse.get_pos()
        ok_btn.update(mouse_pos)
        ok_btn.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_btn.is_clicked(event.pos) and name.strip():
                    return name.strip()
        clock.tick(60)

def settings_screen(settings):
    current = settings.copy()
    snake_color = current["snake_color"][:]
    grid_on = current["grid_on"]
    sound_on = current["sound_on"]

    color_cycle = [[0,255,0], [255,0,0], [0,0,255], [255,255,0], [0,255,255], [255,0,255]]

    back_btn = Button(WIDTH//2 - 60, 340, 120, 45, "BACK", (100,100,100), (150,150,150))

    while True:
        draw_gradient(screen, (20, 20, 30), (40, 40, 60), WIDTH, HEIGHT)

        title = title_font.render("SETTINGS", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        sound_btn = Button(50, 120, 240, 50, 
                          f"Sound: {'ON' if sound_on else 'OFF'}",
                          (50, 150, 50) if sound_on else (150, 50, 50),
                          (80, 200, 80) if sound_on else (200, 80, 80))

        color_map = {"[0, 255, 0]": "Green", "[255, 0, 0]": "Red", "[0, 0, 255]": "Blue",
                     "[255, 255, 0]": "Yellow", "[0, 255, 255]": "Cyan", "[255, 0, 255]": "Purple"}
        color_name = color_map.get(str(snake_color), "Custom")
        color_btn = Button(50, 200, 240, 50, f"Color: {color_name}", (50, 100, 150), (80, 140, 200))

        grid_btn = Button(50, 280, 240, 50,
                         f"Grid: {'ON' if grid_on else 'OFF'}",
                         (150, 150, 50) if grid_on else (100, 100, 100),
                         (200, 200, 80) if grid_on else (150, 150, 150))

        preview_rect = pygame.Rect(320, 205, 40, 40)
        pygame.draw.rect(screen, tuple(snake_color), preview_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, preview_rect, 2, border_radius=5)

        mouse_pos = pygame.mouse.get_pos()
        for btn in [sound_btn, color_btn, grid_btn, back_btn]:
            btn.update(mouse_pos)
            btn.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if sound_btn.is_clicked(pos):
                    sound_on = not sound_on
                elif color_btn.is_clicked(pos):
                    idx = color_cycle.index(snake_color) if snake_color in color_cycle else 0
                    snake_color = color_cycle[(idx+1) % len(color_cycle)]
                elif grid_btn.is_clicked(pos):
                    grid_on = not grid_on
                elif back_btn.is_clicked(pos):
                    current["snake_color"] = snake_color
                    current["grid_on"] = grid_on
                    current["sound_on"] = sound_on
                    save_settings(current)
                    return current
        clock.tick(60)

def leaderboard_screen():
    data = []
    if DB_AVAILABLE:
        try:
            data = get_top_leaderboard(10)
        except Exception as e:
            print(f"Leaderboard error: {e}")

    back_btn = Button(WIDTH//2 - 60, 350, 120, 45, "BACK", (100,100,100), (150,150,150))

    while True:
        draw_gradient(screen, (10, 20, 30), (30, 40, 60), WIDTH, HEIGHT)

        title = title_font.render("TOP SNAKES", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

        y = 80
        if not data:
            msg = font.render("No entries yet. Be the first!" if DB_AVAILABLE else "DB not connected", True, WHITE)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, y))
        else:
            header = font.render(f"{'#':<4} {'NAME':<12} {'SCORE':<8} {'LVL':<6} {'DATE':<16}", True, CYAN)
            screen.blit(header, (50, y))
            y += 30

            for rank, name, score, level, date in data:
                color = YELLOW if rank == 1 else WHITE if rank <= 3 else GRAY
                line = font.render(
                    f"{rank:<4} {name:<12} {score:<8} {level:<6} {date:<16}", True, color)
                screen.blit(line, (50, y))
                y += 28

        mouse_pos = pygame.mouse.get_pos()
        back_btn.update(mouse_pos)
        back_btn.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(event.pos):
                    return
        clock.tick(60)

def game_over_screen(score, level, personal_best):
    retry_btn = Button(150, 260, 110, 45, "RETRY", (50, 200, 50), (80, 255, 80))
    menu_btn = Button(340, 260, 130, 45, "MENU", (200, 50, 50), (255, 80, 80))

    scale = 0.1
    target_scale = 1.0

    while True:
        draw_gradient(screen, (30, 10, 10), (60, 20, 20), WIDTH, HEIGHT)

        scale += (target_scale - scale) * 0.1
        over_text = title_font.render("GAME OVER", True, RED)
        scaled_w = int(over_text.get_width() * scale)
        scaled_h = int(over_text.get_height() * scale)
        scaled = pygame.transform.scale(over_text, (scaled_w, scaled_h))
        screen.blit(scaled, (WIDTH//2 - scaled_w//2, 40))

        stats = [
            (f"Score: {score}", YELLOW),
            (f"Level: {level}", GREEN),
            (f"Personal Best: {personal_best}", CYAN)
        ]
        y = 140
        for text, color in stats:
            txt = font.render(text, True, color)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y))
            y += 35

        mouse_pos = pygame.mouse.get_pos()
        for btn in [retry_btn, menu_btn]:
            btn.update(mouse_pos)
            btn.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if retry_btn.is_clicked(pos):
                    return "retry"
                if menu_btn.is_clicked(pos):
                    return "menu"
        clock.tick(60)

def main_menu():
    buttons = [
        Button(WIDTH//2 - 100, 140, 200, 45, "PLAY", (34, 139, 34), (50, 205, 50)),
        Button(WIDTH//2 - 100, 200, 200, 45, "LEADERBOARD", (70, 130, 180), (100, 149, 237)),
        Button(WIDTH//2 - 100, 260, 200, 45, "SETTINGS", (218, 165, 32), (255, 215, 0)),
        Button(WIDTH//2 - 100, 320, 200, 45, "QUIT", (178, 34, 34), (220, 20, 60))
    ]
    
    angle = 0
    
    while True:
        screen.fill((15, 15, 25))
        
        # Animated dots
        angle += 0.03
        for i in range(8):
            px = int(WIDTH//2 + math.cos(angle + i * 0.8) * 180)
            py = int(80 + math.sin(angle + i * 1.2) * 50)
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                pygame.draw.circle(screen, (40, 40, 60), (px, py), 2)
        
        # Title
        title = title_font.render("SNAKE", True, (50, 255, 100))
        title_rect = title.get_rect(center=(WIDTH//2, 50))
        glow = title_font.render("SNAKE", True, (30, 150, 60))
        screen.blit(glow, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title, title_rect)
        
        # Subtitle
        sub = font.render("TSIS 4 - PostgreSQL Edition", True, (180, 180, 180))
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 95))
        
        # Snake icon - below subtitle
        sx = WIDTH//2 - 25
        sy = 115
        for i in range(4):
            pygame.draw.rect(screen, (50, 255, 50), (sx + i*12, sy, 10, 10), border_radius=3)
        pygame.draw.circle(screen, (255, 50, 50), (sx + 50, sy + 5), 3)
        
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if buttons[0].is_clicked(pos):
                    return "play"
                if buttons[1].is_clicked(pos):
                    return "leaderboard"
                if buttons[2].is_clicked(pos):
                    return "settings"
                if buttons[3].is_clicked(pos):
                    pygame.quit()
                    sys.exit()
        clock.tick(60)

# ---------- Game loop ----------
def game_loop(settings, username):
    snake_color = tuple(settings["snake_color"])
    grid_on = settings["grid_on"]
    sound_on = settings["sound_on"]

    snake_body = [(5,5), (4,5), (3,5)]
    direction = RIGHT
    score = 0
    level = 1
    speed = 10

    obstacles = []
    normal_food, food_weight = get_random_food(snake_body, obstacles)
    poison_pos = None
    powerup = None
    powerup_spawn_timer = 0

    shielded = False
    particles = []

    food_timer_event = pygame.USEREVENT + 1
    pygame.time.set_timer(food_timer_event, 5000)
    poison_spawn_event = pygame.USEREVENT + 2
    pygame.time.set_timer(poison_spawn_event, 8000)

    personal_best = 0
    if DB_AVAILABLE:
        try:
            personal_best = get_personal_best(username)
        except:
            pass

    running = True
    while running:
        clock.tick(speed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT
            if event.type == food_timer_event:
                normal_food, food_weight = get_random_food(snake_body, obstacles)
            if event.type == poison_spawn_event:
                if poison_pos is None:
                    poison_pos = get_random_poison(snake_body, obstacles, normal_food)

        # Move snake
        head = snake_body[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])
        snake_body.insert(0, new_head)

        # Collision with walls
        if (new_head[0] < 0 or new_head[0] >= WIDTH//CELL or
            new_head[1] < 0 or new_head[1] >= HEIGHT//CELL):
            if shielded:
                shielded = False
            else:
                if sound_on:
                    play_sound(crash_sound)
                break

        # Collision with self
        if new_head in snake_body[1:]:
            if shielded:
                shielded = False
            else:
                if sound_on:
                    play_sound(crash_sound)
                break

        # Collision with obstacles
        if new_head in obstacles:
            if shielded:
                shielded = False
            else:
                if sound_on:
                    play_sound(crash_sound)
                break

        # Eat normal food
        if new_head == normal_food:
            score += food_weight
            if sound_on:
                play_sound(eat_sound)
            for _ in range(10):
                particles.append(Particle(
                    normal_food[0]*CELL + CELL//2,
                    normal_food[1]*CELL + CELL//2,
                    FOOD_COLORS[food_weight]
                ))
            normal_food, food_weight = get_random_food(snake_body, obstacles)
            if score % 3 == 0:
                level += 1
                speed += 2
                if sound_on:
                    play_sound(levelup_sound)
                if level >= 3:
                    new_obs = get_random_obstacles(snake_body, normal_food, poison_pos, level)
                    obstacles.extend(new_obs)
        else:
            snake_body.pop()

        # Eat poison
        if poison_pos and new_head == poison_pos:
            if len(snake_body) > 2:
                del snake_body[-2:]
            else:
                if sound_on:
                    play_sound(crash_sound)
                break
            poison_pos = None

        # Power-up spawn
        powerup_spawn_timer += 1
        if powerup is None and powerup_spawn_timer > 600:
            powerup_spawn_timer = 0
            ptype = random.choice(["speed_boost", "slow_motion", "shield"])
            while True:
                ppos = (random.randint(0, (WIDTH//CELL)-1),
                        random.randint(0, (HEIGHT//CELL)-1))
                if ppos not in snake_body and ppos != normal_food and ppos != poison_pos and ppos not in obstacles:
                    break
            duration = 5000
            powerup = (ptype, ppos, pygame.time.get_ticks() + duration)

        # Power-up expiration
        if powerup:
            ptype, ppos, end_ticks = powerup
            if pygame.time.get_ticks() > end_ticks:
                powerup = None
            elif new_head == ppos:
                if sound_on:
                    play_sound(powerup_sound)
                for _ in range(15):
                    particles.append(Particle(
                        ppos[0]*CELL + CELL//2,
                        ppos[1]*CELL + CELL//2,
                        CYAN if ptype == "speed_boost" else ORANGE if ptype == "slow_motion" else BLUE
                    ))
                if ptype == "speed_boost":
                    speed += 3
                elif ptype == "slow_motion":
                    speed = max(3, speed - 3)
                elif ptype == "shield":
                    shielded = True
                powerup = None

        # Update particles
        for p in particles:
            p.update()
        particles = [p for p in particles if p.is_alive()]

        # Draw
        screen.fill(WHITE)

        # Grid
        if grid_on:
            for x in range(0, WIDTH, CELL):
                pygame.draw.line(screen, (220, 220, 220), (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, CELL):
                pygame.draw.line(screen, (220, 220, 220), (0, y), (WIDTH, y))

        # Snake with rounded segments
        for i, seg in enumerate(snake_body):
            color = snake_color
            if i == 0:
                color = tuple(min(255, c + 30) for c in snake_color)
            pygame.draw.rect(screen, color, (seg[0]*CELL+1, seg[1]*CELL+1, CELL-2, CELL-2), border_radius=4)

        # Eyes on snake head
        head_x = snake_body[0][0]*CELL
        head_y = snake_body[0][1]*CELL
        pygame.draw.circle(screen, WHITE, (head_x + 5, head_y + 5), 3)
        pygame.draw.circle(screen, WHITE, (head_x + 15, head_y + 5), 3)
        pygame.draw.circle(screen, BLACK, (head_x + 5, head_y + 5), 1)
        pygame.draw.circle(screen, BLACK, (head_x + 15, head_y + 5), 1)

        # Normal food (glowing)
        food_x = normal_food[0]*CELL
        food_y = normal_food[1]*CELL
        glow_surf = pygame.Surface((CELL+10, CELL+10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*FOOD_COLORS[food_weight], 100), (CELL//2+5, CELL//2+5), CELL//2+5)
        screen.blit(glow_surf, (food_x-5, food_y-5))
        pygame.draw.rect(screen, FOOD_COLORS[food_weight], (food_x+2, food_y+2, CELL-4, CELL-4), border_radius=6)

        weight_text = small_font.render(str(food_weight), True, BLACK)
        screen.blit(weight_text, (food_x + CELL//2 - 4, food_y + CELL//2 - 5))

        # Poison
        if poison_pos:
            px = poison_pos[0]*CELL
            py = poison_pos[1]*CELL
            pygame.draw.rect(screen, DARK_RED, (px, py, CELL, CELL), border_radius=4)
            pygame.draw.circle(screen, WHITE, (px + CELL//2, py + 6), 4)
            pygame.draw.rect(screen, WHITE, (px + 4, py + 10, 12, 6))

        # Obstacles
        for obs in obstacles:
            ox = obs[0]*CELL
            oy = obs[1]*CELL
            pygame.draw.rect(screen, GRAY, (ox, oy, CELL, CELL), border_radius=2)
            pygame.draw.rect(screen, (80, 80, 80), (ox+2, oy+2, CELL-4, CELL-4), border_radius=2)

        # Power-up
        if powerup:
            ptype, ppos, _ = powerup
            color = CYAN if ptype == "speed_boost" else ORANGE if ptype == "slow_motion" else BLUE
            px = ppos[0]*CELL
            py = ppos[1]*CELL
            pulse = int(math.sin(pygame.time.get_ticks() / 200) * 5)
            glow_surf = pygame.Surface((CELL+20, CELL+20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, 150), (CELL//2+10, CELL//2+10), CELL//2+10+pulse)
            screen.blit(glow_surf, (px-10, py-10))
            pygame.draw.rect(screen, color, (px+2, py+2, CELL-4, CELL-4), border_radius=6)
            letter = "S" if ptype == "speed_boost" else "M" if ptype == "slow_motion" else "H"
            letter_text = small_font.render(letter, True, WHITE)
            screen.blit(letter_text, (px + CELL//2 - 4, py + CELL//2 - 5))

        # Shield effect
        if shielded:
            head = snake_body[0]
            shield_surf = pygame.Surface((CELL+20, CELL+20), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (0, 100, 255, 120), (CELL//2+10, CELL//2+10), CELL//2+10)
            pygame.draw.circle(shield_surf, (100, 200, 255, 180), (CELL//2+10, CELL//2+10), CELL//2+10, 2)
            screen.blit(shield_surf, (head[0]*CELL-10, head[1]*CELL-10))

        # Particles
        for p in particles:
            p.draw(screen)

        # HUD background
        hud_bg = pygame.Surface((280, 80), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 120))
        screen.blit(hud_bg, (5, 5))

        # HUD text
        hud_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
        screen.blit(hud_text, (10, 10))
        best_text = font.render(f"Best: {personal_best}", True, YELLOW)
        screen.blit(best_text, (10, 35))
        if shielded:
            shield_text = font.render("SHIELD ON", True, BLUE)
            screen.blit(shield_text, (10, 60))

        pygame.display.flip()

    # Save to DB if available
    if DB_AVAILABLE:
        try:
            save_game_session(username, score, level)
            personal_best = get_personal_best(username)
        except Exception as e:
            print(f"Save error: {e}")

    return score, level, personal_best

# ---------- Main ----------
def main():
    settings = load_settings()
    username = "player"
    while True:
        action = main_menu()
        if action == "play":
            username = input_username_screen()
            score, level, pb = game_loop(settings, username)
            choice = game_over_screen(score, level, pb)
            if choice == "retry":
                score, level, pb = game_loop(settings, username)
                game_over_screen(score, level, pb)
        elif action == "leaderboard":
            leaderboard_screen()
        elif action == "settings":
            settings = settings_screen(settings)

if __name__ == '__main__':
    main()
