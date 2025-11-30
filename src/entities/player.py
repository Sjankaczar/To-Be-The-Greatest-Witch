import pygame
from src.config import *
from src.entities.lantern import Lantern

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        import os
        
        # Dynamic path finding for assets
        current_dir = os.path.dirname(os.path.abspath(__file__))
        spritesheet_path = None
        while True:
            potential_path = os.path.join(current_dir, "assets", "spritesheets_walk.png")
            if os.path.exists(potential_path):
                spritesheet_path = potential_path
                break
            
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir: # Reached root
                raise FileNotFoundError("Could not find assets/spritesheets_walk.png")
            current_dir = parent_dir
            
        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()

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
        
        # Player Stats
        self.rank = 1
        self.intelligence = 24
        self.brain_shape = "Smooth" # Flavor text
        self.fairies_caught = 0
        
        # Toolbar: 9 slots, stores item names or None
        self.toolbar = [None] * 9 
        self.selected_slot = 0 # Index 0-8
        # self.rank = 3 # Removed duplicate assignment
        
        # Starting Items (Dev Helper)
        self.gold = 10000
        self.inventory["Red Herb"] = 99
        self.inventory["Blue Herb"] = 99
        self.inventory["Health Potion"] = 5
        self.inventory["Hoe"] = 1
        self.inventory["Watering Can"] = 1
        self.inventory["Water"] = 99
        
        # Add some to toolbar for convenience
        self.toolbar[0] = {'name': 'Watering Can', 'count': 1}
        self.toolbar[1] = {'name': 'Hoe', 'count': 1}
        self.toolbar[2] = {'name': 'Health Potion', 'count': 3}
        self.toolbar[3] = {'name': 'Intelligence Potion', 'count': 99}
        self.toolbar[4] = {'name': 'Rank Up Potion', 'count': 9}
    
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
            elif effect == "Intelligence":
                self.intelligence -= 10
                print("Intelligence effect wore off.")

        # --- MOVEMENT + ANIMATION ---
        keys = pygame.key.get_pressed()
        moving = False
        
        dx = 0
        dy = 0

        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
            
        if dx != 0 or dy != 0:
            moving = True
            
            # Normalize vector
            length = (dx**2 + dy**2)**0.5
            dx = dx / length
            dy = dy / length
            
            self.rect.x += dx * self.velocity
            self.rect.y += dy * self.velocity
            
            # Update Animation based on direction
            if dx < 0:
                self.current_anim = self.anim_left
            elif dx > 0:
                self.current_anim = self.anim_right
            elif dy < 0:
                self.current_anim = self.anim_up
            elif dy > 0:
                self.current_anim = self.anim_down

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

    def use_item(self, item_name=None, source="inventory", slot_index=None):
        # If no item specified, try to use selected toolbar item
        if item_name is None:
            slot_data = self.toolbar[self.selected_slot]
            if slot_data:
                item_name = slot_data['name']
                source = "toolbar"
                slot_index = self.selected_slot
            else:
                print("No item selected.")
                return False

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
        elif item_name == "Intelligence Potion":
            self.effects["Intelligence"] = 1200 # 20 seconds
            
            # Calculate potential new intelligence
            increase = 10
            new_intel = self.intelligence + increase
            
            # Apply Rank Cap
            if self.rank < 4:
                cap = RANK_INTEL_CAPS.get(self.rank, 25)
                self.intelligence = min(new_intel, cap)
            else:
                self.intelligence = new_intel
                
            print(f"Used Intelligence Potion! Intelligence: {self.intelligence}")
            used = True
        elif item_name == "Rank Up Potion":
            # Check Max Rank (Temporary Limit: Rank 4)
            if self.rank >= 4:
                print("Max Rank Reached (for now)!")
                return False
                
            # Check Intelligence Requirement
            req_intel = RANK_INTEL_CAPS.get(self.rank, 999)
            if self.intelligence < req_intel:
                print(f"Not enough Intelligence! Need {req_intel} to Rank Up.")
                return False
                
            if self.rank < 9:
                self.rank += 1
                self.intelligence += 5 # Permanent boost
                print(f"Used Rank Up Potion! Rank Up! New Rank: {self.rank}")
                # Update brain shape flavor text
                shapes = ["Smooth", "Wrinkled", "Folded", "Complex", "Glowing", "Radiant", "Cosmic", "Transcendent", "Omniscient"]
                self.brain_shape = shapes[self.rank - 1]
            else:
                print("Already at Max Rank!")
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
