import pygame
from src.config import *

class FarmingSystem:
    def __init__(self):
        self.grid = {} # (x, y): {'type': 'grass'|'farmland', 'crop': None|'Red Herb'|..., 'growth': 0, 'watered': False}
        self.tile_size = 32
        
    def get_tile_key(self, x, y):
        # Convert world coordinates to grid coordinates
        grid_x = x // self.tile_size
        grid_y = y // self.tile_size
        return (grid_x, grid_y)
        
    def till_soil(self, x, y):
        key = self.get_tile_key(x, y)
        if key not in self.grid:
            self.grid[key] = {'type': 'farmland', 'crop': None, 'growth': 0, 'watered': False}
            return True
        elif self.grid[key]['type'] == 'grass':
            self.grid[key]['type'] = 'farmland'
            return True
        return False
        
    def plant_crop(self, x, y, crop_name):
        key = self.get_tile_key(x, y)
        if key in self.grid and self.grid[key]['type'] == 'farmland' and self.grid[key]['crop'] is None:
            self.grid[key]['crop'] = crop_name
            self.grid[key]['growth'] = 0
            return True
        return False
        
    def water_crop(self, x, y):
        key = self.get_tile_key(x, y)
        if key in self.grid and self.grid[key]['type'] == 'farmland':
            self.grid[key]['watered'] = True
            return True
        return False
        
    def harvest_crop(self, x, y, inventory):
        key = self.get_tile_key(x, y)
        if key in self.grid and self.grid[key]['crop'] and self.grid[key]['growth'] >= CROP_GROWTH_TIME:
            crop_name = self.grid[key]['crop']
            
            # Map Seeds to Herbs
            yield_item = crop_name
            if crop_name == "Red Seed": yield_item = "Red Herb"
            elif crop_name == "Blue Seed": yield_item = "Blue Herb"
            elif crop_name == "Rare Seed": yield_item = "Rare Herb"
            
            if yield_item in inventory:
                inventory[yield_item] += 2 # Yield 2 herbs
            else:
                inventory[yield_item] = 2
            
            print(f"Harvested {crop_name}! Yield: 2 {yield_item}")
            
            # Reset tile
            self.grid[key]['crop'] = None
            self.grid[key]['growth'] = 0
            self.grid[key]['watered'] = False
            return True
        return False
        
    def update(self):
        for key, tile in self.grid.items():
            if tile['crop'] and tile['watered']:
                tile['growth'] += 1
                if tile['growth'] >= CROP_GROWTH_TIME:
                    tile['growth'] = CROP_GROWTH_TIME
                    tile['watered'] = False # Needs water again? Or just done. Let's say done.
