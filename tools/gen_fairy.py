import pygame
import os

def generate_fairy_sheet():
    pygame.init()
    
    # Dimensions
    FRAME_W, FRAME_H = 32, 32
    COLS, ROWS = 3, 4
    WIDTH = FRAME_W * COLS
    HEIGHT = FRAME_H * ROWS
    
    # Colors
    TRANSPARENT = (0, 0, 0, 0)
    BODY_COLOR = (255, 182, 193) # Light Pink
    WING_COLOR = (200, 255, 255, 200) # Cyan-ish transparent
    DRESS_COLOR = (50, 205, 50) # Lime Green
    
    # Create Surface
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    
    # Draw Frames
    for row in range(ROWS): # 0: Down, 1: Left, 2: Right, 3: Up
        for col in range(COLS):
            # Frame Offset
            x = col * FRAME_W
            y = row * FRAME_H
            
            center_x = x + FRAME_W // 2
            center_y = y + FRAME_H // 2
            
            # Bobbing animation (pixels)
            bob = 0
            if col == 1: bob = -2
            
            # --- Draw Fairy ---
            
            # Wings (Behind)
            # Flutter effect
            wing_spread = 10
            if col == 1: wing_spread = 8 # Flap in
            
            wing_rect_l = pygame.Rect(0, 0, 8, 12)
            wing_rect_r = pygame.Rect(0, 0, 8, 12)
            
            if row == 0 or row == 3: # Front/Back
                wing_rect_l.center = (center_x - wing_spread, center_y - 2 + bob)
                wing_rect_r.center = (center_x + wing_spread, center_y - 2 + bob)
                pygame.draw.ellipse(surface, WING_COLOR, wing_rect_l)
                pygame.draw.ellipse(surface, WING_COLOR, wing_rect_r)
            elif row == 1: # Left
                wing_rect_r.center = (center_x + 4, center_y - 2 + bob)
                pygame.draw.ellipse(surface, WING_COLOR, wing_rect_r)
            elif row == 2: # Right
                wing_rect_l.center = (center_x - 4, center_y - 2 + bob)
                pygame.draw.ellipse(surface, WING_COLOR, wing_rect_l)

            # Body/Dress
            body_rect = pygame.Rect(0, 0, 12, 16)
            body_rect.center = (center_x, center_y + 2 + bob)
            pygame.draw.ellipse(surface, DRESS_COLOR, body_rect)
            
            # Head
            head_radius = 6
            pygame.draw.circle(surface, BODY_COLOR, (center_x, center_y - 6 + bob), head_radius)
            
            # Eyes (if facing front/side)
            if row == 0: # Front
                pygame.draw.circle(surface, (0,0,0), (center_x - 2, center_y - 6 + bob), 1)
                pygame.draw.circle(surface, (0,0,0), (center_x + 2, center_y - 6 + bob), 1)
            elif row == 1: # Left
                pygame.draw.circle(surface, (0,0,0), (center_x - 3, center_y - 6 + bob), 1)
            elif row == 2: # Right
                pygame.draw.circle(surface, (0,0,0), (center_x + 3, center_y - 6 + bob), 1)
                
    # Save
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, "assets")
    output_path = os.path.join(assets_dir, "fairy_spritesheet.png")
    
    pygame.image.save(surface, output_path)
    print(f"Generated fairy spritesheet at {output_path}")

if __name__ == "__main__":
    generate_fairy_sheet()
