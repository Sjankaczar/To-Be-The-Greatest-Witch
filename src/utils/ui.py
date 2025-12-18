import pygame
from src.config import *

class Button:
    def __init__(self, x, y, width, height, text, font, color=GRAY, hover_color=WHITE, text_color=BLACK, image=None, image_pressed=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_pressed = False
        
        self.image = None
        if image:
            self.image = pygame.transform.scale(image, (int(width), int(height)))
            
        self.image_pressed = None
        if image_pressed:
            self.image_pressed = pygame.transform.scale(image_pressed, (int(width), int(height)))

    def draw(self, screen):
        current_image = self.image
        if self.is_pressed and self.image_pressed:
            current_image = self.image_pressed
            
        if current_image:
             # Draw Image
             screen.blit(current_image, self.rect)
             # Optional: Draw text on top?
             if self.text:
                  text_surf = self.font.render(self.text, True, self.text_color)
                  text_rect = text_surf.get_rect(center=self.rect.center)
                  
                  # Text Offset for pressed state (simulates depth)
                  if self.is_pressed and self.image_pressed:
                      text_rect.y += 2
                      
                  screen.blit(text_surf, text_rect)
        else:
            color = self.hover_color if self.is_hovered else self.color
            if self.is_pressed:
                color = self.hover_color # Or darker?
                
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2) # Border
            
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            if not self.is_hovered:
                self.is_pressed = False # Release release if dragged out
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_pressed = True
                # Return True immediately for responsiveness?
                # Or wait for UP? 
                # To show the "pressed" image, we must NOT return specific action yet?
                # But existing code expects immediate action.
                # If I return True here, the state might change (UI closes), so pressed image never seen.
                # BUT for buying items, staying in UI, it works.
                # Let's return True here to maintain existing behavior for now, but set is_pressed.
                # Visuals update next frame.
                return True
                
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_pressed = False
                
        return False
