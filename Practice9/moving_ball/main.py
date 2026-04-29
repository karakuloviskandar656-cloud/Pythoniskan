import pygame
import sys
from ball import Ball

def main():
    pygame.init()
    width, height = 600, 400
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Moving Red Ball")
    clock = pygame.time.Clock()

    ball = Ball(width // 2, height // 2, 25, (255, 0, 0), 20)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    ball.move(0, -1, width, height)
                elif event.key == pygame.K_DOWN:
                    ball.move(0, 1, width, height)
                elif event.key == pygame.K_LEFT:
                    ball.move(-1, 0, width, height)
                elif event.key == pygame.K_RIGHT:
                    ball.move(1, 0, width, height)

        screen.fill((255, 255, 255))
        ball.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()