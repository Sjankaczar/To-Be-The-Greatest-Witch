import pygame
import random
import math
from src.entities.forest_creature import ForestCreature

class ChasingCreature(ForestCreature):
    def __init__(self, x, y, spritesheet, player):
        super().__init__(x, y, spritesheet)
        self.player = player
        self.detection_radius = 250
        self.velocity = 0.6 # Slower speed (ForestCreature is 1.0)
        self.name = "Magma Slime"
        self.chasing = False
        
    def update(self):
        self.move_timer += 1
        
        # Calculate distance to player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.detection_radius:
            self.chasing = True
            if distance > 5: # Don't jitter when on top
                # Normalize
                dir_x = dx / distance
                dir_y = dy / distance
                
                self.direction = (dir_x, dir_y)
                
                # Update moving logic
                self.rect.x += self.direction[0] * self.velocity
                self.rect.y += self.direction[1] * self.velocity
                
                # Update Facing
                if abs(dx) > abs(dy):
                    if dx > 0: self.facing = 3 # Right
                    else: self.facing = 2 # Left
                else:
                    if dy > 0: self.facing = 0 # Down
                    else: self.facing = 1 # Up
        else:
            self.chasing = False
            # Wander Logic (Fallback to random movement)
            if self.move_timer > 60: 
                self.move_timer = 0
                # Random small movement or idle
                self.direction = random.choice([(0.5, 0), (-0.5, 0), (0, 0.5), (0, -0.5), (0, 0)])
                
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
