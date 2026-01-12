import sys
import pygame

from network import Network
from screens.menu import MenuScreen
from screens.hosting import HostingScreen
from screens.joining import JoiningScreen
from screens.game import GameScreen
from screens.gamesize import HostSettingsScreen
from screens.settings import SettingsScreen
from screens.prep import PrepScreen
from screens.game_end import GameEndScreen
import os
import json

# --- Constants & Config ---
WIDTH, HEIGHT = 1440, 720
print("🚀")

class App:
    def __init__(self):
        pygame.init()
        # Load settings once
        self.load_app_settings()
        
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

    def load_app_settings(self):
        path = "settings.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                "music_vol": 0.5, "sfx_vol": 0.5,
                "binds": {
                    "rotate": ["R", "Mouse 3"], 
                    "place": ["SPACE", "Mouse 1"],
                    "fire": ["RETURN", "Mouse 1"]
                }
            }

    def set_screen(self, name: str, **kwargs):
        if name == "menu":
            self.current_screen = MenuScreen(self)
        elif name == "settings":
            self.current_screen = SettingsScreen(self)
        elif name == "hosting":
            self.current_screen = HostingScreen(self, host_ip_display=kwargs["host_ip_display"])
        elif name == "joining":
            self.current_screen = JoiningScreen(self)
        elif name == "prep":
            self.current_screen = PrepScreen(self)
        elif name == "gamesize":
            self.current_screen = HostSettingsScreen(self)
        elif name == "game":
            self.current_screen = GameScreen(self)
        elif name == "game_end":
            self.current_screen = GameEndScreen(self)
        else:
            raise ValueError(f"Unknown screen: {name}")

    def run(self):
        # Run until the app requests exit. Keep running even if the network marks itself stopped,
        # so UI can show errors and user can retry connecting.
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                try:
                    self.current_screen.handle_event(event)
                except Exception as e:
                    print(f"Error handling event: {e}")

            try:
                # allow screens to react to network state but don't exit the whole app on network.stop
                self.current_screen.update(dt)
                self.current_screen.draw(self.window)
            except Exception as e:
                print(f"Screen error: {e}")

            pygame.display.flip()

        # Clean up network and quit
        try:
            self.network.close()
        except Exception:
            pass
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    App().run()