import pygame
from screens.base import ScreenBase
from components.ui import Button, Palette


class MenuScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)
        self.img_host = pygame.image.load("assets/host.png")
        self.img_join = pygame.image.load("assets/join.png")
        self.btn_host = Button(self.app.WIDTH // 2 - 250 - 250 // 2, 420, 250, 80, "HOST")
        self.btn_join = Button(self.app.WIDTH // 2 + 250 - 250 // 2, 420, 250, 80, "JOIN")
        self.btn_settings = Button(self.app.WIDTH // 2 - 250 // 2,  510, 250, 80, "SETTINGS")
        self.quit_btn = Button(self.app.WIDTH // 2 - 250 // 2, 600, 250, 80, "QUIT")

    def handle_event(self, event):
        if self.btn_host.is_clicked(event):
            host_ip = self.app.network.start_host()
            self.app.set_screen("hosting", host_ip_display=host_ip)

        if self.btn_join.is_clicked(event):
            self.app.set_screen("joining")

        if self.quit_btn.is_clicked(event):
            self.app.running = False

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_host.check_hover(mouse_pos)
        self.btn_join.check_hover(mouse_pos)
        self.quit_btn.check_hover(mouse_pos)

    def draw(self, surface):
        surface.fill(Palette.C2)
        title = self.app.title_font.render("Select Mode", True, Palette.C8)
        surface.blit(title, (self.app.WIDTH // 2 - title.get_width() // 2, 100))
        surface.blit(self.img_host, (self.app.WIDTH // 3 + 250, 200))
        surface.blit(self.img_join, (self.app.WIDTH // 3 - 250 + self.app.WIDTH // 3, 200))
        self.btn_host.draw(surface, self.app.font)
        self.btn_join.draw(surface, self.app.font)
        self.btn_settings.draw(surface, self.app.font)
        self.quit_btn.draw(surface, self.app.font)