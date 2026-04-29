import pygame
import sys
from persistence import load_settings, save_settings, load_leaderboard, save_leaderboard

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (100, 100, 100)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)

# Fonts
pygame.font.init()
title_font = pygame.font.SysFont("Verdana", 60)
button_font = pygame.font.SysFont("Verdana", 36)
small_font = pygame.font.SysFont("Verdana", 24)

class Button:
    """A simple clickable button."""
    def __init__(self, x, y, w, h, text, color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class InputBox:
    """Simple text input for username entry."""
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

def show_main_menu(screen, width, height):
    """Display main menu and return action: 'play', 'leaderboard', 'settings', 'quit'."""
    buttons = [
        Button(width//2 - 100, 200, 200, 50, "Play"),
        Button(width//2 - 100, 280, 200, 50, "Leaderboard"),
        Button(width//2 - 100, 360, 200, 50, "Settings"),
        Button(width//2 - 100, 440, 200, 50, "Quit")
    ]
    while True:
        screen.fill(WHITE)
        title = title_font.render("RACER GAME", True, RED)
        screen.blit(title, (width//2 - title.get_width()//2, 50))
        for btn in buttons:
            btn.draw(screen)
        pygame.display.flip()
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
    """Let user toggle sound, pick car color, and difficulty. Save on exit."""
    settings = load_settings()
    colors = ["red", "blue", "green", "yellow"]
    difficulties = ["easy", "normal", "hard"]
    color_index = colors.index(settings.get("car_color", "red")) if settings.get("car_color") in colors else 0
    diff_index = difficulties.index(settings.get("difficulty", "normal")) if settings.get("difficulty") in difficulties else 1

    back_btn = Button(width//2 - 50, 500, 100, 40, "Back")
    sound_btn = Button(width//2 - 80, 200, 160, 50, f"Sound: {'ON' if settings['sound'] else 'OFF'}")
    color_btn = Button(width//2 - 100, 280, 200, 50, f"Color: {colors[color_index]}")
    diff_btn = Button(width//2 - 100, 360, 200, 50, f"Difficulty: {difficulties[diff_index]}")

    while True:
        screen.fill(WHITE)
        for btn in [sound_btn, color_btn, diff_btn, back_btn]:
            btn.draw(screen)
        pygame.display.flip()
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

def show_game_over_screen(screen, width, height, score, distance, coins):
    """Display game over screen, return 'retry' or 'menu'."""
    retry_btn = Button(width//2 - 120, 300, 100, 40, "Retry")
    menu_btn = Button(width//2 + 20, 300, 120, 40, "Main Menu")
    while True:
        screen.fill(WHITE)
        over_text = title_font.render("GAME OVER", True, RED)
        screen.blit(over_text, (width//2 - over_text.get_width()//2, 50))
        info = small_font.render(f"Score: {score}  Distance: {distance}  Coins: {coins}", True, BLACK)
        screen.blit(info, (width//2 - info.get_width()//2, 150))
        retry_btn.draw(screen)
        menu_btn.draw(screen)
        pygame.display.flip()
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
    """Display top 10 leaderboard entries."""
    board = load_leaderboard()
    back_btn = Button(width//2 - 50, 500, 100, 40, "Back")
    while True:
        screen.fill(WHITE)
        title = title_font.render("LEADERBOARD", True, BLUE)
        screen.blit(title, (width//2 - title.get_width()//2, 20))
        y = 100
        if not board:
            msg = small_font.render("No entries yet.", True, BLACK)
            screen.blit(msg, (width//2 - msg.get_width()//2, y))
        else:
            header = small_font.render(f"{'Rank':<5} {'Name':<12} {'Score':<6} {'Distance':<8}", True, BLACK)
            screen.blit(header, (width//2 - 150, y))
            y += 30
            for i, entry in enumerate(board[:10], 1):
                line = small_font.render(
                    f"{i:<5} {entry['name']:<12} {entry['score']:<6} {entry['distance']:<8}", True, BLACK)
                screen.blit(line, (width//2 - 150, y))
                y += 30
        back_btn.draw(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(event.pos):
                    return

def get_username(screen, width, height):
    """Prompt the player to enter a name."""
    input_box = InputBox(width//2 - 100, 250, 200, 40)
    ok_btn = Button(width//2 - 50, 320, 100, 40, "OK")
    while True:
        screen.fill(WHITE)
        prompt = small_font.render("Enter your name:", True, BLACK)
        screen.blit(prompt, (width//2 - prompt.get_width()//2, 200))
        input_box.draw(screen)
        ok_btn.draw(screen)
        pygame.display.flip()
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