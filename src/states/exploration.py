from src.states.game_state import GameState
from src.entities.player import Player
from src.entities.forest_creature import ForestCreature
from src.entities.chasing_creature import ChasingCreature
from src.entities.item import Item
from src.entities.fairy import Fairy
from src.config import *
import pygame
import random
import time

from src.entities.insect import Insect
from src.utils.camera import Camera
from src.utils.ui import Button
import math
import os
from src.assets import IMG_HOME_ICON, IMG_HOTKEY_BOX, IMG_HIGHLIGHT_SLOT, IMG_SLIDER, IMG_VALUE_BAR, IMG_VALUE_BLUE, IMG_TEMPLATE_BOX, MAP_FOREST
from pytmx.util_pygame import load_pygame

# Local Asset
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
IMG_HP_BAR = os.path.join(base_dir, "UI The Greatest Witch", "ValueBar_128x16.png")
# Local Asset Path for Settings
IMG_SETTINGS_BTN = os.path.join(base_dir, "UI The Greatest Witch", "settings_UI.png")
IMG_SLIDER_KNOB = os.path.join(base_dir, "UI The Greatest Witch", "CornerKnot_14x14.png")
SND_PICKUP = os.path.join(base_dir, "assets", "sounds", "sfx", "Pickup.wav")
SND_DEATH = os.path.join(base_dir, "assets", "sounds", "sfx", "det.wav")
IMG_SLIME = os.path.join(base_dir, "assets", "Slime2_Walk_full.png")
IMG_SLIME_3 = os.path.join(base_dir, "assets", "Slime3_Walk_full.png")
IMG_FAIRY = os.path.join(base_dir, "assets", "fairy.png")


