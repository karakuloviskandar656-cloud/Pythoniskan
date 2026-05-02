import pygame
import sys
import math
from persistence import load_settings, save_settings, load_leaderboard

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (180, 180, 180)
RED   = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE  = (50, 100, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 165, 0)
CYAN   = (0, 255, 255)
PURPLE = (150, 50, 255)
DARK_BG = (20, 20, 30)
LIGHT_BG = (240, 240, 240)

# Fonts
pygame.font.init()
title_font = pygame.font.SysFont("Arial", 55, bold=True)
button_font = pygame.font.SysFont("Arial", 32, bold=True)
small_font = pygame.font.SysFont("Arial", 22)
stats_font = pygame.font.SysFont("Arial", 26, bold=True)

def draw_gradient(screen, color1, color2, width, height):
    """Draw a vertical gradient background."""
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

def draw_glow_text(screen, text, font, color, pos, glow_color=(255, 255, 255), glow_radius=2):
    """Draw text with a glow effect."""
    x, y = pos
    # Draw glow layers
    for offset in range(glow_radius, 0, -1):
        alpha = 100 // offset
        glow_surf = font.render(text, True, glow_color)
        glow_surf.set_alpha(alpha)
        screen.blit(glow_surf, (x - offset, y))
        screen.blit(glow_surf, (x + offset, y))
        screen.blit(glow_surf, (x, y - offset))
        screen.blit(glow_surf, (x, y + offset))
    # Draw main text
    text_surf = font.render(text, True, color)
    screen.blit(text_surf, (x, y))

class Button:
    """A clickable button with hover effect and rounded corners."""
    def __init__(self, x, y, w, h, text, color=(100, 100, 100), hover_color=(150, 150, 150), text_color=WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.scale = 1.0
        self.target_scale = 1.0

    def draw(self, screen):
        # Smooth scale animation
        self.scale += (self.target_scale - self.scale) * 0.2

        # Calculate scaled rect
        scaled_w = int(self.rect.width * self.scale)
        scaled_h = int(self.rect.height * self.scale)
        scaled_x = self.rect.centerx - scaled_w // 2
        scaled_y = self.rect.centery - scaled_h // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_w, scaled_h)

        color = self.hover_color if self.hovered else self.color

        # Draw shadow
        shadow_rect = scaled_rect.copy()
        shadow_rect.move_ip(3, 3)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=12)

        # Draw button with rounded corners
        pygame.draw.rect(screen, color, scaled_rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, scaled_rect, 2, border_radius=12)

        # Text centered
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        screen.blit(text_surf, text_rect)

    def update(self, pos):
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(pos)
        if self.hovered:
            self.target_scale = 1.05
        else:
            self.target_scale = 1.0
        return was_hovered != self.hovered

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def draw(self, screen):
        # Draw glow if active
        if self.active:
            glow_rect = self.rect.inflate(6, 6)
            pygame.draw.rect(screen, CYAN, glow_rect, border_radius=8)

        color = CYAN if self.active else GRAY
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=8)
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=8)

        text_surf = small_font.render(self.text, True, BLACK)
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 8))

        # Blinking cursor
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer % 30 < 15:
                cursor_x = self.rect.x + 12 + text_surf.get_width()
                pygame.draw.line(screen, BLACK, (cursor_x, self.rect.y + 8), 
                               (cursor_x, self.rect.y + self.rect.height - 8), 2)

