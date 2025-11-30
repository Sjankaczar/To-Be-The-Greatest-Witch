import pygame
import random
from src.config import *

class Insect(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill((150, 75, 0)) # Brownish color for now
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.speed = 1
        self.direction = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1])).normalize()
        self.change_dir_timer = 0
        
    def update(self):
        # Move
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        # Change direction randomly
        self.change_dir_timer += 1
        if self.change_dir_timer > 60: # Change every second approx
            self.change_dir_timer = 0
            if random.random() < 0.5:
                self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                if self.direction.length() > 0:
                    self.direction = self.direction.normalize()
                    
        # Keep within bounds (handled by state usually, but self-correction helps)
        # For now, just let them roam freely, ExplorationState will handle culling if needed
