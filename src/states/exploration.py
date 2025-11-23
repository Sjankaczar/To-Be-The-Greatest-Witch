import pygame
import random
from src.states.game_state import GameState
from src.entities.forest_creature import ForestCreature
from src.entities.item import Item
from src.config import *
from src.utils.camera import Camera

class ExplorationState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        
        # Map management
        self.generated_chunks = set()
        self.chunk_size = 1000 # Size of area to spawn things in
        
        # Initial spawn
        self.check_chunks()

    def get_chunk(self, x, y):
        return (int(x // self.chunk_size), int(y // self.chunk_size))

    def check_chunks(self):
        # Determine current chunk based on player position
        current_chunk = self.get_chunk(self.game.player.rect.centerx, self.game.player.rect.centery)
        
        # Check surrounding chunks
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                chunk = (current_chunk[0] + dx, current_chunk[1] + dy)
                if chunk not in self.generated_chunks:
                    self.generate_chunk(chunk)
                    self.generated_chunks.add(chunk)

    def generate_chunk(self, chunk):
        # Spawn enemies and items in this chunk
        chunk_x = chunk[0] * self.chunk_size
        chunk_y = chunk[1] * self.chunk_size
        
        # Spawn enemies
        for _ in range(random.randint(2, 5)):
            x = random.randint(chunk_x, chunk_x + self.chunk_size)
            y = random.randint(chunk_y, chunk_y + self.chunk_size)
            enemy = ForestCreature(x, y)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            
        # Spawn items
        for _ in range(random.randint(5, 10)):
            x = random.randint(chunk_x, chunk_x + self.chunk_size)
            y = random.randint(chunk_y, chunk_y + self.chunk_size)
            # Randomize item type
            item_type = random.choice(["Red Herb", "Blue Herb", "Water"])
            color = GREEN if "Herb" in item_type else BLUE
            item = Item(x, y, item_type, color)
            self.items.add(item)
            self.all_sprites.add(item)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.game.change_state("home")
                elif event.key == pygame.K_f:
                    # Use selected item (for now hardcoded to Health Potion if available)
                    self.game.player.use_item("Health Potion")
                # Number keys 1-9 for toolbar selection (placeholder logic)
                elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                    print(f"Selected slot {event.key - pygame.K_0}")

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
        text2 = font.render("Exploration Mode (WASD to Move, F to Use Potion, H for Home)", True, WHITE)
        screen.blit(text2, (10, 30))
        
        # Health Bar
        pygame.draw.rect(screen, RED, (10, 60, 200, 20))
        pygame.draw.rect(screen, GREEN, (10, 60, 200 * (self.game.player.health / self.game.player.max_health), 20))
        pygame.draw.rect(screen, WHITE, (10, 60, 200, 20), 2)
        
        # Inventory Toolbar
        toolbar_y = SCREEN_HEIGHT - 60
        start_x = SCREEN_WIDTH // 2 - (9 * 40) // 2
        for i in range(9):
            rect = pygame.Rect(start_x + i * 45, toolbar_y, 40, 40)
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
            
            # Draw item count if available (Placeholder logic)
            # For now, just show Health Potion in slot 1 if available
            if i == 0 and "Health Potion" in self.game.player.inventory:
                count = self.game.player.inventory["Health Potion"]
                item_text = font.render(f"HP:{count}", True, WHITE)
                screen.blit(item_text, (rect.x + 2, rect.y + 10))
            
            # Draw slot number
            num_text = font.render(str(i + 1), True, BLACK)
            screen.blit(num_text, (rect.x + 2, rect.y + 2))
