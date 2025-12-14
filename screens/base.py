class ScreenBase:
    def __init__(self, app):
        self.app = app  # access to app (fonts, window, network, set_screen)

    def handle_event(self, event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, surface):
        pass