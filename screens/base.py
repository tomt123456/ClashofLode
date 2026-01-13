class ScreenBase:
    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, surface):
        pass