import sys
import pygame

from network import Network
from screens.menu import MenuScreen
from screens.hosting import HostingScreen
from screens.joining import JoiningScreen
from screens.game import GameScreen

# --- Constants & Config ---
WIDTH, HEIGHT = 1440, 720
print("🚀")

class App:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Network Game")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 50)

        self.network = Network()
        self.running = True

        self.current_screen = None
        self.set_screen("menu")

    def set_screen(self, name: str, **kwargs):
        if name == "menu":
            self.current_screen = MenuScreen(self)
        elif name == "hosting":
            self.current_screen = HostingScreen(self, host_ip_display=kwargs["host_ip_display"])
        elif name == "joining":
            self.current_screen = JoiningScreen(self)
        elif name == "game":
            self.current_screen = GameScreen(self)
        else:
            raise ValueError(f"Unknown screen: {name}")

    def run(self):
        while self.running and self.network.running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self.current_screen.handle_event(event)

            self.current_screen.update(dt)
            self.current_screen.draw(self.window)

            pygame.display.flip()

        self.network.close()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    App().run()