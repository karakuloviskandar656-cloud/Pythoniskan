import pygame

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint Program")

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
tool = "pen"   # "pen", "rect", "circle", "eraser"

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
                # Draw final shape on canvas
                if tool == "rect":
                    rect = pygame.Rect(start_pos, (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                    rect.normalize()  # fix negative width/height
                    pygame.draw.rect(canvas, draw_color, rect, 2)
                elif tool == "circle":
                    center = start_pos
                    radius = int(((end_pos[0]-start_pos[0])**2 + (end_pos[1]-start_pos[1])**2)**0.5)
                    pygame.draw.circle(canvas, draw_color, center, radius, 2)

    # --- Draw everything ---
    screen.fill(WHITE)
    screen.blit(canvas, (0, 0))

    # Draw UI panel at the bottom
    panel = pygame.Surface((WIDTH, 80))
    panel.fill((200, 200, 200))
    screen.blit(panel, (0, HEIGHT-80))

    # Tool info
    tool_text = font.render(f"Tool: {tool.upper()} (P=pen, R=rect, C=circle, E=eraser)", True, BLACK)
    screen.blit(tool_text, (10, HEIGHT-70))
    color_text = font.render(f"Color: {draw_color} (0=Black, 1=Red, 2=Green, 3=Blue, 4=Yellow, 5=Purple, 6=Cyan)", True, BLACK)
    screen.blit(color_text, (10, HEIGHT-45))

    # Draw a small preview of current color
    pygame.draw.rect(screen, draw_color, (WIDTH-50, HEIGHT-65, 30, 30))

    pygame.display.flip()
    clock.tick(120)

pygame.quit()