import pygame
from screens.base import ScreenBase
from components.ui import Palette, Button

class SettingsScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)
        self.img_background = pygame.image.load("assets/background1.png")
        self.img_background = pygame.transform.scale(self.img_background, (app.WIDTH, app.HEIGHT))
        self.back_btn = Button(100, 500, 250, 100, "BACK")

    def handle_event(self, event):
        if self.back_btn.is_clicked(event):
            self.app.set_screen("menu")

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.back_btn.check_hover(mouse_pos)


    def draw(self, surface):
        surface.fill(Palette.C2)
        surface.blit(self.img_background, (0, 0))
        self.back_btn.draw(surface, self.app.font)