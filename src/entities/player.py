import pygame
from src.config import *
from src.entities.lantern import Lantern

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.velocity = 5
        self.lantern = Lantern()
        self.inventory = {} # Dictionary to store item_name: count
        
        self.max_health = 100
        self.health = self.max_health

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= self.velocity
        if keys[pygame.K_d]:
            self.rect.x += self.velocity
        if keys[pygame.K_w]:
            self.rect.y -= self.velocity
        if keys[pygame.K_s]:
            self.rect.y += self.velocity
            
        # Keep player on screen - REMOVED for infinite map

    def add_item(self, item_name):
        if item_name in self.inventory:
            self.inventory[item_name] += 1
        else:
            self.inventory[item_name] = 1
        print(f"Collected {item_name}. Inventory: {self.inventory}")

    def use_item(self, item_name):
        if item_name in self.inventory and self.inventory[item_name] > 0:
            if item_name == "Health Potion":
                self.health = min(self.health + 20, self.max_health)
                self.inventory[item_name] -= 1
                if self.inventory[item_name] == 0:
                    del self.inventory[item_name]
                print(f"Used Health Potion. Health: {self.health}")
                return True
        return False
