import pygame
from src.states.game_state import GameState
from src.config import *
from src.systems.crafting import CraftingSystem
from src.systems.shop import ShopSystem
from src.utils.ui import Button

class HomeState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.crafting_system = CraftingSystem()
        self.shop_system = ShopSystem()
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 48)

        self.show_recipes = False
        
        # UI Buttons
        self.btn_explore = Button(50, 100, 200, 40, "Explore (E)", self.font)
        self.btn_recipes = Button(50, 150, 200, 40, "Recipes (R)", self.font)
        self.btn_inventory = Button(50, 200, 200, 40, "Inventory (I)", self.font)
        self.btn_upgrade = Button(50, 250, 250, 40, "Upgrade Lantern (50G)", self.font)
        self.btn_sell = Button(50, 300, 250, 40, "Sell Health Potion (10G)", self.font)
        
        # Crafting UI State
        self.selected_recipe = None
        self.crafting_timer = 0
        self.crafting_duration = 0
        self.crafting_target = None
        
        self.show_inventory = False
        self.dragging_item = None # (item_name, offset_x, offset_y)
        self.dragging_source_index = -1 # -1 for inventory, 0-8 for toolbar (if we allow reordering later)
        
        self.recipe_buttons = []
        y = 115
        for recipe in self.crafting_system.recipes:
            self.recipe_buttons.append(Button(450, y, 200, 30, recipe, self.font))
            y += 35
            
        self.btn_craft = Button(450, 400, 100, 40, "Craft", self.font, color=DARK_GREEN, text_color=WHITE)

    def handle_events(self, events):
        for event in events:
            # Handle Button Clicks
            if self.btn_explore.handle_event(event):
                # Cooldown is now checked on ENTERING exploration, so we can just switch
                self.game.states["exploration"].enter()
                self.game.change_state("exploration")
            
            if self.btn_recipes.handle_event(event):
                self.show_recipes = not self.show_recipes
                self.show_inventory = False # Close inventory if recipes opened
                
            if self.btn_inventory.handle_event(event):
                self.show_inventory = not self.show_inventory
                self.show_recipes = False # Close recipes if inventory opened
                
            if self.btn_upgrade.handle_event(event):
                self.game.gold = self.shop_system.buy_upgrade(self.game.player.lantern, self.game.gold)
                
            if self.btn_sell.handle_event(event):
                self.game.gold = self.shop_system.sell_item(self.game.player.inventory, "Health Potion", self.game.gold)

            # Recipe Selection
            if self.show_recipes:
                for i, btn in enumerate(self.recipe_buttons):
                    if btn.handle_event(event):
                        self.selected_recipe = list(self.crafting_system.recipes.keys())[i]
                
                if self.selected_recipe and self.btn_craft.handle_event(event):
                    if self.crafting_timer == 0: # Start crafting if not already
                        if self.crafting_system.can_craft(self.game.player.inventory, self.selected_recipe):
                            _, duration = self.crafting_system.recipes[self.selected_recipe]
                            self.crafting_duration = duration * 60 # Convert seconds to frames
                            self.crafting_timer = self.crafting_duration
                            self.crafting_target = self.selected_recipe
                            print(f"Started crafting {self.selected_recipe}...")
                        else:
                            print("Cannot craft: Missing ingredients.")

            # Inventory Drag and Drop
            if self.show_inventory:
                window_rect = pygame.Rect(350, 100, 300, 350)
                inv_start_x = window_rect.x + 20
                inv_start_y = window_rect.y + 50
                grid_cols = 5
                slot_size = 40
                padding = 10
                
                # Toolbar positions
                toolbar_start_x = window_rect.x + 15
                toolbar_y = window_rect.bottom - 50
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        mouse_pos = event.pos
                        
                        # Check Inventory Slots
                        items = list(self.game.player.inventory.items())
                        for i in range(20): # 5x4 grid
                            col = i % grid_cols
                            row = i // grid_cols
                            x = inv_start_x + col * (slot_size + padding)
                            y = inv_start_y + row * (slot_size + padding)
                            rect = pygame.Rect(x, y, slot_size, slot_size)
                            
                            if rect.collidepoint(mouse_pos) and i < len(items):
                                item_name, _ = items[i]
                                self.dragging_item = {'name': item_name, 'source': 'inventory', 'index': i}
                                break
                        
                        # Check Toolbar Slots (if not already dragging)
                        if not self.dragging_item:
                            for i in range(9):
                                x = toolbar_start_x + i * 30
                                rect = pygame.Rect(x, toolbar_y, 25, 25)
                                if rect.collidepoint(mouse_pos):
                                    slot_data = self.game.player.toolbar[i]
                                    if slot_data:
                                        self.dragging_item = {'name': slot_data['name'], 'source': 'toolbar', 'index': i}
                                        break
                                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging_item:
                        mouse_pos = event.pos
                        handled = False
                        
                        # Check Drop on Toolbar
                        for i in range(9):
                            x = toolbar_start_x + i * 30
                            rect = pygame.Rect(x, toolbar_y, 25, 25)
                            if rect.collidepoint(mouse_pos):
                                handled = True
                                item_name = self.dragging_item['name']
                                source = self.dragging_item['source']
                                source_index = self.dragging_item['index']
                                
                                if source == 'inventory':
                                    # Inventory -> Toolbar
                                    if item_name in self.game.player.inventory:
                                        count = self.game.player.inventory[item_name]
                                        target_slot = self.game.player.toolbar[i]
                                        
                                        if target_slot is None:
                                            self.game.player.toolbar[i] = {'name': item_name, 'count': count}
                                            del self.game.player.inventory[item_name]
                                        elif target_slot['name'] == item_name:
                                            self.game.player.toolbar[i]['count'] += count
                                            del self.game.player.inventory[item_name]
                                        else:
                                            # Swap
                                            old_item = target_slot
                                            self.game.player.toolbar[i] = {'name': item_name, 'count': count}
                                            del self.game.player.inventory[item_name]
                                            if old_item['name'] in self.game.player.inventory:
                                                self.game.player.inventory[old_item['name']] += old_item['count']
                                            else:
                                                self.game.player.inventory[old_item['name']] = old_item['count']
                                elif source == 'toolbar':
                                    # Toolbar -> Toolbar
                                    if i != source_index:
                                        # Swap slots
                                        self.game.player.toolbar[source_index], self.game.player.toolbar[i] = \
                                            self.game.player.toolbar[i], self.game.player.toolbar[source_index]
                                break
                        
                        # Check Drop on Inventory (if not handled by toolbar)
                        if not handled:
                            # Simple check: if inside window rect but not toolbar, assume inventory drop
                            # Or specifically check grid area. Let's check window rect for simplicity.
                            if window_rect.collidepoint(mouse_pos):
                                if self.dragging_item['source'] == 'toolbar':
                                    # Toolbar -> Inventory
                                    source_index = self.dragging_item['index']
                                    slot_data = self.game.player.toolbar[source_index]
                                    if slot_data:
                                        item_name = slot_data['name']
                                        count = slot_data['count']
                                        
                                        # Add back to inventory
                                        if item_name in self.game.player.inventory:
                                            self.game.player.inventory[item_name] += count
                                        else:
                                            self.game.player.inventory[item_name] = count
                                            
                                        # Clear toolbar slot
                                        self.game.player.toolbar[source_index] = None
                                        print(f"Moved {item_name} back to inventory")

                        self.dragging_item = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e: # Keep shortcut for convenience
                    self.game.states["exploration"].enter()
                    self.game.change_state("exploration")
                elif event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                    self.show_recipes = False

    def update(self):
        # Crafting Logic
        if self.crafting_timer > 0:
            self.crafting_timer -= 1
            if self.crafting_timer == 0:
                self.crafting_system.craft(self.game.player.inventory, self.crafting_target)
                self.crafting_target = None

    def draw(self, screen):
        screen.fill(DARK_GREEN) # Home background
        
        # Draw UI
        title = self.title_font.render("Home Sweet Home", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - 150, 30))
        
        # Draw Buttons
        self.btn_explore.draw(screen)
        self.btn_recipes.draw(screen)
        self.btn_inventory.draw(screen)
        self.btn_upgrade.draw(screen)
        self.btn_sell.draw(screen)
        
        # Info Text
        info_y = 360
        info_lines = [
            f"Gold: {self.game.gold}",
            f"Lantern Level: {self.game.player.lantern.level} (Radius: {self.game.player.lantern.radius})"
        ]
        for line in info_lines:
            text = self.font.render(line, True, WHITE)
            screen.blit(text, (50, info_y))
            info_y += 30
            
        # Inventory Grid Window
        if self.show_inventory:
            # Draw Window Background
            window_rect = pygame.Rect(350, 100, 300, 350) # Taller for toolbar
            pygame.draw.rect(screen, GRAY, window_rect)
            pygame.draw.rect(screen, WHITE, window_rect, 2)
            
            inv_start_x = window_rect.x + 20
            inv_start_y = window_rect.y + 50
            grid_cols = 5
            grid_rows = 4
            slot_size = 40
            padding = 10
            
            inventory_label = self.font.render("Inventory", True, WHITE)
            screen.blit(inventory_label, (window_rect.centerx - inventory_label.get_width() // 2, window_rect.y + 10))
            
            # Get list of items for indexed access
            items = list(self.game.player.inventory.items())
            
            for row in range(grid_rows):
                for col in range(grid_cols):
                    index = row * grid_cols + col
                    x = inv_start_x + col * (slot_size + padding)
                    y = inv_start_y + row * (slot_size + padding)
                    rect = pygame.Rect(x, y, slot_size, slot_size)
                    
                    pygame.draw.rect(screen, DARK_GREEN, rect)
                    pygame.draw.rect(screen, WHITE, rect, 1)
                    
                    if index < len(items):
                        item_name, count = items[index]
                        # Draw item placeholder (colored circle/text)
                        color = WHITE
                        if "Red" in item_name: color = RED
                        elif "Blue" in item_name: color = BLUE
                        elif "Water" in item_name: color = BLUE
                        elif "Potion" in item_name: color = YELLOW
                        
                        pygame.draw.circle(screen, color, rect.center, 12)
                        
                        # Draw count
                        count_text = self.font.render(str(count), True, BLACK)
                        screen.blit(count_text, (rect.right - 12, rect.bottom - 12))
                        
                        # Tooltip (Simple hover check)
                        mouse_pos = pygame.mouse.get_pos()
                        if rect.collidepoint(mouse_pos) and not self.dragging_item:
                            tooltip = self.font.render(item_name, True, WHITE)
                            # Draw tooltip background
                            tooltip_rect = tooltip.get_rect(topleft=(mouse_pos[0] + 10, mouse_pos[1] - 20))
                            pygame.draw.rect(screen, BLACK, tooltip_rect)
                            screen.blit(tooltip, tooltip_rect.topleft)
                            
            # Draw Toolbar Slots in Inventory Window
            toolbar_label = self.font.render("Toolbar (Drag items here)", True, WHITE)
            screen.blit(toolbar_label, (window_rect.x + 20, window_rect.bottom - 75))
            
            toolbar_start_x = window_rect.x + 15
            toolbar_y = window_rect.bottom - 50
            
            for i in range(9):
                x = toolbar_start_x + i * 30
                rect = pygame.Rect(x, toolbar_y, 25, 25)
                pygame.draw.rect(screen, BLACK, rect)
                pygame.draw.rect(screen, WHITE, rect, 1)
                
                # Draw item in toolbar
                slot_data = self.game.player.toolbar[i]
                if slot_data:
                    item_name = slot_data['name']
                    count = slot_data['count']
                    
                    color = WHITE
                    if "Red" in item_name: color = RED
                    elif "Blue" in item_name: color = BLUE
                    elif "Water" in item_name: color = BLUE
                    elif "Potion" in item_name: color = YELLOW
                    pygame.draw.circle(screen, color, rect.center, 8)
                    
                    # Draw count (tiny)
                    # count_text = self.font.render(str(count), True, WHITE) # Might be too small/cluttered, but good for debug

                    
            # Draw Dragging Item
            if self.dragging_item:
                mouse_pos = pygame.mouse.get_pos()
                item_name = self.dragging_item['name']
                color = WHITE
                if "Red" in item_name: color = RED
                elif "Blue" in item_name: color = BLUE
                elif "Water" in item_name: color = BLUE
                elif "Potion" in item_name: color = YELLOW
                pygame.draw.circle(screen, color, mouse_pos, 12)
            
        # Cooldown UI - Only relevant in exploration, but maybe show if active?
        # User said "teleport cooldown is teleport back to home", so in Home state, cooldown doesn't matter for entering forest.
        # So we don't show it here.

        # Recipe Window / Crafting UI
        if self.show_recipes:
            # Draw Background for Crafting Area
            pygame.draw.rect(screen, GRAY, (400, 80, 300, 400))
            pygame.draw.rect(screen, WHITE, (400, 80, 300, 400), 2)
            
            header = self.font.render("Crafting Station", True, WHITE)
            screen.blit(header, (490, 90))
            
            # Draw Recipe Buttons
            for btn in self.recipe_buttons:
                btn.draw(screen)
                
            # Draw Selected Recipe Details
            if self.selected_recipe:
                details_y = 300
                ingredients, time = self.crafting_system.recipes[self.selected_recipe]
                
                name_text = self.font.render(f"Selected: {self.selected_recipe}", True, YELLOW)
                screen.blit(name_text, (420, 260))
                
                # Adjusted spacing to prevent overlap
                for item, count in ingredients.items():
                    has = self.game.player.inventory.get(item, 0)
                    color = GREEN if has >= count else RED
                    ing_text = self.font.render(f"{item}: {has}/{count}", True, color)
                    screen.blit(ing_text, (420, details_y))
                    details_y += 25
                    
                # Draw Craft Button - Moved down slightly
                self.btn_craft.rect.y = 420 
                self.btn_craft.draw(screen)
                
                # Draw Progress Bar
                if self.crafting_timer > 0 and self.crafting_target == self.selected_recipe:
                    progress = 1 - (self.crafting_timer / self.crafting_duration)
                    pygame.draw.rect(screen, BLACK, (450, 465, 200, 20))
                    pygame.draw.rect(screen, BLUE, (450, 465, 200 * progress, 20))
                    pygame.draw.rect(screen, WHITE, (450, 465, 200, 20), 2)
