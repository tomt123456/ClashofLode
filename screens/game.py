import pygame
from screens.base import ScreenBase
from components.ui import Palette, draw_grid


class GameScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)

        # Grid configuration
        self.grid_origin = (40, 100)
        self.grid_size = getattr(app, 'selected_grid_size', 10)
        self.cell_size = 40 if self.grid_size <= 10 else 30


        # Placement state
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ships = []  # placed ships: dicts {x,y,len,orient}
        self.to_place = [5, 4, 3, 3, 2]  # lengths to place in order
        self.current_index = 0
        self.orientation = 'H'  # 'H' or 'V'
        self.placing = True if self.to_place else False

    def handle_event(self, event):
        # Toggle orientation with R
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.orientation = 'V' if self.orientation == 'H' else 'H'
            if event.key == pygame.K_SPACE:
                role_text = "HOST" if self.app.network.is_host else "CLIENT"
                self.app.network.send(f"Ping from {role_text}")

        # Place ship on left click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.placing:
            self.try_place_at(event.pos)

        # Right-click cancels last placed ship
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.ships:
                s = self.ships.pop()
                # clear grid cells
                for i in range(s['length']):
                    gx = s['x'] + (i if s['orient'] == 'H' else 0)
                    gy = s['y'] + (i if s['orient'] == 'V' else 0)
                    self.grid[gy][gx] = 0
                # return ship to placement list
                self.current_index = max(0, self.current_index - 1)
                self.placing = True

    def mouse_to_cell(self, pos):
        ox, oy = self.grid_origin
        mx, my = pos
        cx = (mx - ox) // self.cell_size
        cy = (my - oy) // self.cell_size
        return cx, cy

    def try_place_at(self, mouse_pos):
        cx, cy = self.mouse_to_cell(mouse_pos)
        L = self.to_place[self.current_index] if self.current_index < len(self.to_place) else None
        if L is None:
            self.placing = False
            return

        # bounds check
        if self.orientation == 'H':
            if cx < 0 or cy < 0 or cx + L > self.grid_size or cy >= self.grid_size:
                return
            # overlap check
            for i in range(L):
                if self.grid[cy][cx + i] != 0:
                    return
            # place
            for i in range(L):
                self.grid[cy][cx + i] = 1
            self.ships.append({'x': cx, 'y': cy, 'length': L, 'orient': 'H'})

        else:  # vertical
            if cx < 0 or cy < 0 or cy + L > self.grid_size or cx >= self.grid_size:
                return
            for i in range(L):
                if self.grid[cy + i][cx] != 0:
                    return
            for i in range(L):
                self.grid[cy + i][cx] = 1
            self.ships.append({'x': cx, 'y': cy, 'length': L, 'orient': 'V'})

        # advance to next ship
        self.current_index += 1
        if self.current_index >= len(self.to_place):
            self.placing = False

    def draw(self, surface):
        bg_color = Palette.C4 if getattr(self.app, 'network', None) and self.app.network.is_host else Palette.C4
        surface.fill(bg_color)

        role_text = "HOST" if getattr(self.app, 'network', None) and self.app.network.is_host else "CLIENT"
        txt = self.app.title_font.render(f"GAME ON! Role: {role_text}", True, Palette.C8)
        surface.blit(txt, (50, 30))

        # Draw player grid
        draw_grid(surface, self.grid_origin, self.grid_size, self.cell_size, self.grid)

        # Draw opponent grid
        enemy_origin = (self.grid_origin[0] + self.grid_size * self.cell_size + 100, self.grid_origin[1])
        draw_grid(surface, enemy_origin, self.grid_size, self.cell_size)

        # Draw hover preview for current ship
        if self.placing:
            mx, my = pygame.mouse.get_pos()
            cx, cy = self.mouse_to_cell((mx, my))
            L = self.to_place[self.current_index]
            valid = True
            cells = []
            if self.orientation == 'H':
                for i in range(L):
                    gx = cx + i
                    gy = cy
                    if gx < 0 or gx >= self.grid_size or gy < 0 or gy >= self.grid_size or self.grid[gy][gx] != 0:
                        valid = False
                    cells.append((gx, gy))
            else:
                for i in range(L):
                    gx = cx
                    gy = cy + i
                    if gx < 0 or gx >= self.grid_size or gy < 0 or gy >= self.grid_size or self.grid[gy][gx] != 0:
                        valid = False
                    cells.append((gx, gy))

            color = (0, 200, 0, 120) if valid else (200, 0, 0, 120)
            draw_grid(surface, self.grid_origin, self.grid_size, self.cell_size, highlight_cells=cells,
                      highlight_color=color)

        # Small HUD text
        hud = f"Placing: {self.to_place[self.current_index]} ({self.orientation})" if self.placing else "Placement complete"
        hud_txt = self.app.font.render(hud, True, Palette.C8)
        surface.blit(hud_txt, (50, 70))

        