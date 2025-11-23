import pygame
import random
from src.config import *

class ForestCreature(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(RED)
        
        # Render name
        font = pygame.font.SysFont(None, 12)
        text = font.render("Enemy", True, WHITE)
        text_rect = text.get_rect(center=(TILE_SIZE // 2, TILE_SIZE // 2))
        self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.velocity = 2
        self.move_timer = 0
        self.direction = (0, 0)

    def update(self):
        self.move_timer += 1
        if self.move_timer > 60: # Change direction every 60 frames
            self.move_timer = 0
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)])
        
        self.rect.x += self.direction[0] * self.velocity
        self.rect.y += self.direction[1] * self.velocity

        # Keep on screen - REMOVED for infinite map
        # if self.rect.left < 0:
        #     self.rect.left = 0
        #     self.direction = (-self.direction[0], self.direction[1])
        # if self.rect.right > SCREEN_WIDTH:
        #     self.rect.right = SCREEN_WIDTH
        #     self.direction = (-self.direction[0], self.direction[1])
        # if self.rect.top < 0:
        #     self.rect.top = 0
        #     self.direction = (self.direction[0], -self.direction[1])
        # if self.rect.bottom > SCREEN_HEIGHT:
        #     self.rect.bottom = SCREEN_HEIGHT
        #     self.direction = (self.direction[0], -self.direction[1])
