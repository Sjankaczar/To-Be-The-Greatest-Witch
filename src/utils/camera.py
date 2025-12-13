import pygame
from src.config import *

class Camera:
    def __init__(self, width, height, viewport_width=SCREEN_WIDTH, viewport_height=SCREEN_HEIGHT):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def apply_pos(self, pos):
        return (pos[0] + self.camera.x, pos[1] + self.camera.y)

    def update(self, target):
        if hasattr(target, 'rect'):
            target_rect = target.rect
        else:
            target_rect = target
            
        x = -target_rect.centerx + int(self.viewport_width / 2)
        y = -target_rect.centery + int(self.viewport_height / 2)

        # Clamp to bounds
        # min limit (top-left) is 0
        # max limit (bottom-right) is -(map_width - viewport_width)
        x = min(0, x)  # left side
        y = min(0, y)  # top side
        x = max(-(self.width - self.viewport_width), x)  # right side
        y = max(-(self.height - self.viewport_height), y)  # bottom side

        self.camera = pygame.Rect(x, y, self.width, self.height)

    def update_bounds(self, width, height):
        self.width = width
        self.height = height
