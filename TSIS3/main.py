import pygame
import sys
from persistence import load_settings, save_leaderboard
from ui import (show_main_menu, show_settings_screen, show_game_over_screen,
                show_leaderboard_screen, get_username)
from racer import Game

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("TSIS 3 - Racer Game")
    clock = pygame.time.Clock()

    settings = load_settings()

    while True:
        action = show_main_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        if action == "play":
            username = get_username(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            game = Game(settings)
            stats = game.run()

            if stats:
                entry = {
                    'name': username,
                    'score': stats['score'],
                    'distance': stats['distance']
                }
                save_leaderboard(entry)

                choice = show_game_over_screen(
                    screen, SCREEN_WIDTH, SCREEN_HEIGHT,
                    stats['score'], stats['distance'], stats['coins']
                )

                if choice == "retry":
                    continue
                else:
                    continue

        elif action == "settings":
            settings = show_settings_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        elif action == "leaderboard":
            show_leaderboard_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

if __name__ == '__main__':
    main()
