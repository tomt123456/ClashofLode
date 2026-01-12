import pygame
from screens.base import ScreenBase
from components.ui import Palette

class GameEndScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)
        self.img_background = pygame.image.load("assets/background1.png")
        self.img_background = pygame.transform.scale(self.img_background, (app.WIDTH, app.HEIGHT))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            self.app.set_screen("menu")
            self.app.network.stop_host()

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(Palette.C4)
        surface.blit(self.img_background, (0, 0))
        
        result = getattr(self.app, 'game_result', "GAME OVER")
        color = (0, 255, 0) if result == "VICTORY" else (255, 0, 0)
        
        # Draw result text
        txt = self.app.title_font.render(result, True, color)
        rect = txt.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 50))
        surface.blit(txt, rect)
        
        # Draw instruction
        sub_txt = self.app.font.render("Press any key to return to menu", True, Palette.C8)
        sub_rect = sub_txt.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 50))
        surface.blit(sub_txt, sub_rect)