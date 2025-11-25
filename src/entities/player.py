import pygame
from src.config import *
from src.entities.lantern import Lantern

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.spritesheet = pygame.image.load("/Users/sittiaminah/Documents/SEMESTER 3/OOP/To-Be-The-Greatest-Witch/assets/spritesheets_walk.png").convert_alpha()

        self.frame_width = 32
        self.frame_height = 32

        self.anim_down = [
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 0, 0),
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 1, 0),
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 2, 0),
        ]

        self.anim_up = [
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 0, 3),
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 1, 3),
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 2, 3),
        ]

        self.anim_left = [
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 0, 1),
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 1, 1),
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 2, 1),
        ]

        self.anim_right = [
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 0, 2),
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 1, 2),
            Player.get_frame(self.spritesheet, self.frame_width, self.frame_height, 2, 2),
        ]

        # Animasi awal
        self.current_anim = self.anim_down
        self.current_frame = 0
        self.frame_timer = 0

        # Set image awal
        self.image = self.current_anim[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
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
    
    @staticmethod
    def get_frame(sheet, frame_width, frame_height, fx, fy):
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (fx * frame_width, fy * frame_height, frame_width, frame_height))
        return frame

    def update(self):
        # --- EFFECTS ---
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

        # --- MOVEMENT + ANIMATION ---
        keys = pygame.key.get_pressed()
        moving = False

        # Gerak kiri
        if keys[pygame.K_a]:
            self.rect.x -= self.velocity
            self.current_anim = self.anim_left
            moving = True

        # Gerak kanan
        elif keys[pygame.K_d]:
            self.rect.x += self.velocity
            self.current_anim = self.anim_right
            moving = True

        # Gerak atas
        elif keys[pygame.K_w]:
            self.rect.y -= self.velocity
            self.current_anim = self.anim_up
            moving = True

        # Gerak bawah
        elif keys[pygame.K_s]:
            self.rect.y += self.velocity
            self.current_anim = self.anim_down
            moving = True

        # --- ANIMATE ---
        if moving:
            self.frame_timer += 1
            if self.frame_timer >= 10:   # atur kecepatan animasi
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.current_anim)
                self.image = self.current_anim[self.current_frame]
        else:
            # Idle → frame ke-0
            self.current_frame = 0
            self.image = self.current_anim[0]

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
