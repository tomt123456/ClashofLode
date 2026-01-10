import pygame
from screens.base import ScreenBase
from components.ui import Palette, draw_grid

class PrepScreen(ScreenBase):
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
        if not self.placing:
            return

        L = self.to_place[self.current_index]

        # bounds and overlap check logic
        dx, dy = (1, 0) if self.orientation == 'H' else (0, 1)
        
        # Check if out of bounds
        if self.orientation == 'H' and (cx < 0 or cx + L > self.grid_size or cy < 0 or cy >= self.grid_size): return
        if self.orientation == 'V' and (cx < 0 or cx >= self.grid_size or cy < 0 or cy + L > self.grid_size): return

        # Check for overlap
        for i in range(L):
            if self.grid[cy + i*dy][cx + i*dx] != 0:
                return

        # Place the ship
        for i in range(L):
            self.grid[cy + i*dy][cx + i*dx] = 1
        
        self.ships.append({'x': cx, 'y': cy, 'length': L, 'orient': self.orientation})
        self.current_index += 1
        
        if self.current_index >= len(self.to_place):
            self.placing = False
            # Transition logic would go here, e.g., self.app.set_screen("game")

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(Palette.C4)
        
        txt = self.app.title_font.render("Prepare your fleet!", True, Palette.C8)
        surface.blit(txt, (50, 30))

        # Draw player grid
        draw_grid(surface, self.grid_origin, self.grid_size, self.cell_size, self.grid)

        # Draw hover preview
        if self.placing:
            mx, my = pygame.mouse.get_pos()
            cx, cy = self.mouse_to_cell((mx, my))
            L = self.to_place[self.current_index]
            
            # Simple preview logic
            color = (0, 200, 0, 120)
            cells = []
            dx, dy = (1, 0) if self.orientation == 'H' else (0, 1)
            for i in range(L):
                cells.append((cx + i*dx, cy + i*dy))
            
            draw_grid(surface, self.grid_origin, self.grid_size, self.cell_size, highlight_cells=cells, highlight_color=color)

        hud = f"Placing: {self.to_place[self.current_index]} ({self.orientation})" if self.placing else "Placement complete! Press Space to Start"
        hud_txt = self.app.font.render(hud, True, Palette.C8)
        surface.blit(hud_txt, (50, 70))