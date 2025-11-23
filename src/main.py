import pygame
import sys
from src.config import *
from src.entities.player import Player
from src.states.home import HomeState
from src.states.exploration import ExplorationState

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Make a Potion to Be The Greatest Witch")
        self.clock = pygame.time.Clock()
        
        self.player = Player(100, 100)
        self.gold = 100 # Starting gold
        
        self.states = {
            "home": HomeState(self),
            "exploration": ExplorationState(self)
        }
        self.current_state = self.states["home"]

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
    game = Game()
    game.run()
