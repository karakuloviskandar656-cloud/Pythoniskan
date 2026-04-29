import pygame
import math
import os

class MickeyClock:
    def __init__(self, screen):
        self.screen = screen
        self.center = (screen.get_width() // 2, screen.get_height() // 2)
        self.radius = 200

        # Try to load a Mickey hand image; if not found, draw one
        self.hand_img = None
        img_path = os.path.join('images', 'mickey_hand.png')
        if os.path.exists(img_path):
            self.hand_img = pygame.image.load(img_path).convert_alpha()
        if not self.hand_img:
            self.hand_img = self._make_hand_surface()

    def _make_hand_surface(self):
        surf = pygame.Surface((60, 120), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255), (30, 60), 30)
        pygame.draw.ellipse(surf, (255, 255, 255), (5, 5, 15, 40))
        pygame.draw.ellipse(surf, (255, 255, 255), (22, 0, 15, 45))
        pygame.draw.ellipse(surf, (255, 255, 255), (39, 5, 15, 40))
        pygame.draw.ellipse(surf, (255, 255, 255), (42, 35, 20, 25))
        return surf

    def update(self, current_time):
        minutes = current_time.tm_min
        seconds = current_time.tm_sec
        angle_seconds = -seconds * 6
        angle_minutes = -minutes * 6
        self.rotated_seconds = pygame.transform.rotate(self.hand_img, angle_seconds)
        self.rotated_minutes = pygame.transform.rotate(self.hand_img, angle_minutes)

    def draw(self):
        self.screen.fill((30, 30, 30))
        pygame.draw.circle(self.screen, (255, 255, 255), self.center, self.radius, 4)
        for i in range(12):
            angle = math.radians(30 * i - 90)
            x1 = self.center[0] + (self.radius - 15) * math.cos(angle)
            y1 = self.center[1] + (self.radius - 15) * math.sin(angle)
            x2 = self.center[0] + self.radius * math.cos(angle)
            y2 = self.center[1] + self.radius * math.sin(angle)
            pygame.draw.line(self.screen, (200, 200, 200), (x1, y1), (x2, y2), 2)
        for hand_surf in [self.rotated_seconds, self.rotated_minutes]:
            rect = hand_surf.get_rect(center=self.center)
            self.screen.blit(hand_surf, rect)