def show_main_menu(screen, width, height):
    buttons = [
        Button(width//2 - 110, 200, 220, 55, "PLAY", (50, 150, 50), (80, 200, 80)),
        Button(width//2 - 110, 280, 220, 55, "LEADERBOARD", (50, 100, 150), (80, 140, 200)),
        Button(width//2 - 110, 360, 220, 55, "SETTINGS", (150, 150, 50), (200, 200, 80)),
        Button(width//2 - 110, 440, 220, 55, "QUIT", (150, 50, 50), (200, 80, 80))
    ]
    clock = pygame.time.Clock()
    angle = 0

    while True:
        # Animated gradient background
        draw_gradient(screen, (10, 10, 30), (30, 30, 60), width, height)

        # Animated background particles
        angle += 0.02
        for i in range(5):
            px = width//2 + int(math.cos(angle + i * 1.2) * 150)
            py = height//2 + int(math.sin(angle + i * 1.2) * 100)
            pygame.draw.circle(screen, (50, 50, 80), (px, py), 3)

        # Title with glow
        title = title_font.render("RACER", True, WHITE)
        title_rect = title.get_rect(center=(width//2, 80))

        # Title glow effect
        for offset in range(3, 0, -1):
            glow = title_font.render("RACER", True, (100, 100, 255))
            glow.set_alpha(50)
            screen.blit(glow, (title_rect.x, title_rect.y + offset))

        screen.blit(title, title_rect)

        # Subtitle
        sub = small_font.render("TSIS 3 - Advanced Driving", True, (200, 200, 200))
        screen.blit(sub, (width//2 - sub.get_width()//2, 130))

        # Car icon (simple representation)
        car_x = width//2
        car_y = 165
        pygame.draw.rect(screen, RED, (car_x - 15, car_y, 30, 15), border_radius=3)
        pygame.draw.rect(screen, (100, 100, 255), (car_x - 10, car_y - 5, 20, 8), border_radius=2)

        # Update and draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if buttons[0].is_clicked(pos):
                    return "play"
                if buttons[1].is_clicked(pos):
                    return "leaderboard"
                if buttons[2].is_clicked(pos):
                    return "settings"
                if buttons[3].is_clicked(pos):
                    pygame.quit()
                    sys.exit()

def show_settings_screen(screen, width, height):
    settings = load_settings()
    colors = ["red", "blue", "green", "yellow"]
    difficulties = ["easy", "normal", "hard"]
    color_index = colors.index(settings.get("car_color", "red")) if settings.get("car_color") in colors else 0
    diff_index = difficulties.index(settings.get("difficulty", "normal")) if settings.get("difficulty") in difficulties else 1

    back_btn = Button(width//2 - 60, 500, 120, 45, "BACK", (100, 100, 100), (150, 150, 150))
    sound_btn = Button(width//2 - 120, 200, 240, 50, f"Sound: {'ON' if settings['sound'] else 'OFF'}", 
                       (50, 150, 50), (80, 200, 80))
    color_btn = Button(width//2 - 120, 280, 240, 50, f"Car: {colors[color_index]}",
                       (50, 100, 150), (80, 140, 200))
    diff_btn = Button(width//2 - 120, 360, 240, 50, f"Mode: {difficulties[diff_index]}",
                      (150, 150, 50), (200, 200, 80))

    clock = pygame.time.Clock()
    while True:
        draw_gradient(screen, (20, 20, 30), (40, 40, 60), width, height)

        title = title_font.render("SETTINGS", True, WHITE)
        screen.blit(title, (width//2 - title.get_width()//2, 50))

        # Draw color preview
        color_map = {"red": RED, "blue": BLUE, "green": GREEN, "yellow": YELLOW}
        preview_color = color_map.get(colors[color_index], RED)
        pygame.draw.rect(screen, preview_color, (width//2 + 130, 290, 30, 30), border_radius=5)

        mouse_pos = pygame.mouse.get_pos()
        for btn in [sound_btn, color_btn, diff_btn, back_btn]:
            btn.update(mouse_pos)
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if sound_btn.is_clicked(pos):
                    settings["sound"] = not settings["sound"]
                    sound_btn.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
                elif color_btn.is_clicked(pos):
                    color_index = (color_index + 1) % len(colors)
                    settings["car_color"] = colors[color_index]
                    color_btn.text = f"Car: {colors[color_index]}"
                elif diff_btn.is_clicked(pos):
                    diff_index = (diff_index + 1) % len(difficulties)
                    settings["difficulty"] = difficulties[diff_index]
                    diff_btn.text = f"Mode: {difficulties[diff_index]}"
                elif back_btn.is_clicked(pos):
                    save_settings(settings)
                    return settings

def show_game_over_screen(screen, width, height, score, distance, coins):
    retry_btn = Button(width//2 - 130, 380, 110, 45, "RETRY", (50, 200, 50), (80, 255, 80))
    menu_btn = Button(width//2 + 20, 380, 130, 45, "MENU", (200, 50, 50), (255, 80, 80))
    clock = pygame.time.Clock()

    # Animation variables
    scale = 0.1
    target_scale = 1.0

    while True:
        draw_gradient(screen, (30, 10, 10), (60, 20, 20), width, height)

        # Animated title
        scale += (target_scale - scale) * 0.1
        over_text = title_font.render("GAME OVER", True, RED)
        scaled_w = int(over_text.get_width() * scale)
        scaled_h = int(over_text.get_height() * scale)
        scaled = pygame.transform.scale(over_text, (scaled_w, scaled_h))
        screen.blit(scaled, (width//2 - scaled_w//2, 40))

        # Stats with icons
        stats_lines = [
            (f"Score: {score}", YELLOW),
            (f"Distance: {distance}m", GREEN),
            (f"Coins: {coins}", ORANGE)
        ]
        y = 160
        for line, color in stats_lines:
            txt = stats_font.render(line, True, color)
            screen.blit(txt, (width//2 - txt.get_width()//2, y))
            y += 45

        mouse_pos = pygame.mouse.get_pos()
        for btn in [retry_btn, menu_btn]:
            btn.update(mouse_pos)
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if retry_btn.is_clicked(pos):
                    return "retry"
                if menu_btn.is_clicked(pos):
                    return "menu"

def show_leaderboard_screen(screen, width, height):
    board = load_leaderboard()
    back_btn = Button(width//2 - 60, 530, 120, 45, "BACK", (100, 100, 100), (150, 150, 150))
    clock = pygame.time.Clock()

    while True:
        draw_gradient(screen, (10, 20, 30), (30, 40, 60), width, height)

        title = title_font.render("TOP DRIVERS", True, YELLOW)
        screen.blit(title, (width//2 - title.get_width()//2, 30))

        y = 100
        if not board:
            msg = small_font.render("No entries yet. Be the first!", True, WHITE)
            screen.blit(msg, (width//2 - msg.get_width()//2, y))
        else:
            # Header
            header = small_font.render(f"{'#':<4} {'NAME':<12} {'SCORE':<8} {'DIST':<8}", True, CYAN)
            screen.blit(header, (width//2 - 160, y))
            y += 35

            for i, entry in enumerate(board[:10], 1):
                color = YELLOW if i == 1 else (WHITE if i <= 3 else GRAY)
                line = small_font.render(
                    f"{i:<4} {entry['name']:<12} {entry['score']:<8} {entry['distance']:<8}", True, color)
                screen.blit(line, (width//2 - 160, y))
                y += 32

        mouse_pos = pygame.mouse.get_pos()
        back_btn.update(mouse_pos)
        back_btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(event.pos):
                    return

def get_username(screen, width, height):
    input_box = InputBox(width//2 - 120, 260, 240, 45)
    ok_btn = Button(width//2 - 60, 340, 120, 45, "START", (50, 150, 50), (80, 200, 80))
    clock = pygame.time.Clock()

    while True:
        draw_gradient(screen, (20, 20, 30), (40, 40, 60), width, height)

        title = title_font.render("DRIVER NAME", True, WHITE)
        screen.blit(title, (width//2 - title.get_width()//2, 120))

        prompt = small_font.render("Enter your name:", True, (200, 200, 200))
        screen.blit(prompt, (width//2 - prompt.get_width()//2, 220))

        input_box.draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        ok_btn.update(mouse_pos)
        ok_btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_btn.is_clicked(event.pos) and input_box.text.strip():
                    return input_box.text.strip()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and input_box.text.strip():
                    return input_box.text.strip()
