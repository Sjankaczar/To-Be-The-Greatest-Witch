import pygame
import time
import os
from src.states.game_state import GameState
from src.config import *
from src.systems.crafting import CraftingSystem
from src.systems.shop import ShopSystem
from src.systems.research import ResearchSystem
from src.systems.farming import FarmingSystem
from src.utils.ui import Button
from src.utils.ui import Button
from src.utils.camera import Camera

from src.utils.bitmap_font import BitmapFont
from pytmx.util_pygame import load_pygame
from src.utils.bitmap_font import BitmapFont
from pytmx.util_pygame import load_pygame
from src.assets import MAP_HOME, IMG_STATS_BG, IMG_HOTKEY_BOX, IMG_HIGHLIGHT_SLOT, IMG_TEMPLATE_BOX, IMG_QUIT_ICON, IMG_BUTTON, IMG_BUTTON_PRESSED, IMG_SLIDER, IMG_VALUE_BAR, IMG_VALUE_BLUE
from src.entities.item import Item

# Local Asset Path for Settings
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
IMG_SETTINGS_BTN = os.path.join(base_dir, "UI The Greatest Witch", "settings_UI.png")
IMG_SLIDER_KNOB = os.path.join(base_dir, "UI The Greatest Witch", "CornerKnot_14x14.png")

