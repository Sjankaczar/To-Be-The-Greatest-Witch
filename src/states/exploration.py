from src.states.game_state import GameState
from src.entities.player import Player
from src.entities.forest_creature import ForestCreature
from src.entities.item import Item
from src.entities.fairy import Fairy
from src.config import *
import pygame
import random
import time

from src.entities.insect import Insect
from src.utils.camera import Camera

class ExplorationState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.entities = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.fairies = pygame.sprite.Group()
        self.insects = pygame.sprite.Group()
        self.font = pygame.font.SysFont(None, 24)
        
        # Infinite Map Settings (Virtual Size for Camera)
        self.map_width = 2000 # Arbitrary large size for now
        self.map_height = 2000
        
        # Zoom Settings
        self.zoom = CAMERA_ZOOM
        self.viewport_width = int(SCREEN_WIDTH / self.zoom)
        self.viewport_height = int(SCREEN_HEIGHT / self.zoom)
        
        self.camera = Camera(self.map_width, self.map_height, self.viewport_width, self.viewport_height)
        
        self.chunk_size = 800
        self.loaded_chunks = {}
        
        # Display Surface for Zooming
        self.display_surface = pygame.Surface((self.viewport_width, self.viewport_height))
        
        # Grid Background
        self.grid_surface = pygame.Surface((self.viewport_width, self.viewport_height)) # Optimization: Match viewport
        self.grid_surface.fill(DARK_GREEN_BG)
        self.draw_grid()

    def enter(self):
        print("Entering Exploration State")
        # Start Teleport Cooldown immediately upon entering Exploration
        self.game.player.teleport_cooldown_end = time.time() + TELEPORT_COOLDOWN

    def draw_grid(self):
        # Draw static grid lines on the surface
        # We need to draw enough lines to cover the viewport
        for x in range(0, self.viewport_width, TILE_SIZE):
            pygame.draw.line(self.grid_surface, (30, 60, 30), (x, 0), (x, self.viewport_height))
        for y in range(0, self.viewport_height, TILE_SIZE):
            pygame.draw.line(self.grid_surface, (30, 60, 30), (0, y), (self.viewport_width, y))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    # Check for portal interaction (return home)
                    # Simplified: If near (0,0)
                    if self.game.player.rect.colliderect(pygame.Rect(-50, -50, 100, 100)):
                        # Check cooldown
                        current_time = time.time()
                        if current_time >= self.game.player.teleport_cooldown_end:
                            self.game.states["home"].enter()
                            self.game.change_state("home")

                        else:
                            print(f"Teleport cooling down... {self.game.player.teleport_cooldown_end - current_time:.1f}s left")
                
                # Teleport Home (H)
                if event.key == pygame.K_h:
                    # Check cooldown
                    current_time = time.time()
                    if current_time >= self.game.player.teleport_cooldown_end:
                        self.game.states["home"].enter()
                        self.game.change_state("home")

                        
                if event.key == pygame.K_f:
                     # If not near portal, try use item
                    if not self.game.player.rect.colliderect(pygame.Rect(-50, -50, 100, 100)):
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
                                 print("Caught a Beetle!")

    def update(self):
        self.game.player.update()
        self.camera.update(self.game.player)
        
        # Spawn Enemies
        if random.random() < 0.005: # Reduced from 0.02
            x = self.game.player.rect.x + random.randint(-400, 400)
            y = self.game.player.rect.y + random.randint(-300, 300)
            enemy = ForestCreature(x, y)
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
            insect = Insect(x, y)
            self.insects.add(insect)
            
        # Update Entities
        self.entities.update()
        self.fairies.update()
        self.insects.update()
        
        # Collisions
        # Enemy
        hits = pygame.sprite.spritecollide(self.game.player, self.entities, False)
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
            
            # Knockback or damage logic here
            
        # Item Collection
        collected = pygame.sprite.spritecollide(self.game.player, self.items, True)
        for item in collected:
            self.game.player.add_item(item.name)
            
        # Fairy Collection
        caught_fairies = pygame.sprite.spritecollide(self.game.player, self.fairies, True)
        for fairy in caught_fairies:
            self.game.player.fairies_caught += 1
            print(f"Caught a Fairy! Total: {self.game.player.fairies_caught}")

    def draw(self, screen):
        # Draw to display_surface first (Zoomed View)
        
        # Draw Infinite Grid Background
        # Calculate offset for grid scrolling
        cam_x = self.camera.camera.x
        cam_y = self.camera.camera.y
        
        # Modulo to repeat pattern
        bg_x = cam_x % self.viewport_width
        bg_y = cam_y % self.viewport_height
        
        # Draw 4 tiles to cover screen
        self.display_surface.blit(self.grid_surface, (bg_x - self.viewport_width, bg_y - self.viewport_height))
        self.display_surface.blit(self.grid_surface, (bg_x, bg_y - self.viewport_height))
        self.display_surface.blit(self.grid_surface, (bg_x - self.viewport_width, bg_y))
        self.display_surface.blit(self.grid_surface, (bg_x, bg_y))
        
        # Draw Portal (at 0,0)
        portal_rect = pygame.Rect(-50, -50, 100, 100)
        pygame.draw.rect(self.display_surface, (100, 0, 100), self.camera.apply_rect(portal_rect))
        
        # Draw Entities
        for entity in self.entities:
            self.display_surface.blit(entity.image, self.camera.apply(entity))
            
        for item in self.items:
            self.display_surface.blit(item.image, self.camera.apply(item))
            
        for fairy in self.fairies:
            fairy.draw(self.display_surface, self.camera)
            
        # Draw Insects
        # Draw Insects
        for insect in self.insects:
            self.display_surface.blit(insect.image, self.camera.apply(insect))

        # Draw Player
        if hasattr(self.game.player, 'image'):
            self.display_surface.blit(self.game.player.image, self.camera.apply(self.game.player))
        else:
            pygame.draw.rect(self.display_surface, BLUE, self.camera.apply(self.game.player))
            
        # --- Darkness / Lantern Effect ---
        # Create darkness surface if not exists (optimization)
        if not hasattr(self, 'darkness_surface'):
            self.darkness_surface = pygame.Surface((self.viewport_width, self.viewport_height), pygame.SRCALPHA)
            
        # Fill with semi-transparent black (Night time)
        self.darkness_surface.fill((0, 0, 0, 200)) 
        
        # Create Lantern Light (Gradient Circle)
        # We subtract alpha from the darkness surface to create light
        player_rect = self.camera.apply(self.game.player)
        center = player_rect.center
        
        # Simple hole for now (can be improved with gradient texture later)
        pygame.draw.circle(self.darkness_surface, (0, 0, 0, 0), center, 150) # Clear circle
        
        # Draw darkness
        self.display_surface.blit(self.darkness_surface, (0, 0))
        
        # --- Scale and Blit to Main Screen ---
        pygame.transform.scale(self.display_surface, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)
            
        # --- HUD (Draw directly on screen for sharpness) ---
        
        # HP Bar
        hp_bar_width = 200
        hp_bar_height = 20
        hp_x = 20
        hp_y = 20
        
        # Background
        pygame.draw.rect(screen, RED, (hp_x, hp_y, hp_bar_width, hp_bar_height))
        # Foreground
        hp_percent = max(0, self.game.player.health / self.game.player.max_health)
        pygame.draw.rect(screen, GREEN, (hp_x, hp_y, hp_bar_width * hp_percent, hp_bar_height))
        # Border
        pygame.draw.rect(screen, WHITE, (hp_x, hp_y, hp_bar_width, hp_bar_height), 2)
        # Text
        hp_text = self.font.render(f"HP: {self.game.player.health}/{self.game.player.max_health}", True, WHITE)
        screen.blit(hp_text, (hp_x + 5, hp_y + 2))

        # Toolbar
        toolbar_start_x = (SCREEN_WIDTH - (9 * 40)) // 2
        toolbar_y = SCREEN_HEIGHT - 50
        
        for i in range(9):
            x = toolbar_start_x + i * 40
            rect = pygame.Rect(x, toolbar_y, 32, 32)
            
            # Highlight selected
            if i == self.game.player.selected_slot:
                pygame.draw.rect(screen, YELLOW, (x-2, toolbar_y-2, 36, 36), 2)
            
            pygame.draw.rect(screen, BLACK, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)
            
            slot_data = self.game.player.toolbar[i]
            if slot_data:
                # Draw Item Icon (Placeholder)
                pygame.draw.rect(screen, PURPLE, (x+2, toolbar_y+2, 28, 28))
                
                # Draw Count
                count = slot_data['count']
                count_text = self.font.render(str(count), True, WHITE)
                screen.blit(count_text, (x + 2, toolbar_y + 2))
                
                # Draw Name (Small)
                name = slot_data['name']
                name_surf = pygame.font.SysFont(None, 12).render(name[:3], True, WHITE)
                screen.blit(name_surf, (x+2, toolbar_y+20))
                
        # Cooldown Text / Teleport Message
        current_time = time.time()
        if current_time < self.game.player.teleport_cooldown_end:
            remaining = self.game.player.teleport_cooldown_end - current_time
            cd_text = self.font.render(f"Teleport Cooldown: {remaining:.1f}s", True, RED)
            screen.blit(cd_text, (SCREEN_WIDTH // 2 - 100, 50))
        else:
            # Show "Press H to Return Home"
            msg_text = self.font.render("Press H to Return Home", True, GREEN)
            screen.blit(msg_text, (SCREEN_WIDTH // 2 - 100, 50))
