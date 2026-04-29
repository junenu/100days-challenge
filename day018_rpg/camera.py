import pygame

import config as C


class Camera:
    def __init__(self, width=C.MAP_PX_W, height=C.MAP_PX_H):
        self.width = width
        self.height = height
        self.offset = pygame.Vector2()

    def update(self, target):
        self.offset.x = target.pos.x - C.WIDTH / 2
        self.offset.y = target.pos.y - C.HEIGHT / 2
        self.offset.x = max(0, min(self.offset.x, self.width - C.WIDTH))
        self.offset.y = max(0, min(self.offset.y, self.height - C.HEIGHT))

    def apply(self, rect):
        return rect.move(-self.offset.x, -self.offset.y)

    def to_screen(self, pos):
        return pygame.Vector2(pos.x - self.offset.x, pos.y - self.offset.y)
