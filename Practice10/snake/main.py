import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
FPS = 10

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake with Levels")

# Fonts
font = pygame.font.SysFont("Verdana", 20)
game_over_font = pygame.font.SysFont("Verdana", 50)

# Clock
clock = pygame.time.Clock()

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def draw_snake(snake_body):
    """Draw the snake on the screen."""
    for segment in snake_body:
        pygame.draw.rect(screen, GREEN,
                         (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE,
                          CELL_SIZE, CELL_SIZE))

def draw_food(food_pos):
    """Draw the food (red square)."""
    pygame.draw.rect(screen, RED,
                     (food_pos[0]*CELL_SIZE, food_pos[1]*CELL_SIZE,
                      CELL_SIZE, CELL_SIZE))

def get_random_food(snake_body):
    """Generate food at a random position, but not on the snake."""
    while True:
        pos = (random.randint(0, (WIDTH//CELL_SIZE)-1),
               random.randint(0, (HEIGHT//CELL_SIZE)-1))
        if pos not in snake_body:
            return pos

def check_collision(snake_head, snake_body):
    """Check if the snake hit a wall or itself."""
    # Wall collision
    if (snake_head[0] < 0 or snake_head[0] >= WIDTH//CELL_SIZE or
        snake_head[1] < 0 or snake_head[1] >= HEIGHT//CELL_SIZE):
        return True
    # Self collision (head hits body)
    if snake_head in snake_body[1:]:
        return True
    return False

def show_game_over(score, level):
    """Display game over screen."""
    screen.fill(BLACK)
    over_text = game_over_font.render("GAME OVER", True, RED)
    score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
    restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 80))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 30))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True   # restart
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
    return False

def game_loop():
    """Main game loop."""
    # Initial state
    snake_body = [(5, 5), (4, 5), (3, 5)]   # head at (5,5)
    direction = RIGHT
    score = 0
    level = 1
    speed = FPS

    food = get_random_food(snake_body)

    running = True
    while running:
        clock.tick(speed)

        # --- Event handling ---
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

        # --- Move snake ---
        head = snake_body[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])
        snake_body.insert(0, new_head)

        # --- Check collisions ---
        if check_collision(new_head, snake_body):
            if show_game_over(score, level):
                game_loop()   # recursive restart
            return

        # --- Check food eaten ---
        if new_head == food:
            score += 1
            food = get_random_food(snake_body)
            # Level up every 3 foods
            if score % 3 == 0:
                level += 1
                speed = FPS + (level - 1) * 2  # increase speed
        else:
            # Remove tail (normal movement)
            snake_body.pop()

        # --- Draw everything ---
        screen.fill(BLACK)
        draw_snake(snake_body)
        draw_food(food)

        # Score and level display
        score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.update()

# Start the game
game_loop()