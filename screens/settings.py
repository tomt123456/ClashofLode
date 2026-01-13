import pygame
import json
import os
from screens.base import ScreenBase
from components.ui import Palette, Button, Slider

class SettingsScreen(ScreenBase):
    def __init__(self, app):
        super().__init__(app)
        self.path = "settings.json"
        self.settings = self.load_settings()
        
        self.img_background = pygame.image.load("assets/background1.png")
        self.img_background = pygame.transform.scale(self.img_background, (app.WIDTH, app.HEIGHT))
        self.title_font = pygame.font.SysFont(None, 120)
        
        # Audio Sliders
        self.music_slider = Slider(200, 200, 300, 20, self.settings.get("music_vol", 0.5))
        self.sfx_slider = Slider(200, 280, 300, 20, self.settings.get("sfx_vol", 0.5))
        
        # Keybinds
        self.rebinding = None
        self.bind_buttons = {}
        
        actions = ["rotate", "place", "fire"]
        for i, action in enumerate(actions):
            self.bind_buttons[(action, 0)] = Button(850, 200 + i*70, 180, 40, str(self.settings["binds"][action][0]))
            self.bind_buttons[(action, 1)] = Button(1050, 200 + i*70, 180, 40, str(self.settings["binds"][action][1]))
        
        self.back_btn = Button(app.WIDTH // 2 - 125, 580, 250, 80, "BACK & SAVE")

    def load_settings(self):
        default = {
            "music_vol": 0.5, "sfx_vol": 0.5,
            "binds": {
                "rotate": ["R", "Mouse 3"], 
                "place": ["SPACE", "Mouse 1"],
                "fire": ["RETURN", "Mouse 1"]
            }
        }
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                try: 
                    data = json.load(f)
                    for k in default["binds"]:
                        if k not in data["binds"] or not isinstance(data["binds"][k], list):
                            data["binds"][k] = default["binds"][k]
                    return data
                except: return default
        return default

    def save_settings(self):
        self.settings["music_vol"] = self.music_slider.val
        self.settings["sfx_vol"] = self.sfx_slider.val
        with open(self.path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def handle_event(self, event):
        if self.rebinding:
            action, idx = self.rebinding
            new_val = None
            if event.type == pygame.KEYDOWN:
                new_val = pygame.key.name(event.key).upper()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                new_val = f"Mouse {event.button}"
            
            if new_val:
                self.settings["binds"][action][idx] = new_val
                self.bind_buttons[(action, idx)].text = new_val
                self.rebinding = None
            return

        if self.back_btn.is_clicked(event):
            self.save_settings()
            self.app.set_screen("menu")

        self.music_slider.handle_event(event)
        if self.music_slider.handle_event(event):
            pygame.mixer.music.set_volume(self.music_slider.val)
            
        if self.sfx_slider.handle_event(event):
            pass

        for key, btn in self.bind_buttons.items():
            if btn.is_clicked(event):
                self.rebinding = key
                btn.text = "???"

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.back_btn.check_hover(mouse_pos)
        for btn in self.bind_buttons.values():
            btn.check_hover(mouse_pos)

    def draw(self, surface):
        surface.fill(Palette.C2)
        surface.blit(self.img_background, (0, 0))

        au_lbl = self.app.title_font.render("Audio", True, Palette.C8)
        surface.blit(au_lbl, (300, 110))
        co_lbl = self.app.title_font.render("Controls", True, Palette.C8)
        surface.blit(co_lbl, (950, 110))
        
        self.music_slider.draw(surface, self.app.font, "Music Volume")
        self.sfx_slider.draw(surface, self.app.font, "SFX Volume")

        p_lbl = self.app.font.render("Primary", True, Palette.C6)
        s_lbl = self.app.font.render("Secondary", True, Palette.C6)
        surface.blit(p_lbl, (850, 160))
        surface.blit(s_lbl, (1050, 160))

        actions = ["rotate", "place", "fire"]
        for i, action in enumerate(actions):
            lbl = self.app.font.render(f"{action.capitalize()}:", True, Palette.C8)
            surface.blit(lbl, (750, 200 + i*70 + 10))
            self.bind_buttons[(action, 0)].draw(surface, self.app.font)
            self.bind_buttons[(action, 1)].draw(surface, self.app.font)

        if self.rebinding:
            overlay = pygame.Surface((self.app.WIDTH, self.app.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0,0))
            msg = self.app.title_font.render(f"Binding {self.rebinding[0]} {['Primary','Secondary'][self.rebinding[1]]}...", True, Palette.C8)
            rect = msg.get_rect(center=(self.app.WIDTH//2, self.app.HEIGHT//2))
            surface.blit(msg, rect)

        self.back_btn.draw(surface, self.app.font)