import pygame
import random
import math
from src.config import *

class Fairy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW) # Placeholder for fairy
        self.rect = self.image.get_rect(topleft=(x, y))
        self.start_y = y
        self.hover_offset = 0
        self.hover_speed = 0.1
        self.name = "Forest Fairy"
        
    def update(self):
        # Hover animation
        self.hover_offset += self.hover_speed
        self.rect.y = self.start_y + math.sin(self.hover_offset) * 5
        
    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))
        
        # Draw Name
        font = pygame.font.SysFont(None, 16)
        text = font.render(self.name, True, WHITE)
        screen.blit(text, (self.rect.centerx - text.get_width() // 2 + camera.camera.x, self.rect.y - 15 + camera.camera.y))
