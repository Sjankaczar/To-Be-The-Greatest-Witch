import pygame
import math
from src.config import *

class Golem(pygame.sprite.Sprite):
    def __init__(self, x, y, home_state):
        super().__init__()
        self.home_state = home_state
        
        # Visuals
        self.image = pygame.Surface((24, 24))
        self.image.fill((139, 69, 19)) # Wood color
        pygame.draw.rect(self.image, (0, 255, 0), (8, 4, 8, 4)) # Eyes
        self.rect = self.image.get_rect(center=(x, y))
        
        # Stats
        self.energy = GOLEM_MAX_ENERGY
        self.max_energy = GOLEM_MAX_ENERGY
        self.speed = GOLEM_SPEED
        self.inventory = {} # Placeholder
        
        # State Machine
        self.state = "IDLE" # IDLE, MOVING, WATERING, EXPANDING
        self.target_pos = None
        self.target_action = None # "WATER", "EXPAND"
        self.target_tile_key = None # (grid_x, grid_y)
        
    def update(self):
        # Recharge if idle
        if self.state == "IDLE":
            if self.energy < self.max_energy:
                self.energy += GOLEM_RECHARGE_RATE
                if self.energy > self.max_energy:
                    self.energy = self.max_energy
            
            # Look for tasks if we have energy
            if self.energy > 10:
                self.find_task()
                
        elif self.state == "MOVING":
            if self.target_pos:
                self.move_towards(self.target_pos)
            else:
                self.state = "IDLE"
                
        elif self.state == "WATERING":
            self.perform_water()
            
        elif self.state == "EXPANDING":
            self.perform_expand()
            
    def find_task(self):
        # Priority 1: Expand (User Command)
        if self.home_state.expansion_queue:
            # Get first task
            target_grid = self.home_state.expansion_queue[0]
            
            # Check cost
            if self.energy >= GOLEM_EXPAND_COST:
                self.target_tile_key = target_grid
                self.target_pos = (target_grid[0] * TILE_SIZE + TILE_SIZE//2, target_grid[1] * TILE_SIZE + TILE_SIZE//2)
                self.target_action = "EXPAND"
                self.state = "MOVING"
                self.home_state.expansion_queue.pop(0) # Remove from queue so other golems don't take it
                print(f"Golem accepted expansion task at {target_grid}")
                return

        # Priority 2: Water Crops
        # Scan farming grid
        for key, tile in self.home_state.farming_system.grid.items():
            if tile['type'] == 'farmland' and tile['crop'] and not tile['watered']:
                # Found dry crop
                if self.energy >= GOLEM_WATER_COST:
                    self.target_tile_key = key
                    self.target_pos = (key[0] * self.home_state.farming_system.tile_size + self.home_state.farming_system.tile_size//2, 
                                     key[1] * self.home_state.farming_system.tile_size + self.home_state.farming_system.tile_size//2)
                    self.target_action = "WATER"
                    self.state = "MOVING"
                    print(f"Golem found dry crop at {key}")
                    return
                    
    def move_towards(self, target):
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        
        if dist <= self.speed:
            self.rect.center = target
            # Arrived
            if self.target_action == "WATER":
                self.state = "WATERING"
            elif self.target_action == "EXPAND":
                self.state = "EXPANDING"
            else:
                self.state = "IDLE"
        else:
            dx = dx / dist
            dy = dy / dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            
    def perform_water(self):
        if self.target_tile_key:
            grid_x, grid_y = self.target_tile_key
            # Convert grid to world for the system call
            world_x = grid_x * TILE_SIZE
            world_y = grid_y * TILE_SIZE
            
            if self.home_state.farming_system.water_crop(world_x, world_y):
                self.energy -= GOLEM_WATER_COST
                print("Golem watered crop!")
            else:
                print("Golem failed to water (already watered or gone).")
                
        self.reset_task()
        
    def perform_expand(self):
        if self.target_tile_key:
            grid_x, grid_y = self.target_tile_key
            
            # Convert to pixel coordinates for extra_tiles
            pixel_pos = (grid_x * TILE_SIZE, grid_y * TILE_SIZE)
            
            # Add to extra tiles
            if pixel_pos not in self.home_state.extra_tiles:
                self.home_state.extra_tiles.append(pixel_pos)
                
                # Update map bounds
                self.home_state.map_width = max(self.home_state.map_width, (grid_x * TILE_SIZE) + TILE_SIZE)
                self.home_state.map_height = max(self.home_state.map_height, (grid_y * TILE_SIZE) + TILE_SIZE)
                self.home_state.camera.update_bounds(self.home_state.map_width, self.home_state.map_height)
                
                self.energy -= GOLEM_EXPAND_COST
                print(f"Golem expanded area at {pixel_pos}!")
            else:
                print("Area already expanded.")
                
        self.reset_task()
        
    def reset_task(self):
        self.state = "IDLE"
        self.target_pos = None
        self.target_action = None
        self.target_tile_key = None
