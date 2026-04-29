import pygame
import sys
import random
import json
import os
from db import get_top_leaderboard, save_game_session, get_personal_best, get_or_create_player

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
pygame.display.set_caption("TSIS 4 - Snake")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 20)
small_font = pygame.font.SysFont("Verdana", 14)
big_font = pygame.font.SysFont("Verdana", 40)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
GRAY  = (100, 100, 100)
DARK_RED = (139, 0, 0)
CYAN  = (0, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Directions
UP    = (0, -1)
DOWN  = (0, 1)
LEFT  = (-1, 0)
RIGHT = (1, 0)

# ---------- Helper functions ----------
def draw_text(text, x, y, color=BLACK, size="small"):
    if size == "big":
        surf = big_font.render(text, True, color)
    elif size == "small":
        surf = small_font.render(text, True, color)
    else:
        surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

def draw_button(rect, text, color=GRAY):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def point_in_rect(pos, rect):
    return rect.collidepoint(pos)

# ---------- Food helpers ----------
FOOD_COLORS = {
    1: (255, 215, 0),
    2: (255, 165, 0),
    3: (255, 0, 0)
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
        # must not be on snake, food, poison or already placed
        if pos not in snake_body and pos != food_pos and pos != poison_pos and pos not in obs:
            # ensure not completely surrounding the snake head
            head = snake_body[0]
            neighbors = [(head[0]+dx, head[1]+dy) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]]
            if all(n in obs for n in neighbors):
                continue  # would trap head, skip
            obs.add(pos)
    return list(obs)

# ---------- Screens ----------
def input_username_screen():
    """Let the player type a username. Returns the string."""
    name = ""
    active = True
    while active:
        screen.fill(WHITE)
        draw_text("Enter your username:", 150, 150, BLACK, "normal")
        draw_text(name + ("|" if pygame.time.get_ticks() % 1000 < 500 else ""), 200, 200, BLUE, "big")
        draw_button(pygame.Rect(250, 280, 100, 40), "OK")
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
                if point_in_rect(event.pos, pygame.Rect(250, 280, 100, 40)) and name.strip():
                    return name.strip()
        clock.tick(30)

def settings_screen(settings):
    """Return updated settings dict."""
    current = settings.copy()
    snake_color = current["snake_color"][:]   # list copy
    grid_on = current["grid_on"]
    sound_on = current["sound_on"]

    color_cycle = [[0,255,0], [255,0,0], [0,0,255], [255,255,0], [0,255,255], [255,0,255]]

    while True:
        screen.fill(WHITE)
        draw_text("Settings", 230, 30, BLACK, "big")
        draw_text(f"Snake color: {tuple(snake_color)}", 50, 100, BLACK, "normal")
        draw_button(pygame.Rect(50, 140, 200, 40), "Cycle Color")
        draw_text(f"Grid: {'ON' if grid_on else 'OFF'}", 50, 200, BLACK, "normal")
        draw_button(pygame.Rect(50, 240, 200, 40), "Toggle Grid")
        draw_text(f"Sound: {'ON' if sound_on else 'OFF'}", 50, 300, BLACK, "normal")
        draw_button(pygame.Rect(50, 340, 200, 40), "Toggle Sound")
        draw_button(pygame.Rect(400, 340, 150, 40), "Save & Back")
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if point_in_rect(pos, pygame.Rect(50, 140, 200, 40)):
                    # cycle color
                    idx = color_cycle.index(snake_color) if snake_color in color_cycle else 0
                    snake_color = color_cycle[(idx+1) % len(color_cycle)]
                elif point_in_rect(pos, pygame.Rect(50, 240, 200, 40)):
                    grid_on = not grid_on
                elif point_in_rect(pos, pygame.Rect(50, 340, 200, 40)):
                    sound_on = not sound_on
                elif point_in_rect(pos, pygame.Rect(400, 340, 150, 40)):
                    current["snake_color"] = snake_color
                    current["grid_on"] = grid_on
                    current["sound_on"] = sound_on
                    save_settings(current)
                    return current

def leaderboard_screen():
    """Display top 10 from DB."""
    data = get_top_leaderboard(10)
    while True:
        screen.fill(WHITE)
        draw_text("Leaderboard", 200, 10, BLACK, "big")
        y = 60
        if not data:
            draw_text("No entries yet.", 50, y, GRAY, "normal")
        else:
            for rank, name, score, level, date in data:
                draw_text(f"{rank}. {name}  Score:{score}  Lvl:{level}  {date}", 50, y, BLACK, "small")
                y += 25
        draw_button(pygame.Rect(250, 340, 100, 40), "Back")
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if point_in_rect(event.pos, pygame.Rect(250, 340, 100, 40)):
                    return

def game_over_screen(score, level, personal_best):
    """Display final stats and choices."""
    while True:
        screen.fill(WHITE)
        draw_text("GAME OVER", 180, 30, RED, "big")
        draw_text(f"Score: {score}  Level: {level}", 150, 100, BLACK, "normal")
        draw_text(f"Personal Best: {personal_best}", 150, 140, BLACK, "normal")
        draw_button(pygame.Rect(150, 220, 100, 40), "Retry")
        draw_button(pygame.Rect(350, 220, 120, 40), "Main Menu")
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if point_in_rect(pos, pygame.Rect(150, 220, 100, 40)):
                    return "retry"
                if point_in_rect(pos, pygame.Rect(350, 220, 120, 40)):
                    return "menu"

def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text("SNAKE GAME", 170, 30, BLACK, "big")
        draw_button(pygame.Rect(200, 100, 200, 50), "Play")
        draw_button(pygame.Rect(200, 170, 200, 50), "Leaderboard")
        draw_button(pygame.Rect(200, 240, 200, 50), "Settings")
        draw_button(pygame.Rect(200, 310, 200, 50), "Quit")
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if point_in_rect(pos, pygame.Rect(200, 100, 200, 50)):
                    return "play"
                if point_in_rect(pos, pygame.Rect(200, 170, 200, 50)):
                    return "leaderboard"
                if point_in_rect(pos, pygame.Rect(200, 240, 200, 50)):
                    return "settings"
                if point_in_rect(pos, pygame.Rect(200, 310, 200, 50)):
                    pygame.quit()
                    sys.exit()

# ---------- Game loop ----------
def game_loop(settings, username):
    """Runs the Snake game and returns final stats when game over."""
    snake_color = tuple(settings["snake_color"])
    grid_on = settings["grid_on"]
    sound_on = settings["sound_on"]

    # Initial snake
    snake_body = [(5,5), (4,5), (3,5)]
    direction = RIGHT
    score = 0
    level = 1
    speed = 10

    obstacles = []   # obstacle positions (x,y) in grid units
    normal_food, food_weight = get_random_food(snake_body, obstacles)
    poison_pos = None
    poison_timer = 0
    powerup = None          # (type, pos, end_ticks)
    powerup_spawn_timer = 0

    # Shield state (lasts until hit)
    shielded = False

    # Timers
    food_timer_event = pygame.USEREVENT + 1
    pygame.time.set_timer(food_timer_event, 5000)  # normal food moves every 5 sec
    poison_spawn_event = pygame.USEREVENT + 2
    pygame.time.set_timer(poison_spawn_event, 8000)

    personal_best = get_personal_best(username)

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
                # move normal food to a new random location
                normal_food, food_weight = get_random_food(snake_body, obstacles)
            if event.type == poison_spawn_event:
                # spawn poison if not already present
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
                break   # game over

        # Collision with self
        if new_head in snake_body[1:]:
            if shielded:
                shielded = False
            else:
                break

        # Collision with obstacles
        if new_head in obstacles:
            if shielded:
                shielded = False
            else:
                break

        # Eat normal food
        if new_head == normal_food:
            score += food_weight
            normal_food, food_weight = get_random_food(snake_body, obstacles)
            # Level up every 3 foods
            if score % 3 == 0:
                level += 1
                speed += 2
                # Add obstacles from level 3
                if level >= 3:
                    new_obs = get_random_obstacles(snake_body, normal_food, poison_pos, level)
                    obstacles.extend(new_obs)
        else:
            snake_body.pop()   # normal movement

        # Eat poison
        if poison_pos and new_head == poison_pos:
            # shorten by 2 segments
            if len(snake_body) > 2:
                del snake_body[-2:]
            else:
                break   # too short, game over
            poison_pos = None

        # Power-up spawn (every 10 seconds, only one active)
        powerup_spawn_timer += 1
        if powerup is None and powerup_spawn_timer > 600:
            powerup_spawn_timer = 0
            # random type
            ptype = random.choice(["speed_boost", "slow_motion", "shield"])
            while True:
                ppos = (random.randint(0, (WIDTH//CELL)-1),
                        random.randint(0, (HEIGHT//CELL)-1))
                if ppos not in snake_body and ppos != normal_food and ppos != poison_pos and ppos not in obstacles:
                    break
            duration = 5000   # 5 seconds
            powerup = (ptype, ppos, pygame.time.get_ticks() + duration)

        # Power-up expiration
        if powerup:
            ptype, ppos, end_ticks = powerup
            if pygame.time.get_ticks() > end_ticks:
                powerup = None
            elif new_head == ppos:
                # collect power-up
                if ptype == "speed_boost":
                    speed += 3
                elif ptype == "slow_motion":
                    speed = max(3, speed - 3)
                elif ptype == "shield":
                    shielded = True
                powerup = None

        # Draw
        screen.fill(WHITE)

        # Grid overlay
        if grid_on:
            for x in range(0, WIDTH, CELL):
                pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, CELL):
                pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

        # Snake
        for seg in snake_body:
            pygame.draw.rect(screen, snake_color, (seg[0]*CELL, seg[1]*CELL, CELL, CELL))

        # Normal food (with weight number)
        pygame.draw.rect(screen, FOOD_COLORS[food_weight],
                         (normal_food[0]*CELL, normal_food[1]*CELL, CELL, CELL))
        draw_text(str(food_weight), normal_food[0]*CELL+4, normal_food[1]*CELL+1, BLACK, "small")

        # Poison food
        if poison_pos:
            pygame.draw.rect(screen, DARK_RED, (poison_pos[0]*CELL, poison_pos[1]*CELL, CELL, CELL))
            draw_text("P", poison_pos[0]*CELL+4, poison_pos[1]*CELL+1, WHITE, "small")

        # Obstacles
        for obs in obstacles:
            pygame.draw.rect(screen, GRAY, (obs[0]*CELL, obs[1]*CELL, CELL, CELL))

        # Power-up
        if powerup:
            ptype, ppos, _ = powerup
            color = CYAN if ptype == "speed_boost" else ORANGE if ptype == "slow_motion" else BLUE
            pygame.draw.rect(screen, color, (ppos[0]*CELL, ppos[1]*CELL, CELL, CELL))
            draw_text("P", ppos[0]*CELL+4, ppos[1]*CELL+1, WHITE, "small")

        # HUD
        draw_text(f"Score: {score}  Level: {level}", 10, 10, BLACK, "normal")
        draw_text(f"Best: {personal_best}", 450, 10, BLACK, "normal")
        if shielded:
            draw_text("SHIELD ON", 250, 10, BLUE, "normal")

        pygame.display.flip()

    # Game over – save session and return stats
    save_game_session(username, score, level)
    new_pb = get_personal_best(username)
    return score, level, new_pb

# ---------- Main ----------
def main():
    settings = load_settings()
    # If no username set, prompt once
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