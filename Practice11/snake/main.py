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

# Food colors by weight (points)
FOOD_COLORS = {
    1: (255, 215, 0),   # gold (1 point)
    2: (255, 165, 0),   # orange (2 points)
    3: (255, 0, 0)      # red (3 points)
}

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake with Weights & Timer")

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

def draw_food(food_pos, food_weight):
    """Draw the food with a color based on its weight."""
    color = FOOD_COLORS.get(food_weight, RED)
    pygame.draw.rect(screen, color,
                     (food_pos[0]*CELL_SIZE, food_pos[1]*CELL_SIZE,
                      CELL_SIZE, CELL_SIZE))
    # Draw weight number
    weight_text = font.render(str(food_weight), True, BLACK)
    screen.blit(weight_text, (food_pos[0]*CELL_SIZE + 4, food_pos[1]*CELL_SIZE + 1))

def get_random_food(snake_body):
    """Generate food at a random position (not on the snake) with a random weight."""
    while True:
        pos = (random.randint(0, (WIDTH//CELL_SIZE)-1),
               random.randint(0, (HEIGHT//CELL_SIZE)-1))
        if pos not in snake_body:
            weight = random.randint(1, 3)   # random weight 1-3
            return pos, weight

def check_collision(snake_head, snake_body):
    """Check if the snake hit a wall or itself."""
    # Wall collision
    if (snake_head[0] < 0 or snake_head[0] >= WIDTH//CELL_SIZE or
        snake_head[1] < 0 or snake_head[1] >= HEIGHT//CELL_SIZE):
        return True
    # Self collision
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

# Custom event for food timer
FOOD_TIMER = pygame.USEREVENT + 1
pygame.time.set_timer(FOOD_TIMER, 5000)  # 5 seconds

def game_loop():
    """Main game loop."""
    # Initial state
    snake_body = [(5, 5), (4, 5), (3, 5)]
    direction = RIGHT
    score = 0
    level = 1
    speed = FPS

    food_pos, food_weight = get_random_food(snake_body)

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
            if event.type == FOOD_TIMER:
                # Timer expired – move food to a new location (with new weight)
                food_pos, food_weight = get_random_food(snake_body)

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
        if new_head == food_pos:
            score += food_weight          # add the weight to score
            food_pos, food_weight = get_random_food(snake_body)
            # Level up every 3 foods (by count, not by points)
            if score % 3 == 0:
                level += 1
                speed = FPS + (level - 1) * 2
        else:
            # Remove tail (normal movement)
            snake_body.pop()

        # --- Draw everything ---
        screen.fill(BLACK)
        draw_snake(snake_body)
        draw_food(food_pos, food_weight)

        # Score and level display
        score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        timer_text = font.render("Food changes every 5s", True, WHITE)
        screen.blit(timer_text, (10, 35))

        pygame.display.update()

# Start the game
game_loop()