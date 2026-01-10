import pygame
from screens.base import ScreenBase
from components.ui import Button, Palette

class HostSettingsScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)
        self.buttons = [
            Button(200, 150, 250, 50, "Small (8x8)"),
            Button(200, 220, 250, 50, "Medium (10x10)"),
            Button(200, 290, 250, 50, "Large (12x12)"),
            Button(200, 360, 250, 50, "Massive (15x15)"),
            Button(200, 450, 250, 50, "Start Game")
        ]
        self.selected_size = 10

    def handle_event(self, event):
        pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.check_hover(pos)
            if btn.is_clicked(event):
                if "Small" in btn.text: self.selected_size = 8
                elif "Medium" in btn.text: self.selected_size = 10
                elif "Large" in btn.text: self.selected_size = 12
                elif "Massive" in btn.text: self.selected_size = 15
                elif "Start" in btn.text:
                    # Notify Client
                    self.app.network.send(f"START_GAME|{self.selected_size}")
                    self.app.selected_grid_size = self.selected_size
                    self.app.set_screen("prep")

    def draw(self, surface):
        surface.fill(Palette.C3)
        title = self.app.title_font.render(f"Host Settings - Grid: {self.selected_size}x{self.selected_size}", True, Palette.C8)
        surface.blit(title, (100, 100))
        for btn in self.buttons:
            btn.draw(surface, self.app.font)