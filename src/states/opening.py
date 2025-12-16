from src.states.game_state import GameState
from src.config import *
import pygame
import cv2
import os
import numpy as np

class OpeningState(GameState):
    def __init__(self, game):
        super().__init__(game)
        
        # Video Path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        video_path = os.path.join(base_dir, "assets", "videos", "1214.mp4")
        
        self.video_path = video_path
        self.cap = None
        self.frame_surface = None
        
        if os.path.exists(video_path):
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                print(f"Error: Could not open video at {video_path}")
                self.cap = None
            else:
                 print(f"Opening Video Loaded: {video_path}")
        else:
            print(f"Error: Video file not found at {video_path}")
            
        # Transition Logic
        self.fading_out = False
        self.fade_alpha = 0
        self.fade_speed = 5
        self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill(BLACK)

    def enter(self):
        print("Entering Opening State")
        # Restart video if needed
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
        # Fade variables reset? 
        # Actually usually we want fresh start.
        self.fading_out = False
        self.fade_alpha = 0

    def exit(self):
        print("Exiting Opening State")
        # Do not release cap here if we want to reuse it? 
        # Or release and reload? Better to keep loaded if we might come back (though usually openings are once).
        # For memory safety, let's keep it open but maybe we can release if needed.
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                    if not self.fading_out:
                        self.start_fade_out()
            
            # Optional: Allow skipping with Key press too? User said "Click left".
            # if event.type == pygame.KEYDOWN:
            #     if not self.fading_out:
            #         self.start_fade_out()

    def start_fade_out(self):
        print("Starting Fade Out...")
        self.fading_out = True

    def update(self):
        # Update Video Frame
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert BGR (OpenCV) to RGB (Pygame)
                # cv2 reads as (height, width, channels)
                # pygame wants (width, height) surface
                
                # Resize if needed?
                # Assuming video matches screen or we scale it.
                # Let's scale frame to SCREEN_WIDTH, SCREEN_HEIGHT
                frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
                
                # Resize to screen
                frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
                
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Fix orientation for Pygame
                # Pygame expects (Width, Height, 3)
                # CV2 gives (Height, Width, 3)
                # We need to swap the first two axes
                frame = np.swapaxes(frame, 0, 1)
                
                # Create Surface
                self.frame_surface = pygame.surfarray.make_surface(frame)
                
            else:
                # End of video -> Loop
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # Fade Logic
        if self.fading_out:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                # Switch State
                self.game.change_state("home")
                self.game.states["home"].enter()

    def draw(self, screen):
        # Draw Video
        if self.frame_surface:
            screen.blit(self.frame_surface, (0, 0))
        else:
            screen.fill(BLACK)
            
        # Draw Fade Overlay
        if self.fading_out and self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            screen.blit(self.fade_surface, (0, 0))
