import pygame
from screens.base import ScreenBase
from components.ui import Palette, draw_grid


class GameScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)

        # Grid configuration
        self.grid_origin = (40, 100)
        self.grid_size = getattr(app, 'selected_grid_size', 10)
        self.cell_size = 40 if self.grid_size <= 10 else 30

        # Game state (receives grid and ships from PrepScreen eventually)
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.enemy_grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ships = []
        self.my_turn = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                role_text = "HOST" if self.app.network.is_host else "CLIENT"
                self.app.network.send(f"Ping from {role_text}")

    def draw(self, surface):
        bg_color = Palette.C4
        surface.fill(bg_color)

        role_text = "HOST" if getattr(self.app, 'network', None) and self.app.network.is_host else "CLIENT"
        txt = self.app.title_font.render(f"GAME ON! Role: {role_text}", True, Palette.C8)
        surface.blit(txt, (50, 30))

        # Draw player grid
        draw_grid(surface, self.grid_origin, self.grid_size, self.cell_size, self.grid)

        # Draw opponent grid
        enemy_origin = (self.grid_origin[0] + self.grid_size * self.cell_size + 100, self.grid_origin[1])
        draw_grid(surface, enemy_origin, self.grid_size, self.cell_size, self.enemy_grid)

        