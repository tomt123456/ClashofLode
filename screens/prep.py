import pygame
import os
from screens.base import ScreenBase
from components.ui import Palette, draw_grid
from data.ship_data import MAP_CONFIGS

class PrepScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)
    
        # Grid configuration
        self.grid_origin = (40, 100)
        self.grid_size = getattr(app, 'selected_grid_size', 10)
        
        # Target total grid width is 540px (12 * 45)
        # We calculate cell_size dynamically so any grid fits this area
        self.cell_size = 540 // self.grid_size

        # Placement state
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ships = []  
        
        # Read from ship_data.py
        config = MAP_CONFIGS.get(self.grid_size, MAP_CONFIGS[10])
        self.available_ships = list(config["ships"])

        # Sidebar configuration - Kept at 850 as it fits the 540px grid + 40px origin well
        self.sidebar_x = 850
        self.ship_menu_rects = {}

        # Load and scale assets
        self.ship_images = {}
        # Load up to length 6, starting from 1 to support small ships
        for i in range(1, 7):
            path = os.path.join("assets", f"ship{i}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                self.ship_images[i] = pygame.transform.scale(img, (i * self.cell_size, self.cell_size))
            except pygame.error:
                # If ship1.png is missing, we can fallback to a colored square or just print
                print(f"Could not load {path}")

        # Selection State
        self.selected_ship_idx = None 
        self.orientation = 'H'

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.orientation = 'V' if self.orientation == 'H' else 'H'
            if event.key == pygame.K_SPACE and not self.available_ships:
                self.app.set_screen("game")

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Right-click to rotate
            if event.button == 3:
                self.orientation = 'V' if self.orientation == 'H' else 'H'
                return

            # Left-click logic
            if event.button == 1:
                # Check if clicking on sidebar ships
                clicked_new_ship = False
                for idx, rect in self.ship_menu_rects.items():
                    if rect.collidepoint(event.pos):
                        self.selected_ship_idx = idx
                        clicked_new_ship = True
                        break
            
                # If not sidebar, check if clicking a placed ship to move it
                if not clicked_new_ship:
                    cx, cy = self.mouse_to_cell(event.pos)
                    ship_to_pick = None
                    for i, s in enumerate(self.ships):
                        # Check if cell (cx, cy) is part of this ship
                        for j in range(s['length']):
                            sx = s['x'] + (j if s['orient'] == 'H' else 0)
                            sy = s['y'] + (j if s['orient'] == 'V' else 0)
                            if sx == cx and sy == cy:
                                ship_to_pick = i
                                break
                        if ship_to_pick is not None: break

                    if ship_to_pick is not None:
                        # Pick up the ship: remove from grid and list, make it available for placement
                        s = self.ships.pop(ship_to_pick)
                        for j in range(s['length']):
                            self.grid[s['y'] + (j if s['orient'] == 'V' else 0)][s['x'] + (j if s['orient'] == 'H' else 0)] = 0
                        
                        self.available_ships.append(s['length'])
                        self.selected_ship_idx = len(self.available_ships) - 1
                        self.orientation = s['orient']
                    
                    # If we have a selected ship and didn't just pick one up, try placing it
                    elif self.selected_ship_idx is not None:
                        # Check if click is inside grid bounds
                        cx, cy = self.mouse_to_cell(event.pos)
                        if 0 <= cx < self.grid_size and 0 <= cy < self.grid_size:
                            if self.try_place_at(event.pos):
                                self.available_ships.pop(self.selected_ship_idx)
                                self.selected_ship_idx = None
                        else:
                            # Clicked outside the grid: return ship to sidebar
                            self.selected_ship_idx = None

    def mouse_to_cell(self, pos):
        ox, oy = self.grid_origin
        mx, my = pos
        cx = (mx - ox) // self.cell_size
        cy = (my - oy) // self.cell_size
        return cx, cy

    def try_place_at(self, mouse_pos):
        cx, cy = self.mouse_to_cell(mouse_pos)
        L = self.available_ships[self.selected_ship_idx]
        
        dx, dy = (1, 0) if self.orientation == 'H' else (0, 1)
        
        # Bounds check
        if self.orientation == 'H' and (cx < 0 or cx + L > self.grid_size or cy < 0 or cy >= self.grid_size): return False
        if self.orientation == 'V' and (cx < 0 or cx >= self.grid_size or cy < 0 or cy + L > self.grid_size): return False

        # Overlap check
        for i in range(L):
            if self.grid[cy + i*dy][cx + i*dx] != 0: return False

        # Place
        for i in range(L):
            self.grid[cy + i*dy][cx + i*dx] = 1
        self.ships.append({'x': cx, 'y': cy, 'length': L, 'orient': self.orientation})
        return True

    def draw(self, surface):
        surface.fill(Palette.C4)
        
            # Title
        txt = self.app.title_font.render("Ship Selection", True, Palette.C8)
        surface.blit(txt, (50, 30))

            # 1. Draw the grid lines first
        draw_grid(surface, self.grid_origin, self.grid_size, self.cell_size)

            # 2. Draw placed ship assets
        for s in self.ships:
            self.draw_ship(surface, s['x'], s['y'], s['length'], s['orient'], is_preview=False)

            # 3. Draw Sidebar with Column Logic
        self.ship_menu_rects = {}
        sidebar_txt = self.app.font.render("Available Ships:", True, Palette.C8)
        surface.blit(sidebar_txt, (self.sidebar_x, 100))
        
        start_y = 150
        max_y = 650 
        current_x = self.sidebar_x
        current_y = start_y
        
        # Calculate column width based on the largest possible ship (length 6) 
        # and add 50px spacing
        col_spacing = 50
        max_ship_width = 6 * self.cell_size 
        col_offset = max_ship_width + col_spacing

        for i, length in enumerate(self.available_ships):
            if self.selected_ship_idx == i: continue 
            
                # Check if we need to wrap to the next column
            if current_y + self.cell_size > max_y:
                current_y = start_y
                current_x += col_offset

            rect = pygame.Rect(current_x, current_y, length * self.cell_size, self.cell_size)
            self.ship_menu_rects[i] = rect
            
                # Draw ship in menu
            if length in self.ship_images:
                    # Scale for menu display if necessary, but here we use loaded assets
                    # Note: assets are scaled to current self.cell_size in __init__
                img = self.ship_images[length]
                surface.blit(img, rect.topleft)
                
                # Advance Y for next ship
            current_y += self.cell_size + 20

            # Draw selected ship following mouse
        if self.selected_ship_idx is not None:
            mx, my = pygame.mouse.get_pos()
            length = self.available_ships[self.selected_ship_idx]
                # Center the ship on mouse
            draw_pos = (mx - self.cell_size // 2, my - self.cell_size // 2)
            
            img = self.ship_images[length].copy()
            if self.orientation == 'V':
                img = pygame.transform.rotate(img, -90)
            img.set_alpha(180)
            surface.blit(img, draw_pos)

        hud = "All ships placed! Press SPACE to start" if not self.available_ships else "Select a ship and place it. 'R' to rotate."
        hud_txt = self.app.font.render(hud, True, Palette.C8)
        surface.blit(hud_txt, (50, 70))

    def draw_ship(self, surface, gx, gy, length, orient, is_preview=False):
        if length not in self.ship_images:
                # Fallback debug square if image failed to load
            px = self.grid_origin[0] + gx * self.cell_size
            py = self.grid_origin[1] + gy * self.cell_size
            pygame.draw.rect(surface, (255, 0, 0), (px, py, self.cell_size, self.cell_size), 2)
            return
            
        img = self.ship_images[length].copy()
        
            # Calculate pixel position BEFORE rotation
        px = self.grid_origin[0] + gx * self.cell_size
        py = self.grid_origin[1] + gy * self.cell_size

        if orient == 'V':
                # Rotate -90 degrees (clockwise)
            img = pygame.transform.rotate(img, -90)
        
        if is_preview:
            img.set_alpha(150)
            
        surface.blit(img, (px, py))