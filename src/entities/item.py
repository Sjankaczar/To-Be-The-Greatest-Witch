import pygame
from src.config import *
from src.assets import *

import os

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, name, color=YELLOW):
        super().__init__()
        
        # Load Spritesheet
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sheet_path = os.path.join(base_dir, "UI The Greatest Witch", "items.png")
        
        self.image = pygame.Surface((32, 32))
        image_found = False
        
        if name == "Water" and os.path.exists(IMG_WATER_BOTTLE):
             try:
                 img = pygame.image.load(IMG_WATER_BOTTLE).convert_alpha()
                 # Scale to smaller size (20x20) as per user request to reduce size and hitbox
                 self.image = pygame.transform.scale(img, (20, 20))
                 image_found = True
             except Exception as e:
                 print(f"Error loading water sprite: {e}")
                 
        if not image_found and os.path.exists(sheet_path):
            try:
                sheet = pygame.image.load(sheet_path).convert_alpha()
                
                # Auto-scale if large
                if sheet.get_width() > 160:
                     scale_factor = 32 / 100 # Assuming 100px per tile basis from 500px/5cols
                     new_w = int(sheet.get_width() * scale_factor)
                     new_h = int(sheet.get_height() * scale_factor)
                     sheet = pygame.transform.scale(sheet, (new_w, new_h))
                     
                
                # Coords (Col, Row, OffsetX, OffsetY)
                # Row 1: Plants (Red, Blue, Green, Yellow)
                coords = {
                    "Red Herb": (0, 1, 0, 0),
                    "Blue Herb": (1, 1, -5, 0), # Shift left 5px
                    "Rare Herb": (3, 1, -12, 0), # Shift left 12px
                    # "Water": (3, 0, 0, 0), # Removed: Conflict with Health Potion
                    
                    # Seeds (Custom Sizes)
                    # Base Col 3 = 96px.
                    # Red: 110-125 (Offset 14, W 15)
                    "Red Seed": (3, 1, 14, 0, 15, 32),
                    # Blue: 125-140 (Offset 29, W 15) 
                    "Blue Seed": (3, 1, 29, 0, 15, 32),
                    # Rare: 140-160 (Offset 44, W 20)
                    "Rare Seed": (3, 1, 44, 0, 20, 32),

                    # Row 1 (Index 0) Potions
                    "Rank Up Potion": (0, 0, 0, 0),
                    "Invisibility Potion": (1, 0, 0, 0),
                    "Intelligence Potion": (2, 0, 0, 0),
                    "Health Potion": (3, 0, 0, 0),
                    "Speed Potion": (4, 0, 0, 0),

                    # Row 3 (Index 2) Tools
                    "Axe": (0, 2, 0, 0),
                    "Hoe": (2, 2, 0, 0),
                    "Watering Can": (3, 2, 0, 0),
                    "Bug Net": (4, 2, 0, 0),
                }
                
                if name in coords:
                    val = coords[name]
                    width, height = 32, 32 # Default size
                    
                    if len(val) == 2:
                        col, row = val
                        off_x, off_y = 0, 0
                    elif len(val) == 4:
                        col, row, off_x, off_y = val
                    elif len(val) == 6:
                        col, row, off_x, off_y, width, height = val
                    else:
                        col, row, off_x, off_y = 0, 0, 0, 0 # Fallback
                        
                    # Calculate Rect
                    rect = pygame.Rect((col * 32) + off_x, (row * 32) + off_y, width, height)
                    
                    # Safety Clip
                    if rect.right > sheet.get_width(): rect.width = sheet.get_width() - rect.x
                    if rect.bottom > sheet.get_height(): rect.height = sheet.get_height() - rect.y
                    
                    self.image = sheet.subsurface(rect)
                    
                    # If item is small (like seeds), maybe center it on a 32x32 tile?
                    if width < 32 or height < 32:
                        base = pygame.Surface((32, 32), pygame.SRCALPHA)
                        # Center logic
                        dest_x = (32 - width) // 2
                        dest_y = (32 - height) // 2
                        base.blit(self.image, (dest_x, dest_y))
                        self.image = base
                        
                    image_found = True
            except Exception as e:
                print(f"Error loading item sprite: {e}")
        
        if not image_found:
            self.image.fill(color)
            # Render name text fallback
            font = pygame.font.SysFont(None, 12)
            text = font.render(name[:4], True, BLACK)
            text_rect = text.get_rect(center=(16, 16))
            self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.name = name
