import pygame
from pathlib import Path
from screens.base import ScreenBase
from components.ui import Button, Palette



def load_image(filename, size=None):
    img = pygame.image.load(str(filename))
    img = img.convert_alpha() if img.get_alpha() else img.convert()
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img


class MenuScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)
        self.img_background = load_image("assets/background1.png", size=(app.WIDTH, app.HEIGHT))
        self.img_host = load_image("assets/host.png", size=(400, 400))
        self.img_join = load_image("assets/join.png", size=(400, 400))
        self.btn_host = Button(self.app.WIDTH // 2 - 650, 510, 400, 80, "HOST")
        self.btn_join = Button(self.app.WIDTH // 2 + 500 // 2, 510, 400, 80, "JOIN")
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
        self.btn_settings.check_hover(mouse_pos)
        self.quit_btn.check_hover(mouse_pos)

    def draw(self, surface):
        surface.fill(Palette.C2)
        surface.blit(self.img_background, (0,0))
        title = self.app.title_font.render("Select Mode", True, Palette.C8)
        surface.blit(title, (self.app.WIDTH // 2 - title.get_width() // 2, 100))
        if getattr(self, 'img_host', None):
            surface.blit(self.img_host, (self.app.WIDTH // 2 - 650, 150))
        if getattr(self, 'img_join', None):
            surface.blit(self.img_join, (self.app.WIDTH // 2 + 250, 150))
        self.btn_host.draw(surface, self.app.font)
        self.btn_join.draw(surface, self.app.font)
        self.btn_settings.draw(surface, self.app.font)
        self.quit_btn.draw(surface, self.app.font)