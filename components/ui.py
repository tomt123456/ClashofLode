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


def draw_grid(surface, origin, grid_size, cell_size, grid_data=None, highlight_cells=None,
              highlight_color=(0, 200, 0, 120)):
    ox, oy = origin
    for y in range(grid_size):
        for x in range(grid_size):
            rect = pygame.Rect(ox + x * cell_size, oy + y * cell_size, cell_size, cell_size)
            pygame.draw.rect(surface, Palette.C2, rect, 1)

            # Draw placed ships if grid_data is provided
            if grid_data and grid_data[y][x] == 1:
                inner = rect.inflate(-4, -4)
                pygame.draw.rect(surface, Palette.C6, inner)

    # Draw highlights (e.g., placement preview)
    if highlight_cells:
        for (gx, gy) in highlight_cells:
            if 0 <= gx < grid_size and 0 <= gy < grid_size:
                rect = pygame.Rect(ox + gx * cell_size, oy + gy * cell_size, cell_size, cell_size)
                s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                s.fill(highlight_color)
                surface.blit(s, rect.topleft)


def encode_ip(ip: str) -> str:
    """Converts an IP address string to a Base36 room code."""
    try:
        parts = [int(p) for p in ip.split('.')]
        # Pack the 4 bytes into one integer
        val = (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
        
        # Convert to Base36
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        code = ""
        while val > 0:
            val, i = divmod(val, 36)
            code = chars[i] + code
        return code or "0"
    except (ValueError, IndexError):
        return "invalid"


def decode_ip(code: str) -> str:
    """Converts a Base36 room code back to an IP address string."""
    try:
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        val = 0
        for char in code.lower():
            val = val * 36 + chars.index(char)
        
        # Unpack the integer back into 4 bytes
        parts = [
            (val >> 24) & 0xFF,
            (val >> 16) & 0xFF,
            (val >> 8) & 0xFF,
            val & 0xFF
        ]
        return ".".join(map(str, parts))
    except (ValueError, KeyError):
        return ""
