import pygame
import sys
from persistence import load_settings, save_settings, load_leaderboard, save_leaderboard

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (180, 180, 180)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_BG = (30, 30, 30)
LIGHT_BG = (240, 240, 240)

# Fonts
pygame.font.init()
title_font = pygame.font.SysFont("Verdana", 60, bold=True)
button_font = pygame.font.SysFont("Verdana", 36)
small_font = pygame.font.SysFont("Verdana", 24)
stats_font = pygame.font.SysFont("Verdana", 28)

class Button:
    """A clickable button with hover effect."""
    def __init__(self, x, y, w, h, text, color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, screen):
        # Draw button background
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)   # border
        # Text centered
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# ---------- Input box for username ----------
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def draw(self, screen):
        color = GREEN if self.active else GRAY
        pygame.draw.rect(screen, color, self.rect, 2)
        text_surf = small_font.render(self.text, True, BLACK)
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

# ---------- Main Menu ----------
def show_main_menu(screen, width, height):
    buttons = [
        Button(width//2 - 100, 180, 200, 50, "Play", (100, 200, 100)),
        Button(width//2 - 100, 250, 200, 50, "Leaderboard", (100, 100, 200)),
        Button(width//2 - 100, 320, 200, 50, "Settings", (200, 200, 100)),
        Button(width//2 - 100, 390, 200, 50, "Quit", (200, 100, 100))
    ]
    clock = pygame.time.Clock()
    while True:
        screen.fill(WHITE)
        # Title
        title = title_font.render("RACER GAME", True, RED)
        screen.blit(title, (width//2 - title.get_width()//2, 50))
        # Subtitle
        sub = small_font.render("TSIS 3 – Advanced Driving", True, BLUE)
        screen.blit(sub, (width//2 - sub.get_width()//2, 120))
        # Buttons
        for btn in buttons:
            btn.draw(screen)
        pygame.display.flip()
        clock.tick(30)
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

# ---------- Settings Screen ----------
def show_settings_screen(screen, width, height):
    settings = load_settings()
    colors = ["red", "blue", "green", "yellow"]
    difficulties = ["easy", "normal", "hard"]
    color_index = colors.index(settings.get("car_color", "red")) if settings.get("car_color") in colors else 0
    diff_index = difficulties.index(settings.get("difficulty", "normal")) if settings.get("difficulty") in difficulties else 1

    back_btn = Button(width//2 - 50, 480, 100, 40, "Back")
    sound_btn = Button(width//2 - 100, 180, 200, 50, f"Sound: {'ON' if settings['sound'] else 'OFF'}")
    color_btn = Button(width//2 - 100, 260, 200, 50, f"Color: {colors[color_index]}")
    diff_btn = Button(width//2 - 100, 340, 200, 50, f"Difficulty: {difficulties[diff_index]}")

    clock = pygame.time.Clock()
    while True:
        screen.fill(WHITE)
        title = title_font.render("SETTINGS", True, BLUE)
        screen.blit(title, (width//2 - title.get_width()//2, 50))
        sound_btn.draw(screen)
        color_btn.draw(screen)
        diff_btn.draw(screen)
        back_btn.draw(screen)
        pygame.display.flip()
        clock.tick(30)
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
                    color_btn.text = f"Color: {colors[color_index]}"
                elif diff_btn.is_clicked(pos):
                    diff_index = (diff_index + 1) % len(difficulties)
                    settings["difficulty"] = difficulties[diff_index]
                    diff_btn.text = f"Difficulty: {difficulties[diff_index]}"
                elif back_btn.is_clicked(pos):
                    save_settings(settings)
                    return settings

# ---------- Game Over Screen ----------
def show_game_over_screen(screen, width, height, score, distance, coins):
    retry_btn = Button(width//2 - 130, 360, 100, 40, "Retry", (100,255,100))
    menu_btn = Button(width//2 + 30, 360, 120, 40, "Main Menu", (255,100,100))
    clock = pygame.time.Clock()
    while True:
        screen.fill(WHITE)
        # Title
        over_text = title_font.render("GAME OVER", True, RED)
        screen.blit(over_text, (width//2 - over_text.get_width()//2, 50))
        # Stats (centered, nicely spaced)
        stats_lines = [
            f"Score: {score}",
            f"Distance: {distance}",
            f"Coins: {coins}"
        ]
        y = 150
        for line in stats_lines:
            txt = stats_font.render(line, True, BLACK)
            screen.blit(txt, (width//2 - txt.get_width()//2, y))
            y += 40
        # Buttons
        retry_btn.draw(screen)
        menu_btn.draw(screen)
        pygame.display.flip()
        clock.tick(30)
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

# ---------- Leaderboard Screen ----------
def show_leaderboard_screen(screen, width, height):
    board = load_leaderboard()
    back_btn = Button(width//2 - 50, 520, 100, 40, "Back")
    clock = pygame.time.Clock()
    while True:
        screen.fill(WHITE)
        title = title_font.render("LEADERBOARD", True, BLUE)
        screen.blit(title, (width//2 - title.get_width()//2, 20))
        y = 100
        if not board:
            msg = small_font.render("No entries yet.", True, BLACK)
            screen.blit(msg, (width//2 - msg.get_width()//2, y))
        else:
            header = small_font.render(f"{'Rank':<5} {'Name':<12} {'Score':<6} {'Dist':<8}", True, BLACK)
            screen.blit(header, (width//2 - 150, y))
            y += 30
            for i, entry in enumerate(board[:10], 1):
                line = small_font.render(
                    f"{i:<5} {entry['name']:<12} {entry['score']:<6} {entry['distance']:<8}", True, BLACK)
                screen.blit(line, (width//2 - 150, y))
                y += 30
        back_btn.draw(screen)
        pygame.display.flip()
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(event.pos):
                    return

# ---------- Username entry ----------
def get_username(screen, width, height):
    input_box = InputBox(width//2 - 100, 250, 200, 40)
    ok_btn = Button(width//2 - 50, 320, 100, 40, "OK")
    clock = pygame.time.Clock()
    while True:
        screen.fill(WHITE)
        prompt = small_font.render("Enter your name:", True, BLACK)
        screen.blit(prompt, (width//2 - prompt.get_width()//2, 200))
        input_box.draw(screen)
        ok_btn.draw(screen)
        pygame.display.flip()
        clock.tick(30)
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