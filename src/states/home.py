import pygame
from src.states.game_state import GameState
from src.config import *
from src.systems.crafting import CraftingSystem
from src.systems.shop import ShopSystem

class HomeState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.crafting_system = CraftingSystem()
        self.shop_system = ShopSystem()
        self.font = pygame.font.SysFont(None, 24)

        self.show_recipes = False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.game.change_state("exploration")
                elif event.key == pygame.K_c:
                    self.crafting_system.craft(self.game.player.inventory, "Health Potion")
                elif event.key == pygame.K_u:
                    self.game.gold = self.shop_system.buy_upgrade(self.game.player.lantern, self.game.gold)
                elif event.key == pygame.K_r:
                    self.show_recipes = not self.show_recipes
                elif event.key == pygame.K_s:
                    self.game.gold = self.shop_system.sell_item(self.game.player.inventory, "Health Potion", self.game.gold)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(DARK_GREEN) # Home background
        
        # Draw UI
        title = self.font.render("Home Sweet Home", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - 50, 50))
        
        instructions = [
            "Press E to Explore",
            "Press R to Toggle Recipe Window",
            "Press C to Craft Health Potion (Shortcut)",
            "Press U to Upgrade Lantern (Cost: 50 Gold)",
            "Press S to Sell Health Potion (Value: 10 Gold)",
            f"Gold: {self.game.gold}",
            f"Inventory: {self.game.player.inventory}",
            f"Lantern Level: {self.game.player.lantern.level} (Radius: {self.game.player.lantern.radius})"
        ]
        
        y = 100
        for line in instructions:
            text = self.font.render(line, True, WHITE)
            screen.blit(text, (50, y))
            y += 30

        # Recipe Window Overlay
        if self.show_recipes:
            overlay = pygame.Surface((400, 300))
            overlay.fill(GRAY)
            overlay_rect = overlay.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(overlay, overlay_rect)
            
            pygame.draw.rect(screen, WHITE, overlay_rect, 2) # Border
            
            header = self.font.render("Recipes", True, WHITE)
            screen.blit(header, (overlay_rect.centerx - header.get_width() // 2, overlay_rect.top + 10))
            
            ry = overlay_rect.top + 50
            for potion, ingredients in self.crafting_system.recipes.items():
                ing_text = ", ".join([f"{k}: {v}" for k, v in ingredients.items()])
                recipe_text = self.font.render(f"{potion}: {ing_text}", True, WHITE)
                screen.blit(recipe_text, (overlay_rect.left + 20, ry))
                ry += 30
