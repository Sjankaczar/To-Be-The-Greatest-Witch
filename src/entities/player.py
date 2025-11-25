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
        
        self.effects = {} # {effect_name: duration_frames}
        self.base_velocity = 5
        self.velocity = self.base_velocity
        
        self.teleport_cooldown_end = 0.0 # Timestamp
        
        # Toolbar: 9 slots, stores item names or None
        self.toolbar = [None] * 9 
        self.selected_slot = 0 # Index 0-8

    def update(self):
        # Update effects
        to_remove = []
        for effect, duration in self.effects.items():
            self.effects[effect] -= 1
            if self.effects[effect] <= 0:
                to_remove.append(effect)
        
        for effect in to_remove:
            del self.effects[effect]
            if effect == "Speed":
                self.velocity = self.base_velocity
                print("Speed effect wore off.")
            elif effect == "Invisibility":
                print("Invisibility effect wore off.")

        # Update cooldowns - No longer frame based for teleport
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= self.velocity
        if keys[pygame.K_d]:
            self.rect.x += self.velocity
        if keys[pygame.K_w]:
            self.rect.y -= self.velocity
        if keys[pygame.K_s]:
            self.rect.y += self.velocity

    def add_item(self, item_name):
        # Check toolbar first
        for slot in self.toolbar:
            if slot and slot['name'] == item_name:
                slot['count'] += 1
                print(f"Collected {item_name}. Added to Toolbar.")
                return

        # Then inventory
        if item_name in self.inventory:
            self.inventory[item_name] += 1
        else:
            self.inventory[item_name] = 1
        print(f"Collected {item_name}. Inventory: {self.inventory}")

    def use_item(self, item_name, source="inventory", slot_index=None):
        # Check availability
        if source == "inventory":
            if item_name not in self.inventory or self.inventory[item_name] <= 0:
                return False
        elif source == "toolbar":
            if slot_index is None or self.toolbar[slot_index] is None or self.toolbar[slot_index]['name'] != item_name:
                return False

        used = False
        if item_name == "Health Potion":
            self.health = min(self.health + 20, self.max_health)
            used = True
            print(f"Used Health Potion. Health: {self.health}")
        elif item_name == "Speed Potion":
            self.effects["Speed"] = 600 # 10 seconds at 60 FPS
            self.velocity = self.base_velocity * 2
            used = True
            print("Used Speed Potion!")
        elif item_name == "Invisibility Potion":
            self.effects["Invisibility"] = 300 # 5 seconds
            used = True
            print("Used Invisibility Potion!")
        elif item_name == "Mana Potion":
            # Placeholder for mana
            print("Used Mana Potion! (Mana not implemented yet)")
            used = True
        
        if used:
            if source == "inventory":
                self.inventory[item_name] -= 1
                if self.inventory[item_name] == 0:
                    del self.inventory[item_name]
            elif source == "toolbar" and slot_index is not None:
                self.toolbar[slot_index]['count'] -= 1
                if self.toolbar[slot_index]['count'] == 0:
                    self.toolbar[slot_index] = None
            return True
        return False
