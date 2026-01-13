import pygame

from screens.base import ScreenBase
from components.ui import Palette, Button, encode_ip


class HostingScreen(ScreenBase):
    def __init__(self, app, host_ip_display: str):
        print("host init")
        super().__init__(app)
        self.host_ip_display = host_ip_display
        self.title_font = pygame.font.Font(None, 60)
        self.img_background = pygame.image.load("assets/background1.png")
        self.img_background = pygame.transform.scale(self.img_background, (app.WIDTH, app.HEIGHT))
        self.back_btn = Button(app.WIDTH // 2 - 125, 500, 250, 100, "BACK")
        self.room_code = encode_ip(self.host_ip_display)

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

        msg1 = self.app.title_font.render("Waiting for player...", True, Palette.C8)
        msg2 = self.app.title_font.render(f"Room Code: {self.room_code.upper()}", True, Palette.C8)
        surface.blit(msg1, (550, 150))
        surface.blit(msg2, (550, 200))
        self.back_btn.draw(surface, self.app.font)