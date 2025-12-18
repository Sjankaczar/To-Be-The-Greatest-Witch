import pygame
import random
import math
import os
from src.config import *

class Fairy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Spritesheet Loading
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        img_path = os.path.join(base_dir, "assets", "fairy.png")
        
        self.animations = []
        self.frame_index = 0
        self.animation_speed = 0.1
        self.animation_timer = 0
        self.facing = 0 # 0: Down, 1: Left, 2: Right, 3: Up
        
        # Dimensions derived from 1488x2012, 3 cols, 4 rows
        FRAME_W = 496
        FRAME_H = 503
        TARGET_SIZE = (64, 64) # Increased size
        
        if os.path.exists(img_path):
            sprite_sheet = pygame.image.load(img_path).convert_alpha()
            
            # Extract Frames
            for row in range(4):
                frames = []
                for col in range(3):
                    rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
                    try:
                        image = sprite_sheet.subsurface(rect)
                        image = pygame.transform.smoothscale(image, TARGET_SIZE)
                        frames.append(image)
                    except ValueError:
                        print(f"Error extracting fairy frame {row},{col}")
                self.animations.append(frames)
            
            self.image = self.animations[0][0]
        else:
             print(f"Warning: Fairy image not found at {img_path}")
             self.image = pygame.Surface(TARGET_SIZE)
             self.image.fill(YELLOW) 
             self.animations = [[self.image]] # Fallback
             
        # Hitbox (smaller than visual)
        # Visual is 64x64, let's make hitbox 8x8 centered (User Request)
        self.rect = pygame.Rect(x, y, 8, 8)
        self.rect.center = (x, y) # maintain center pos
        
        self.start_y = self.rect.y
        self.hover_offset = 0
        self.hover_speed = 0.1
        self.name = "Forest Fairy"
        
    def update(self):
        # Hover animation
        self.hover_offset += self.hover_speed
        self.rect.y = self.start_y + math.sin(self.hover_offset) * 5
        
        # Sprite Animation
        if self.animations and len(self.animations) > 0:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.facing])
                self.image = self.animations[self.facing][self.frame_index]
        
    def draw(self, screen, camera):
        # Draw Image centered on Hitbox
        # Camera applies to hitbox (self.rect)
        rect_screen = camera.apply(self)
        
        # Calculate visual offset
        # Image is 64x64, Hitbox is 32x32
        # Offset = (Image_W - Hitbox_W) / 2
        offset_x = (self.image.get_width() - self.rect.width) // 2
        offset_y = (self.image.get_height() - self.rect.height) // 2
        
        draw_pos = (rect_screen.x - offset_x, rect_screen.y - offset_y)
        
        screen.blit(self.image, draw_pos)
        
        # Debug: Draw Hitbox
        # pygame.draw.rect(screen, (255, 0, 0), rect_screen, 1)
