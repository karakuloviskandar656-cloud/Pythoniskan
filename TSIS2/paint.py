import pygame
import math
from datetime import datetime

# ========== Initialise ==========
pygame.init()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 2 - Paint Application")

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (200, 200, 200)

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

# Tool / color state
draw_color = BLACK
tool = "pencil"          # pencil, line, rect, circle, square, r_triangle, equilateral, rhombus, eraser, fill, text
brush_size = 2           # small default
drawing = False
start_pos = (0, 0)
last_pos = (0, 0)
line_preview = False     # True while dragging a line

# Text tool state
text_typing = False
text_buffer = ""
text_cursor = (0, 0)
font = pygame.font.SysFont("Verdana", 20)
ui_font = pygame.font.SysFont("Verdana", 14)

clock = pygame.time.Clock()

# ========== Helper functions ==========
def flood_fill(pos, fill_color):
    """Simple stack-based flood fill (exact color match)."""
    target_color = canvas.get_at(pos)
    if target_color == fill_color:
        return
    stack = [pos]
    w, h = canvas.get_size()
    while stack:
        x, y = stack.pop()
        if x < 0 or x >= w or y < 0 or y >= h:
            continue
        if canvas.get_at((x, y)) != target_color:
            continue
        canvas.set_at((x, y), fill_color)
        stack.append((x+1, y))
        stack.append((x-1, y))
        stack.append((x, y+1))
        stack.append((x, y-1))

def draw_line_preview(start, end, color, size):
    """Draw a live preview line on the screen (not on canvas)."""
    pygame.draw.line(screen, color, start, end, size)

