import pygame
from src.config import *

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, name, color=YELLOW):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE)) # Made it full tile size for visibility
        self.image.fill(color)
        
        # Render name
        font = pygame.font.SysFont(None, 12)
        text = font.render(name, True, BLACK)
        text_rect = text.get_rect(center=(TILE_SIZE // 2, TILE_SIZE // 2))
        self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.name = name
