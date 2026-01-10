import pygame
from screens.base import ScreenBase
from components.ui import Palette, draw_grid


class GameScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)

        # Grid configuration
        self.grid_origin = (40, 100)
        self.grid_size = getattr(app, 'selected_grid_size', 10)
        self.cell_size = 540 // self.grid_size
        self.enemy_origin = (self.grid_origin[0] + self.grid_size * self.cell_size + 100, self.grid_origin[1])

        # Game state
        self.grid = getattr(app, 'player_grid', [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)])
        self.enemy_grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ships = getattr(app, 'player_ships', [])
        self.enemy_ships = [] # We'll store known sunken ships here
        self.my_turn = self.app.network.is_host

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.my_turn:
            mx, my = event.pos
            ex, ey = self.enemy_origin
            
            # Check if click is inside enemy grid
            cx = (mx - ex) // self.cell_size
            cy = (my - ey) // self.cell_size

            if 0 <= cx < self.grid_size and 0 <= cy < self.grid_size:
                # Only allow clicking on unknown cells (0)
                if self.enemy_grid[cy][cx] == 0:
                    self.app.network.send(f"SHOT:{cx},{cy}")

    def update(self, dt):
        msg = self.app.network.receive()
        if not msg:
            return

        if msg.startswith("SHOT:"):
            # Opponent shot at us
            _, coords = msg.split(":")
            cx, cy = map(int, coords.split(","))
            
            if self.grid[cy][cx] == 1 or self.grid[cy][cx] == 2: # Hit or already Hit
                self.grid[cy][cx] = 2 
                
                # Check if the ship this cell belongs to is sunk
                sunk_data = self._check_if_sunk(cx, cy, self.grid, self.ships)
                if sunk_data:
                    self.app.network.send(f"RES:{cx},{cy},SUNK,{sunk_data}")
                    # Check if all our ships are sunk
                    if self._all_ships_sunk(self.grid, self.ships):
                        self.app.game_result = "DEFEAT"
                        self.app.set_screen("game_end")
                else:
                    self.app.network.send(f"RES:{cx},{cy},HIT")
                self.my_turn = False
            else: # Miss
                self.grid[cy][cx] = 3 # Mark as miss
                self.app.network.send(f"RES:{cx},{cy},MISS")
                self.my_turn = True

        elif msg.startswith("RES:"):
            # Result of our shot
            _, data = msg.split(":")
            parts = data.split(",")
            cx, cy, result = int(parts[0]), int(parts[1]), parts[2]
            
            if result == "HIT":
                self.enemy_grid[cy][cx] = 2
                self.my_turn = True
            elif result == "SUNK":
                self.enemy_grid[cy][cx] = 2
                # parts[3:] contains x, y, len, orient
                ship_info = {'x': int(parts[3]), 'y': int(parts[4]), 'length': int(parts[5]), 'orient': parts[6]}
                self.enemy_ships.append(ship_info)
                
                # Check if we won
                config = self.app.selected_grid_size if hasattr(self.app, 'selected_grid_size') else 10
                from data.ship_data import MAP_CONFIGS
                total_ships = len(MAP_CONFIGS.get(config, MAP_CONFIGS[10])["ships"])
                if len(self.enemy_ships) >= total_ships:
                    self.app.game_result = "VICTORY"
                    self.app.set_screen("game_end")
                
                self.my_turn = True
            else:
                self.enemy_grid[cy][cx] = 3
                self.my_turn = False

    def _all_ships_sunk(self, grid, ships):
        for s in ships:
            for i in range(s['length']):
                sx = s['x'] + (i if s['orient'] == 'H' else 0)
                sy = s['y'] + (i if s['orient'] == 'V' else 0)
                if grid[sy][sx] != 2:
                    return False
        return True

    def _check_if_sunk(self, cx, cy, grid, ships):
        for s in ships:
            ship_cells = []
            for i in range(s['length']):
                scx = s['x'] + (i if s['orient'] == 'H' else 0)
                scy = s['y'] + (i if s['orient'] == 'V' else 0)
                ship_cells.append((scx, scy))
            
            if (cx, cy) in ship_cells:
                if all(grid[y][x] == 2 for x, y in ship_cells):
                    return f"{s['x']},{s['y']},{s['length']},{s['orient']}"
        return None

    def draw(self, surface):
        bg_color = Palette.C4
        surface.fill(bg_color)

        role_text = "HOST" if getattr(self.app, 'network', None) and self.app.network.is_host else "CLIENT"
        turn_text = "YOUR TURN" if self.my_turn else "OPPONENT'S TURN"
        txt = self.app.title_font.render(f"{role_text} - {turn_text}", True, Palette.C8)
        surface.blit(txt, (50, 30))

        # Draw player grid
        draw_grid(surface, self.grid_origin, self.grid_size, self.cell_size, self.grid)

        # Draw opponent grid
        draw_grid(surface, self.enemy_origin, self.grid_size, self.cell_size, self.enemy_grid)

        # Draw sunken ships indicators
        # Player sunken ships
        for s in self.ships:
            if all(self.grid[s['y'] + (i if s['orient'] == 'V' else 0)][s['x'] + (i if s['orient'] == 'H' else 0)] == 2 for i in range(s['length'])):
                self._draw_sunken_visual(surface, self.grid_origin, s)

        # Enemy sunken ships
        for s in self.enemy_ships:
            self._draw_sunken_visual(surface, self.enemy_origin, s)

        # Draw Hover effect and Status overlays
        mx, my = pygame.mouse.get_pos()
        
        # Enemy Grid Hover
        ex, ey = self.enemy_origin
        ecx = (mx - ex) // self.cell_size
        ecy = (my - ey) // self.cell_size
        
        if self.my_turn and 0 <= ecx < self.grid_size and 0 <= ecy < self.grid_size:
            if self.enemy_grid[ecy][ecx] == 0:
                hover_rect = (ex + ecx * self.cell_size, ey + ecy * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(surface, (255, 255, 255, 100), hover_rect, 2)

        # Visual Feedback for Hits/Misses on both grids
        for gy in range(self.grid_size):
            for gx in range(self.grid_size):
                # Player Grid results
                self._draw_cell_status(surface, self.grid_origin, gx, gy, self.grid[gy][gx])
                # Enemy Grid results
                self._draw_cell_status(surface, self.enemy_origin, gx, gy, self.enemy_grid[gy][gx])

    def _draw_sunken_visual(self, surface, origin, ship):
        ox, oy = origin
        px = ox + ship['x'] * self.cell_size
        py = oy + ship['y'] * self.cell_size
        w = (ship['length'] if ship['orient'] == 'H' else 1) * self.cell_size
        h = (ship['length'] if ship['orient'] == 'V' else 1) * self.cell_size
        
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, 60)) # Semi-transparent red
        surface.blit(overlay, (px, py))
        pygame.draw.rect(surface, (150, 0, 0), (px, py, w, h), 3)

    def _draw_cell_status(self, surface, origin, gx, gy, status):
        if status < 2: return # 0=empty, 1=ship
        
        ox, oy = origin
        px = ox + gx * self.cell_size
        py = oy + gy * self.cell_size
        center = (px + self.cell_size // 2, py + self.cell_size // 2)
        
        if status == 2: # HIT
            pygame.draw.line(surface, (255, 0, 0), (px, py), (px + self.cell_size, py + self.cell_size), 3)
            pygame.draw.line(surface, (255, 0, 0), (px + self.cell_size, py), (px, py + self.cell_size), 3)
        elif status == 3: # MISS
            pygame.draw.circle(surface, (200, 200, 200), center, self.cell_size // 4)