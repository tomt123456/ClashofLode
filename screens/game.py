import pygame
from screens.base import ScreenBase

GREEN = (0, 100, 0)
BLUE = (0, 0, 100)
WHITE = (255, 255, 255)


class GameScreen(ScreenBase):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            role_text = "HOST" if self.app.network.is_host else "CLIENT"
            self.app.network.send(f"Ping from {role_text}")

    def draw(self, surface):
        bg_color = GREEN if self.app.network.is_host else BLUE
        surface.fill(bg_color)

        role_text = "HOST" if self.app.network.is_host else "CLIENT"
        txt = self.app.title_font.render(f"GAME ON! Role: {role_text}", True, WHITE)
        surface.blit(txt, (50, 150))