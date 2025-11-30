import pygame
import time
from src.states.game_state import GameState
from src.config import *
from src.systems.crafting import CraftingSystem
from src.systems.shop import ShopSystem
from src.systems.research import ResearchSystem
from src.systems.farming import FarmingSystem
from src.utils.ui import Button
from src.utils.ui import Button
from src.utils.camera import Camera
from src.entities.golem import Golem

class HomeState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.crafting_system = CraftingSystem()
        self.shop_system = ShopSystem()
        self.research_system = ResearchSystem()
        self.farming_system = FarmingSystem()
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 48)



        # Home Area State
        self.base_map_width = 1600
        self.base_map_height = 1200
        self.map_width = self.base_map_width
        self.map_height = self.base_map_height
        self.extra_tiles = [] # List of (x, y) tuples for expanded safe zone
        self.extra_tiles = [] # List of (x, y) tuples for expanded safe zone
        self.camera = Camera(self.map_width, self.map_height)
        
        # Golems
        self.golems = pygame.sprite.Group()
        self.expansion_queue = [] # List of (grid_x, grid_y)
        self.command_mode = False
        
        # Initialize Player Position in Home
        self.game.player.rect.topleft = (self.map_width // 2, self.map_height // 2)
        
        # Buildings (Positions relative to map)
        self.portal_rect = pygame.Rect(self.map_width // 2 - 50, 100, 100, 60)
        self.crafting_rect = pygame.Rect(300, self.map_height // 2 - 50, 80, 100)
        self.shop_rect = pygame.Rect(self.map_width - 380, self.map_height // 2 - 50, 80, 100)
        self.research_rect = pygame.Rect(self.map_width // 2 - 50, self.map_height - 200, 100, 80)
        
        self.show_recipes = False
        self.show_inventory = False
        self.show_research = False
        self.show_shop = False 
        
        # UI Buttons
        self.btn_recipes = Button(50, 150, 200, 40, "Recipes (R)", self.font) 
        self.btn_inventory = Button(50, 200, 200, 40, "Inventory (E)", self.font) 
        self.btn_upgrade = Button(50, 250, 250, 40, "Upgrade Lantern (50G)", self.font)
        self.btn_sell = Button(50, 300, 250, 40, "Sell Health Potion (10G)", self.font)
        
        # Close Buttons
        self.btn_close_crafting = Button(0, 0, 30, 30, "X", self.font, color=RED, text_color=WHITE)
        self.btn_close_research = Button(0, 0, 30, 30, "X", self.font, color=RED, text_color=WHITE)
        
        # Crafting UI State
        self.selected_recipe = None
        self.crafting_timer = 0
        self.crafting_duration = 0
        self.crafting_target = None
        
        self.dragging_item = None 
        self.dragging_source_index = -1
        
        self.crafting_tab = "Potions"
        self.btn_tab_potions = Button(0, 0, 80, 30, "Potions", self.font, color=BLUE, text_color=WHITE)
        self.btn_tab_seeds = Button(0, 0, 80, 30, "Seeds", self.font, color=BLUE, text_color=WHITE)
        self.btn_tab_golems = Button(0, 0, 80, 30, "Golems", self.font, color=BLUE, text_color=WHITE)
        
        self.recipe_buttons = []
        self.update_recipe_list()
            
        self.btn_craft = Button(450, 400, 100, 40, "Craft", self.font, color=DARK_GREEN, text_color=WHITE)

    def update_recipe_list(self):
        self.recipe_buttons = []
        y = 115
        
        recipes = self.crafting_system.get_all_recipes(self.crafting_tab)
        for recipe in recipes:
            self.recipe_buttons.append(Button(450, y, 200, 30, recipe, self.font))
            y += 35
        
        # Research UI State
        self.research_buttons = []
        y = 115
        for topic in self.research_system.topics:
            self.research_buttons.append(Button(450, y, 200, 30, topic, self.font))
            y += 35
        self.selected_research = None
        self.btn_start_research = Button(450, 400, 150, 40, "Start Research", self.font, color=BLUE, text_color=WHITE)

        # Shop UI State
        self.shop_tab = "buy" # "buy" or "sell"
        self.btn_shop_buy_tab = Button(0, 0, 100, 30, "Buy", self.font)
        self.btn_shop_sell_tab = Button(0, 0, 100, 30, "Sell", self.font)
        self.btn_close_shop = Button(0, 0, 30, 30, "X", self.font, color=RED, text_color=WHITE)
        
        self.shop_items_buy = self.shop_system.get_all_items()
        self.shop_buy_buttons = []
        for item in self.shop_items_buy:
            self.shop_buy_buttons.append(Button(0, 0, 200, 30, f"{item} ({PRICES.get(item, 0)}G)", self.font))
            
        self.shop_sell_buttons = [] # Dynamic based on inventory
        self.selected_shop_item = None
        self.btn_shop_action = Button(0, 0, 100, 40, "Buy", self.font, color=YELLOW, text_color=BLACK)
        self.shop_scroll_y = 0

    def enter(self):
        print("Entering Home State")

    def handle_events(self, events):
        for event in events:
            # Handle UI Button Clicks
            
            # Key Handling
            if event.type == pygame.KEYDOWN:
                # Toolbar Selection (1-9)
                if pygame.K_1 <= event.key <= pygame.K_9:
                    self.game.player.selected_slot = event.key - pygame.K_1
                    print(f"Selected slot {self.game.player.selected_slot + 1}")
                
                # Use Item / Harvest (F)
                if event.key == pygame.K_f:
                    # Harvesting Logic
                    mouse_pos = pygame.mouse.get_pos()
                    world_x = mouse_pos[0] - self.camera.camera.x
                    world_y = mouse_pos[1] - self.camera.camera.y
                    
                    # Try to harvest at mouse position first (if mouse is over a tile)
                    if self.farming_system.harvest_crop(world_x, world_y, self.game.player.inventory):
                        pass # Harvested successfully
                    else:
                        # Fallback: Try to harvest in front of player or at player position
                        player_center = self.game.player.rect.center
                        if self.farming_system.harvest_crop(player_center[0], player_center[1], self.game.player.inventory):
                            pass
                        else:
                            # Use Item (Fallback if not harvesting)
                            self.game.player.use_item()
                            
                # Toggle Command Mode (G)
                if event.key == pygame.K_g:
                    self.command_mode = not self.command_mode
                    print(f"Command Mode: {'ON' if self.command_mode else 'OFF'}")

            # Crafting UI Events
            if self.show_recipes:
                # Close button for crafting
                if self.btn_close_crafting.handle_event(event):
                    self.show_recipes = False
                
                # Tab Selection
                if self.btn_tab_potions.handle_event(event):
                    self.crafting_tab = "Potions"
                    self.selected_recipe = None
                    self.update_recipe_list()
                if self.btn_tab_seeds.handle_event(event):
                    self.crafting_tab = "Seeds"
                    self.selected_recipe = None
                    self.update_recipe_list()
                if self.btn_tab_golems.handle_event(event):
                    self.crafting_tab = "Golems"
                    self.selected_recipe = None
                    self.update_recipe_list()
                
                # Scroll Handling
                if event.type == pygame.MOUSEWHEEL:
                    if hasattr(self, 'crafting_ui_screen_rect') and self.crafting_ui_screen_rect.collidepoint(pygame.mouse.get_pos()):
                        if not hasattr(self, 'crafting_scroll_y'):
                            self.crafting_scroll_y = 0
                        self.crafting_scroll_y -= event.y * 20 # Scroll speed
                        
                        # Clamp Scroll
                        list_height = 175
                        total_height = len(self.recipe_buttons) * 35
                        max_scroll = max(0, total_height - list_height)
                        self.crafting_scroll_y = max(0, min(self.crafting_scroll_y, max_scroll))
                
                # Recipe Selection
                # Check if click is within list area
                if hasattr(self, 'crafting_ui_screen_rect'):
                    rect = self.crafting_ui_screen_rect
                    # Match the list_rect from draw()
                    list_height = 175
                    list_rect = pygame.Rect(rect.x + 20, rect.y + 80, rect.width - 40, list_height)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if list_rect.collidepoint(event.pos):
                            if not hasattr(self, 'crafting_scroll_y'):
                                self.crafting_scroll_y = 0
                                
                            mouse_x, mouse_y = event.pos
                            relative_y = mouse_y - list_rect.y + self.crafting_scroll_y
                            
                            index = relative_y // 35
                            if 0 <= index < len(self.recipe_buttons):
                                self.selected_recipe = self.recipe_buttons[index].text
                                print(f"Selected recipe: {self.selected_recipe}")

                if self.selected_recipe and self.btn_craft.handle_event(event):
                    if self.crafting_timer == 0: # Start crafting if not already
                        if self.crafting_system.can_craft(self.game.player, self.crafting_tab, self.selected_recipe):
                            _, duration = self.crafting_system.get_recipe(self.crafting_tab, self.selected_recipe)
                            self.crafting_duration = duration * 60 # Convert seconds to frames
                            self.crafting_timer = self.crafting_duration
                            self.crafting_target = self.selected_recipe
                            self.crafting_target_category = self.crafting_tab
                            print(f"Started crafting {self.selected_recipe}...")
                        else:
                            print("Cannot craft: Missing ingredients or Gold.")

            # Research UI Events
            if self.show_research:
                # Close button for research
                if self.btn_close_research.handle_event(event):
                    self.show_research = False

                # Research Topic Selection
                for i, btn in enumerate(self.research_buttons):
                    if btn.handle_event(event):
                        self.selected_research = list(self.research_system.topics.keys())[i]
                
                # Start Research Button
                if self.selected_research and self.btn_start_research.handle_event(event):
                    if not self.research_system.current_research: # Only start if not already researching
                        if self.research_system.can_research(self.selected_research, self.game.player.intelligence):
                            self.research_system.start_research(self.selected_research)
                            print(f"Started research on {self.selected_research}...")
                        else:
                            print("Cannot research: Not enough intelligence or already researched.")

            # Inventory Button (Always Active)
            if self.btn_inventory.handle_event(event):
                self.show_inventory = not self.show_inventory
                self.show_recipes = False

            if self.show_inventory:
                # Center the window (Must match draw logic)
                window_width = 300
                window_height = 350
                window_x = (SCREEN_WIDTH - window_width) // 2
                window_y = (SCREEN_HEIGHT - window_height) // 2
                window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
                
                inv_start_x = window_rect.x + 20
                inv_start_y = window_rect.y + 50
                grid_cols = 5
                slot_size = 40
                padding = 10
                
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
                        
                        # Check Toolbar Slots (Persistent)
                        if not self.dragging_item:
                            toolbar_start_x = (SCREEN_WIDTH - (9 * 40)) // 2
                            toolbar_y = SCREEN_HEIGHT - 50
                            
                            for i in range(9):
                                x = toolbar_start_x + i * 40
                                rect = pygame.Rect(x, toolbar_y, 32, 32)
                                
                                if rect.collidepoint(mouse_pos):
                                    slot_data = self.game.player.toolbar[i]
                                    if slot_data:
                                        self.dragging_item = {'name': slot_data['name'], 'source': 'toolbar', 'index': i}
                                    break
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging_item:
                        mouse_pos = event.pos
                        handled = False
                        
                        # Check Drop on Toolbar (Persistent at bottom)
                        toolbar_start_x = (SCREEN_WIDTH - (9 * 40)) // 2
                        toolbar_y = SCREEN_HEIGHT - 50
                        
                        for i in range(9):
                            x = toolbar_start_x + i * 40
                            rect = pygame.Rect(x, toolbar_y, 32, 32)
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
                                break
                        
                        # Check Drop on Inventory (if not handled by toolbar)
                        if not handled:
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

            # Persistent Toolbar Interaction (Selection)
            if event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_9:
                    self.game.player.selected_slot = event.key - pygame.K_1
                    
                if event.key == pygame.K_e: # Toggle Inventory
                    self.show_inventory = not self.show_inventory
                    self.show_recipes = False
                elif event.key == pygame.K_i: # Alternate key
                    self.show_inventory = not self.show_inventory
                    self.show_recipes = False

            # Interaction (F) - Always checked
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                # Check collisions using game.player.rect
                player_rect = self.game.player.rect
                if player_rect.colliderect(self.portal_rect):
                    self.game.states["exploration"].enter()
                    self.game.change_state("exploration")
                elif player_rect.colliderect(self.crafting_rect):
                    self.show_recipes = True
                    print("Opened Crafting Station")
                elif player_rect.colliderect(self.shop_rect):
                    self.show_shop = True
                    self.show_inventory = True # Open inventory too for convenience
                    print("Opened Shop")
                elif player_rect.colliderect(self.research_rect):
                    if self.game.player.rank >= 4:
                        self.show_research = True
                        print("Opened Research Center")
                    else:
                        print("Research Center unlocks at Rank 4!")
                    
            # Shop UI Events
            if self.show_shop:
                if self.btn_close_shop.handle_event(event):
                    self.show_shop = False
                    
                if self.btn_shop_buy_tab.handle_event(event):
                    self.shop_tab = "buy"
                    self.selected_shop_item = None
                    self.btn_shop_action.text = "Buy"
                    self.shop_scroll_y = 0 # Reset scroll
                    # Refresh buy list (Show all)
                    self.shop_items_buy = self.shop_system.get_all_items()
                    self.shop_buy_buttons = []
                    for item in self.shop_items_buy:
                        self.shop_buy_buttons.append(Button(0, 0, 200, 30, f"{item} ({PRICES.get(item, 0)}G)", self.font))
                    
                if self.btn_shop_sell_tab.handle_event(event):
                    self.shop_tab = "sell"
                    self.selected_shop_item = None
                    self.btn_shop_action.text = "Sell"
                    self.shop_scroll_y = 0 # Reset scroll
                    # Refresh sell buttons
                    self.shop_sell_buttons = []
                    y_offset = 0
                    for item, count in self.game.player.inventory.items():
                        price = PRICES.get(item, 0) // 2
                        self.shop_sell_buttons.append(Button(0, 0, 200, 30, f"{item} x{count} ({price}G)", self.font))
                
                # Scroll Handling
                if event.type == pygame.MOUSEWHEEL:
                    if hasattr(self, 'shop_ui_screen_rect') and self.shop_ui_screen_rect.collidepoint(pygame.mouse.get_pos()):
                        self.shop_scroll_y -= event.y * 20 # Scroll speed
                        
                        # Clamp Scroll
                        list_height = 250
                        item_height = 35
                        num_items = 0
                        if self.shop_tab == "buy":
                            num_items = len(self.shop_buy_buttons)
                        elif self.shop_tab == "sell":
                            num_items = len(self.shop_sell_buttons)
                            
                        total_content_height = num_items * item_height
                        max_scroll = max(0, total_content_height - list_height)
                        
                        if self.shop_scroll_y < 0:
                            self.shop_scroll_y = 0
                        elif self.shop_scroll_y > max_scroll:
                            self.shop_scroll_y = max_scroll
                        
                # Handle Item Selection (with scroll)
                if hasattr(self, 'shop_ui_screen_rect'):
                    rect = self.shop_ui_screen_rect
                    list_rect = pygame.Rect(rect.x + 20, rect.y + 80, rect.width - 40, 250)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if list_rect.collidepoint(event.pos):
                            mouse_x, mouse_y = event.pos
                            relative_y = mouse_y - list_rect.y + self.shop_scroll_y
                            
                            index = relative_y // 35
                            
                            if self.shop_tab == "buy":
                                if 0 <= index < len(self.shop_buy_buttons):
                                    self.selected_shop_item = self.shop_items_buy[index]
                            elif self.shop_tab == "sell":
                                current_inv_items = list(self.game.player.inventory.keys())
                                if 0 <= index < len(current_inv_items):
                                    self.selected_shop_item = current_inv_items[index]
                            
                # Handle Action (Buy/Sell)
                if self.selected_shop_item and self.btn_shop_action.handle_event(event):
                    if self.shop_tab == "buy":
                        # Check Rank
                        req_rank = self.shop_system.get_required_rank(self.selected_shop_item)
                        if self.game.player.rank >= req_rank:
                            price = PRICES.get(self.selected_shop_item, 0)
                            if self.game.player.gold >= price:
                                self.game.player.gold -= price
                                self.game.player.add_item(self.selected_shop_item)
                                print(f"Bought {self.selected_shop_item} for {price}G")
                            else:
                                print("Not enough gold!")
                        else:
                            print(f"Item locked! Unlocks at Rank {req_rank}")
                    elif self.shop_tab == "sell":
                        if self.selected_shop_item in self.game.player.inventory:
                            price = PRICES.get(self.selected_shop_item, 0) // 2
                            self.game.player.gold += price
                            self.game.player.inventory[self.selected_shop_item] -= 1
                            if self.game.player.inventory[self.selected_shop_item] <= 0:
                                del self.game.player.inventory[self.selected_shop_item]
                                self.selected_shop_item = None # Deselect if run out
                            print(f"Sold {self.selected_shop_item} for {price}G")
                            
                            # Refresh sell buttons immediately
                            self.shop_sell_buttons = []

            # Tool Usage (Mouse Click)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_mouse_on_ui(event.pos):
                    # If on UI, do not use tools.
                    pass
                elif self.command_mode:
                    # Command Mode Logic (Queue Expansion)
                    mouse_x, mouse_y = event.pos
                    world_x = mouse_x - self.camera.camera.x
                    world_y = mouse_y - self.camera.camera.y
                    
                    tile_x = (world_x // TILE_SIZE)
                    tile_y = (world_y // TILE_SIZE)
                    
                    # Check if valid expansion target (not in base, not in extra, adjacent to existing?)
                    # For simplicity, just check if not already safe
                    in_base_rect = (0 <= tile_x * TILE_SIZE < self.base_map_width) and (0 <= tile_y * TILE_SIZE < self.base_map_height)
                    is_extra = (tile_x * TILE_SIZE, tile_y * TILE_SIZE) in self.extra_tiles
                    
                    if not in_base_rect and not is_extra:
                        if (tile_x, tile_y) not in self.expansion_queue:
                            self.expansion_queue.append((tile_x, tile_y))
                            print(f"Queued expansion at ({tile_x}, {tile_y})")
                        else:
                            print("Already queued.")
                    else:
                        print("Tile is already safe.")
                        
                else:
                    # Convert mouse pos to world pos
                    mouse_x, mouse_y = event.pos
                    world_x = mouse_x - self.camera.camera.x
                    world_y = mouse_y - self.camera.camera.y

                    # Get selected tool
                    selected_slot_index = self.game.player.selected_slot
                    selected_item = self.game.player.toolbar[selected_slot_index]
                    
                    if selected_item:
                        item_name = selected_item['name']
                        
                        # Axe Logic (Can be used outside map)
                        if item_name == "Axe":
                            # Snap to grid
                            tile_x = (world_x // TILE_SIZE) * TILE_SIZE
                            tile_y = (world_y // TILE_SIZE) * TILE_SIZE
                        
                            # Check if tile is already safe
                            in_base_rect = (0 <= tile_x < self.base_map_width) and (0 <= tile_y < self.base_map_height)
                            is_extra = (tile_x, tile_y) in self.extra_tiles
                            
                            if not in_base_rect and not is_extra:
                                # Check durability
                                if selected_item.get('durability', AXE_DURABILITY) > 0:
                                    # Add new safe tile
                                    self.extra_tiles.append((tile_x, tile_y))
                                    
                                    # Update map bounds if necessary (to allow camera/player to reach it)
                                    self.map_width = max(self.map_width, tile_x + TILE_SIZE)
                                    self.map_height = max(self.map_height, tile_y + TILE_SIZE)
                                    self.camera.update_bounds(self.map_width, self.map_height)
                                
                                    # Decrease durability
                                    selected_item['durability'] = selected_item.get('durability', AXE_DURABILITY) - 1
                                    print(f"Expanded Safe Zone at ({tile_x}, {tile_y})! Axe durability: {selected_item['durability']}")
                                    
                                    if selected_item['durability'] <= 0:
                                        self.game.player.toolbar[selected_slot_index] = None
                                        print("Axe broke!")
                            else:
                                print("Tile is already safe!")

                        # Other Tools (Must be inside map)
                        elif 0 <= world_x < self.map_width and 0 <= world_y < self.map_height:
                            if item_name == "Hoe":
                                if self.farming_system.till_soil(world_x, world_y):
                                    print("Tilled soil!")
                            elif item_name == "Watering Can":
                                if self.farming_system.water_crop(world_x, world_y):
                                    print("berhasil menyiram tanaman")
                            elif item_name in ["Red Herb", "Blue Herb", "Rare Herb", "Red Seed", "Blue Seed", "Rare Seed"]:
                                # Check research requirement
                                can_plant = False
                                if item_name in ["Red Herb", "Blue Herb", "Red Seed", "Blue Seed"] and "Herbology" in self.research_system.completed_research:
                                    can_plant = True
                                elif item_name in ["Rare Herb", "Rare Seed"] and "Rare Herbs" in self.research_system.completed_research:
                                    can_plant = True
                                    
                                if can_plant:
                                    if self.farming_system.plant_crop(world_x, world_y, item_name): 
                                        selected_item['count'] -= 1
                                        if selected_item['count'] <= 0:
                                            self.game.player.toolbar[selected_slot_index] = None
                                        
                                        key = self.farming_system.get_tile_key(world_x, world_y)
                                        if key in self.farming_system.grid and self.farming_system.grid[key]['type'] == 'farmland' and self.farming_system.grid[key]['crop'] is None:
                                            self.farming_system.grid[key]['crop'] = item_name
                                            self.farming_system.grid[key]['growth'] = 0
                                            print(f"Planted {item_name}!")
                                else:
                                    print("Cannot plant: Research required.")
                            
                            elif item_name == "Wood Golem":
                                # Spawn Golem
                                golem = Golem(world_x, world_y, self)
                                self.golems.add(golem)
                                selected_item['count'] -= 1
                                if selected_item['count'] <= 0:
                                    self.game.player.toolbar[selected_slot_index] = None
                                print("Spawned Wood Golem!")

    def update(self):
        # Crafting Logic
        if self.crafting_timer > 0:
            self.crafting_timer -= 1
            if self.crafting_timer == 0:
                category = getattr(self, 'crafting_target_category', 'Potions')
                self.crafting_system.craft(self.game.player, category, self.crafting_target)
                self.crafting_target = None
                
        # Research Logic
        # Fairies only spawn if Rank >= 4
        fairies_spawn = self.game.player.rank >= 4
        self.research_system.update(self.game.player.intelligence, self.game.player.fairies_caught, spawn_fairies=fairies_spawn)
        
        # Farming Logic
        self.farming_system.update()
        
        # Golem Logic
        self.golems.update()
        
        # Update Player (Movement & Animation)
        prev_rect = self.game.player.rect.copy()
        self.game.player.update()
        
        # Validate Position
        player_center = self.game.player.rect.center
        in_base = (0 <= player_center[0] < self.base_map_width) and (0 <= player_center[1] < self.base_map_height)
        
        in_extra = False
        # Optimization: Check only if not in base
        if not in_base:
            # Simple check: is center inside any extra tile rect?
            # Since tiles are grid aligned, we can just check grid coords
            grid_x = (player_center[0] // TILE_SIZE) * TILE_SIZE
            grid_y = (player_center[1] // TILE_SIZE) * TILE_SIZE
            if (grid_x, grid_y) in self.extra_tiles:
                in_extra = True
                
        if not in_base and not in_extra:
            # Invalid move, revert
            self.game.player.rect = prev_rect
        
        # Update Camera
        self.camera.update(self.game.player)
        
        # Constrain Player to Map (Legacy constraint, might not be needed if validation works, but keeps player from flying off to infinity if bugged)
        # self.game.player.rect.x = max(0, min(self.game.player.rect.x, self.map_width - 32))
        # self.game.player.rect.y = max(0, min(self.game.player.rect.y, self.map_height - 32))
        
        # --- UPDATE UI POSITIONS (World Space -> Screen Space) ---
        
        # Research UI
        if self.show_research:
            # Window Position (World Space: Above Research Building)
            world_rect = pygame.Rect(self.research_rect.centerx - 150, self.research_rect.top - 420, 300, 400)
            screen_rect = self.camera.apply_rect(world_rect)
            self.research_ui_screen_rect = screen_rect # Store for drawing
            
            # Update Buttons
            # Topics
            for i, btn in enumerate(self.research_buttons):
                # Relative to window: x=50, y=35 + i*35
                btn.rect.x = screen_rect.x + 50
                btn.rect.y = screen_rect.y + 35 + i * 35
                
            # Start Button
            self.btn_start_research.rect.x = screen_rect.x + 50
            self.btn_start_research.rect.y = screen_rect.bottom - 60
            
            # Close Button
            self.btn_close_research.rect.topright = (screen_rect.right - 10, screen_rect.top + 10)

        # Crafting UI
        if self.show_recipes:
            # Window Position (World Space: Right of Crafting Building)
            world_rect = pygame.Rect(self.crafting_rect.right + 20, self.crafting_rect.centery - 200, 300, 400)
            screen_rect = self.camera.apply_rect(world_rect)
            self.crafting_ui_screen_rect = screen_rect
            
            # Update Buttons
            # Tabs
            self.btn_tab_potions.rect.topleft = (screen_rect.x + 20, screen_rect.y + 40)
            self.btn_tab_seeds.rect.topleft = (screen_rect.x + 110, screen_rect.y + 40)
            self.btn_tab_golems.rect.topleft = (screen_rect.x + 200, screen_rect.y + 40)

            # Recipes
            # Adjust start y for recipes to account for tabs
            start_y = screen_rect.y + 80
            for i, btn in enumerate(self.recipe_buttons):
                btn.rect.x = screen_rect.x + 50
                btn.rect.y = start_y + i * 35
                
            # Craft Button
            self.btn_craft.rect.x = screen_rect.x + 50
            self.btn_craft.rect.y = screen_rect.bottom - 60
            
            # Close Button
            self.btn_close_crafting.rect.topright = (screen_rect.right - 10, screen_rect.top + 10)

        # Shop UI
        if self.show_shop:
            # Window Position (World Space: Above Shop Building)
            world_rect = pygame.Rect(self.shop_rect.centerx - 150, self.shop_rect.top - 420, 300, 400)
            screen_rect = self.camera.apply_rect(world_rect)
            self.shop_ui_screen_rect = screen_rect
            
            # Update Buttons
            # Tabs
            self.btn_shop_buy_tab.rect.topleft = (screen_rect.x + 20, screen_rect.y + 40)
            self.btn_shop_sell_tab.rect.topleft = (screen_rect.x + 130, screen_rect.y + 40)
            
            # List Items
            start_y = screen_rect.y + 80
            if self.shop_tab == "buy":
                for i, btn in enumerate(self.shop_buy_buttons):
                    btn.rect.x = screen_rect.x + 50
                    btn.rect.y = start_y + i * 35
            elif self.shop_tab == "sell":
                for i, btn in enumerate(self.shop_sell_buttons):
                    btn.rect.x = screen_rect.x + 50
                    btn.rect.y = start_y + i * 35
                    
            # Action Button
            self.btn_shop_action.rect.x = screen_rect.x + 100
            self.btn_shop_action.rect.y = screen_rect.bottom - 60
            
            # Close Button
            self.btn_close_shop.rect.topright = (screen_rect.right - 10, screen_rect.top + 10)

    def is_mouse_on_ui(self, pos):
        # Check all active UI rects
        if self.show_inventory:
            # Recalculate rect to be safe or store it in self
            window_width = 300
            window_height = 350
            window_x = (SCREEN_WIDTH - window_width) // 2
            window_y = (SCREEN_HEIGHT - window_height) // 2
            if pygame.Rect(window_x, window_y, window_width, window_height).collidepoint(pos):
                return True
                
        if self.show_recipes and hasattr(self, 'crafting_ui_screen_rect'):
            if self.crafting_ui_screen_rect.collidepoint(pos):
                return True
                
        if self.show_research and hasattr(self, 'research_ui_screen_rect'):
            if self.research_ui_screen_rect.collidepoint(pos):
                return True
                
        if self.show_shop and hasattr(self, 'shop_ui_screen_rect'):
            if self.shop_ui_screen_rect.collidepoint(pos):
                return True
                
        # Check persistent buttons
        if self.btn_inventory.rect.collidepoint(pos):
            return True
            
        # Check Toolbar
        toolbar_start_x = (SCREEN_WIDTH - (9 * 40)) // 2
        toolbar_y = SCREEN_HEIGHT - 50
        toolbar_rect = pygame.Rect(toolbar_start_x, toolbar_y, 9 * 40, 40)
        if toolbar_rect.collidepoint(pos):
            return True
            
        return False

    def draw(self, screen):
        screen.fill(DARK_GREEN) # Forest background (outside map)
        
        # Draw Home Area (Light Green)
        # Draw Home Area (Light Green)
        home_rect = pygame.Rect(0, 0, self.base_map_width, self.base_map_height)
        pygame.draw.rect(screen, LIGHT_GREEN, self.camera.apply_rect(home_rect))
        
        # Draw Extra Safe Tiles
        for tile_pos in self.extra_tiles:
            tile_rect = pygame.Rect(tile_pos[0], tile_pos[1], TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, LIGHT_GREEN, self.camera.apply_rect(tile_rect))
            
        # Draw Axe Targeting Highlight
        selected_slot = self.game.player.selected_slot
        selected_item = self.game.player.toolbar[selected_slot]
        if selected_item and selected_item['name'] == "Axe":
            mouse_pos = pygame.mouse.get_pos()
            world_x = mouse_pos[0] - self.camera.camera.x
            world_y = mouse_pos[1] - self.camera.camera.y
            
            tile_x = (world_x // TILE_SIZE) * TILE_SIZE
            tile_y = (world_y // TILE_SIZE) * TILE_SIZE
            
            in_base_rect = (0 <= tile_x < self.base_map_width) and (0 <= tile_y < self.base_map_height)
            is_extra = (tile_x, tile_y) in self.extra_tiles
            
            highlight_color = (255, 0, 0, 128) # Red (Invalid)
            if not in_base_rect and not is_extra:
                highlight_color = (0, 255, 0, 128) # Green (Valid)
                
            highlight_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            highlight_surf.fill(highlight_color)
            screen.blit(highlight_surf, self.camera.apply_rect(pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)))
            
        # Draw Command Mode Highlight
        if self.command_mode:
            mouse_pos = pygame.mouse.get_pos()
            world_x = mouse_pos[0] - self.camera.camera.x
            world_y = mouse_pos[1] - self.camera.camera.y
            
            tile_x = (world_x // TILE_SIZE) * TILE_SIZE
            tile_y = (world_y // TILE_SIZE) * TILE_SIZE
            
            in_base_rect = (0 <= tile_x < self.base_map_width) and (0 <= tile_y < self.base_map_height)
            is_extra = (tile_x, tile_y) in self.extra_tiles
            
            highlight_color = (255, 0, 0, 128) # Red (Invalid)
            if not in_base_rect and not is_extra:
                highlight_color = (0, 255, 0, 128) # Green (Valid)
                
            highlight_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            highlight_surf.fill(highlight_color)
            screen.blit(highlight_surf, self.camera.apply_rect(pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)))
        
        # Draw Farming Grid (Farmland and Crops)
        for key, tile in self.farming_system.grid.items():
            grid_x, grid_y = key
            world_x = grid_x * self.farming_system.tile_size
            world_y = grid_y * self.farming_system.tile_size
            rect = pygame.Rect(world_x, world_y, self.farming_system.tile_size, self.farming_system.tile_size)
            
            if tile['type'] == 'farmland':
                color = BROWN
                if tile['watered']:
                    color = (100, 50, 0) # Darker brown if watered
                pygame.draw.rect(screen, color, self.camera.apply_rect(rect))
                pygame.draw.rect(screen, BLACK, self.camera.apply_rect(rect), 1) # Grid lines
                
                if tile['crop']:
                    # Draw Crop
                    if tile['growth'] == 0:
                        # Draw Seeds (Dots)
                        seed_color = (200, 200, 100) # Default seed color
                        if "Red" in tile['crop']: seed_color = (200, 50, 50)
                        elif "Blue" in tile['crop']: seed_color = (50, 50, 200)
                        elif "Rare" in tile['crop']: seed_color = (200, 50, 200)
                        
                        # Draw 3 dots
                        center = rect.center
                        pygame.draw.circle(screen, seed_color, (center[0] + self.camera.camera.x - 5, center[1] + self.camera.camera.y + 5), 3)
                        pygame.draw.circle(screen, seed_color, (center[0] + self.camera.camera.x + 5, center[1] + self.camera.camera.y + 5), 3)
                        pygame.draw.circle(screen, seed_color, (center[0] + self.camera.camera.x, center[1] + self.camera.camera.y - 5), 3)
                    else:
                        # Growth stage color?
                        growth_stage = tile['growth'] / CROP_GROWTH_TIME
                        crop_color = GREEN
                        if growth_stage < 0.3:
                            crop_color = (100, 255, 100) # Sprout
                        elif growth_stage < 0.7:
                            crop_color = (50, 200, 50) # Growing
                        else:
                            crop_color = (0, 150, 0) # Mature
                            
                        # Draw circle for crop
                        center = rect.center
                        radius = 5 + (10 * growth_stage)
                        pygame.draw.circle(screen, crop_color, (center[0] + self.camera.camera.x, center[1] + self.camera.camera.y), int(radius))
        
        # Draw Buildings (World Space)
        # Portal
        pygame.draw.rect(screen, (100, 0, 100), self.camera.apply_rect(self.portal_rect))
        portal_text = self.font.render("Portal", True, WHITE)
        screen.blit(portal_text, (self.portal_rect.centerx - 20 + self.camera.camera.x, self.portal_rect.centery - 10 + self.camera.camera.y))
        
        # Crafting
        pygame.draw.rect(screen, (139, 69, 19), self.camera.apply_rect(self.crafting_rect)) # Brown
        craft_text = self.font.render("Crafting", True, WHITE)
        screen.blit(craft_text, (self.crafting_rect.centerx - 30 + self.camera.camera.x, self.crafting_rect.centery - 10 + self.camera.camera.y))
        
        # Shop
        pygame.draw.rect(screen, (218, 165, 32), self.camera.apply_rect(self.shop_rect)) # Goldenrod
        shop_text = self.font.render("Shop", True, WHITE)
        screen.blit(shop_text, (self.shop_rect.centerx - 20 + self.camera.camera.x, self.shop_rect.centery - 10 + self.camera.camera.y))
        
        # Research
        pygame.draw.rect(screen, (70, 130, 180), self.camera.apply_rect(self.research_rect)) # Steel Blue
        res_text = self.font.render("Research", True, WHITE)
        screen.blit(res_text, (self.research_rect.centerx - 30 + self.camera.camera.x, self.research_rect.centery - 10 + self.camera.camera.y))
        
        # Draw Player (World Space)
        if hasattr(self.game.player, 'image'):
            screen.blit(self.game.player.image, self.camera.apply_rect(self.game.player.rect))
        else:
            pygame.draw.rect(screen, BLUE, self.camera.apply_rect(self.game.player.rect))
            
        # Draw Golems
        for golem in self.golems:
            screen.blit(golem.image, self.camera.apply_rect(golem.rect))
            
        # Draw Expansion Queue (Ghost Tiles)
        for tile_pos in self.expansion_queue:
            rect = pygame.Rect(tile_pos[0] * TILE_SIZE, tile_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            s.fill((255, 255, 0, 100)) # Yellow transparent
            screen.blit(s, self.camera.apply_rect(rect))
        
        # --- UI LAYER (Screen Space) ---
        
        # Draw UI Title
        title = self.title_font.render("Home Sweet Home", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - 150, 30))
        
        # Draw Stats UI (Left of Toolbar)
        stats_x = 20
        stats_y = SCREEN_HEIGHT - 120
        pygame.draw.rect(screen, (50, 50, 50), (stats_x, stats_y, 150, 100))
        pygame.draw.rect(screen, WHITE, (stats_x, stats_y, 150, 100), 2)
        
        rank_text = self.font.render(f"Rank: {self.game.player.rank}", True, WHITE)
        gold_text = self.font.render(f"Gold: {self.game.player.gold}", True, YELLOW)
        
        # Intel Cap Logic
        current_intel = int(self.game.player.intelligence)
        rank = self.game.player.rank
        if rank >= 4:
            cap = current_intel
        else:
            cap = RANK_INTEL_CAPS.get(rank, 25)
            
        intel_text = self.font.render(f"Intel: {current_intel}/{cap}", True, (100, 100, 255))
        
        screen.blit(rank_text, (stats_x + 10, stats_y + 10))
        screen.blit(gold_text, (stats_x + 10, stats_y + 40))
        screen.blit(intel_text, (stats_x + 10, stats_y + 70))
        
        # Draw Command Mode Indicator
        if self.command_mode:
            cmd_text = self.font.render("COMMAND MODE (Click to Expand)", True, (255, 255, 0))
            screen.blit(cmd_text, (SCREEN_WIDTH // 2 - 150, 70))
        
        # Draw Buttons (Only Inventory is persistent UI)
        # Position Inventory Button at bottom right or somewhere convenient
        self.btn_inventory.rect.topleft = (SCREEN_WIDTH - 220, SCREEN_HEIGHT - 60)
        self.btn_inventory.draw(screen)
        

        # Recipe Window / Crafting UI
        if self.show_recipes and hasattr(self, 'crafting_ui_screen_rect'):
            rect = self.crafting_ui_screen_rect
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
            
            # Title
            title_surf = self.font.render("Crafting Station", True, BLACK)
            screen.blit(title_surf, (self.crafting_ui_screen_rect.centerx - title_surf.get_width() // 2, self.crafting_ui_screen_rect.y + 10))
            
            # Draw Tabs
            self.btn_tab_potions.draw(screen)
            self.btn_tab_seeds.draw(screen)
            self.btn_tab_golems.draw(screen)
            
            # Highlight selected tab
            if self.crafting_tab == "Potions":
                pygame.draw.rect(screen, YELLOW, self.btn_tab_potions.rect, 2)
            elif self.crafting_tab == "Seeds":
                pygame.draw.rect(screen, YELLOW, self.btn_tab_seeds.rect, 2)
            elif self.crafting_tab == "Golems":
                pygame.draw.rect(screen, YELLOW, self.btn_tab_golems.rect, 2)

            # Draw List Background
            list_height = 175
            list_rect = pygame.Rect(self.crafting_ui_screen_rect.x + 20, self.crafting_ui_screen_rect.y + 80, self.crafting_ui_screen_rect.width - 40, list_height)
            pygame.draw.rect(screen, WHITE, list_rect)
            pygame.draw.rect(screen, BLACK, list_rect, 1)
            
            # Clip drawing to list area
            old_clip = screen.get_clip()
            screen.set_clip(list_rect)

            # Draw Recipe Buttons with scroll offset
            # Initialize scroll_offset if not exists
            if not hasattr(self, 'crafting_scroll_y'):
                self.crafting_scroll_y = 0
                
            # Calculate total height
            total_height = len(self.recipe_buttons) * 35
            max_scroll = max(0, total_height - list_rect.height)
            
            # Clamp scroll
            self.crafting_scroll_y = max(0, min(self.crafting_scroll_y, max_scroll))
            
            start_y = list_rect.y - self.crafting_scroll_y
            
            for i, btn in enumerate(self.recipe_buttons):
                # Update button position relative to scroll
                btn.rect.x = list_rect.x
                btn.rect.y = start_y + i * 35
                btn.rect.width = list_rect.width
                
                # Only draw if visible
                if list_rect.colliderect(btn.rect):
                    btn.draw(screen)
                    
            screen.set_clip(old_clip)
            
            # Draw Scrollbar if needed
            if max_scroll > 0:
                scroll_bar_height = list_rect.height * (list_rect.height / total_height)
                scroll_bar_y = list_rect.y + (self.crafting_scroll_y / max_scroll) * (list_rect.height - scroll_bar_height)
                pygame.draw.rect(screen, GRAY, (list_rect.right - 10, scroll_bar_y, 8, scroll_bar_height))

            # Draw Selected Recipe Details (Bottom Half)
            details_y_start = list_rect.bottom + 20
            
            if self.selected_recipe:
                recipe = self.crafting_system.get_recipe(self.crafting_tab, self.selected_recipe)
                if recipe:
                    ingredients, time = recipe
                    
                    name_text = self.font.render(f"Selected: {self.selected_recipe}", True, YELLOW)
                    screen.blit(name_text, (rect.x + 20, details_y_start))
                    
                    ing_y = details_y_start + 30
                    for item, count in ingredients.items():
                        if item == "Gold":
                            has = self.game.player.gold
                        else:
                            has = self.game.player.inventory.get(item, 0)
                        
                        color = GREEN if has >= count else RED
                        ing_text = self.font.render(f"{item}: {has}/{count}", True, color)
                        screen.blit(ing_text, (rect.x + 20, ing_y))
                        ing_y += 25
                        
                    # Draw Craft Button or Lock Message
                    req_rank = self.crafting_system.get_required_rank(self.selected_recipe)
                    if self.game.player.rank >= req_rank:
                        self.btn_craft.rect.topleft = (rect.centerx - 50, rect.bottom - 50)
                        self.btn_craft.draw(screen)
                    else:
                        lock_text = self.font.render(f"Unlocked at Rank {req_rank}", True, RED)
                        screen.blit(lock_text, (rect.centerx - lock_text.get_width()//2, rect.bottom - 50))
                    
                    # Draw Progress Bar
                    if self.crafting_timer > 0 and self.crafting_target == self.selected_recipe:
                        progress = 1 - (self.crafting_timer / self.crafting_duration)
                        bar_rect = pygame.Rect(rect.x + 50, rect.bottom - 80, rect.width - 100, 20)
                        pygame.draw.rect(screen, BLACK, bar_rect)
                        pygame.draw.rect(screen, BLUE, (bar_rect.x, bar_rect.y, bar_rect.width * progress, 20))
                        pygame.draw.rect(screen, WHITE, bar_rect, 2)
                else:
                    # Handle case where recipe is not found (shouldn't happen if logic is correct)
                    self.selected_recipe = None
            else:
                info_text = self.font.render("Select a recipe", True, WHITE)
                screen.blit(info_text, (rect.centerx - info_text.get_width()//2, details_y_start + 50))
                    
            # Draw Close Button
            if hasattr(self, 'btn_close_crafting'):
                self.btn_close_crafting.draw(screen)

        # Shop UI
        if self.show_shop and hasattr(self, 'shop_ui_screen_rect'):
            try:
                rect = self.shop_ui_screen_rect
                pygame.draw.rect(screen, GRAY, rect)
                pygame.draw.rect(screen, WHITE, rect, 2)
                
                header = self.font.render("General Store", True, WHITE)
                screen.blit(header, (rect.centerx - header.get_width()//2, rect.y + 10))
                
                # Draw Tabs
                self.btn_shop_buy_tab.draw(screen)
                self.btn_shop_sell_tab.draw(screen)
                
                # Highlight Active Tab
                if self.shop_tab == "buy":
                    pygame.draw.rect(screen, YELLOW, self.btn_shop_buy_tab.rect, 2)
                else:
                    pygame.draw.rect(screen, YELLOW, self.btn_shop_sell_tab.rect, 2)
                    
                # Draw List (Clipped)
                list_rect = pygame.Rect(rect.x + 20, rect.y + 80, rect.width - 40, 250)
                screen.set_clip(list_rect)
                
                start_y = list_rect.y - self.shop_scroll_y
                
                if self.shop_tab == "buy":
                    for i, btn in enumerate(self.shop_buy_buttons):
                        btn.rect.topleft = (rect.x + 50, start_y + i * 35)
                        btn.draw(screen)
                elif self.shop_tab == "sell":
                    if not self.shop_sell_buttons:
                        empty_text = self.font.render("Inventory Empty", True, WHITE)
                        screen.blit(empty_text, (rect.centerx - empty_text.get_width()//2, rect.centery))
                    for i, btn in enumerate(self.shop_sell_buttons):
                        btn.rect.topleft = (rect.x + 50, start_y + i * 35)
                        btn.draw(screen)
                        
                screen.set_clip(None) # Reset clip
                        
                # Draw Selected Item Details
                if self.selected_shop_item:
                    # Draw Action Button or Lock Message
                    if self.shop_tab == "buy":
                        req_rank = self.shop_system.get_required_rank(self.selected_shop_item)
                        if self.game.player.rank >= req_rank:
                            self.btn_shop_action.draw(screen)
                        else:
                            lock_text = self.font.render(f"Unlocked at Rank {req_rank}", True, RED)
                            screen.blit(lock_text, (rect.centerx - lock_text.get_width()//2, 410)) # Adjust Y as needed
                    else:
                        self.btn_shop_action.draw(screen)
                    
                    # Draw Selection Highlight
                    # Find button for selected item
                    target_btn = None
                    if self.shop_tab == "buy":
                        for i, item in enumerate(self.shop_items_buy):
                            if item == self.selected_shop_item:
                                target_btn = self.shop_buy_buttons[i]
                                break
                    elif self.shop_tab == "sell":
                        # This is tricky because sell buttons are dynamic.
                        # We rely on the button text or index.
                        # Simplified: Just highlight the button if we can find it
                        pass 
                    
                    if target_btn:
                        pygame.draw.rect(screen, YELLOW, target_btn.rect, 2)
                
                # Draw Close Button
                self.btn_close_shop.draw(screen)
            except Exception as e:
                print(f"Error drawing Shop UI: {e}")

        # Research UI
        if self.show_research and hasattr(self, 'research_ui_screen_rect'):
            rect = self.research_ui_screen_rect
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
            
            header = self.font.render("Research Center", True, WHITE)
            screen.blit(header, (rect.centerx - header.get_width()//2, rect.y + 10))
            
            # Draw Topics
            topic_keys = list(self.research_system.topics.keys())
            for i, btn in enumerate(self.research_buttons):
                btn.draw(screen)
                
                if i < len(topic_keys):
                    topic = topic_keys[i]
                    
                    # Highlight selected
                    if topic == self.selected_research:
                        pygame.draw.rect(screen, YELLOW, btn.rect, 2)
                        
                    # Show status (Completed/In Progress)
                    if topic in self.research_system.completed_research:
                        status_text = self.font.render("Done", True, GREEN)
                        screen.blit(status_text, (btn.rect.right + 10, btn.rect.centery - 10))
                    elif self.research_system.current_research == topic:
                        # Show progress
                        progress = int(self.research_system.research_timer)
                        cost_duration = self.research_system.topics[topic][1] * 60 # Duration in frames
                        status_text = self.font.render(f"{int(progress/60)}s / {int(cost_duration/60)}s", True, BLUE)
                        screen.blit(status_text, (btn.rect.right + 10, btn.rect.centery - 10))
            
            # Draw Start Button
            self.btn_start_research.draw(screen)
            
            # Draw Close Button
            self.btn_close_research.draw(screen)

        # Inventory Window (Screen Space - Centered)
        if self.show_inventory:
            # Center the window
            window_width = 300
            window_height = 350
            window_x = (SCREEN_WIDTH - window_width) // 2
            window_y = (SCREEN_HEIGHT - window_height) // 2
            window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
            
            pygame.draw.rect(screen, GRAY, window_rect)
            pygame.draw.rect(screen, WHITE, window_rect, 2)
            
            header = self.font.render("Inventory", True, WHITE)
            screen.blit(header, (window_rect.centerx - header.get_width()//2, window_rect.y + 10))
            
            # Draw Grid
            inv_start_x = window_rect.x + 20
            inv_start_y = window_rect.y + 50
            grid_cols = 5
            slot_size = 40
            padding = 10
            
            # Inventory Slots
            items = list(self.game.player.inventory.items())
            for i in range(20): # 5x4 grid
                col = i % grid_cols
                row = i // grid_cols
                x = inv_start_x + col * (slot_size + padding)
                y = inv_start_y + row * (slot_size + padding)
                rect = pygame.Rect(x, y, slot_size, slot_size)
                
                pygame.draw.rect(screen, DARK_GREEN, rect)
                pygame.draw.rect(screen, WHITE, rect, 1)
                
                if i < len(items):
                    item_name, count = items[i]
                    # Draw Item (Placeholder color/text)
                    pygame.draw.rect(screen, PURPLE, (x+2, y+2, slot_size-4, slot_size-4))
                    # Draw Count
                    count_text = self.font.render(str(count), True, WHITE)
                    screen.blit(count_text, (x + 2, y + 2))
                    
            # Dragging Item
            if self.dragging_item:
                mouse_pos = pygame.mouse.get_pos()
                pygame.draw.circle(screen, YELLOW, mouse_pos, 10) # Cursor indicator

        # Persistent Toolbar (Screen Space - Bottom Center)
        toolbar_start_x = (SCREEN_WIDTH - (9 * 40)) // 2
        toolbar_y = SCREEN_HEIGHT - 50
        
        for i in range(9):
            x = toolbar_start_x + i * 40
            rect = pygame.Rect(x, toolbar_y, 32, 32)
            
            # Highlight selected
            if i == self.game.player.selected_slot:
                try:
                    pygame.draw.rect(screen, YELLOW, pygame.Rect(x-2, toolbar_y-2, 36, 36), 2)
                except Exception as e:
                    print(f"Error drawing highlight: {e}")
            
            pygame.draw.rect(screen, BLACK, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)
            
            slot_data = self.game.player.toolbar[i]
            if slot_data:
                # Draw Item Icon (Placeholder)
                pygame.draw.rect(screen, PURPLE, pygame.Rect(x+2, toolbar_y+2, 28, 28))
                
                # Draw Count
                count = slot_data['count']
                count_text = self.font.render(str(count), True, WHITE)
                screen.blit(count_text, (x + 2, toolbar_y + 2))
                
                # Draw Name (Small)
                name = slot_data['name']
                # Use pre-loaded small font if available, else create (but try to add it to init)
                if not hasattr(self, 'small_font'):
                    self.small_font = pygame.font.SysFont(None, 12)
                name_surf = self.small_font.render(name[:3], True, WHITE)
                screen.blit(name_surf, (x+2, toolbar_y+20))
