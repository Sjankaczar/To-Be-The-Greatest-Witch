import pygame
import os
from src.assets import FONT_LETTERS_PATH, FONT_NUMBERS_PATH

class BitmapFont:
    def __init__(self, cell_width=32, cell_height=32):
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.chars = {} # map char to surface
        
        self.load_fonts()

    def load_fonts(self):
        # 1. Load Letters
        if os.path.exists(FONT_LETTERS_PATH):
            try:
                sheet = pygame.image.load(FONT_LETTERS_PATH).convert_alpha()
                chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                cols = 5
                for i, char in enumerate(chars):
                    row = i // cols
                    col = i % cols
                    rect = pygame.Rect(col * self.cell_width, row * self.cell_height, 
                                     self.cell_width, self.cell_height)
                    self.chars[char] = sheet.subsurface(rect)
                    self.chars[char.lower()] = sheet.subsurface(rect) # Map lowercase
            except Exception as e:
                print(f"Error loading letters font: {e}")
        else:
            print(f"Warning: Font file not found: {FONT_LETTERS_PATH}")

        # 2. Load Numbers & Special chars
        if os.path.exists(FONT_NUMBERS_PATH):
            try:
                sheet_num = pygame.image.load(FONT_NUMBERS_PATH).convert_alpha()
                mapping = [
                    ('0', 0, 0), ('1', 0, 1), ('2', 0, 2), ('3', 0, 3),
                    ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('7', 1, 3),
                    ('8', 2, 0), ('9', 2, 1), ('/', 2, 2), ('K', 2, 3),
                    ('M', 3, 0)
                ]
                for char, row, col in mapping:
                    rect = pygame.Rect(col * self.cell_width, row * self.cell_height, 
                                     self.cell_width, self.cell_height)
                    self.chars[char] = sheet_num.subsurface(rect)
                    if char in ['K', 'M']:
                        self.chars[char.lower()] = sheet_num.subsurface(rect)
            except Exception as e:
                 print(f"Error loading numbers font: {e}")
        else:
            print(f"Warning: Font file not found: {FONT_NUMBERS_PATH}")
            
    def render(self, surface, text, x, y, scale=1.0, spacing=0):
        """Renders text to the surface"""
        text = str(text)
        current_x = x
        
        for char in text:
            if char == ' ':
                current_x += int(self.cell_width * scale / 2) + spacing
                continue
                
            if char in self.chars:
                img = self.chars[char]
                if scale != 1.0:
                    width = int(self.cell_width * scale)
                    height = int(self.cell_height * scale)
                    img = pygame.transform.scale(img, (width, height))
                else:
                    width = self.cell_width
                    # height = self.cell_height
                    
                surface.blit(img, (current_x, y))
                current_x += width + spacing # space between chars
            else:
                # Skip unknown or render space
                current_x += int(self.cell_width * scale / 2) + spacing

    def get_width(self, text, scale=1.0, spacing=0):
        """Calculate width of rendered text"""
        width = 0
        text = str(text)
        for i, char in enumerate(text):
            char_w = 0
            if char == ' ':
                char_w = int(self.cell_width * scale / 2)
            elif char in self.chars:
                char_w = int(self.cell_width * scale)
            else:
                char_w = int(self.cell_width * scale / 2)
            
            width += char_w
            if i < len(text) - 1:
                width += spacing
        return width

    def format_number(self, value):
        """Formats number with K/M suffixes"""
        try:
            value = float(value)
        except ValueError:
            return str(value)

        if value >= 1_000_000:
            val = int(value // 1_000_000)
            return f"{val}M"
        elif value >= 1_000:
            # Check if it's exactly thousands or e.g. 1500 -> 1.5K? 
            # Usually games map 1500 -> 1K or 1.5K. 
            # Given integers only K/M chars, likely 1K 2K.
            val = int(value // 1_000)
            return f"{val}K"
        else:
            return str(int(value))