# ========== Main loop ==========
running = True
while running:
    # ----- Events -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            # ---------- Brush size ----------
            if event.key == pygame.K_1:
                brush_size = 2
            elif event.key == pygame.K_2:
                brush_size = 5
            elif event.key == pygame.K_3:
                brush_size = 10

            # ---------- Tool selection ----------
            elif event.key == pygame.K_p:
                tool = "pencil"
            elif event.key == pygame.K_l:
                tool = "line"
            elif event.key == pygame.K_r:
                tool = "rect"
            elif event.key == pygame.K_c:
                tool = "circle"
            elif event.key == pygame.K_e:
                tool = "eraser"
            elif event.key == pygame.K_s:
                tool = "square"
            elif event.key == pygame.K_t:
                tool = "r_triangle"
            elif event.key == pygame.K_u:
                tool = "equilateral"
            elif event.key == pygame.K_h:
                tool = "rhombus"
            elif event.key == pygame.K_f:
                tool = "fill"
            elif event.key == pygame.K_x:
                tool = "text"

            # ---------- Colors ----------
            elif event.key == pygame.K_0:
                draw_color = BLACK
            elif event.key == pygame.K_4:
                draw_color = RED
            elif event.key == pygame.K_5:
                draw_color = GREEN
            elif event.key == pygame.K_6:
                draw_color = BLUE
            elif event.key == pygame.K_7:
                draw_color = YELLOW
            elif event.key == pygame.K_8:
                draw_color = PURPLE
            elif event.key == pygame.K_9:
                draw_color = CYAN

            # ---------- Save (Ctrl+S) ----------
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"canvas_{timestamp}.png"
                pygame.image.save(canvas, filename)
                print(f"Saved as {filename}")

            # ---------- Text tool typing ----------
            if tool == "text" and text_typing:
                if event.key == pygame.K_RETURN:
                    # Confirm – render text on canvas
                    text_surf = font.render(text_buffer, True, draw_color)
                    canvas.blit(text_surf, text_cursor)
                    text_buffer = ""
                    text_typing = False
                elif event.key == pygame.K_ESCAPE:
                    # Cancel
                    text_buffer = ""
                    text_typing = False
                elif event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]
                else:
                    text_buffer += event.unicode

        # ----- Mouse events -----
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left button
                if tool == "text":
                    text_typing = True
                    text_cursor = event.pos
                    text_buffer = ""
                elif tool == "fill":
                    flood_fill(event.pos, draw_color)
                else:
                    drawing = True
                    start_pos = event.pos
                    last_pos = event.pos
                    if tool == "pencil":
                        pygame.draw.circle(canvas, draw_color, event.pos, brush_size//2)
                    elif tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, event.pos, brush_size)

        if event.type == pygame.MOUSEMOTION:
            if drawing:
                if tool == "pencil":
                    pygame.draw.line(canvas, draw_color, last_pos, event.pos, brush_size)
                    last_pos = event.pos
                elif tool == "eraser":
                    pygame.draw.line(canvas, WHITE, last_pos, event.pos, brush_size*2)
                    last_pos = event.pos
                elif tool == "line":
                    line_preview = True
                    # preview is drawn later using start_pos and current event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False
                end_pos = event.pos

                # --- Tools that draw on canvas ---
                if tool == "line":
                    line_preview = False
                    pygame.draw.line(canvas, draw_color, start_pos, end_pos, brush_size)

                elif tool == "rect":
                    rect = pygame.Rect(start_pos, (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                    rect.normalize()
                    pygame.draw.rect(canvas, draw_color, rect, brush_size)

                elif tool == "circle":
                    radius = int(math.hypot(end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                    pygame.draw.circle(canvas, draw_color, start_pos, radius, brush_size)

                elif tool == "square":
                    side = max(abs(end_pos[0]-start_pos[0]), abs(end_pos[1]-start_pos[1]))
                    rect = pygame.Rect(start_pos, (side, side))
                    if end_pos[0] < start_pos[0]:
                        rect.x = start_pos[0] - side
                    if end_pos[1] < start_pos[1]:
                        rect.y = start_pos[1] - side
                    pygame.draw.rect(canvas, draw_color, rect, brush_size)

                elif tool == "r_triangle":
                    p1 = start_pos
                    p2 = (end_pos[0], start_pos[1])
                    p3 = (start_pos[0], end_pos[1])
                    pygame.draw.polygon(canvas, draw_color, [p1, p2, p3], brush_size)

                elif tool == "equilateral":
                    cx, cy = start_pos
                    height = abs(end_pos[1] - start_pos[1])
                    side = height * 2 / math.sqrt(3)
                    half = side / 2
                    top = (cx, cy - height//2)
                    br = (cx + half, cy + height//2)
                    bl = (cx - half, cy + height//2)
                    pygame.draw.polygon(canvas, draw_color, [top, br, bl], brush_size)

                elif tool == "rhombus":
                    left = min(start_pos[0], end_pos[0])
                    right = max(start_pos[0], end_pos[0])
                    top = min(start_pos[1], end_pos[1])
                    bottom = max(start_pos[1], end_pos[1])
                    cx, cy = (left+right)//2, (top+bottom)//2
                    pts = [(cx, top), (right, cy), (cx, bottom), (left, cy)]
                    pygame.draw.polygon(canvas, draw_color, pts, brush_size)

    # ========== Draw ==========
    screen.blit(canvas, (0, 0))

    # Live line preview (drawn on screen, not canvas)
    if line_preview and drawing:
        draw_line_preview(start_pos, pygame.mouse.get_pos(), draw_color, brush_size)

    # Text cursor indication (blinking line)
    if tool == "text" and text_typing:
        preview_surf = font.render(text_buffer, True, draw_color)
        screen.blit(preview_surf, text_cursor)
        # small cursor line
        tw, th = preview_surf.get_size()
        pygame.draw.line(screen, draw_color,
                         (text_cursor[0]+tw, text_cursor[1]),
                         (text_cursor[0]+tw, text_cursor[1]+th), 2)

    # ---------- Toolbar ----------
    bar = pygame.Surface((WIDTH, 80))
    bar.fill(GRAY)
    screen.blit(bar, (0, HEIGHT-80))

    tool_text = ui_font.render(
        f"Tool: {tool} | P=pencil L=line R=rect C=circle S=square T=rTri U=eTri H=rhombus E=eraser F=fill X=text",
        True, BLACK)
    screen.blit(tool_text, (10, HEIGHT-70))

    size_text = ui_font.render(f"Size: {brush_size} (1=small 2=medium 3=large)", True, BLACK)
    screen.blit(size_text, (10, HEIGHT-45))

    color_preview = pygame.Surface((30, 30))
    color_preview.fill(draw_color)
    screen.blit(color_preview, (WIDTH-50, HEIGHT-65))

    pygame.display.flip()
    clock.tick(120)

pygame.quit()