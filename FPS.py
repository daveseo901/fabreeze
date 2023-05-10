import pygame

class FPScounter:
    def __init__(self, position, size=20):
        pygame.font.init()
        self.clock = pygame.time.Clock()
        font = pygame.font.get_default_font()
        self.font = pygame.font.SysFont(font, size)
        self.color = (0,255,0)
        self.text = self.font.render(str(round(self.clock.get_fps(), 2)), True, self.color)
        self.position = position
        self.FPStotal = 0
        self.counter = 0

    def draw(self, surface):
        fps = self.clock.get_fps()
        self.text = self.font.render(str(round(fps, 2)), True, self.color)
        surface.blit(self.text, self.position)
        if self.counter < 1000000:
            self.counter += 1
            self.FPStotal += fps

    def average(self):
        return self.FPStotal / self.counter
