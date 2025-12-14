import pygame
from screens.base import ScreenBase
from ui import Palette as c


class GameScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)

        self.grid_img = pygame.image.load("assets/grid.png").convert_alpha()

        w, h = self.grid_img.get_size()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            role_text = "HOST" if self.app.network.is_host else "CLIENT"
            self.app.network.send(f"Ping from {role_text}")

    def draw(self, surface):
        bg_color = c.C4 if self.app.network.is_host else c.C4
        surface.fill(bg_color)

        role_text = "HOST" if self.app.network.is_host else "CLIENT"
        txt = self.app.title_font.render(f"GAME ON! Role: {role_text}", True, c.C8)
        surface.blit(txt, (50, 30))


        surface.blit(self.grid_img, (40, 100))
        surface.blit(self.grid_img, (800, 100))