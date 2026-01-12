import pygame
import os
import random
from screens.base import ScreenBase
from components.ui import Palette, draw_grid, Button
from data.ship_data import MAP_CONFIGS

class PrepScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)
        self.img_background = pygame.image.load("assets/background2.png")
        self.img_background = pygame.transform.scale(self.img_background, (app.WIDTH, app.HEIGHT))
    
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

        # Ready state
        self.is_ready = False
        self.opponent_ready = False
        self.ready_btn = Button(self.sidebar_x, 660, 180, 40, "Ready")
        self.random_btn = Button(self.sidebar_x, 600, 180, 40, "Randomize")

    def handle_event(self, event):
        if self.is_ready: # Block placement once ready
            return

        # Helper to check if an event matches a set of binds
        def check_bind(action):
            binds = self.app.settings["binds"][action]
            if event.type == pygame.KEYDOWN:
                return pygame.key.name(event.key).upper() in binds
            if event.type == pygame.MOUSEBUTTONDOWN:
                return f"Mouse {event.button}" in binds
            return False

        # 1. Check Rotation binds
        if check_bind("rotate"):
            self.orientation = 'V' if self.orientation == 'H' else 'H'
            return

        # 2. Check UI Buttons (Randomize/Ready) - these always use Mouse 1
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.random_btn.is_clicked(event):
                self.randomize_ships()
                return 

            if not self.available_ships and self.ready_btn.is_clicked(event):
                self.is_ready = True
                self.app.network.send("READY")
                return

        # 3. Placement Action (Pickup / Place / Sidebar Select)
        if check_bind("place"):
            # We need the current mouse position for these checks
            m_pos = pygame.mouse.get_pos()
            
            # A. Check if clicking on sidebar ships
            clicked_new_ship = False
            for idx, rect in self.ship_menu_rects.items():
                if rect.collidepoint(m_pos):
                    self.selected_ship_idx = idx
                    clicked_new_ship = True
                    break
    
            if not clicked_new_ship:
                cx, cy = self.mouse_to_cell(m_pos)
                
                # B. Try picking up a ship from the grid
                ship_to_pick = None
                for i, s in enumerate(self.ships):
                    for j in range(s['length']):
                        sx = s['x'] + (j if s['orient'] == 'H' else 0)
                        sy = s['y'] + (j if s['orient'] == 'V' else 0)
                        if sx == cx and sy == cy:
                            ship_to_pick = i
                            break
                    if ship_to_pick is not None: break

                if ship_to_pick is not None:
                    s = self.ships.pop(ship_to_pick)
                    for j in range(s['length']):
                        self.grid[s['y'] + (j if s['orient'] == 'V' else 0)][s['x'] + (j if s['orient'] == 'H' else 0)] = 0
                    self.available_ships.append(s['length'])
                    self.selected_ship_idx = len(self.available_ships) - 1
                    self.orientation = s['orient']
            
                # C. Try placing the currently selected ship
                elif self.selected_ship_idx is not None:
                    if 0 <= cx < self.grid_size and 0 <= cy < self.grid_size:
                        if self.try_place_at(m_pos):
                            self.available_ships.pop(self.selected_ship_idx)
                            self.selected_ship_idx = None
                    else:
                        # Clicked outside grid: Put it back
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
        
        return self.place_ship_logic(cx, cy, L, self.orientation)

    def place_ship_logic(self, cx, cy, L, orientation):
        dx, dy = (1, 0) if orientation == 'H' else (0, 1)
    
        # Bounds check
        if orientation == 'H' and (cx < 0 or cx + L > self.grid_size or cy < 0 or cy >= self.grid_size): return False
        if orientation == 'V' and (cx < 0 or cx >= self.grid_size or cy < 0 or cy + L > self.grid_size): return False

        # Overlap check
        for i in range(L):
            if self.grid[cy + i*dy][cx + i*dx] != 0: return False

        # Place
        for i in range(L):
            self.grid[cy + i*dy][cx + i*dx] = 1
        self.ships.append({'x': cx, 'y': cy, 'length': L, 'orient': orientation})
        return True

    def randomize_ships(self):
        """Clears the grid and places all ships from the current config randomly."""
        # Reset current state
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ships = []
        config = MAP_CONFIGS.get(self.grid_size, MAP_CONFIGS[10])
        
        # Use the full list from config, not the current (potentially partial) available_ships
        all_to_place = list(config["ships"])
        
        # Sort ships by length (largest first) to make placement easier
        all_to_place.sort(reverse=True)

        for length in all_to_place:
            placed = False
            attempts = 0
            while not placed and attempts < 500:
                attempts += 1
                rx = random.randint(0, self.grid_size - 1)
                ry = random.randint(0, self.grid_size - 1)
                rorient = random.choice(['H', 'V'])
                if self.place_ship_logic(rx, ry, length, rorient):
                    placed = True
                
                if not placed:
                    # Retry the whole board if we hit a dead end
                    self.randomize_ships()
                    return

            # CRITICAL: Mark all ships as used so they disappear from the sidebar
            self.available_ships = []
            self.selected_ship_idx = None

    def update(self, dt):
        # Check for network messages
        msg = self.app.network.receive()
        if msg == "READY":
            self.opponent_ready = True
        
        # If both are ready, start game
        if self.is_ready and self.opponent_ready:
            # Optionally pass ships/grid to app before switching
            self.app.player_ships = self.ships
            self.app.player_grid = self.grid
            self.app.set_screen("game")

    def draw(self, surface):
        surface.fill(Palette.C4)
        surface.blit(self.img_background, (0, 0))
        
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
                img = self.ship_images[length]
                surface.blit(img, rect.topleft)
            
            # Advance Y for next ship
            current_y += self.cell_size + 20

        # Draw Randomize Button - Now stays visible until Ready is clicked
        if not self.is_ready:
            self.random_btn.check_hover(pygame.mouse.get_pos())
            self.random_btn.draw(surface, self.app.font)

        # Draw Ready Button
        if not self.available_ships:
            self.ready_btn.check_hover(pygame.mouse.get_pos())
            if self.is_ready:
                self.ready_btn.text = "Waiting..."
            self.ready_btn.draw(surface, self.app.font)

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

        place_binds = " or ".join(self.app.settings["binds"]["place"])
        rotate_binds = " or ".join(self.app.settings["binds"]["rotate"])

        hud = f"Press {place_binds} to select/place. {rotate_binds} to rotate."

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