import pygame
import time
from src.states.game_state import GameState
from src.config import *
from src.entities.forest_creature import ForestCreature
from src.entities.item import Item
from src.utils.camera import Camera

class ExplorationState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        
        # Infinite Map Logic
        self.chunk_size = SCREEN_WIDTH
        self.loaded_chunks = set()
        
        # Initial spawn
        self.check_chunks()

    def generate_chunk(self, chunk_x, chunk_y):
        import random
        
        # Spawn enemies
        if random.random() < 0.5: # 50% chance of enemy per chunk
            enemy = ForestCreature(
                chunk_x * self.chunk_size + random.randint(0, self.chunk_size),
                chunk_y * self.chunk_size + random.randint(0, self.chunk_size)
            )
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            
        # Spawn items
        if random.random() < 0.7: # 70% chance of item
            item_type = random.choice(["Red Herb", "Blue Herb", "Water"])
            item = Item(
                chunk_x * self.chunk_size + random.randint(0, self.chunk_size),
                chunk_y * self.chunk_size + random.randint(0, self.chunk_size),
                item_type
            )
            self.items.add(item)
            self.all_sprites.add(item)

    def check_chunks(self):
        # Calculate current chunk based on player position
        player_x, player_y = self.game.player.rect.center
        chunk_x = int(player_x // self.chunk_size)
        chunk_y = int(player_y // self.chunk_size)
        
        # Load surrounding chunks (3x3 grid)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                chunk_coord = (chunk_x + dx, chunk_y + dy)
                if chunk_coord not in self.loaded_chunks:
                    self.generate_chunk(chunk_coord[0], chunk_coord[1])
                    self.loaded_chunks.add(chunk_coord)

    def enter(self):
        # Reset player position
        self.game.player.rect.topleft = (0, 0)
        # Set cooldown on ENTER
        self.game.player.teleport_cooldown_end = time.time() + TELEPORT_COOLDOWN
        print(f"Entered Exploration Mode. Position reset. Cooldown until {self.game.player.teleport_cooldown_end}")

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    current_time = time.time()
                    if current_time >= self.game.player.teleport_cooldown_end:
                        self.game.change_state("home")
                    else:
                        remaining = int(self.game.player.teleport_cooldown_end - current_time)
                        print(f"Teleport on cooldown: {remaining}s")
                elif event.key == pygame.K_f:
                    # Use item in selected slot
                    selected_slot = self.game.player.selected_slot
                    slot_data = self.game.player.toolbar[selected_slot]
                    
                    if slot_data:
                        item_name = slot_data['name']
                        # Use item from toolbar source
                        self.game.player.use_item(item_name, source="toolbar", slot_index=selected_slot)
                    else:
                        print("No item in selected slot!")
                        
                # Number keys 1-9 for toolbar selection
                elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                    slot = event.key - pygame.K_1
                    self.game.player.selected_slot = slot
                    print(f"Selected slot {slot + 1}")

    def update(self):
        self.game.player.update()
        self.camera.update(self.game.player)
        self.check_chunks()
        
        # Update only sprites near player (optimization) could be added here
        self.enemies.update()
        
        # Collision detection
        # Player vs Items
        hits = pygame.sprite.spritecollide(self.game.player, self.items, True)
        for hit in hits:
            self.game.player.add_item(hit.name)
            
        # Player vs Enemies
        # Check for invisibility
        if "Invisibility" not in self.game.player.effects:
            if pygame.sprite.spritecollideany(self.game.player, self.enemies):
                print("Ouch! Hit by a forest creature!")
                # Push player back slightly
                self.game.player.rect.x -= self.game.player.velocity * 5 # Stronger knockback
                self.game.player.rect.y -= self.game.player.velocity * 5
                
                # Reduce health
                self.game.player.health -= 10
                print(f"Health: {self.game.player.health}")
                
                if self.game.player.health <= 0:
                    print("You died! Respawning at home...")
                    self.game.player.health = self.game.player.max_health
                    self.game.player.rect.topleft = (100, 100) # Reset position
                    self.game.change_state("home")

    def draw(self, screen):
        screen.fill(DARK_GREEN_BG) # Dark forest background
        
        # Draw World Grid
        grid_size = 50
        # Calculate offset based on camera position
        start_x = self.camera.camera.x % grid_size
        start_y = self.camera.camera.y % grid_size
        
        for x in range(start_x, SCREEN_WIDTH, grid_size):
            pygame.draw.line(screen, (34, 139, 34), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(start_y, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(screen, (34, 139, 34), (0, y), (SCREEN_WIDTH, y))
        
        # Draw all sprites with camera offset
        for sprite in self.all_sprites:
            screen.blit(sprite.image, self.camera.apply(sprite))
            
        # Draw player with camera offset
        screen.blit(self.game.player.image, self.camera.apply(self.game.player))
        
        # Lantern Effect (Fog of War)
        dark_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
        dark_surface.fill((0, 0, 0, 230)) 
        
        player_screen_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        pygame.draw.circle(dark_surface, (0, 0, 0, 0), player_screen_pos, self.game.player.lantern.get_radius())
        
        screen.blit(dark_surface, (0, 0))
        
        # UI
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"Pos: {self.game.player.rect.topleft}", True, WHITE)
        screen.blit(text, (10, 10))
        text2 = font.render("Exploration Mode (WASD to Move, 1-9 to Select, F to Use, H for Home)", True, WHITE)
        screen.blit(text2, (10, 30))
        
        # Cooldown UI
        current_time = time.time()
        if current_time < self.game.player.teleport_cooldown_end:
            remaining = int(self.game.player.teleport_cooldown_end - current_time)
            cd_text = font.render(f"Teleport Cooldown: {remaining}s", True, RED)
            screen.blit(cd_text, (SCREEN_WIDTH - 200, 10))
        
        # Health Bar
        pygame.draw.rect(screen, RED, (10, 60, 200, 20))
        pygame.draw.rect(screen, GREEN, (10, 60, 200 * (self.game.player.health / self.game.player.max_health), 20))
        pygame.draw.rect(screen, WHITE, (10, 60, 200, 20), 2)
        
        # Inventory Toolbar
        toolbar_y = SCREEN_HEIGHT - 60
        start_x = SCREEN_WIDTH // 2 - (9 * 40) // 2
        for i in range(9):
            rect = pygame.Rect(start_x + i * 45, toolbar_y, 40, 40)
            
            # Highlight selected slot
            if i == self.game.player.selected_slot:
                pygame.draw.rect(screen, YELLOW, rect, 3)
            else:
                pygame.draw.rect(screen, GRAY, rect)
                pygame.draw.rect(screen, WHITE, rect, 2)
            
            # Draw item in slot
            slot_data = self.game.player.toolbar[i]
            if slot_data:
                item_name = slot_data['name']
                count = slot_data['count']
                
                # Draw item placeholder (colored circle)
                color = WHITE
                if "Red" in item_name: color = RED
                elif "Blue" in item_name: color = BLUE
                elif "Water" in item_name: color = BLUE
                elif "Potion" in item_name: color = YELLOW
                pygame.draw.circle(screen, color, rect.center, 15)
                
                # Draw count
                count_text = font.render(str(count), True, BLACK)
                screen.blit(count_text, (rect.right - 15, rect.bottom - 15))
            
            # Draw slot number
            num_text = font.render(str(i + 1), True, BLACK)
            screen.blit(num_text, (rect.x + 2, rect.y + 2))
