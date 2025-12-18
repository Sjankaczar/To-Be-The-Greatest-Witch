import pygame
import random
from src.config import *

class ForestCreature(pygame.sprite.Sprite):
    def __init__(self, x, y, spritesheet=None):
        super().__init__()
        
        self.spritesheet = spritesheet
        self.frame_index = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        
        # Standardize Frame Size
        if self.spritesheet:
            self.sheet_w = self.spritesheet.get_width()
            self.sheet_h = self.spritesheet.get_height()
            self.cols = 8 # Assuming 8 frames per row from "Walk_full" usually
            self.rows = 4 # Assuming 4 directions
            self.frame_width = self.sheet_w // self.cols
            self.frame_height = self.sheet_h // self.rows
            
            # Initial Image
            self.image = self.spritesheet.subsurface((0, 0, self.frame_width, self.frame_height))
        else:
            # Fallback
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(RED)
            font = pygame.font.SysFont(None, 12)
            text = font.render("Enemy", True, WHITE)
            text_rect = text.get_rect(center=(TILE_SIZE // 2, TILE_SIZE // 2))
            self.image.blit(text, text_rect)
            self.frame_width = TILE_SIZE
            self.frame_height = TILE_SIZE
            
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.velocity = 1 # Slow them down a bit for the animation to look nice
        self.move_timer = 0
        self.direction = (0, 0)
        self.facing = 0 # 0: Down, 1: Left, 2: Right, 3: Up (Standard guess)

    def update(self):
        self.move_timer += 1
        if self.move_timer > 60: # Change direction every 60 frames
            self.move_timer = 0
            # Random direction
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)])
            
            # Update Facing Index based on direction
            if self.direction[1] > 0: self.facing = 0 # Down
            elif self.direction[1] < 0: self.facing = 1 # Up
            elif self.direction[0] < 0: self.facing = 2 # Left
            elif self.direction[0] > 0: self.facing = 3 # Right
            
        self.rect.x += self.direction[0] * self.velocity
        self.rect.y += self.direction[1] * self.velocity

        # Animation
        if self.spritesheet:
             self.animate()

    def animate(self):
        # Update frame index
        self.animation_timer += self.animation_speed
        if self.animation_timer >= self.cols:
            self.animation_timer = 0
            
        self.frame_index = int(self.animation_timer)
        
        # Calculate Frame Rect
        # Row order: 0 Down, 1 Left, 2 Right, 3 Up (Common) 
        # Check if row count matches facing
        row = self.facing
        if row >= self.rows: row = 0
        
        # Clip
        src_rect = pygame.Rect(self.frame_index * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height)
        self.image = self.spritesheet.subsurface(src_rect)
