import pygame

from screens.base import ScreenBase
from components.ui import Palette, Button


class HostingScreen(ScreenBase):
    def __init__(self, app, host_ip_display: str):
        super().__init__(app)
        self.host_ip_display = host_ip_display
        self.img_background = pygame.image.load("assets/background1.png")
        self.img_background = pygame.transform.scale(self.img_background, (app.WIDTH, app.HEIGHT))
        self.back_btn = Button(100, 500, 250, 100, "BACK")

    def handle_event(self, event):
        if self.back_btn.is_clicked(event):
            self.app.set_screen("menu")
            self.app.network.stop_host()

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.back_btn.check_hover(mouse_pos)

        if self.app.network.connected:
            self.app.set_screen("gamesize")

    def draw(self, surface):
        surface.fill(Palette.C2)
        surface.blit(self.img_background, (0, 0))

        msg1 = self.app.font.render("Waiting for player...", True, Palette.C8)
        msg2 = self.app.font.render(f"Your IP: {self.host_ip_display}", True, Palette.C8)
        surface.blit(msg1, (50, 150))
        surface.blit(msg2, (50, 200))
        self.back_btn.draw(surface, self.app.font)