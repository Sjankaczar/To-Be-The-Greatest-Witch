import pygame
import random
from src.config import *

class Insect(pygame.sprite.Sprite):
    def __init__(self, x, y, image=None):
        super().__init__()
        if image:
            # Assume 3x2 spritesheet or similar. Let's try to extract frames.
            # User provided "butterfly.png".
            # If it's a spritesheet, we should handle it.
            # Let's assume standard behavior: Animated.
            self.spritesheet = image
            self.frames = []
            
            # Extract frames (Assuming 3 frames horizontal, 2 vertical? Or just 1 row?)
            # Usually these assets are small. Let's try to guess or use standard 16x16 or 32x32.
            # If we don't know, let's look at image size in ExplorationState or just handle it here blindly?
            # Better: Load whole image and split.
            sheet_w = self.spritesheet.get_width()
            sheet_h = self.spritesheet.get_height()
            
            # Assume 2 rows, 3 cols (common for simple rpg assets)
            cols = 3
            rows = 2
            frame_w = sheet_w // cols
            frame_h = sheet_h // rows
            
            for row in range(rows):
                for col in range(cols):
                    rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                    self.frames.append(self.spritesheet.subsurface(rect))
            
            self.current_frame = 0
            self.image = self.frames[0]
            self.animation_timer = 0
        else:
             self.image = pygame.Surface((16, 16))
             self.image.fill((150, 75, 0))
             self.frames = []

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
        
        # Determine Direction Flip (Left/Right)
        # If moving Left (dir.x < 0), flip image?
        # If the sprite faces Right by default.
        flip = self.direction.x < 0
        
        # Animation
        if self.frames:
            self.animation_timer += 1
            if self.animation_timer > 5: # Speed of animation
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
                
                if flip:
                     self.image = pygame.transform.flip(self.image, True, False)
        
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
