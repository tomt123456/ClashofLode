import pygame


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.is_hovered = False

    def draw(self, screen, font):
        color = Palette.C3 if self.is_hovered else Palette.C4
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        text_surf = font.render(self.text, True, Palette.C8)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, event):
        return self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

class Palette:
    C1 = (0, 0, 0)  # Black
    C2 = (22, 25, 37)  # Shadow Gray
    C3 = (28, 37, 65)  # Space Indigo
    C4 = (64, 110, 142)  # Rich Cerulean
    C5 = (0,126,167) # Cerulean
    C6 = (180,197,228) # Powder Blue
    C7 = (204, 219, 220)  # Alabaster Grey
    C8 = (255,255,255) # White