class ExplorationState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.entities = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.fairies = pygame.sprite.Group()
        self.insects = pygame.sprite.Group()
        self.font = pygame.font.SysFont(None, 24)
        
        # Cache for Item Sprites
        self.item_images = {}
        
        # Load HP Bar
        self.hp_bar_image = None
        if os.path.exists(IMG_HP_BAR):
             self.hp_bar_image = pygame.image.load(IMG_HP_BAR).convert_alpha()
        else:
             print(f"Warning: HP Bar not found at {IMG_HP_BAR}")
             
        # Settings UI Init
        self.show_settings = False
        self.dragging_volume = False
        self.small_ui_font = pygame.font.SysFont(None, 20)
        
        # Settings Button
        self.settings_btn_image = None
        if os.path.exists(IMG_SETTINGS_BTN):
             self.settings_btn_image = pygame.image.load(IMG_SETTINGS_BTN).convert_alpha()
             self.settings_btn_image = pygame.transform.scale(self.settings_btn_image, (80, 80))
        else:
             print(f"Warning: Settings Btn not found at {IMG_SETTINGS_BTN}")
             
        self.btn_settings = Button(0, 0, 80, 80, "", self.font, color=GRAY, image=self.settings_btn_image)
        # Position it above the HP bar? Or Top Right?
        # Home uses stats_x, stats_y - 42.
        # Exploration HP Bar is at 20, 20.
        # Let's put Settings button at Top Right to avoid cluttering HP bar area, or maybe below HP bar?
        # User didn't specify position, but consistency is key.
        # In Home, it's near stats. Here we don't have stats.
        # Let's put it Top RightCorner for now: SCREEN_WIDTH - 100, 20
        self.btn_settings.rect.topleft = (SCREEN_WIDTH - 100, 20)
        
        # Volume Assets
        self.slider_image = None
        if os.path.exists(IMG_SLIDER):
             self.slider_image = pygame.image.load(IMG_SLIDER).convert_alpha()
             
        self.value_bar_image = None
        if os.path.exists(IMG_VALUE_BAR):
             self.value_bar_image = pygame.image.load(IMG_VALUE_BAR).convert_alpha()
             
        self.value_blue_image = None
        if os.path.exists(IMG_VALUE_BLUE):
             self.value_blue_image = pygame.image.load(IMG_VALUE_BLUE).convert_alpha()
             
        if os.path.exists(IMG_TEMPLATE_BOX):
             self.template_box_image = pygame.image.load(IMG_TEMPLATE_BOX).convert_alpha()
             
        self.slider_knob_image = None
        if os.path.exists(IMG_SLIDER_KNOB):
             self.slider_knob_image = pygame.image.load(IMG_SLIDER_KNOB).convert_alpha()
             self.slider_knob_image = pygame.transform.scale(self.slider_knob_image, (28, 28))
        
        # Map Loading (Forest TMX)
        self.tmx_data = load_pygame(MAP_FOREST)
        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight
        
        # Zoom Settings
        self.zoom = CAMERA_ZOOM
        self.viewport_width = int(SCREEN_WIDTH / self.zoom)
        self.viewport_height = int(SCREEN_HEIGHT / self.zoom)
        
        self.camera = Camera(self.map_width, self.map_height, self.viewport_width, self.viewport_height)
        
        self.chunk_size = 800
        self.loaded_chunks = {}
        
        # Display Surface for Zooming
        self.display_surface = pygame.Surface((self.viewport_width, self.viewport_height))
        
        # Grid Background (Obsolete with map, but good fallback)
        self.grid_surface = pygame.Surface((self.viewport_width, self.viewport_height)) 
        self.grid_surface.fill(DARK_GREEN_BG)
        # self.draw_grid()

        # Load Home Icon
        if os.path.exists(IMG_HOME_ICON):
             self.home_icon = pygame.image.load(IMG_HOME_ICON).convert_alpha()
             self.home_icon_rect = self.home_icon.get_rect()
             # Position Home Icon at bottom, right of toolbox?
             # User said toolbox centered.
             # Let's keep existing pos logic but maybe adjust later.
             self.home_icon_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
        else:
             print(f"Warning: Home Icon not found at {IMG_HOME_ICON}")
             self.home_icon = None
             self.home_icon_rect = pygame.Rect(SCREEN_WIDTH // 2 - 20, 20, 40, 40) # Fallback rect
             
        # Load Toolbox Images
        self.toolbar_box_image = None
        if os.path.exists(IMG_HOTKEY_BOX):
             self.toolbar_box_image = pygame.image.load(IMG_HOTKEY_BOX).convert_alpha()
        else:
             print(f"Warning: HotkeyBox not found at {IMG_HOTKEY_BOX}")

        self.highlight_image = None
        if os.path.exists(IMG_HIGHLIGHT_SLOT):
             self.highlight_image = pygame.image.load(IMG_HIGHLIGHT_SLOT).convert_alpha()
             self.highlight_image = pygame.transform.scale(self.highlight_image, (40, 40)) # Larger than box to surround it 
        else:
             print(f"Warning: HighlightSlot not found at {IMG_HIGHLIGHT_SLOT}")

        # Load Sounds
        self.pickup_sound = None
        if os.path.exists(SND_PICKUP):
             self.pickup_sound = pygame.mixer.Sound(SND_PICKUP)
        else:
             print(f"Warning: Pickup Sound not found at {SND_PICKUP}")

        self.death_sound = None
        if os.path.exists(SND_DEATH):
             self.death_sound = pygame.mixer.Sound(SND_DEATH)
        else:
             print(f"Warning: Death Sound not found at {SND_DEATH}")

        self.slime_image = None
        if os.path.exists(IMG_SLIME):
             self.slime_image = pygame.image.load(IMG_SLIME).convert_alpha()
        else:
             print(f"Warning: Slime Image not found at {IMG_SLIME}")

        self.slime3_image = None
        if os.path.exists(IMG_SLIME_3):
             self.slime3_image = pygame.image.load(IMG_SLIME_3).convert_alpha()
        else:
             print(f"Warning: Slime3 Image not found at {IMG_SLIME_3}")
             
        if os.path.exists(IMG_FAIRY):
             self.fairy_image = pygame.image.load(IMG_FAIRY).convert_alpha()
        else:
             print(f"Warning: Fairy Image not found at {IMG_FAIRY}")

        # Load Butterfly Image
        self.butterfly_image = None
        from src.assets import IMG_BUTTERFLY
        if os.path.exists(IMG_BUTTERFLY):
             self.butterfly_image = pygame.image.load(IMG_BUTTERFLY).convert_alpha()
        else:
             print(f"Warning: Butterfly Image not found at {IMG_BUTTERFLY}")

    def enter(self):
        print("Entering Exploration State")
        # Start Teleport Cooldown immediately upon entering Exploration
        self.game.player.teleport_cooldown_end = time.time() + TELEPORT_COOLDOWN

    def get_item_image(self, name):
        if name not in self.item_images:
            try:
                temp_item = Item(0, 0, name)
                self.item_images[name] = temp_item.image
            except Exception as e:
                print(f"Error loading icon for {name}: {e}")
                s = pygame.Surface((32, 32))
                s.fill((128, 0, 128))
                self.item_images[name] = s
        return self.item_images[name]

    def draw_grid(self):
        # Draw static grid lines on the surface
        # We need to draw enough lines to cover the viewport
        for x in range(0, self.viewport_width, TILE_SIZE):
            pygame.draw.line(self.grid_surface, (30, 60, 30), (x, 0), (x, self.viewport_height))
        for y in range(0, self.viewport_height, TILE_SIZE):
            pygame.draw.line(self.grid_surface, (30, 60, 30), (0, y), (self.viewport_width, y))

    def handle_events(self, events):
        for event in events:
            # Settings Button
            if self.btn_settings.handle_event(event):
                 self.show_settings = not self.show_settings
                 self.game.paused = self.show_settings # Optional: Pause game? Home doesn't pause explicitly but blocks input.
                 print(f"Settings toggled: {self.show_settings}")
                 
            # Settings UI Logic (Volume Slider)
            if self.show_settings:
                 # Calculate Bar Rect (Same as Draw)
                 # Popup centered
                 popup_w = 300
                 popup_h = 200
                 popup_rect = pygame.Rect((SCREEN_WIDTH - popup_w)//2, (SCREEN_HEIGHT - popup_h)//2, popup_w, popup_h)
                 
                 # Volume Slider Rect
                 # Match draw: x+100, y+70, 128x16 (Moved left from 120)
                 bar_rect = pygame.Rect(popup_rect.x + 100, popup_rect.y + 70, 128, 16)
                 
                 if event.type == pygame.MOUSEBUTTONDOWN:
                      if bar_rect.inflate(20, 20).collidepoint(event.pos):
                           self.dragging_volume = True
                           # Calculate new volume
                           relative_x = event.pos[0] - bar_rect.x
                           self.game.volume = max(0.0, min(1.0, relative_x / bar_rect.width))
                           pygame.mixer.music.set_volume(self.game.volume)
                           
                 elif event.type == pygame.MOUSEBUTTONUP:
                      self.dragging_volume = False
                      
                 elif event.type == pygame.MOUSEMOTION:
                      if self.dragging_volume:
                           # Update Volume
                           relative_x = event.pos[0] - bar_rect.x
                           self.game.volume = max(0.0, min(1.0, relative_x / bar_rect.width))
                           pygame.mixer.music.set_volume(self.game.volume)

            # Block other input if Settings Open OR clicked on Settings Button
            if self.show_settings:
                # Still allow MOUSEBUTTONUP to bubble up if needed, but blocking Down is key
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                     # Allow 'Escape' to close settings?
                     continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                     # Check Home Button
                     if hasattr(self, 'home_icon_rect') and self.home_icon_rect.collidepoint(event.pos):
                         current_time = time.time()
                         if current_time >= self.game.player.teleport_cooldown_end:
                             self.game.player.rect.topleft = (90, 165)
                             self.game.states["home"].enter()
                             self.game.change_state("home")
                         else:
                             print(f"Teleport cooling down...")

            if event.type == pygame.KEYDOWN:
                # Toolbar Selection (1-9)
                if pygame.K_1 <= event.key <= pygame.K_9:
                     index = event.key - pygame.K_1
                     self.game.player.selected_slot = index
                     self.game.player.selected_slot = index
                     print(f"Selected slot {index + 1}")

                if event.key == pygame.K_f:
                     # Item Usage only (Portal is now automatic)
                     self.game.player.use_item()
                          
                     # Check for Bug Net usage
                     selected_slot = self.game.player.selected_slot
                     selected_item = self.game.player.toolbar[selected_slot]
                     if selected_item and selected_item['name'] == "Bug Net":
                         # Check collision with insects
                         # Create a "net" rect in front of player? Or just use player rect for simplicity
                         # For now, use player rect + small range
                         catch_rect = self.game.player.rect.inflate(20, 20)
                         caught_insects = [insect for insect in self.insects if catch_rect.colliderect(insect.rect)]
                         
                         for insect in caught_insects:
                             self.insects.remove(insect)
                             # Add insect to inventory (Generic "Insect" item or specific?)
                             # For now, let's say "Beetle" or just "Insect"
                             # Config doesn't specify insect types yet, let's use "Beetle"
                             self.game.player.add_item("Beetle")
                             if self.pickup_sound:
                                 self.pickup_sound.play()
                             print("Caught a Beetle!")

    def update(self):
        self.game.player.update()
        self.camera.update(self.game.player)
        
        # Portal Trigger (Automatic) - Removed as per user request (Direction reversed)
        # Spawn Enemies
        if random.random() < 0.01: # Slightly increased spawn rate
            x = self.game.player.rect.x + random.randint(-400, 400)
            y = self.game.player.rect.y + random.randint(-300, 300)
            
            # Chance to spawn Chasing Creature
            if random.random() < 0.3: # 30% chance for Magma Slime
                enemy = ChasingCreature(x, y, self.slime3_image, self.game.player)
            else:
                enemy = ForestCreature(x, y, self.slime_image)
            self.entities.add(enemy)
            
        # Spawn Items
        if random.random() < 0.01:
            x = self.game.player.rect.x + random.randint(-400, 400)
            y = self.game.player.rect.y + random.randint(-300, 300)
            item_type = random.choice(["Water", "Red Herb", "Blue Herb"])
            # Rare Herb chance
            if random.random() < 0.1:
                item_type = "Rare Herb"
                
            item = Item(x, y, item_type)
            self.items.add(item)
            
        # Spawn Fairies
        if self.game.player.rank >= 4 and random.random() < FAIRY_SPAWN_CHANCE:
            x = self.game.player.rect.x + random.randint(-400, 400)
            y = self.game.player.rect.y + random.randint(-300, 300)
            fairy = Fairy(x, y)
            self.fairies.add(fairy)

        # Spawn Insects
        if random.random() < INSECT_SPAWN_CHANCE:
            x = self.game.player.rect.x + random.randint(-400, 400)
            y = self.game.player.rect.y + random.randint(-300, 300)
            insect = Insect(x, y, self.butterfly_image)
            self.insects.add(insect)
            
        # Update Entities
        self.entities.update()
        self.fairies.update()
        self.insects.update()
        
        # Collisions
        # Enemy
        hits = pygame.sprite.spritecollide(self.game.player, self.entities, False, pygame.sprite.collide_rect_ratio(0.6))
        if hits:
            current_time = time.time()
            if not hasattr(self.game.player, 'last_hit_time'):
                self.game.player.last_hit_time = 0
                
            if current_time - self.game.player.last_hit_time > 1.0: # 1 second invulnerability
                self.game.player.health -= 10
                self.game.player.last_hit_time = current_time
                print(f"Ouch! Hit by a forest creature! HP: {self.game.player.health}")
                
                # Knockback (Simple)
                for enemy in hits:
                    dx = self.game.player.rect.centerx - enemy.rect.centerx
                    dy = self.game.player.rect.centery - enemy.rect.centery
                    dist = (dx**2 + dy**2)**0.5
                    if dist != 0:
                        self.game.player.rect.x += (dx/dist) * 20
                        self.game.player.rect.y += (dy/dist) * 20
            
            # Check Death
            if self.game.player.health <= 0:
                print("Player Died!")
                if self.death_sound:
                    self.death_sound.play()
                
                # Restore HP
                self.game.player.health = self.game.player.max_health
                
                # Teleport Home
                self.game.player.rect.topleft = (90, 165)
                self.game.states["home"].enter()
                self.game.change_state("home")
                return # Stop processing update
            
            # Knockback or damage logic here
            
        # Item Collection
        collected = pygame.sprite.spritecollide(self.game.player, self.items, True)
        for item in collected:
            self.game.player.add_item(item.name)
            if self.pickup_sound:
                self.pickup_sound.play()
            
        # Fairy Collection
        caught_fairies = pygame.sprite.spritecollide(self.game.player, self.fairies, True)
        for fairy in caught_fairies:
            self.game.player.fairies_caught += 1
            print(f"Caught a Fairy! Total: {self.game.player.fairies_caught}")

    def draw(self, screen):
        # Draw to display_surface first (Zoomed View)
        # Fill Background
        self.display_surface.fill(BLACK)
        
        # --- Draw Map Layers (Bottom) ---
        # Draw layers EXCEPT 14 and 15
        if hasattr(self, 'tmx_data'):
             for layer in self.tmx_data.visible_layers:
                 # Check Layer ID (if available) or name
                 # Pytmx layers usually have 'id' property if loaded from recent Tiled
                 # If not, we might need to rely on name or index
                 # User asked for "Layer 14 and 15", presumably IDs.
                 try:
                     layer_id = layer.id
                 except AttributeError:
                     # Fallback if id not found, though visible_layers usually have it
                     layer_id = -1
                     
                 if layer_id in [14, 15]:
                     continue # Draw later
                 
                 if hasattr(layer, 'tiles'):
                     for x, y, gid in layer:
                         tile = self.tmx_data.get_tile_image_by_gid(gid)
                         if tile:
                             target_x = x * self.tmx_data.tilewidth + self.camera.camera.x
                             target_y = y * self.tmx_data.tileheight + self.camera.camera.y
                             self.display_surface.blit(tile, (target_x, target_y))
        
        else:
             # Fallback if map not loaded
             self.display_surface.blit(self.grid_surface, (0, 0))

        # Draw Portal (at 0,0) - Only if not using map or as overlay?
        # With forest map, maybe portal is part of map?
        # Let's keep it for now as invisible marker or simple rect
        portal_rect = pygame.Rect(-50, -50, 100, 100)
        # pygame.draw.rect(self.display_surface, (100, 0, 100), self.camera.apply_rect(portal_rect))
        
        # Draw Entities
        for entity in self.entities:
            self.display_surface.blit(entity.image, self.camera.apply(entity))
            
        for item in self.items:
            self.display_surface.blit(item.image, self.camera.apply(item))
            
        for fairy in self.fairies:
            fairy.draw(self.display_surface, self.camera)
            
        # Draw Insects
        for insect in self.insects:
            self.display_surface.blit(insect.image, self.camera.apply(insect))

        # Draw Player
        if hasattr(self.game.player, 'image'):
            self.display_surface.blit(self.game.player.image, self.camera.apply(self.game.player))
        else:
            pygame.draw.rect(self.display_surface, BLUE, self.camera.apply(self.game.player))
            
        # --- Draw Map Layers (Top) ---
        # Layers 14 and 15 (Foregound/Overhead)
        if hasattr(self, 'tmx_data'):
             for layer in self.tmx_data.visible_layers:
                 try:
                     layer_id = layer.id
                 except AttributeError:
                     layer_id = -1
                     
                 if layer_id in [14, 15]:
                     if hasattr(layer, 'tiles'):
                         for x, y, gid in layer:
                             tile = self.tmx_data.get_tile_image_by_gid(gid)
                             if tile:
                                 target_x = x * self.tmx_data.tilewidth + self.camera.camera.x
                                 target_y = y * self.tmx_data.tileheight + self.camera.camera.y
                                 self.display_surface.blit(tile, (target_x, target_y))
            
        # --- Darkness / Lantern Effect ---
        # Create darkness surface if not exists (optimization)
        if not hasattr(self, 'darkness_surface'):
            self.darkness_surface = pygame.Surface((self.viewport_width, self.viewport_height), pygame.SRCALPHA)

        # Generate Light Mask if not exists (Lazy Load)
        if not hasattr(self, 'light_mask'):
             self.generate_light_mask()
            
        # Fill with semi-transparent black (Night time)
        self.darkness_surface.fill((0, 0, 0, LANTERN_MAX_ALPHA)) 
        
        # Apply Lantern Light (Subtract alpha from darkness)
        player_rect = self.camera.apply(self.game.player)
        center = player_rect.center
        
        # Blit the pre-generated gradient mask using BLEND_RGBA_SUB
        # Result = Dest - Source.
        # Dest Alpha = 200. Source Alpha = Gradient (200->0).
        # Center: 200 - 200 = 0 (Transparent). Edge: 200 - 0 = 200 (Dark).
        mask_rect = self.light_mask.get_rect(center=center)
        self.darkness_surface.blit(self.light_mask, mask_rect, special_flags=pygame.BLEND_RGBA_SUB)
        
        # Draw darkness
        self.display_surface.blit(self.darkness_surface, (0, 0))


        
        # --- Scale and Blit to Main Screen ---
        pygame.transform.scale(self.display_surface, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)
            
        # --- HUD (Draw directly on screen for sharpness) ---
        
        # HP Bar
        hp_x = 20
        hp_y = 20
        
        # HP Calculation
        hp_percent = max(0, self.game.player.health / self.game.player.max_health)
        
        if self.hp_bar_image:
            # Draw Frame (128x16)
            screen.blit(self.hp_bar_image, (hp_x, hp_y))
            
            # Draw Fill (Green) Inside
            # Assuming 128x16 frame has ~4px border. Inner size ~120x8.
            inner_w = 120
            inner_h = 8
            padding_x = 4
            padding_y = 4
            
            # Draw Empty backing (Dark Red/Black)
            pygame.draw.rect(screen, (50, 0, 0), (hp_x + padding_x, hp_y + padding_y, inner_w, inner_h))
            
            # Draw Current HP
            if hp_percent > 0:
                pygame.draw.rect(screen, GREEN, (hp_x + padding_x, hp_y + padding_y, inner_w * hp_percent, inner_h))
            
            # Text (Moved slightly down/right to not overlap small bar)
            hp_text = self.font.render(f"HP: {self.game.player.health}/{self.game.player.max_health}", True, WHITE)
            screen.blit(hp_text, (hp_x + 135, hp_y)) # To the right of the bar
            
        else:
            # Fallback code
            hp_bar_width = 200
            hp_bar_height = 20
            
            # Background
            pygame.draw.rect(screen, RED, (hp_x, hp_y, hp_bar_width, hp_bar_height))
            # Foreground
            pygame.draw.rect(screen, GREEN, (hp_x, hp_y, hp_bar_width * hp_percent, hp_bar_height))
            # Border
            pygame.draw.rect(screen, WHITE, (hp_x, hp_y, hp_bar_width, hp_bar_height), 2)
            # Text
            hp_text = self.font.render(f"HP: {self.game.player.health}/{self.game.player.max_health}", True, WHITE)
            screen.blit(hp_text, (hp_x + 5, hp_y + 2))

        # Toolbar
        # Calculate Start X based on Config
        total_width = (9 * TOOLBAR_SLOT_SIZE) + (8 * TOOLBAR_SPACING)
        toolbar_start_x = (SCREEN_WIDTH - total_width) // 2 + TOOLBAR_X_SHIFT
        toolbar_y = SCREEN_HEIGHT - TOOLBAR_Y_OFFSET
        
        for i in range(9):
            x = toolbar_start_x + i * (TOOLBAR_SLOT_SIZE + TOOLBAR_SPACING)
            rect = pygame.Rect(x, toolbar_y, TOOLBAR_SLOT_SIZE, TOOLBAR_SLOT_SIZE)
            
            # Draw Slot Background
            if self.toolbar_box_image:
                 # Scale box to new size
                 scaled_box = pygame.transform.scale(self.toolbar_box_image, (TOOLBAR_SLOT_SIZE, TOOLBAR_SLOT_SIZE))
                 screen.blit(scaled_box, (x, toolbar_y))
            else:
                 pygame.draw.rect(screen, BLACK, rect)
                 pygame.draw.rect(screen, WHITE, rect, 1)

            slot_data = self.game.player.toolbar[i]
            if slot_data:
                # Draw Item Icon
                icon = self.get_item_image(slot_data['name'])
                
                # Scale Item
                item_size = int(TOOLBAR_SLOT_SIZE * TOOLBAR_ITEM_SCALE)
                icon = pygame.transform.scale(icon, (item_size, item_size))
                
                # Center Item
                offset = (TOOLBAR_SLOT_SIZE - item_size) // 2
                screen.blit(icon, (x + offset, toolbar_y + offset))
                
                # Draw Count
                count = slot_data['count']
                count_text = self.font.render(str(count), True, WHITE)
                screen.blit(count_text, (x + 2, toolbar_y + 2))
                
                # Draw Name (Small)
                name = slot_data['name']
                name_surf = pygame.font.SysFont(None, 12).render(name[:3], True, WHITE)
                screen.blit(name_surf, (x+2, toolbar_y + TOOLBAR_SLOT_SIZE - 12))
                
            # Highlight selected
            if i == self.game.player.selected_slot:
                if self.highlight_image:
                     # Draw aligned with box (Scale highlight to match)
                     highlight_size = int(TOOLBAR_SLOT_SIZE * 1.2)
                     offset = (highlight_size - TOOLBAR_SLOT_SIZE) // 2
                     scaled_highlight = pygame.transform.scale(self.highlight_image, (highlight_size, highlight_size))
                     screen.blit(scaled_highlight, (x - offset, toolbar_y - offset))
                else:
                     pygame.draw.rect(screen, YELLOW, rect.inflate(4, 4), 2)
                
        # Draw Home Icon
        if hasattr(self, 'home_icon') and self.home_icon:
            screen.blit(self.home_icon, self.home_icon_rect)
        else:
            # Fallback
            if hasattr(self, 'home_icon_rect'):
                 pygame.draw.rect(screen, (100, 50, 0), self.home_icon_rect)

        # Cooldown Overlay on Home Icon
        current_time = time.time()
        if current_time < self.game.player.teleport_cooldown_end:
            remaining = self.game.player.teleport_cooldown_end - current_time
            max_cd = TELEPORT_COOLDOWN
            ratio = remaining / max_cd
            
            # Dark overlay (Clock sweep)
            # Draw full 50% black circle first? No, user said "area berkurang".
            # So we draw the black sector representing the remaining cooldown.
            # Center at icon center. radius roughly icon width/2.
            icon_rect = self.home_icon_rect
            center = icon_rect.center
            radius = icon_rect.width // 2
            
            # Create a localized surface for alpha blending if needed, OR just draw directly with rgba if pygame supports it (Shape drawing supports alpha in newer pygame, but safe bet is a separate surface or polygon with alpha color)
            # Actually, standard draw.polygon doesn't support alpha on main screen directly in older pygame?
            # It does in recent versions. Let's try drawing to a temp surface.
            
            overlay_surf = pygame.Surface((icon_rect.width, icon_rect.height), pygame.SRCALPHA)
            
            # Calculate polygon points for the "remaining" slice
            # Start from top (12 o'clock) -> -90 degrees
            # Angle covers 360 * ratio
            
            points = [ (radius, radius) ] # Center relative to surf
            
            # Number of segments for smoothness
            num_segments = int(360 * ratio)
            if num_segments < 3: num_segments = 3
            
            start_angle = -90
            end_angle = start_angle + (360 * ratio)
            
            # We want to fill the area from start_angle to end_angle?
            # User: "lingkaran hitam ... areanya berkurang ... animasinya seperti jam"
            # Usually means the "black part" represents the cooldown time left.
            # So full circle at max CD. 0 circle at 0 CD.
            # So yes, draw sector of angle `360 * ratio`.
            
            for i in range(num_segments + 1):
                angle_deg = start_angle - (360 * ratio * (i / num_segments)) # Clockwise?
                # Usually clock wipe: 12 -> 3 -> 6. 
                # Let's do Counter-Clockwise from 12? Or Clockwise?
                # "Animasinya seperti jam" (Clockwise).
                # So from -90, go +degrees.
                current_angle = start_angle + (360 * ratio) if False else start_angle - (i * (360*ratio)/num_segments) 
                
                # Wait, usually cooldown overlay starts full and "unfills".
                # If ratio is 0.5, we want 180 degrees of black.
                # Let's draw from -90 to -90 + (360*ratio) CLOCKWISE.
                # Wait, standard trig: 0 is right, -90 is up. Clockwise increases angle? No, standard math angle increases CCW.
                # To go Clockwise from -90: -90, -91, ...
                
                angle_rad = math.radians(start_angle - (360 * ratio * (i/num_segments))) * -1 # Reflect for screen coords if needed? No, just use std formula
                # x = r * cos(theta), y = r * sin(theta)
                # But we want Clockwise.
                # Let's just use `angle_deg = -90 + (360 * (1-ratio))`? No.
                # Let's simplify: Draw the "remaining" wedge.
                # Points: Center, Top, ... around to current progress.
                
                # Let's try: angle runs from -90 (top) to -90 + (360 * ratio) in Clockwise direction??
                # Clockwise from top: -90 -> 0 (Right) -> 90 (Bottom). 
                # So Angle increases? Yes in screen space (y down).
                # math.sin(0) = 0. sin(90) = 1.
                # So screen angle: 0 is Right, 90 is Down.
                # -90 is Up.
                # So we want to fill from -90 to -90 + (360*ratio).
                
                passbase = -90
                theta = math.radians(passbase + (360 * ratio * (i/num_segments))) # Wait, this goes Clockwise 12->3
                
                x = radius + radius * math.cos(theta)
                y = radius + radius * math.sin(theta)
                points.append((x, y))
                
            if len(points) > 2:
                pygame.draw.polygon(overlay_surf, (0, 0, 0, 128), points)
                screen.blit(overlay_surf, icon_rect)

        else:
             # Cooldown finished
             pass
             
        # "Home" Text
        label_surf = self.font.render("Home", True, WHITE)
        # Center below icon
        label_x = self.home_icon_rect.centerx - label_surf.get_width() // 2
        label_y = self.home_icon_rect.bottom + 5
        screen.blit(label_surf, (label_x, label_y))
        
        # --- Settings UI ---
        # Draw Settings Button
        self.btn_settings.draw(screen)
        
        # Draw Settings Popup
        if self.show_settings:
             # Center Screen
             popup_w = 300
             popup_h = 200
             popup_rect = pygame.Rect((SCREEN_WIDTH - popup_w)//2, (SCREEN_HEIGHT - popup_h)//2, popup_w, popup_h)
             
             if self.template_box_image:
                  scaled_box = pygame.transform.scale(self.template_box_image, (popup_w, popup_h))
                  screen.blit(scaled_box, popup_rect)
             else:
                  pygame.draw.rect(screen, GRAY, popup_rect)
                  pygame.draw.rect(screen, WHITE, popup_rect, 2)
                  
             # Title "Settings"
             title_surf = self.font.render("Settings", True, WHITE)
             screen.blit(title_surf, (popup_rect.centerx - title_surf.get_width()//2, popup_rect.y + 20))
             
             # Volume Control
             # Match HomeState Layout
             vol_text = self.small_ui_font.render("Volume", True, WHITE)
             screen.blit(vol_text, (popup_rect.x + 58, popup_rect.y + 70))
             
             # Slider Bar
             bar_w = 128
             bar_h = 16
             bar_rect = pygame.Rect(popup_rect.x + 100, popup_rect.y + 70, bar_w, bar_h)
             
             if self.value_bar_image and self.value_blue_image:
                 # Draw Frame
                 screen.blit(self.value_bar_image, bar_rect)
                 
                 # Draw/Clip Blue Fill
                 inner_max_w = 120
                 fill_w = int(inner_max_w * self.game.volume)
                 
                 if fill_w > 0:
                     fill_w = max(0, min(fill_w, inner_max_w))
                     sub_surf = self.value_blue_image.subsurface((0, 0, fill_w, 8))
                     screen.blit(sub_surf, (bar_rect.x + 4, bar_rect.y + 4))
             else:
                 # Fallback
                 pygame.draw.rect(screen, BLACK, bar_rect)
                 fill_width = int(bar_rect.width * self.game.volume)
                 pygame.draw.rect(screen, GREEN, (bar_rect.x, bar_rect.y, fill_width, bar_rect.height))
                 pygame.draw.rect(screen, WHITE, bar_rect, 2)
             
             # Slider Knob (Square Button)
             travel_w = 120
             knob_size = 28
             knob_center_x = bar_rect.x + 4 + int(travel_w * self.game.volume)
             knob_y = bar_rect.centery - knob_size // 2
             
             knob_rect = pygame.Rect(knob_center_x - knob_size//2, knob_y, knob_size, knob_size)
             
             if hasattr(self, 'slider_knob_image') and self.slider_knob_image:
                  screen.blit(self.slider_knob_image, knob_rect)
             else:
                  pygame.draw.rect(screen, (200, 200, 200), knob_rect) # Light Gray face
                  pygame.draw.rect(screen, WHITE, knob_rect, 2) # Border

    def generate_light_mask(self):
        # Create a radial gradient surface
        radius = LANTERN_RADIUS
        max_alpha = LANTERN_MAX_ALPHA
        size = radius * 2
        
        self.light_mask = pygame.Surface((size, size), pygame.SRCALPHA)
        self.light_mask.fill((0,0,0,0))
        
        # Pixel Array approach (Robust)
        cx, cy = radius, radius
        for x in range(size):
             for y in range(size):
                  dx = x - cx
                  dy = y - cy
                  dist = (dx*dx + dy*dy)**0.5
                  if dist <= radius:
                       alpha = int(max_alpha * (1 - dist/radius))
                       if alpha < 0: alpha = 0
                       self.light_mask.set_at((x, y), (0, 0, 0, alpha))
