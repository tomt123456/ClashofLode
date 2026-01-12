import pygame
from screens.base import ScreenBase
from components.ui import Palette, Button, decode_ip



class JoiningScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)
        self.user_ip = ""
        self.input_rect = pygame.Rect(200, 150, 200, 32)
        self.input_active = False
        self.connection_status = ""
        self.img_background = pygame.image.load("assets/background1.png")
        self.img_background = pygame.transform.scale(self.img_background, (app.WIDTH, app.HEIGHT))
        self.back_btn = Button(100, 500, 250, 100, "BACK")

    def handle_event(self, event):
        if self.back_btn.is_clicked(event):
            self.app.set_screen("menu")

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.input_active = self.input_rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self.connection_status = "Connecting..."
                # Decode the entered room code back to an IP
                target_ip = decode_ip(self.user_ip.strip())
                success = self.app.network.start_client(target_ip)
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
        surface.blit(self.img_background, (0, 0))

        label = self.app.font.render("Enter Room Code:", True, Palette.C8)
        surface.blit(label, (200, 120))

        color = Palette.C5 if self.input_active else Palette.C4
        pygame.draw.rect(surface, color, self.input_rect, 2)

        text_surf = self.app.font.render(self.user_ip, True, Palette.C8)
        surface.blit(text_surf, (self.input_rect.x + 5, self.input_rect.y + 5))

        self.back_btn.draw(surface, self.app.font)

        if self.connection_status:
            status_surf = self.app.font.render(self.connection_status, True, (255, 200, 200))
            surface.blit(status_surf, (200, 200))