class HomeState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.crafting_system = CraftingSystem()
        self.shop_system = ShopSystem()
        self.shop_system = ShopSystem()
        self.research_system = game.research_system # Use shared system
        self.farming_system = FarmingSystem()
        self.farming_system = FarmingSystem()
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 48)



        # Home Area State
        
        # Load Map First to get dimensions
        self.tmx_data = load_pygame(MAP_HOME)
        self.tile_w = self.tmx_data.tilewidth
        self.tile_h = self.tmx_data.tileheight
        
        self.base_map_width = self.tmx_data.width * self.tile_w
        self.base_map_height = self.tmx_data.height * self.tile_h
        self.map_width = self.base_map_width
        self.map_height = self.base_map_height
        
        self.extra_tiles = [] # List of (x, y) tuples for expanded safe zone
        
        # Virtual Screen for Zoom
        self.virtual_width = int(SCREEN_WIDTH / CAMERA_ZOOM)
        self.virtual_height = int(SCREEN_HEIGHT / CAMERA_ZOOM)
        self.virtual_screen = pygame.Surface((self.virtual_width, self.virtual_height))
        
        # Camera with top offset to hide empty row (16px)
        self.camera = Camera(self.map_width, self.map_height, self.virtual_width, self.virtual_height, min_offset_y=-16)
        
        # Golems

        self.expansion_queue = [] # List of (grid_x, grid_y)
        self.command_mode = False
        
        # Initialize Player Position in Home
        self.game.player.rect.topleft = (90, 165)
        
        # Buildings (Positions relative to map)
        self.portal_rect = pygame.Rect(425, 137, 100, 60) # Center (475, 167)
        self.crafting_rect = pygame.Rect(13, 293, 80, 100) # Center (53, 343)
        self.shop_rect = pygame.Rect(210, 16, 44, 14) # Hidden Shop Area (210,16) to (254,30)
        self.research_rect = pygame.Rect(150, 310, 100, 80) # Center (200, 350)
        
        self.show_recipes = False
        self.show_inventory = False
        self.show_research = False
        self.show_shop = False 
        
        # Load Generic Button Images
        self.button_image = None
        self.button_pressed_image = None
        if os.path.exists(IMG_BUTTON):
            self.button_image = pygame.image.load(IMG_BUTTON).convert_alpha()
        if os.path.exists(IMG_BUTTON_PRESSED):
            self.button_pressed_image = pygame.image.load(IMG_BUTTON_PRESSED).convert_alpha()

        # Load Research Highlight (3-Slice Scaling)
        self.research_highlight_image = None
        if os.path.exists(IMG_HIGHLIGHT_SLOT):
             raw = pygame.image.load(IMG_HIGHLIGHT_SLOT).convert_alpha()
             self.research_highlight_image = self.create_3_slice_highlight(raw, 200, 30)
             self.crafting_highlight_image = self.create_3_slice_highlight(raw, 260, 30)


        # UI Buttons
        self.btn_recipes = Button(50, 150, 200, 40, "Recipes (R)", self.font, image=self.button_image, image_pressed=self.button_pressed_image) 
        self.btn_inventory = Button(50, 200, 200, 40, "Inventory (E)", self.font, image=self.button_image, image_pressed=self.button_pressed_image) 
        self.btn_upgrade = Button(50, 250, 250, 40, "Upgrade Lantern (50G)", self.font, image=self.button_image, image_pressed=self.button_pressed_image)
        self.btn_sell = Button(50, 300, 250, 40, "Sell Health Potion (10G)", self.font, image=self.button_image, image_pressed=self.button_pressed_image)
        
        # Close Buttons
        # Close Buttons
        # Load Quit Icon
        self.quit_icon_image = None
        if os.path.exists(IMG_QUIT_ICON):
            self.quit_icon_image = pygame.image.load(IMG_QUIT_ICON).convert_alpha()
        else:
            print(f"Warning: QuitIcon not found at {IMG_QUIT_ICON}")



        self.btn_close_crafting = Button(0, 0, 30, 30, "", self.font, color=RED, text_color=WHITE, image=self.quit_icon_image)
        self.btn_close_research = Button(0, 0, 30, 30, "", self.font, color=RED, text_color=WHITE, image=self.quit_icon_image)
        self.btn_close_inventory = Button(0, 0, 30, 30, "", self.font, color=RED, text_color=WHITE, image=self.quit_icon_image)
        
        # Cache for Item Sprites
        self.item_images = {}
        
        # Crafting UI State
        self.selected_recipe = None
        self.crafting_timer = 0
        self.crafting_duration = 0
        self.crafting_target = None
        
        self.dragging_item = None 
        self.dragging_source_index = -1
        
        self.crafting_tab = "Potions"
        self.btn_tab_potions = Button(0, 0, 80, 30, "Potions", self.font, color=BLUE, text_color=WHITE, image=self.button_image)
        self.btn_tab_seeds = Button(0, 0, 80, 30, "Seeds", self.font, color=BLUE, text_color=WHITE, image=self.button_image)

        
        self.recipe_buttons = []
        self.update_recipe_list()
            
        self.btn_craft = Button(450, 400, 100, 40, "Craft", self.font, color=DARK_GREEN, text_color=WHITE, image=self.button_image, image_pressed=self.button_pressed_image)

    def get_item_image(self, name):
        if name not in self.item_images:
            # Create dummy item to load sprite
            # Position doesn't matter
            try:
                temp_item = Item(0, 0, name)
                self.item_images[name] = temp_item.image
            except Exception as e:
                print(f"Error loading icon for {name}: {e}")
                # Create fallback surface
                s = pygame.Surface((32, 32))
                s.fill((128, 0, 128)) # Purple
                self.item_images[name] = s
            
        return self.item_images[name]

    def update_recipe_list(self):
        self.recipe_buttons = []
        y = 115
        
        recipes = self.crafting_system.get_all_recipes(self.crafting_tab)
        for recipe in recipes:
            self.recipe_buttons.append(Button(450, y, 260, 30, recipe, self.font, image=self.button_image))
            y += 35
        
        # Research UI State
        self.research_buttons = []
        y = 115
        for topic in self.research_system.topics:
            self.research_buttons.append(Button(450, y, 200, 30, topic, self.font, image=self.button_image)) # Use generic button, no pressed effect
            y += 35
        self.selected_research = None
        self.btn_start_research = Button(450, 400, 150, 40, "Start Research", self.font, color=BLUE, text_color=WHITE, image=self.button_image, image_pressed=self.button_pressed_image)

        # Shop UI State
        self.shop_tab = "buy" # "buy" or "sell"
        self.btn_shop_buy_tab = Button(0, 0, 100, 30, "Buy", self.font, color=BLUE, text_color=WHITE, image=self.button_image)
        self.btn_shop_sell_tab = Button(0, 0, 100, 30, "Sell", self.font, color=BLUE, text_color=WHITE, image=self.button_image)
        self.btn_close_shop = Button(0, 0, 30, 30, "", self.font, color=RED, text_color=WHITE, image=self.quit_icon_image)
        
        self.shop_items_buy = self.shop_system.get_all_items()
        self.shop_buy_buttons = []
        for item in self.shop_items_buy:
            self.shop_buy_buttons.append(Button(0, 0, 200, 30, f"{item} ({PRICES.get(item, 0)}G)", self.font, image=self.button_image))
            
        self.shop_sell_buttons = [] # Dynamic based on inventory
        self.selected_shop_item = None
        self.btn_shop_action = Button(0, 0, 100, 40, "Buy", self.font, color=YELLOW, text_color=BLACK, image=self.button_image, image_pressed=self.button_pressed_image)
        self.shop_scroll_y = 0
        
        # Settings UI
        self.show_settings = False
        # Settings UI
        self.show_settings = False
        self.settings_btn_image = None
        # Load UI Images
        if os.path.exists(IMG_HIGHLIGHT_SLOT):
             self.raw_highlight = pygame.image.load(IMG_HIGHLIGHT_SLOT).convert_alpha()
             # Pre-generate highlight for Research (200px)
             self.research_highlight_image = self.create_3_slice_highlight(self.raw_highlight, 200, 30)
             # Pre-generate for Shop Tabs (100px - matching button width)
             self.shop_tab_highlight_image = self.create_3_slice_highlight(self.raw_highlight, 100, 30)
        else:
             self.research_highlight_image = None
             self.shop_tab_highlight_image = None
        if os.path.exists(IMG_SETTINGS_BTN):
             self.settings_btn_image = pygame.image.load(IMG_SETTINGS_BTN).convert_alpha()
             # Scale if needed
             self.settings_btn_image = pygame.transform.scale(self.settings_btn_image, (80, 80))
        else:
             print(f"Warning: Settings Btn not found at {IMG_SETTINGS_BTN}")
             
        self.btn_settings = Button(0, 0, 80, 80, "", self.font, color=GRAY, image=self.settings_btn_image)
        
        # Volume Slider
        self.slider_image = None
        if os.path.exists(IMG_SLIDER):
             self.slider_image = pygame.image.load(IMG_SLIDER).convert_alpha()
        else:
             print(f"Warning: Slider not found at {IMG_SLIDER}")

        if os.path.exists(IMG_VALUE_BAR):
             self.value_bar_image = pygame.image.load(IMG_VALUE_BAR).convert_alpha()
             
        self.slider_knob_image = None
        if os.path.exists(IMG_SLIDER_KNOB):
             self.slider_knob_image = pygame.image.load(IMG_SLIDER_KNOB).convert_alpha()
             self.slider_knob_image = pygame.transform.scale(self.slider_knob_image, (28, 28))
        else:
             print(f"Warning: ValueBar not found at {IMG_VALUE_BAR}")
             
        self.value_blue_image = None
        if os.path.exists(IMG_VALUE_BLUE):
             self.value_blue_image = pygame.image.load(IMG_VALUE_BLUE).convert_alpha()
        else:
             print(f"Warning: ValueBlue not found at {IMG_VALUE_BLUE}")
             
        self.dragging_volume = False
        self.small_ui_font = pygame.font.SysFont(None, 18)
        
        # Load Stats UI Background
        
        # Load Stats UI Background
        if os.path.exists(IMG_STATS_BG):
            self.stats_bg_image = pygame.image.load(IMG_STATS_BG).convert_alpha()
            self.stats_bg_image = pygame.transform.scale(self.stats_bg_image, (135, 135)) # Uniform scale 1.5x (90->135) to avoid distortion
        else:
            print(f"Warning: Stats background not found at {IMG_STATS_BG}")
            self.stats_bg_image = None
            
        # Load Toolbar Box Image
        if os.path.exists(IMG_HOTKEY_BOX):
             self.toolbar_box_image = pygame.image.load(IMG_HOTKEY_BOX).convert_alpha()
        else:
             print(f"Warning: HotkeyBox not found at {IMG_HOTKEY_BOX}")
             self.toolbar_box_image = None

        # Load Highlight Image
        if os.path.exists(IMG_HIGHLIGHT_SLOT):
             self.highlight_image = pygame.image.load(IMG_HIGHLIGHT_SLOT).convert_alpha()
             self.highlight_image = pygame.transform.scale(self.highlight_image, (40, 40)) # Larger than box to surround it
        else:
             print(f"Warning: HighlightSlot not found at {IMG_HIGHLIGHT_SLOT}")
             self.highlight_image = None
             
        # Load Template Box (UI Background)
        if os.path.exists(IMG_TEMPLATE_BOX):
            self.template_box_image = pygame.image.load(IMG_TEMPLATE_BOX).convert_alpha()
        else:
            print(f"Warning: Template box not found at {IMG_TEMPLATE_BOX}")
            self.template_box_image = None

        # Pre-load Tileset Image for Manual Extraction (Fallback/Primary for farmland)
        tileset_path = os.path.join("assets", "tiles", "free_sample_tileset.png")
        self.manual_tileset_image = None
        if os.path.exists(tileset_path):
             try:
                 self.manual_tileset_image = pygame.image.load(tileset_path).convert_alpha()
                 print(f"Loaded manual tileset: {tileset_path}")
             except Exception as e:
                 print(f"Error loading manual tileset: {e}")
            
        # UI Box Constants (Verified via script)
        self.box_orig_w = 90
        self.box_orig_h = 90
        self.box_pad_left = 14
        self.box_pad_top = 6
        self.box_inner_w = 62 # 90 - 14 - 14
        self.box_inner_h = 78 # 90 - 6 - 6 (Assuming symmetry for visual balance)

        # Load Bitmap Font
        # Load Bitmap Font
        # New BitmapFont implementation handles loading both font files internally
        self.bitmap_font = BitmapFont(32, 32)

    def create_3_slice_highlight(self, raw_img, target_w, target_h):
        # 1. Scale uniformly to target height to establish correct border thickness
        # This assumes the visual "height" of the border should roughly equal the button height
        base_surf = pygame.transform.scale(raw_img, (target_h, target_h))
        
        # 2. Slice
        border_w = 10
        left_part = base_surf.subsurface((0, 0, border_w, target_h))
        right_part = base_surf.subsurface((target_h - border_w, 0, border_w, target_h))
        mid_part = base_surf.subsurface((border_w, 0, target_h - 2 * border_w, target_h))
        
        # 3. Stretch Middle
        mid_width = target_w - 2 * border_w
        if mid_width < 0: mid_width = 0
        mid_stretched = pygame.transform.scale(mid_part, (mid_width, target_h))
        
        # 4. Assemble
        final_surf = pygame.Surface((target_w, target_h), pygame.SRCALPHA)
        final_surf.blit(left_part, (0, 0))
        final_surf.blit(mid_stretched, (border_w, 0))
        final_surf.blit(right_part, (target_w - border_w, 0))
        
        return final_surf

    def enter(self, params=None):
        print("Entering Home State")
        # Always force player to start at specific position
        self.game.player.rect.topleft = (90, 165)
        print(f"Set player position to (90, 165)")

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
                    world_x = (mouse_pos[0] / CAMERA_ZOOM) - self.camera.camera.x
                    world_y = (mouse_pos[1] / CAMERA_ZOOM) - self.camera.camera.y
                    
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
                # Close Inventory Button
                if self.btn_close_inventory.handle_event(event):
                    self.show_inventory = False
                    
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
                if player_rect.colliderect(self.crafting_rect):
                    self.show_recipes = True
                    print("Opened Crafting Station")
                elif player_rect.colliderect(self.shop_rect):
                    self.show_shop = True
                    # self.show_inventory = True # User requested to NOT open inventory
                    print("Opened Shop")
                elif player_rect.colliderect(self.research_rect):
                    if self.game.player.rank >= 4:
                        self.show_research = True
                        print("Opened Research Center")
                    else:
                        print("Research Center unlocks at Rank 4!")
                    
            # Settings Button Handle (Global)
            if self.btn_settings.handle_event(event):
                self.show_settings = not self.show_settings
                print(f"Settings toggled: {self.show_settings}")
            
            # Close Settings if open and click outside
            if self.show_settings:
                 # Calculate popup rect (Same as draw)
                 popup_w = 300
                 popup_h = 200
                 popup_rect = pygame.Rect((SCREEN_WIDTH - popup_w)//2, (SCREEN_HEIGHT - popup_h)//2, popup_w, popup_h)
                 
                 # Volume Slider Rect
                 # Match draw: x+100, y+70, 128x16 (Moved left from 120)
                 bar_rect = pygame.Rect(popup_rect.x + 100, popup_rect.y + 70, 128, 16)
                 
                 if event.type == pygame.MOUSEBUTTONDOWN:
                      if bar_rect.inflate(20, 20).collidepoint(event.pos):
                           self.dragging_volume = True
                           # Update volume
                           val = (event.pos[0] - bar_rect.x) / bar_rect.width
                           self.game.volume = max(0.0, min(1.0, val))
                           pygame.mixer.music.set_volume(self.game.volume)
                      elif not popup_rect.collidepoint(event.pos) and not self.btn_settings.rect.collidepoint(event.pos):
                           # Close if clicked outside
                           pass # Optional: self.show_settings = False
                           
                 elif event.type == pygame.MOUSEBUTTONUP:
                      self.dragging_volume = False
                      
                 elif event.type == pygame.MOUSEMOTION:
                      if self.dragging_volume:
                           val = (event.pos[0] - bar_rect.x) / bar_rect.width
                           self.game.volume = max(0.0, min(1.0, val))
                           pygame.mixer.music.set_volume(self.game.volume)

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
                        self.shop_buy_buttons.append(Button(0, 0, 200, 30, f"{item} ({PRICES.get(item, 0)}G)", self.font, image=self.button_image))
                    
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
                        self.shop_sell_buttons.append(Button(0, 0, 200, 30, f"{item} x{count} ({price}G)", self.font, image=self.button_image))
                
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
                    world_x = (mouse_x / CAMERA_ZOOM) - self.camera.camera.x
                    world_y = (mouse_y / CAMERA_ZOOM) - self.camera.camera.y
                    
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
                    world_x = (mouse_x / CAMERA_ZOOM) - self.camera.camera.x
                    world_y = (mouse_y / CAMERA_ZOOM) - self.camera.camera.y

                    # Get selected tool
                    selected_slot_index = self.game.player.selected_slot
                    selected_item = self.game.player.toolbar[selected_slot_index]
                    
                    if selected_item:
                        item_name = selected_item['name']
                        print(f"DEBUG: Clicked with item '{item_name}' at world pos ({world_x:.2f}, {world_y:.2f})")
                        
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
                                if item_name in ["Red Herb", "Blue Herb", "Red Seed", "Blue Seed"]:
                                    # Basic herbs/seeds no longer require research
                                    can_plant = True
                                elif item_name in ["Rare Herb", "Rare Seed"] and "Rare Herbs" in self.research_system.completed_research:
                                    can_plant = True
                                
                                else:
                                     print(f"Research check failed for {item_name}. Completed: {self.research_system.completed_research}")

                                if can_plant:
                                    print(f"Attempting to plant {item_name} at ({world_x:.2f}, {world_y:.2f})")
                                    if self.farming_system.plant_crop(world_x, world_y, item_name): 
                                        selected_item['count'] -= 1
                                        if selected_item['count'] <= 0:
                                            self.game.player.toolbar[selected_slot_index] = None
                                        
                                        key = self.farming_system.get_tile_key(world_x, world_y)
                                        print(f"Plant success at key {key}")
                                        if key in self.farming_system.grid and self.farming_system.grid[key]['type'] == 'farmland' and self.farming_system.grid[key]['crop'] is None:
                                            self.farming_system.grid[key]['crop'] = item_name
                                            self.farming_system.grid[key]['growth'] = 0
                                            print(f"Planted {item_name}!")
                                    else:
                                        print(f"plant_crop returned False. Grid Key: {self.farming_system.get_tile_key(world_x, world_y)}")
                                        key = self.farming_system.get_tile_key(world_x, world_y)
                                        if key in self.farming_system.grid:
                                             print(f"Tile Data: {self.farming_system.grid[key]}")
                                        else:
                                             print("Key not in grid.")
                                else:
                                    print("Cannot plant: Research required.")
                            


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
        

        
        # Update Player (Movement & Animation)
        # Update Player (Movement & Animation)
        prev_rect = self.game.player.rect.copy()
        
        if self.command_mode:
             self.handle_command_mode_input()
        else:
            self.game.player.update()
            
            # Check for Room Teleport (Specific Coordinates)
            px, py = self.game.player.rect.topleft
            if (px==88 or px==89 or px == 90 or px == 91 or px == 92 or px==93 or px==94) and (py == 119 or py == 120 or py == 121 or py == 122):
                print(f"Teleporting to Room from {px},{py}")
                self.game.states["room"].enter()
                self.game.change_state("room")

            # Check for Portal Teleport (Exploration) - Automatic Trigger
            # Line (462, 149) to (462, 174)
            portal_trigger = pygame.Rect(462, 149, 5, 25)
            if self.game.player.rect.colliderect(portal_trigger):
                self.last_player_pos = self.game.player.rect.topleft
                print(f"Auto-entering Exploration from {self.last_player_pos}")
                self.game.player.rect.topleft = (0, 70) # Set spawn point
                self.game.states["exploration"].enter()
                self.game.change_state("exploration")

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
            
        # Invisible Barrier Check
        # Area: (60, 102) to (132, 119) -> Rect(60, 102, 72, 17)
        # New Barrier: Center at (320, 89)
        # Size 29x29 -> TopLeft (320-14, 89-14) = (306, 75)
        barriers = [
            pygame.Rect(60, 102, 72, 17),
            pygame.Rect(345, 112, 8, 2)
        ]
        
        for barrier in barriers:
             if self.game.player.rect.colliderect(barrier):
                  # Collision with barrier, revert
                  self.game.player.rect = prev_rect
                  break
                  
        # Clamp Player Y to 0 (Prevent negative Y / Void walking)
        # Force clamp rect AND position properties if any
        if self.game.player.rect.top < 16:
            self.game.player.rect.top = 16
            # Also reset velocity if player has it physics-wise to prevent sticking
            if hasattr(self.game.player, 'velocity_y') and self.game.player.velocity_y < 0:
                self.game.player.velocity_y = 0
        
        # Update Camera
        self.camera.update(self.game.player)
        
        # Constrain Player to Map (Legacy constraint, might not be needed if validation works, but keeps player from flying off to infinity if bugged)
        # self.game.player.rect.x = max(0, min(self.game.player.rect.x, self.map_width - 32))
        # self.game.player.rect.y = max(0, min(self.game.player.rect.y, self.map_height - 32))
        
        # --- UPDATE UI POSITIONS (World Space -> Screen Space) ---
        
        # Research UI
        if self.show_research:
            # Window Position (Screen Space: Centered)
            window_width = 300
            window_height = 400
            screen_rect = pygame.Rect((SCREEN_WIDTH - window_width) // 2, (SCREEN_HEIGHT - window_height) // 2, window_width, window_height)
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
            # Window Position (Screen Space: Centered)
            window_width = 300
            window_height = 400
            screen_rect = pygame.Rect((SCREEN_WIDTH - window_width) // 2, (SCREEN_HEIGHT - window_height) // 2, window_width, window_height)
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
            # Window Position (Screen Space: Centered)
            window_width = 300
            window_height = 400
            screen_rect = pygame.Rect((SCREEN_WIDTH - window_width) // 2, (SCREEN_HEIGHT - window_height) // 2, window_width, window_height)
            self.shop_ui_screen_rect = screen_rect
            
            # Update Buttons
            # Tabs
            self.btn_shop_buy_tab.rect.topleft = (screen_rect.x + 45, screen_rect.y + 40)
            self.btn_shop_sell_tab.rect.topleft = (screen_rect.x + 155, screen_rect.y + 40)
            
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
            
        # Inventory UI Position Update
        if self.show_inventory:
             window_width = 300
             window_height = 350
             window_x = (SCREEN_WIDTH - window_width) // 2
             window_y = (SCREEN_HEIGHT - window_height) // 2
             window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
             
             self.btn_close_inventory.rect.topright = (window_rect.right - 10, window_rect.top + 10)

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
        return False

    def draw_ui_background(self, screen, rect):
        """Draws the template box stretched so its VISIBLE content matches rect."""
        if self.template_box_image:
            # Calculate Scale Factors
            scale_x = rect.width / self.box_inner_w
            scale_y = rect.height / self.box_inner_h
            
            # Calculate New Total Size
            new_w = int(self.box_orig_w * scale_x)
            new_h = int(self.box_orig_h * scale_y)
            
            # Scale Image
            scaled_img = pygame.transform.scale(self.template_box_image, (new_w, new_h))
            
            # Calculate Offset Position
            # We want the inner top-left to be at rect.x, rect.y
            # The inner top-left is at (pad_left * scale_x, pad_top * scale_y) relative to image
            pos_x = rect.x - int(self.box_pad_left * scale_x)
            pos_y = rect.y - int(self.box_pad_top * scale_y)
            
            screen.blit(scaled_img, (pos_x, pos_y))
        else:
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)

    def draw(self, screen):
        native_screen = screen
        screen = self.virtual_screen
        screen.fill(BLACK) # Background default (Void color)

        # --- Render Layer Map TMX with Z-Ordering ---
        
        # Explicitly draw Black Void for y < 0 to cover any gaps if camera moves down
        void_rect = pygame.Rect(-10000, -10000, 20000, 10000) # Covers everything above y=0
        pygame.draw.rect(screen, BLACK, self.camera.apply_rect(void_rect))
        
        entities_drawn = False
        
        for layer in self.tmx_data.visible_layers:
            # Draw Tile Layer
            if hasattr(layer, "tiles"):
                for x, y, tile in layer.tiles():
                    world_x = x * self.tile_w
                    world_y = y * self.tile_h
                    screen.blit(tile, self.camera.apply_pos((world_x, world_y)))
            
            # Check for injection point (After Layer 5, Before Layer 6)
            # Use getattr because some layer types might not have id
            if getattr(layer, "id", -1) == 5:
                 # --- DRAW ENTITIES PLANE ---
                 
                 # Draw Crops (On top of ground/Layer 5)
                 for key, tile in self.farming_system.grid.items():
                    grid_x, grid_y = key
                    world_x = grid_x * self.farming_system.tile_size
                    world_y = grid_y * self.farming_system.tile_size
                    rect = pygame.Rect(world_x, world_y, self.farming_system.tile_size, self.farming_system.tile_size)
                    
                    if tile['type'] == 'farmland':
                        # 9-Slice Autotiling Logic
                        # IDs based on GID 1308 (Top-Left) and Columns 70
                        # TL=1308, T=1309, TR=1310
                        # L=1378,  C=1379, R=1380
                        # BL=1448, B=1449, BR=1450
                        
                        # Check Neighbors
                        n = (grid_x, grid_y - 1) in self.farming_system.grid and self.farming_system.grid[(grid_x, grid_y - 1)]['type'] == 'farmland'
                        s = (grid_x, grid_y + 1) in self.farming_system.grid and self.farming_system.grid[(grid_x, grid_y + 1)]['type'] == 'farmland'
                        w = (grid_x - 1, grid_y) in self.farming_system.grid and self.farming_system.grid[(grid_x - 1, grid_y)]['type'] == 'farmland'
                        e = (grid_x + 1, grid_y) in self.farming_system.grid and self.farming_system.grid[(grid_x + 1, grid_y)]['type'] == 'farmland'
                        
                        # Bitmask: N=1, S=2, W=4, E=8
                        mask = 0
                        if n: mask += 1
                        if s: mask += 2
                        if w: mask += 4
                        if e: mask += 8
                        
                        # GID Mapping (Base 1308)
                        # 4x4 Grid Structure assumed:
                        # Row 0: 1308(TL), 1309(T), 1310(TR), 1311(V-Top)
                        # Row 1: 1378(L),  1379(C), 1380(R),  1381(V-Mid)
                        # Row 2: 1448(BL), 1449(B), 1450(BR), 1451(V-Bot)
                        # Row 3: 1518(H-L), 1519(H-M), 1520(H-R), 1521(Iso)
                        
                        gid_map = {
                            0: 1521,  # None -> Isolated
                            
                            # Horizontal Strip (No N/S)
                            8: 1518,  # E -> H-Left
                            4: 1520,  # W -> H-Right
                            12: 1519, # W+E -> H-Mid
                            
                            # Vertical Strip (No W/E)
                            2: 1311,  # S -> V-Top
                            1: 1451,  # N -> V-Bottom
                            3: 1381,  # N+S -> V-Mid
                            
                            # 3x3 Block Context
                            10: 1308, # N=0, S=1, W=0, E=1 -> TL (S+E)
                            6: 1310,  # N=0, S=1, W=1, E=0 -> TR (S+W)
                            9: 1448,  # N=1, S=0, W=0, E=1 -> BL (N+E)
                            5: 1450,  # N=1, S=0, W=1, E=0 -> BR (N+W)
                            
                            14: 1378, # N=1, S=1, W=0, E=1 -> L (N+S+E)
                            7: 1380,  # N=0, S=1, W=1, E=1 -> R (S+W+E) ? No. R needs N+S+W. 
                                      # Wait. Edge 'Left' means neighbors on N, S, E.
                                      # Edge 'Right' means neighbors on N, S, W.
                                      # Let's re-verify:
                                      # Left Edge (1378) visually matches 'Left Border'. So it should be used when there IS stuff to the right, but NOT to the left.
                                      # Neighbors: N, S, E. (Mask 1+2+8=11)
                                      
                            11: 1378, # N+S+E -> Left Edge (Visual Left border)
                            13: 1380, # N=1, S=1, W=1 -> N+S+W -> Right Edge (Visual Right border)
                            
                            15: 1379, # All -> Center
                            
                            # T-Junctions (Missing one side) or 2-side corners
                            # Top Edge (1309): Needs S, W, E. (No N). Mask 2+4+8=14
                            14: 1309, 
                            
                            # Bottom Edge (1449): Needs N, W, E. (No S). Mask 1+4+8=13. No wait.
                            # Standard 3x3 logic usually:
                            # 1309 (Top Edge) -> Used when: Has S. Has W? Has E?
                            # Actually, a simple 'Hull' logic might be safer than explicit mask if combinations are weird.
                            # But strict mask is best for strips.
                            
                            # Let's fix the 3x3 mapping based on "Connects to":
                            # TL (1308) connects S and E.
                            # T (1309) connects S, W, E.
                            # TR (1310) connects S, W.
                            # L (1378) connects N, S, E.
                            # C (1379) connects N, S, W, E.
                            # R (1380) connects N, S, W.
                            # BL (1448) connects N, E.
                            # B (1449) connects N, W, E.
                            # BR (1450) connects N, W.
                            
                            # Re-evaluating masks:
                            # S+E (2+8=10) -> TL (1308)
                            # S+W+E (2+4+8=14) -> T (1309)
                            # S+W (2+4=6) -> TR (1310)
                            # N+S+E (1+2+8=11) -> L (1378)
                            # N+S+W+E (15) -> C (1379)
                            # N+S+W (1+2+4=7) -> R (1380)
                            # N+E (1+8=9) -> BL (1448)
                            # N+W+E (1+4+8=13) -> B (1449)
                            # N+W (1+4=5) -> BR (1450)
                        }
                        
                        gid = gid_map.get(mask, 1379) # Default to center if unknown combo (should cover all though)
                        
                        # Special case: Isolation override is 1521 (Mask 0)
                        # Horizontal strip override:
                        # If N=0 and S=0:
                        #   W=0, E=0 -> 1521
                        #   W=0, E=1 -> 1518
                        #   W=1, E=1 -> 1519
                        #   W=1, E=0 -> 1520
                        # Vertical strip override:
                        # If W=0 and E=0:
                        #   N=0, S=1 -> 1311
                        #   N=1, S=1 -> 1381
                        #   N=1, S=0 -> 1451
                        
                        # The map above covers these exactly!
                        # 0 -> 1521
                        # 8 -> 1518
                        # 4 -> 1520
                        # 12 -> 1519
                        # 2 -> 1311
                        # 1 -> 1451
                         # 3 -> 1381
                         
                        # What if we have weird shapes? e.g. N only (1)? Mapped to 1451. Correct.
                        # What if N and E? (9). Mapped to 1448 (BL). Correct.
                        # It seems consistent.
                        
                        # Get Tile Image
                        tile_img = None
                        
                        # Try Manual Extraction first (Reliable based on view_tile_id.py)
                        if self.manual_tileset_image:
                             try:
                                 # GID 1-based, index 0-based
                                 # Assuming GID matches raw index + 1 for this tileset (firstgid=1)
                                 # GID 1308 -> Index 1307
                                 idx = gid - 1 
                                 cols = 70 # Hardcoded as per halaman.tmx
                                 row = idx // cols
                                 col = idx % cols
                                 
                                 x = col * 16 # Tile Size 16
                                 y = row * 16
                                 
                                 if x + 16 <= self.manual_tileset_image.get_width() and y + 16 <= self.manual_tileset_image.get_height():
                                      tile_img = self.manual_tileset_image.subsurface(pygame.Rect(x, y, 16, 16))
                             except Exception as e:
                                 print(f"Manual tile extract error: {e}")

                        # Fallback to pytmx if manual failed (or if tileset mismatch)
                        if not tile_img:
                             try:
                                 tile_img = self.tmx_data.get_tile_image_by_gid(gid)
                             except Exception:
                                 pass

                        if tile_img:
                             screen.blit(tile_img, self.camera.apply_rect(rect))
                        else:
                             # Fallback if image not found
                             pygame.draw.rect(screen, BROWN, self.camera.apply_rect(rect))
                             pygame.draw.rect(screen, BLACK, self.camera.apply_rect(rect), 1)
                        
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
                 # Portal - Removed visual as per user request
                 # pygame.draw.rect(screen, (100, 0, 100), self.camera.apply_rect(self.portal_rect))
                 # portal_text = self.font.render("Portal", True, WHITE)
                 # screen.blit(portal_text, (self.portal_rect.centerx - 20 + self.camera.camera.x, self.portal_rect.centery - 10 + self.camera.camera.y))
                 

                 
                 # Shop - Hidden/Transparent as per request
                 # pygame.draw.rect(screen, (218, 165, 32), self.camera.apply_rect(self.shop_rect)) # Goldenrod
                 # shop_text = self.font.render("Shop", True, WHITE)
                 # screen.blit(shop_text, (self.shop_rect.centerx - 20 + self.camera.camera.x, self.shop_rect.centery - 10 + self.camera.camera.y))
                 

                 
                 # Draw Player (World Space)
                 if hasattr(self.game.player, 'image'):
                     screen.blit(self.game.player.image, self.camera.apply_rect(self.game.player.rect))
                 else:
                     pygame.draw.rect(screen, BLUE, self.camera.apply_rect(self.game.player.rect))
                     

                     
                 # Draw Expansion Queue (Ghost Tiles)
                 for tile_pos in self.expansion_queue:
                     rect = pygame.Rect(tile_pos[0] * TILE_SIZE, tile_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                     s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                     s.fill((255, 255, 0, 100)) # Yellow transparent
                     screen.blit(s, self.camera.apply_rect(rect))
                 
                 entities_drawn = True
        
        # Fallback: If entities weren't drawn (e.g. Layer 5 missing), draw them now
        if not entities_drawn:
             # Draw Player (World Space) - condensed fallback
             if hasattr(self.game.player, 'image'):
                 screen.blit(self.game.player.image, self.camera.apply_rect(self.game.player.rect))
             else:
                 pygame.draw.rect(screen, BLUE, self.camera.apply_rect(self.game.player.rect))
            
        # Draw Axe Targeting Highlight
        selected_slot = self.game.player.selected_slot
        selected_item = self.game.player.toolbar[selected_slot]
        if selected_item and selected_item['name'] == "Axe":
            mouse_pos = pygame.mouse.get_pos()
            world_x = (mouse_pos[0] / CAMERA_ZOOM) - self.camera.camera.x
            world_y = (mouse_pos[1] / CAMERA_ZOOM) - self.camera.camera.y
            
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
        
        # --- DRAW WORLD TO SCREEN (SCALED) ---
        scaled_surface = pygame.transform.scale(self.virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
        native_screen.blit(scaled_surface, (0, 0))
        
        screen = native_screen # Switch back to native screen for UI
        
        # --- UI LAYER (Screen Space) ---
        
        # Draw UI Title
        # title = self.title_font.render("Home Sweet Home", True, WHITE)
        # screen.blit(title, (SCREEN_WIDTH // 2 - 150, 30))
        
        # Draw Stats UI (Left of Toolbar)
        stats_x = 20
        stats_x = 10
        stats_y = SCREEN_HEIGHT - 140 # Adjusted for taller box (135px)
        
        if self.stats_bg_image:
            screen.blit(self.stats_bg_image, (stats_x, stats_y))
        else:
            pygame.draw.rect(screen, (50, 50, 50), (stats_x, stats_y, 150, 100))
            pygame.draw.rect(screen, WHITE, (stats_x, stats_y, 150, 100), 2)
        
        if self.bitmap_font:
             # Rank
             self.bitmap_font.render(screen, str(self.game.player.rank), stats_x + 68, stats_y + 12, scale=1.5, spacing=-10)
             
             # Intel Cap Logic
             current_intel = int(self.game.player.intelligence)
             rank = self.game.player.rank
             if rank >= 4:
                 cap = current_intel
             else:
                 cap = RANK_INTEL_CAPS.get(rank, 25)
             
             # Intel (current/cap)
             # Basic formatting ensuring / exists
             # If using K/M for intel, apply format_number to parts? For now keep simple.
             intel_str = f"{current_intel}/{cap}"
             self.bitmap_font.render(screen, intel_str, stats_x + 38, stats_y + 38, scale=1.5, spacing=-38)
             
             # Gold
             gold_str = self.bitmap_font.format_number(self.game.player.gold)
             self.bitmap_font.render(screen, gold_str, stats_x + 45, stats_y + 68, scale=1.5, spacing=-38)
             
        else:
            rank_text = self.font.render(f"{self.game.player.rank}", True, WHITE)
            gold_text = self.font.render(f"{self.game.player.gold}", True, YELLOW)
            
            # Intel Cap Logic
            current_intel = int(self.game.player.intelligence)
            rank = self.game.player.rank
            if rank >= 4:
                cap = current_intel
            else:
                cap = RANK_INTEL_CAPS.get(rank, 25)
                
            intel_text = self.font.render(f"{current_intel}/{cap}", True, (100, 100, 255))
            
            screen.blit(rank_text, (stats_x + 90, stats_y + 19))
            screen.blit(gold_text, (stats_x + 70, stats_y + 62))
            screen.blit(intel_text, (stats_x + 70, stats_y + 38))

        
        # Draw Settings Button (Above Stats UI)
        # Stats Y is ~SCREEN_HEIGHT - 140.
        # Button 32x32.
        # Padding 10px.
        settings_x = stats_x
        settings_y = stats_y - 80 - 10
        self.btn_settings.rect.topleft = (settings_x, settings_y)
        self.btn_settings.draw(screen)
        
        # Draw Settings Popup
        if self.show_settings:
             # Center Screen
             popup_w = 300
             popup_h = 200
             popup_rect = pygame.Rect((SCREEN_WIDTH - popup_w)//2, (SCREEN_HEIGHT - popup_h)//2, popup_w, popup_h)
             
             if self.template_box_image:
                  # Use 3-slice or just scale the template box? 
                  # User said "tampilkan saja dulu 'template box.png'".
                  # Assuming template box is a scalable asset (9-slice would be ideal but maybe just scale)
                  scaled_box = pygame.transform.scale(self.template_box_image, (popup_w, popup_h))
                  screen.blit(scaled_box, popup_rect)
             else:
                  pygame.draw.rect(screen, GRAY, popup_rect)
                  pygame.draw.rect(screen, WHITE, popup_rect, 2)
                  
             # Title "Settings"
             title_surf = self.font.render("Settings", True, WHITE)
             screen.blit(title_surf, (popup_rect.centerx - title_surf.get_width()//2, popup_rect.y + 20))
             
             # Volume Control
             # Adjusted position to be inside the box
             # Use smaller font as requested
             vol_text = self.small_ui_font.render("Volume", True, WHITE)
             screen.blit(vol_text, (popup_rect.x + 58, popup_rect.y + 70)) # Moved right from 40
             
             # Slider Bar
             # BarRect should match image size (128x16)
             bar_w = 128
             bar_h = 16
             bar_rect = pygame.Rect(popup_rect.x + 100, popup_rect.y + 70, bar_w, bar_h) # Moved left from 120 
             
             # Draw Box logic or Image
             if self.value_bar_image and self.value_blue_image:
                 # Draw Frame
                 screen.blit(self.value_bar_image, bar_rect)
                 
                 # Draw/Clip Blue Fill
                 # Fill width proportional to volume
                 # Inner width 120, height 8. Padding 4,4.
                 inner_max_w = 120
                 fill_w = int(inner_max_w * self.game.volume)
                 
                 if fill_w > 0:
                     # Create subsurface or clipped blit
                     # Safeguard against fill_w being 0 or larger than image
                     fill_w = max(0, min(fill_w, inner_max_w))
                     
                     # Subsurface is safer for blitting part of image
                     # Assuming image is 120x8 exactly
                     if fill_w > 0:
                         sub_surf = self.value_blue_image.subsurface((0, 0, fill_w, 8))
                         screen.blit(sub_surf, (bar_rect.x + 4, bar_rect.y + 4))
             else:
                 # Fallback
                 pygame.draw.rect(screen, BLACK, bar_rect)
                 fill_width = int(bar_rect.width * self.game.volume)
                 pygame.draw.rect(screen, GREEN, (bar_rect.x, bar_rect.y, fill_width, bar_rect.height))
                 pygame.draw.rect(screen, WHITE, bar_rect, 2)
             
             # Slider Knob (Square Button)
             # Should follow the fill position? Or the bar?
             # Slider knob usually centers on the current value point.
             # Range is from x+4 to x+4+120 (120px travel).
             travel_w = 120
             knob_size = 28
             # Knob X center matches value
             knob_center_x = bar_rect.x + 4 + int(travel_w * self.game.volume)
             knob_y = bar_rect.centery - knob_size // 2
             
             knob_rect = pygame.Rect(knob_center_x - knob_size//2, knob_y, knob_size, knob_size)
             
             if hasattr(self, 'slider_knob_image') and self.slider_knob_image:
                  screen.blit(self.slider_knob_image, knob_rect)
             else:
                  pygame.draw.rect(screen, (200, 200, 200), knob_rect)
                  pygame.draw.rect(screen, WHITE, knob_rect, 2)

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
            # Background
            self.draw_ui_background(screen, rect)
            
            # Title
            
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
                    
                    # Highlight Selected
                    if self.selected_recipe == btn.text:
                         if self.crafting_highlight_image:
                              screen.blit(self.crafting_highlight_image, btn.rect)
                         else:
                              pygame.draw.rect(screen, YELLOW, btn.rect, 2)
                    
            screen.set_clip(old_clip)
            
            # Draw Scrollbar if needed
            if max_scroll > 0:
                scroll_bar_height = list_rect.height * (list_rect.height / total_height)
                scroll_bar_y = list_rect.y + (self.crafting_scroll_y / max_scroll) * (list_rect.height - scroll_bar_height)
                
                # Use slider image if available
                if self.slider_image:
                     # Force scale to calculated height and fixed width (Wider now)
                     # User complained it was too thin. 
                     # Increase width to 40px.
                     sb_img = pygame.transform.scale(self.slider_image, (60, max(20, int(scroll_bar_height))))
                     screen.blit(sb_img, (list_rect.right - 30, scroll_bar_y)) # Adjust X to align
                else:
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
                # Background
                self.draw_ui_background(screen, rect)
                
                header = self.font.render("General Store", True, WHITE)
                screen.blit(header, (rect.centerx - header.get_width()//2, rect.y + 10))
                
                # Draw Tabs
                self.btn_shop_buy_tab.draw(screen)
                self.btn_shop_sell_tab.draw(screen)
                
                # Highlight Active Tab
                if self.shop_tab == "buy":
                    if getattr(self, 'shop_tab_highlight_image', None):
                        screen.blit(self.shop_tab_highlight_image, self.btn_shop_buy_tab.rect)
                    else:
                        pygame.draw.rect(screen, YELLOW, self.btn_shop_buy_tab.rect, 2)
                else:
                    if getattr(self, 'shop_tab_highlight_image', None):
                        screen.blit(self.shop_tab_highlight_image, self.btn_shop_sell_tab.rect)
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
                
                # Draw Scrollbar if needed
                # Re-calculate max scroll to verify
                list_height = 250
                item_height = 35
                num_items = 0
                if self.shop_tab == "buy":
                    num_items = len(self.shop_buy_buttons)
                elif self.shop_tab == "sell":
                    num_items = len(self.shop_sell_buttons)
                    
                total_content_height = num_items * item_height
                max_scroll = max(0, total_content_height - list_height)
                
                if max_scroll > 0:
                    scroll_bar_height = list_height * (list_height / total_content_height)
                    # Safety clamp
                    scroll_bar_height = max(20, scroll_bar_height)
                    
                    scroll_info_denom = max_scroll
                    if scroll_info_denom == 0: scroll_info_denom = 1
                    
                    scroll_pct = self.shop_scroll_y / scroll_info_denom
                    scroll_bar_y = list_rect.y + scroll_pct * (list_height - scroll_bar_height)
                    
                    if self.slider_image:
                         sb_width = 60 # Requested width
                         sb_img = pygame.transform.scale(self.slider_image, (sb_width, int(scroll_bar_height)))
                         # Position: Right side of list_rect, centered on the boundary?
                         # Taking list_rect.right - (sb_width // 2) or similar
                         # Crafting was list_rect.right - 30 for 60px width.
                         screen.blit(sb_img, (list_rect.right - (sb_width // 2 + 10), scroll_bar_y))
                    else:
                         pygame.draw.rect(screen, GRAY, (list_rect.right - 10, scroll_bar_y, 8, scroll_bar_height))
                        
                # Draw Selected Item Details
                if self.selected_shop_item:
                    # Draw Action Button or Lock Message
                    if self.shop_tab == "buy":
                        req_rank = self.shop_system.get_required_rank(self.selected_shop_item)
                        if self.game.player.rank >= req_rank:
                            self.btn_shop_action.draw(screen)
                        else:
                            lock_text = self.font.render(f"Unlocked at Rank {req_rank}", True, RED)
                            screen.blit(lock_text, (rect.centerx - lock_text.get_width()//2, 450)) # Adjust Y as needed
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
                        # Match selected item to button index via inventory keys
                        current_inv_items = list(self.game.player.inventory.keys())
                        if self.selected_shop_item in current_inv_items:
                            try:
                                index = current_inv_items.index(self.selected_shop_item)
                                if 0 <= index < len(self.shop_sell_buttons):
                                    target_btn = self.shop_sell_buttons[index]
                            except ValueError:
                                pass 
                    
                    if target_btn:
                        if self.research_highlight_image:
                             # Use research highlight since it is 200px wide, same as shop buttons
                             screen.blit(self.research_highlight_image, target_btn.rect)
                        else:
                             pygame.draw.rect(screen, YELLOW, target_btn.rect, 2)
                
                # Draw Close Button
                self.btn_close_shop.draw(screen)
            except Exception as e:
                print(f"Error drawing Shop UI: {e}")

        # Research UI
        if self.show_research and hasattr(self, 'research_ui_screen_rect'):
            rect = self.research_ui_screen_rect
            # Background
            self.draw_ui_background(screen, rect)
            
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
                        if self.research_highlight_image:
                             screen.blit(self.research_highlight_image, btn.rect)
                        else:
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
            
            # Background
            self.draw_ui_background(screen, window_rect)
            
            header = self.font.render("Inventory", True, WHITE)
            screen.blit(header, (window_rect.centerx - header.get_width()//2, window_rect.y + 10))
            
            # Draw Grid
            # Draw Grid
            inv_start_x = window_rect.x + 20
            inv_start_y = window_rect.y + 50
            grid_cols = 5
            
            # Layout Constants
            grid_pitch = 50       # Distance between slot centers (was 40+10)
            box_size = 46         # Visual size of the slot background (Target 46px)
            item_size = 32        # Fixed size for items (to fit inside border)
            
            # Recalculate window size to fit grid
            content_width = grid_cols * grid_pitch + 40 
            content_height = 4 * grid_pitch + 100 
            
            if content_width > window_width:
                 window_width = content_width
                 window_rect.width = window_width
                 window_rect.x = (SCREEN_WIDTH - window_width) // 2
                 inv_start_x = window_rect.x + 20 # Re-align start x
                 
            if content_height > window_height:
                 window_height = content_height
                 window_rect.height = window_height
                 window_rect.y = (SCREEN_HEIGHT - window_height) // 2
                 inv_start_y = window_rect.y + 50 # Re-align start y
            
            # Inventory Slots
            items = list(self.game.player.inventory.items())
            for i in range(20): # 5x4 grid
                col = i % grid_cols
                row = i // grid_cols
                
                # Calculate Center of Slot based on Pitch
                center_x = inv_start_x + col * grid_pitch + grid_pitch // 2
                center_y = inv_start_y + row * grid_pitch + grid_pitch // 2
                
                # Calculate Top-Left for Box (Centered)
                box_x = center_x - box_size // 2
                box_y = center_y - box_size // 2
                rect = pygame.Rect(box_x, box_y, box_size, box_size)
                
                if self.toolbar_box_image:
                     # Scale box to visual size (46x46)
                     box_img = pygame.transform.scale(self.toolbar_box_image, (box_size, box_size))
                     screen.blit(box_img, (box_x, box_y))
                else:
                     pygame.draw.rect(screen, DARK_GREEN, rect)
                     pygame.draw.rect(screen, WHITE, rect, 1)
                
                if i < len(items):
                    item_name, count = items[i]
                    
                    # Draw Item Icon (Centered, Fixed Size)
                    item_x = center_x - item_size // 2
                    item_y = center_y - item_size // 2
                    
                    # Draw Sprite
                    icon = self.get_item_image(item_name)
                    # Center it
                    icon_rect = icon.get_rect(center=(center_x, center_y))
                    screen.blit(icon, icon_rect)
                    
                    # Draw Count (Bottom Right of item area)
                    count_text = self.font.render(str(count), True, WHITE)
                    screen.blit(count_text, (item_x + 2, item_y + 2))
                    
            # Dragging Item
            if self.dragging_item:
                mouse_pos = pygame.mouse.get_pos()
                pygame.draw.circle(screen, YELLOW, mouse_pos, 10) # Cursor indicator

            # Draw Close Button
            self.btn_close_inventory.draw(screen)

        # Persistent Toolbar (Screen Space - Bottom Center)
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
                # Use pre-loaded small font if available
                if not hasattr(self, 'small_font'):
                    self.small_font = pygame.font.SysFont(None, 12)
                name_surf = self.small_font.render(name[:3], True, WHITE)
                screen.blit(name_surf, (x+2, toolbar_y + TOOLBAR_SLOT_SIZE - 12))

            # Highlight selected (Drawn ON TOP of item)
            if i == self.game.player.selected_slot:
                if self.highlight_image:
                    # Draw aligned with box (Scale highlight to match)
                    # Highlight is usually slightly larger
                    highlight_size = int(TOOLBAR_SLOT_SIZE * 1.2)
                    offset = (highlight_size - TOOLBAR_SLOT_SIZE) // 2
                    scaled_highlight = pygame.transform.scale(self.highlight_image, (highlight_size, highlight_size))
                    screen.blit(scaled_highlight, (x - offset, toolbar_y - offset))
                else:
                    try:
                         # Fallback
                        highlight_rect = rect.inflate(4, 4)
                        pygame.draw.rect(screen, YELLOW, highlight_rect, 2)
                    except Exception as e:
                        print(f"Error drawing highlight: {e}")

        # Draw Player Coordinates (Top-Left)
        # Draw Player Coordinates (Top-Left)
        # player_pos_text = self.font.render(f"Pos: ({self.game.player.rect.x}, {self.game.player.rect.y})", True, WHITE)
        # screen.blit(player_pos_text, (10, 10))
