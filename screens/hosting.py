from screens.base import ScreenBase

GREEN = (0, 100, 0)
WHITE = (255, 255, 255)


class HostingScreen(ScreenBase):
    def __init__(self, app, host_ip_display: str):
        super().__init__(app)
        self.host_ip_display = host_ip_display

    def update(self, dt):
        if self.app.network.connected:
            self.app.set_screen("game")

    def draw(self, surface):
        surface.fill(GREEN)
        msg1 = self.app.font.render("Waiting for player...", True, WHITE)
        msg2 = self.app.font.render(f"Your IP: {self.host_ip_display}", True, WHITE)
        surface.blit(msg1, (50, 150))
        surface.blit(msg2, (50, 200))