import pygame
import sys
from src.config import *
from src.entities.player import Player
from src.states.home import HomeState
from src.states.exploration import ExplorationState
from src.states.opening import OpeningState
from src.states.room import RoomState
from src.assets import AUDIO_BGM
from src.systems.research import ResearchSystem
import os

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Make a Potion to Be The Greatest Witch")
        pygame.display.set_caption("Make a Potion to Be The Greatest Witch")
        self.clock = pygame.time.Clock()
        
        # Audio Initialization
        self.volume = 0.5
        if os.path.exists(AUDIO_BGM):
            try:
                pygame.mixer.music.load(AUDIO_BGM)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1) # Loop forever
                print(f"Playing BGM: {AUDIO_BGM}")
            except Exception as e:
                print(f"Error loading BGM: {e}")
        else:
            print(f"Warning: BGM not found at {AUDIO_BGM}")
        
        self.player = Player(90, 165)
        self.research_system = ResearchSystem() # Shared Research State
        # self.gold moved to player.gold
        
        self.states = {
            "home": HomeState(self),
            "exploration": ExplorationState(self),
            "opening": OpeningState(self),
            "room": RoomState(self)
        }
        
        if SHOW_OPENING_SCREEN:
            self.current_state = self.states["opening"]
            self.current_state.enter()
        else:
            self.current_state = self.states["home"]
            self.current_state.enter() # Ensure enter is called

    def change_state(self, state_name):
        if state_name in self.states:
            self.current_state = self.states[state_name]

    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            
            self.current_state.handle_events(events)
            self.current_state.update()
            self.current_state.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
