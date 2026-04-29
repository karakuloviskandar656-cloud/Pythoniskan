import pygame
import sys
from player import MusicPlayer

def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Music Player")
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    player = MusicPlayer()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()
                elif event.key == pygame.K_s:
                    player.stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.prev_track()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        screen.fill((30, 30, 30))

        # Display playlist info
        track_name = player.get_current_track_name()
        status = "Playing" if player.playing and not player.paused else "Paused" if player.paused else "Stopped"

        text1 = font.render(f"Track: {track_name or 'None'}", True, (255, 255, 255))
        text2 = font.render(f"Status: {status}", True, (255, 255, 255))
        text3 = font.render("[P]lay  [S]top  [N]ext  [B]ack  [Q]uit", True, (200, 200, 200))

        screen.blit(text1, (20, 30))
        screen.blit(text2, (20, 70))
        screen.blit(text3, (20, 120))

        # Progress (optional)
        progress = player.get_progress()
        if progress:
            pos, _ = progress
            progress_text = font.render(f"Time: {int(pos)}s", True, (200, 200, 200))
            screen.blit(progress_text, (20, 160))

        pygame.display.flip()
        clock.tick(10)

if __name__ == '__main__':
    main()