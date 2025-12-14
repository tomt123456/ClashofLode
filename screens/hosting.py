from screens.base import ScreenBase
from ui import Palette as c


class HostingScreen(ScreenBase):
    def __init__(self, app, host_ip_display: str):
        super().__init__(app)
        self.host_ip_display = host_ip_display

    def update(self, dt):
        if self.app.network.connected:
            self.app.set_screen("game")

    def draw(self, surface):
        surface.fill(c.C2)
        msg1 = self.app.font.render("Waiting for player...", True, c.C8)
        msg2 = self.app.font.render(f"Your IP: {self.host_ip_display}", True, c.C8)
        surface.blit(msg1, (50, 150))
        surface.blit(msg2, (50, 200))