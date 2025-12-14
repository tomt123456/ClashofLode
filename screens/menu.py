import pygame
from screens.base import ScreenBase
from ui import Button
from ui import Palette as c


class MenuScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)
        self.btn_host = Button(100, 200, 150, 50, "HOST")
        self.btn_join = Button(350, 200, 150, 50, "JOIN")

    def handle_event(self, event):
        if self.btn_host.is_clicked(event):
            host_ip = self.app.network.start_host()
            self.app.set_screen("hosting", host_ip_display=host_ip)

        if self.btn_join.is_clicked(event):
            self.app.set_screen("joining")

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_host.check_hover(mouse_pos)
        self.btn_join.check_hover(mouse_pos)

    def draw(self, surface):
        surface.fill(c.C2)
        title = self.app.title_font.render("Select Mode", True, c.C8)
        surface.blit(title, (self.app.WIDTH // 2 - title.get_width() // 2, 100))
        self.btn_host.draw(surface, self.app.font)
        self.btn_join.draw(surface, self.app.font)