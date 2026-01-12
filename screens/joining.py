import pygame
from screens.base import ScreenBase
from components.ui import Palette, Button

def load_image(filename, size=None):
    img = pygame.image.load(str(filename))
    img = img.convert_alpha() if img.get_alpha() else img.convert()
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img

class JoiningScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)
        self.user_ip = ""
        self.input_rect = pygame.Rect(200, 150, 200, 32)
        self.input_active = False
        self.connection_status = ""
        self.img_back = load_image('assets/background1.png', (app.WIDTH, app.HEIGHT))
        self.back_btn = Button(100, 500, 250, 100, "BACK")

    def handle_event(self, event):
        if self.back_btn.is_clicked(event):
            self.app.set_screen("menu")

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.input_active = self.input_rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self.connection_status = "Connecting..."
                success = self.app.network.start_client(self.user_ip)
                if not success:
                    self.connection_status = "Failed. Try again."
            elif event.key == pygame.K_BACKSPACE:
                self.user_ip = self.user_ip[:-1]
            else:
                self.user_ip += event.unicode

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.back_btn.check_hover(mouse_pos)
        msg = self.app.network.receive()
        if msg and msg.startswith("START_GAME|"):
            try:
                size = int(msg.split("|")[1])
                self.app.selected_grid_size = size
                self.app.set_screen("prep")
            except ValueError:
                pass

    def draw(self, surface):
        surface.fill(Palette.C2)
        surface.blit(self.img_back, (0, 0))

        label = self.app.font.render("Enter Host IP:", True, Palette.C8)
        surface.blit(label, (200, 120))

        color = Palette.C5 if self.input_active else Palette.C4
        pygame.draw.rect(surface, color, self.input_rect, 2)

        text_surf = self.app.font.render(self.user_ip, True, Palette.C8)
        surface.blit(text_surf, (self.input_rect.x + 5, self.input_rect.y + 5))

        self.back_btn.draw(surface, self.app.font)

        if self.connection_status:
            status_surf = self.app.font.render(self.connection_status, True, (255, 200, 200))
            surface.blit(status_surf, (200, 200))