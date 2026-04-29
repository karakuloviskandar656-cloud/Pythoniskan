import pygame
import math

# Initialise pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint with Shapes")

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Default settings
draw_color = BLACK
brush_size = 5
tool = "pen"   # "pen", "rect", "circle", "eraser", "square", "r_triangle", "equilateral", "rhombus"

# Create a surface to draw on
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

# Font for UI
font = pygame.font.SysFont("Verdana", 14)

clock = pygame.time.Clock()
running = True
drawing = False   # True when mouse button is held down
start_pos = (0, 0)
last_pos = (0, 0)

while running:
    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard shortcuts for tools and colors
        if event.type == pygame.KEYDOWN:
            # Tool selection
            if event.key == pygame.K_p:
                tool = "pen"
            elif event.key == pygame.K_r:
                tool = "rect"
            elif event.key == pygame.K_c:
                tool = "circle"
            elif event.key == pygame.K_e:
                tool = "eraser"
            elif event.key == pygame.K_s:      # Square
                tool = "square"
            elif event.key == pygame.K_t:      # Right triangle
                tool = "r_triangle"
            elif event.key == pygame.K_u:      # Equilateral triangle
                tool = "equilateral"
            elif event.key == pygame.K_h:      # Rhombus
                tool = "rhombus"
            # Color selection
            elif event.key == pygame.K_1:
                draw_color = RED
            elif event.key == pygame.K_2:
                draw_color = GREEN
            elif event.key == pygame.K_3:
                draw_color = BLUE
            elif event.key == pygame.K_4:
                draw_color = YELLOW
            elif event.key == pygame.K_5:
                draw_color = PURPLE
            elif event.key == pygame.K_6:
                draw_color = CYAN
            elif event.key == pygame.K_0:
                draw_color = BLACK

        # Mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left button
                drawing = True
                start_pos = event.pos
                last_pos = event.pos
                # For pen/eraser, draw a small circle immediately
                if tool == "pen":
                    pygame.draw.circle(canvas, draw_color, event.pos, brush_size)
                elif tool == "eraser":
                    pygame.draw.circle(canvas, WHITE, event.pos, brush_size*2)

        if event.type == pygame.MOUSEMOTION:
            if drawing:
                if tool == "pen":
                    pygame.draw.line(canvas, draw_color, last_pos, event.pos, brush_size)
                    last_pos = event.pos
                elif tool == "eraser":
                    pygame.draw.line(canvas, WHITE, last_pos, event.pos, brush_size*2)
                    last_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False
                end_pos = event.pos

                # ---------- Drawing shapes ----------
                if tool == "rect":
                    rect = pygame.Rect(start_pos, (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                    rect.normalize()  # fix negative width/height
                    pygame.draw.rect(canvas, draw_color, rect, 2)

                elif tool == "circle":
                    center = start_pos
                    radius = int(math.hypot(end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                    pygame.draw.circle(canvas, draw_color, center, radius, 2)

                elif tool == "square":
                    side = max(abs(end_pos[0]-start_pos[0]), abs(end_pos[1]-start_pos[1]))
                    # Force the rectangle to be square, using the starting corner
                    rect = pygame.Rect(start_pos, (side, side))
                    # Adjust direction if the mouse is to the left/above
                    if end_pos[0] < start_pos[0]:
                        rect.x = start_pos[0] - side
                    if end_pos[1] < start_pos[1]:
                        rect.y = start_pos[1] - side
                    pygame.draw.rect(canvas, draw_color, rect, 2)

                elif tool == "r_triangle":
                    # Right triangle: the start and end points define the two legs
                    p1 = start_pos
                    p2 = (end_pos[0], start_pos[1])   # horizontal leg
                    p3 = (start_pos[0], end_pos[1])   # vertical leg
                    pygame.draw.polygon(canvas, draw_color, [p1, p2, p3], 2)

                elif tool == "equilateral":
                    # Equilateral triangle: centre at start_pos, height = vertical distance to end_pos
                    center_x, center_y = start_pos
                    height = abs(end_pos[1] - start_pos[1])
                    side = height * 2 / math.sqrt(3)
                    half_side = side / 2
                    # Three vertices
                    top = (center_x, center_y - height // 2)
                    bottom_right = (center_x + half_side, center_y + height // 2)
                    bottom_left = (center_x - half_side, center_y + height // 2)
                    pygame.draw.polygon(canvas, draw_color, [top, bottom_right, bottom_left], 2)

                elif tool == "rhombus":
                    # Rhombus: start = one corner, end = opposite corner
                    left = min(start_pos[0], end_pos[0])
                    right = max(start_pos[0], end_pos[0])
                    top = min(start_pos[1], end_pos[1])
                    bottom = max(start_pos[1], end_pos[1])
                    center_x = (left + right) // 2
                    center_y = (top + bottom) // 2
                    # Vertices: top, right, bottom, left
                    vertices = [
                        (center_x, top),
                        (right, center_y),
                        (center_x, bottom),
                        (left, center_y)
                    ]
                    pygame.draw.polygon(canvas, draw_color, vertices, 2)

    # --- Draw everything ---
    screen.fill(WHITE)
    screen.blit(canvas, (0, 0))

    # Draw UI panel at the bottom
    panel = pygame.Surface((WIDTH, 80))
    panel.fill((200, 200, 200))
    screen.blit(panel, (0, HEIGHT-80))

    # Tool info
    tool_text = font.render(
        f"Tool: {tool.upper()} (P=pen, R=rect, C=circle, E=eraser, S=square, T=rightTri, U=equiTri, H=rhombus)",
        True, BLACK)
    screen.blit(tool_text, (10, HEIGHT-70))
    color_text = font.render(
        f"Color: {draw_color} (0=Black, 1=Red, 2=Green, 3=Blue, 4=Yellow, 5=Purple, 6=Cyan)",
        True, BLACK)
    screen.blit(color_text, (10, HEIGHT-45))

    # Draw a small preview of current color
    pygame.draw.rect(screen, draw_color, (WIDTH-50, HEIGHT-65, 30, 30))

    pygame.display.flip()
    clock.tick(120)

pygame.quit()