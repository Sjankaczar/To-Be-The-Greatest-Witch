from src.states.game_state import GameState
from src.config import *
import pygame
import cv2
import os
import numpy as np

from src.utils.ui import Button
from src.assets import IMG_PLAY_BTN, IMG_EXIT_BTN
import sys

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

        # Buttons
        self.font = pygame.font.SysFont(None, 36)
        
        # Play Button
        self.play_img = None
        if os.path.exists(IMG_PLAY_BTN):
             self.play_img = pygame.image.load(IMG_PLAY_BTN).convert_alpha()
             # Scale 3x (User Request)
             w, h = self.play_img.get_size()
             self.play_img = pygame.transform.scale(self.play_img, (w * 3, h * 3))
        else:
             print(f"Warning: Play Button not found at {IMG_PLAY_BTN}")

        # Exit Button
        self.exit_img = None
        if os.path.exists(IMG_EXIT_BTN):
             self.exit_img = pygame.image.load(IMG_EXIT_BTN).convert_alpha()
             # Scale 3x (User Request)
             w, h = self.exit_img.get_size()
             self.exit_img = pygame.transform.scale(self.exit_img, (w * 3, h * 3))
        else:
             print(f"Warning: Exit Button not found at {IMG_EXIT_BTN}")

        # Position Buttons (Center Screen, vertically stacked?)
        # User didn't specify pos, assume Standard center
        btn_w, btn_h = 200, 60 # Default size if no image
        if self.play_img:
            btn_w, btn_h = self.play_img.get_size()
            
        center_x = ((SCREEN_WIDTH - btn_w) // 2) - 215
        play_y = SCREEN_HEIGHT // 2 - 50
        exit_y = play_y + btn_h + 20
        
        self.btn_play = Button(center_x, play_y, btn_w, btn_h, "", self.font, image=self.play_img)
        self.btn_exit = Button(center_x, exit_y, btn_w, btn_h, "", self.font, image=self.exit_img)
            
        # Transition Logic
        self.fading_out = False
        self.fade_alpha = 0
        self.fade_speed = 5
        self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill(BLACK)
        self.next_action = None # 'play' or 'exit'

    def enter(self):
        print("Entering Opening State")
        # Restart video if needed
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.fading_out = False
        self.fade_alpha = 0
        self.next_action = None

    def exit(self):
        print("Exiting Opening State")
        # Do not release cap here if we want to reuse it? 
        # Or release and reload? Better to keep loaded if we might come back (though usually openings are once).
        # For memory safety, let's keep it open but maybe we can release if needed.
        pass

    def handle_events(self, events):
        for event in events:
            # Play Button
            if self.btn_play.handle_event(event):
                 if not self.fading_out:
                     self.start_fade_out('play')
                     
            # Exit Button
            if self.btn_exit.handle_event(event):
                 if not self.fading_out:
                     self.start_fade_out('exit')

    def start_fade_out(self, action):
        print(f"Starting Fade Out ({action})...")
        self.fading_out = True
        self.next_action = action

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
                
                # Execute Action
                if self.next_action == 'play':
                    self.game.change_state("home")
                    self.game.states["home"].enter()
                elif self.next_action == 'exit':
                    pygame.quit()
                    sys.exit()

    def draw(self, screen):
        # Draw Video
        if self.frame_surface:
            screen.blit(self.frame_surface, (0, 0))
        else:
            screen.fill(BLACK)
            
        # Draw Buttons
        if not self.fading_out: # Hide buttons during fade? Or keep them? Usually keep them or they fade out too.
             # If we draw them before fade overlay, they will fade out.
             self.btn_play.draw(screen)
             self.btn_exit.draw(screen)
            
        # Draw Fade Overlay
        if self.fading_out and self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            screen.blit(self.fade_surface, (0, 0))
