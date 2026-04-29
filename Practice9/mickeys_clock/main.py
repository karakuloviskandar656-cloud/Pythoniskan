import pygame
import sys
import time
from clock import MickeyClock

def main():
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Mickey's Clock")
    clock_obj = MickeyClock(screen)
    fps_clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        now = time.localtime()
        clock_obj.update(now)
        clock_obj.draw()
        pygame.display.flip()
        fps_clock.tick(1)

if __name__ == '__main__':
    main()