import pygame
import os
from src.states.game_state import GameState
from src.config import *
from pytmx.util_pygame import load_pygame
from src.utils.camera import Camera
from src.assets import *
from src.utils.ui import Button
from src.systems.crafting import CraftingSystem
from src.systems.research import ResearchSystem

class RoomState(GameState):
    def __init__(self, game):
        super().__init__(game)
        
        # Load Map
        self.tmx_data = load_pygame(MAP_ROOM)
        self.tile_w = self.tmx_data.tilewidth
        self.tile_h = self.tmx_data.tileheight
        
        self.map_width = self.tmx_data.width * self.tile_w
        self.map_height = self.tmx_data.height * self.tile_h
        
        self.virtual_width = int(SCREEN_WIDTH / CAMERA_ZOOM)
        self.virtual_height = int(SCREEN_HEIGHT / CAMERA_ZOOM)
        self.display_surface = pygame.Surface((self.virtual_width, self.virtual_height))
        
        self.camera = Camera(self.map_width, self.map_height, self.virtual_width, self.virtual_height)

        self.start_pos = (135, 125)
        
        # Invisible Barriers
        self.barriers = [
            pygame.Rect(43, 198, 202, 1),
            pygame.Rect(43, 38, 202, 1),
            pygame.Rect(275, 60, 1, 202),
            pygame.Rect(10, 60, 1, 202),
            # pygame.Rect(133, 168, 16, 16)
        ]
        
        # --- UI ASSETS ---
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 36)
        
        self.button_image = None
        self.button_pressed_image = None
        self.quit_icon_image = None
        self.slider_image = None
        self.crafting_highlight_image = None
        self.research_highlight_image = None
        self.template_box_image = None

        if os.path.exists(IMG_BUTTON):
            self.button_image = pygame.image.load(IMG_BUTTON).convert_alpha()
        if os.path.exists(IMG_BUTTON_PRESSED):
            self.button_pressed_image = pygame.image.load(IMG_BUTTON_PRESSED).convert_alpha()
        if os.path.exists(IMG_QUIT_ICON):
            self.quit_icon_image = pygame.image.load(IMG_QUIT_ICON).convert_alpha()
        if os.path.exists(IMG_SLIDER):
             self.slider_image = pygame.image.load(IMG_SLIDER).convert_alpha()
        if os.path.exists(IMG_HIGHLIGHT_SLOT):
             raw = pygame.image.load(IMG_HIGHLIGHT_SLOT).convert_alpha()
             self.crafting_highlight_image = self.create_3_slice_highlight(raw, 300, 30)
             self.research_highlight_image = self.create_3_slice_highlight(raw, 300, 30)
             self.tab_highlight_image = self.create_3_slice_highlight(raw, 80, 30)
        if os.path.exists(IMG_TEMPLATE_BOX):
             self.template_box_image = pygame.image.load(IMG_TEMPLATE_BOX).convert_alpha()
        
        # Load Progress Bar Images
        self.bar_bg_image = None
        self.bar_fill_image = None
        if os.path.exists(IMG_VALUE_BAR):
             self.bar_bg_image = pygame.image.load(IMG_VALUE_BAR).convert_alpha()
        if os.path.exists(IMG_VALUE_BLUE):
             self.bar_fill_image = pygame.image.load(IMG_VALUE_BLUE).convert_alpha()

        # --- CHOICE UI ---
        self.show_choice_ui = False
        # Define Rect for background (Even Larger)
        self.choice_ui_rect = pygame.Rect(0, 0, 400, 100)
        self.choice_ui_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        
        # Center Buttons vertically in the middle (since no title)
        btn_y = self.choice_ui_rect.centery - 20
        self.btn_choice_craft = Button(self.choice_ui_rect.centerx - 117, btn_y, 100, 40, "Craft", self.font, (100, 100, 100), image=self.button_image)
        self.btn_choice_research = Button(self.choice_ui_rect.centerx + 3, btn_y, 100, 40, "Research", self.font, (100, 100, 100), image=self.button_image)
        
        # Close Button moved slightly left (was -40, now -55)
        self.btn_close_ui = Button(self.choice_ui_rect.right - 105, self.choice_ui_rect.top , 30, 30, "X", self.font, RED, image=self.quit_icon_image)

        # --- CRAFTING UI ---
        # Height 450 to fit details
        self.crafting_ui_screen_rect = pygame.Rect((SCREEN_WIDTH - 500)//2, (SCREEN_HEIGHT - 450)//2, 500, 450)
        self.show_crafting_ui = False
        self.crafting_tab = "Potions"
        self.selected_recipe = None
        self.crafting_timer = 0
        self.crafting_duration = 0
        self.crafting_target = None
        self.crafting_target_category = None
        self.crafting_scroll_y = 0
        
        self.recipe_buttons = []
        
        ui_x = self.crafting_ui_screen_rect.x
        ui_y = self.crafting_ui_screen_rect.y
        
        # Centre Align 2 Tabs (Total width ~400 internal, so center is ~200)
        # 112 was potion start. With 2 tabs, let's center them.
        self.btn_tab_potions = Button(ui_x + 150, ui_y + 75, 80, 30, "Potions", self.font, color=(150, 150, 150), image=self.button_image)
        self.btn_tab_seeds = Button(ui_x + 250, ui_y + 75, 80, 30, "Seeds", self.font, color=(150, 150, 150), image=self.button_image)
        
        self.btn_close_crafting = Button(self.crafting_ui_screen_rect.right - 125, self.crafting_ui_screen_rect.y + 30, 30, 30, "X", self.font, RED, image=self.quit_icon_image)
        self.btn_craft_action = Button(0, 0, 100, 30, "Craft", self.font, (20, 100, 20), image=self.button_image)

        # Init Crafting System
        if not hasattr(self.game, 'crafting_system'):
            self.game.crafting_system = CraftingSystem()
        self.crafting_system = self.game.crafting_system
        
        self.update_recipe_list()

        # --- RESEARCH UI ---
        self.research_ui_rect = pygame.Rect((SCREEN_WIDTH - 500)//2, (SCREEN_HEIGHT - 350)//2, 500, 350)
        self.show_research_ui = False
        self.selected_research = None
        self.research_buttons = []
        
        self.btn_start_research = Button(0, 0, 120, 30, "Start", self.font, (100, 100, 255), image=self.button_image)
        self.btn_close_research = Button(self.research_ui_rect.right - 123, self.research_ui_rect.y + 21, 30, 30, "X", self.font, RED, image=self.quit_icon_image)

        self.research_system = self.game.research_system
        
        self.update_research_list()

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
        
    def enter(self):
        print("Entering Room State")
        self.game.player.rect.topleft = self.start_pos
        self.show_choice_ui = False
        self.show_crafting_ui = False
        self.show_research_ui = False

    def update_research_list(self):
        self.research_buttons = []
        topics = self.research_system.topics
        start_y = self.research_ui_rect.y + 65
        
        for i, topic in enumerate(topics.keys()):
             # Center buttons: Panel width 500. Button width 300.
             btn_w = 300
             btn_x = self.research_ui_rect.centerx - (btn_w // 2) - 10
             btn = Button(btn_x, start_y + i * 40, btn_w, 30, topic, self.font, color=(128, 128, 128), image=self.button_image)
             self.research_buttons.append(btn)

    def update_recipe_list(self):
        self.recipe_buttons = []
        recipes = []
        if self.crafting_tab == "Potions":
            recipes = ["Health Potion", "Mana Potion", "Speed Potion", "Invisibility Potion", "Intelligence Potion", "Rank Up Potion"]
        elif self.crafting_tab == "Seeds":
            recipes = ["Red Seed", "Blue Seed", "Rare Seed"]

            
        start_y = self.crafting_ui_screen_rect.y + 115
        for i, r in enumerate(recipes):
            # Use 300 width for buttons
            btn = Button(self.crafting_ui_screen_rect.x + 20, start_y + i * 35, 300, 30, r, self.font, color=(128, 128, 128), image=self.button_image)
            self.recipe_buttons.append(btn)
            
    def handle_events(self, events):
        for event in events:
            # UI Interaction
            if self.show_choice_ui: 
                # Choice UI
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.show_choice_ui = False
                
                # Check buttons
                if self.btn_choice_craft.handle_event(event):
                    self.show_choice_ui = False
                    self.show_crafting_ui = True
                    self.update_recipe_list()
                if self.btn_choice_research.handle_event(event):
                    self.show_choice_ui = False
                    self.show_research_ui = True
                    self.update_research_list()
                if self.btn_close_ui.handle_event(event):
                    self.show_choice_ui = False
                    
            elif self.show_crafting_ui:
                # Crafting UI
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                     self.show_crafting_ui = False
                     
                if self.btn_close_crafting.handle_event(event):
                     self.show_crafting_ui = False
                     
                if self.btn_tab_potions.handle_event(event):
                     self.crafting_tab = "Potions"
                     self.selected_recipe = None
                     self.update_recipe_list()
                if self.btn_tab_seeds.handle_event(event):
                     self.crafting_tab = "Seeds"
                     self.selected_recipe = None
                     self.update_recipe_list()

                     
                # Scroll Logic (Mouse Wheel)
                if event.type == pygame.MOUSEWHEEL:
                    list_height = 175
                    total_height = len(self.recipe_buttons) * 35
                    max_scroll = max(0, total_height - list_height)
                    self.crafting_scroll_y = max(0, min(self.crafting_scroll_y - event.y * 20, max_scroll))
                     
                # Recipe Selection (Click on List)
                list_rect = pygame.Rect(self.crafting_ui_screen_rect.x + 20, self.crafting_ui_screen_rect.y + 115, self.crafting_ui_screen_rect.width - 40, 175)
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                     if list_rect.collidepoint(event.pos):
                          # Calculate index
                          rel_y = event.pos[1] - list_rect.y + self.crafting_scroll_y
                          idx = rel_y // 35
                          if 0 <= idx < len(self.recipe_buttons):
                               self.selected_recipe = self.recipe_buttons[idx].text
                               
                # Craft Action
                if self.selected_recipe and self.btn_craft_action.handle_event(event):
                     # Start Crafting
                     if self.crafting_timer == 0:
                          if self.crafting_system.can_craft(self.game.player, self.crafting_tab, self.selected_recipe):
                               _, duration = self.crafting_system.get_recipe(self.crafting_tab, self.selected_recipe)
                               self.crafting_duration = duration * 60
                               self.crafting_timer = self.crafting_duration
                               self.crafting_target = self.selected_recipe
                               self.crafting_target_category = self.crafting_tab
                               print(f"Started crafting {self.selected_recipe}")
                          else:
                               print("Cannot craft: Missing ingredients or Gold.")

            elif self.show_research_ui:
                # Research UI
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                     self.show_research_ui = False
                     
                if self.btn_close_research.handle_event(event):
                     self.show_research_ui = False
                     
                for i, btn in enumerate(self.research_buttons):
                     if btn.handle_event(event):
                          topics = list(self.research_system.topics.keys())
                          if i < len(topics):
                               self.selected_research = topics[i]
                               
                if self.btn_start_research.handle_event(event):
                     if self.selected_research and not self.research_system.current_research:
                          if self.research_system.can_research(self.selected_research, self.game.player.intelligence):
                               self.research_system.start_research(self.selected_research)
                               print(f"Started research on {self.selected_research}")

            else:
                 # Normal Gameplay
                 if event.type == pygame.KEYDOWN:
                     if event.key == pygame.K_f:
                          # Check interaction (simplified check for table area)
                          interact_rect = pygame.Rect(58, 54, 15, 25)
                          if self.game.player.rect.colliderect(interact_rect):
                               self.show_choice_ui = True
                               self.game.player.stop_walking_sound()
                
    def update(self):
        # Always update research system
        self.research_system.update(self.game.player.intelligence)
        
        if self.show_choice_ui or self.show_crafting_ui or self.show_research_ui:
             pass 
        else:
            prev_rect = self.game.player.rect.copy()
            self.game.player.update()
            
            # Barrier Collision
            for barrier in self.barriers:
                if self.game.player.rect.colliderect(barrier):
                    self.game.player.rect = prev_rect
                    
            # Exit Trigger (126, 193)
            trigger_rect = pygame.Rect(126, 193, 20, 1)
            if self.game.player.rect.colliderect(trigger_rect):
                print("Exiting Room...")
                self.game.states["home"].enter()
                self.game.change_state("home")
            
            self.camera.update(self.game.player)
            
            self.game.player.rect.x = max(0, min(self.game.player.rect.x, self.map_width - self.game.player.rect.width))
            self.game.player.rect.y = max(0, min(self.game.player.rect.y, self.map_height - self.game.player.rect.height))
            
            pygame.display.set_caption(f"Room - Player Pos: {self.game.player.rect.topleft} | Rank: {self.game.player.rank}")

        # Update Crafting Timer
        if self.crafting_timer > 0:
             self.crafting_timer -= 1
             if self.crafting_timer <= 0:
                  if self.crafting_system.craft(self.game.player, self.crafting_target_category, self.crafting_target):
                       print(f"Crafted {self.crafting_target}!")
                  self.crafting_target = None

    def draw_ui_background(self, screen, rect):
        if self.template_box_image:
             scaled = pygame.transform.scale(self.template_box_image, (rect.width, rect.height))
             screen.blit(scaled, (rect.x - 5, rect.y - 5))
        else:
             pygame.draw.rect(screen, (50, 50, 50), rect)
             pygame.draw.rect(screen, WHITE, rect, 2)



    def draw(self, screen):
        self.display_surface.fill(BLACK)
        
        # Draw Map
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        target_x = x * self.tile_w + self.camera.camera.x
                        target_y = y * self.tile_h + self.camera.camera.y
                        self.display_surface.blit(tile, (target_x, target_y))
                        
        # Draw Player
        screen_pos = self.camera.apply(self.game.player)
        self.display_surface.blit(self.game.player.image, screen_pos)
        
        # Scale to Screen
        scaled_surf = pygame.transform.scale(self.display_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_surf, (0, 0))
        
        # --- UI LAYER ---
        if self.show_choice_ui:
             overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
             overlay.fill((0, 0, 0, 150))
             screen.blit(overlay, (0,0))
             
             # Draw Background Box
             self.draw_ui_background(screen, self.choice_ui_rect)
             
             self.btn_choice_craft.draw(screen)
             self.btn_choice_research.draw(screen)
             self.btn_close_ui.draw(screen)
             
        if self.show_crafting_ui:
            # CRAFTING STATION UI
            # Draw Background
            self.draw_ui_background(screen, self.crafting_ui_screen_rect)
            
            # Title
            title_surf = self.title_font.render("Crafting Station", True, BLACK)
            screen.blit(title_surf, (self.crafting_ui_screen_rect.centerx - (title_surf.get_width() // 2) - 5, self.crafting_ui_screen_rect.y + 40))
            
            # Draw Tabs
            self.btn_tab_potions.draw(screen)
            self.btn_tab_seeds.draw(screen)
            
            # Highlight selected tab
            target_rect = None
            if self.crafting_tab == "Potions":
                target_rect = self.btn_tab_potions.rect
            elif self.crafting_tab == "Seeds":
                target_rect = self.btn_tab_seeds.rect

                
            if target_rect:
                if hasattr(self, 'tab_highlight_image') and self.tab_highlight_image:
                     screen.blit(self.tab_highlight_image, target_rect)
                else:
                     pygame.draw.rect(screen, YELLOW, target_rect, 2)

            # Draw List Area (No background)
            list_height = 175
            list_rect = pygame.Rect(self.crafting_ui_screen_rect.x + 20, self.crafting_ui_screen_rect.y + 115, self.crafting_ui_screen_rect.width - 40, list_height)
            # Clip drawing
            old_clip = screen.get_clip()
            screen.set_clip(list_rect)

            # Draw Recipe Buttons
            # Claculate scroll
            total_height = len(self.recipe_buttons) * 35
            max_scroll = max(0, total_height - list_rect.height)
            self.crafting_scroll_y = max(0, min(self.crafting_scroll_y, max_scroll))
            
            start_y = list_rect.y - self.crafting_scroll_y
            
            for i, btn in enumerate(self.recipe_buttons):
                # Center buttons adjusted right (+10 offset)
                btn.rect.x = list_rect.centerx - (btn.rect.width // 2) - 10
                btn.rect.y = start_y + i * 35
                btn.rect.height = 30
                
                if list_rect.colliderect(btn.rect):
                    btn.draw(screen)
                    # Highlight Selected - Use CLEAN rect border as requested for "Rapi"
                    if self.selected_recipe == btn.text:
                        if self.crafting_highlight_image:
                            screen.blit(self.crafting_highlight_image, btn.rect)
                        else:
                            pygame.draw.rect(screen, YELLOW, btn.rect, 2)
                    
            screen.set_clip(old_clip)
            
            # Scrollbar
            if max_scroll > 0:
                scroll_bar_height = list_rect.height * (list_rect.height / total_height)
                scroll_bar_y = list_rect.y + (self.crafting_scroll_y / max_scroll) * (list_rect.height - scroll_bar_height)
                if self.slider_image:
                    sb_img = pygame.transform.scale(self.slider_image, (40, max(20, int(scroll_bar_height))))
                    screen.blit(sb_img, (list_rect.right - 107, scroll_bar_y))
                else:
                    pygame.draw.rect(screen, GRAY, (list_rect.right - 10, scroll_bar_y, 8, scroll_bar_height))

            # Details
            if self.selected_recipe:
                details_y_start = list_rect.bottom + 20
                
                # Retrieve recipe info using system
                recipe = self.crafting_system.get_recipe(self.crafting_tab, self.selected_recipe)
                if recipe:
                    ingredients, time_val = recipe
                    name_text = self.font.render(f"Selected: {self.selected_recipe}", True, YELLOW)
                    screen.blit(name_text, (self.crafting_ui_screen_rect.x + 100, details_y_start-17))
                    
                    ing_y = details_y_start + 30
                    for item, count in ingredients.items():
                        if item == "Gold":
                            has = self.game.player.gold
                        else:
                            has = self.game.player.inventory.get(item, 0)
                        
                        color = GREEN if has >= count else RED
                        ing_text = self.font.render(f"{item}: {has}/{count}", True, color)
                        screen.blit(ing_text, (self.crafting_ui_screen_rect.x + 100, ing_y - 25))
                        ing_y += 18

                    # Draw Craft Button or Lock logic
                    req_rank = self.crafting_system.get_required_rank(self.selected_recipe)
                    if self.game.player.rank >= req_rank:
                        # Only show Craft button if NO active crafting matching this recipe (or generally not crafting)
                        # User wants button hidden if bar is visible. Bar is visible if crafting_timer > 0.
                        # Wait, user said "tombol craft hilang... muncul kembali apabila bar selesai".
                        # So if ANY crafting is happening? Or just check timer?
                        # Simplest: if crafting_timer == 0, show button.
                        if self.crafting_timer == 0:
                            self.btn_craft_action.rect.topleft = (self.crafting_ui_screen_rect.centerx - 50, self.crafting_ui_screen_rect.bottom - 90)
                            self.btn_craft_action.draw(screen)
                    else:
                        lock_text = self.font.render(f"Unlocked at Rank {req_rank}", True, RED)
                        screen.blit(lock_text, (self.crafting_ui_screen_rect.centerx - lock_text.get_width()//2, self.crafting_ui_screen_rect.bottom - 80))
                    
                    # Draw Progress Bar
                    if self.crafting_timer > 0 and self.crafting_target == self.selected_recipe:
                        progress = 1 - (self.crafting_timer / self.crafting_duration)
                        # Reduce width to 200 (centered).
                        bar_w = 200
                        # Shift Left 25px
                        bar_x = self.crafting_ui_screen_rect.centerx - (bar_w // 2) - 7
                        # Position it where button was (bottom - 90) or slightly lower. Button is 30px high.
                        # Button y = bottom - 90.
                        bar_h = 24
                        bar_rect = pygame.Rect(bar_x, self.crafting_ui_screen_rect.bottom - 85, bar_w, bar_h)
                        
                        if getattr(self, 'bar_bg_image', None) and getattr(self, 'bar_fill_image', None):
                            # Draw Background
                            bg_scaled = pygame.transform.scale(self.bar_bg_image, (bar_w, bar_h))
                            screen.blit(bg_scaled, bar_rect)
                            
                            # Calculate Fill Dimensions based on original asset ratio
                            # ValueBar: 128x16, ValueBlue: 120x8
                            # Margin X = (128-120)/2 = 4 (relative to 128) -> 4/128 = 0.03125
                            # Margin Y = (16-8)/2 = 4 (relative to 16) -> 4/16 = 0.25
                            
                            ratio_w = 120 / 128
                            ratio_h = 8 / 16
                            
                            fill_max_w = int(bar_w * ratio_w)
                            fill_h = int(bar_h * ratio_h)
                            
                            offset_x = (bar_w - fill_max_w) // 2
                            offset_y = (bar_h - fill_h) // 2
                            
                            current_fill_w = int(fill_max_w * progress)
                            
                            if current_fill_w > 0:
                                fill_scaled = pygame.transform.scale(self.bar_fill_image, (current_fill_w, fill_h))
                                screen.blit(fill_scaled, (bar_rect.x + offset_x, bar_rect.y + offset_y))
                        else:
                            pygame.draw.rect(screen, BLACK, bar_rect)
                            pygame.draw.rect(screen, BLUE, (bar_rect.x, bar_rect.y, bar_rect.width * progress, bar_h))
                            pygame.draw.rect(screen, WHITE, bar_rect, 2)
            
            self.btn_close_crafting.draw(screen)

        if self.show_research_ui:
            rect = self.research_ui_rect
            self.draw_ui_background(screen, rect)
             
            title = self.title_font.render("Research Center", True, WHITE)
            screen.blit(title, (rect.centerx - title.get_width()//2, rect.y + 30))
             
            # Research Buttons
            for i, btn in enumerate(self.research_buttons):
                btn.draw(screen)
                topic_keys = list(self.research_system.topics.keys())
                if i < len(topic_keys):
                    topic = topic_keys[i]
                    if topic == self.selected_research:
                        if self.research_highlight_image:
                            screen.blit(self.research_highlight_image, btn.rect)
                        else:
                            pygame.draw.rect(screen, YELLOW, btn.rect, 2)
                       
                    # Status - Only 'Done' marks specific buttons
                    if topic in self.research_system.completed_research:
                        status_text = self.font.render("Done", True, GREEN)
                        screen.blit(status_text, (btn.rect.right + 10, btn.rect.centery - 10))
                        
            if self.research_system.current_research:
                 res_text = self.font.render(f"Researching: {self.research_system.current_research}...", True, YELLOW)
                 screen.blit(res_text, (self.research_ui_rect.centerx - res_text.get_width()//2, self.research_ui_rect.bottom - 110))
                 
                 # Research Progress Bar (Similar to Crafting)
                 progress = self.research_system.get_progress()
                 bar_w = 200
                 bar_h = 24
                 bar_x = self.research_ui_rect.centerx - (bar_w // 2)
                 bar_y = self.research_ui_rect.bottom - 90
                 bar_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
                 
                 if getattr(self, 'bar_bg_image', None) and getattr(self, 'bar_fill_image', None):
                     bg_scaled = pygame.transform.scale(self.bar_bg_image, (bar_w, bar_h))
                     screen.blit(bg_scaled, bar_rect)
                     
                     # Ratio Calcs
                     ratio_w = 120 / 128
                     ratio_h = 8 / 16
                     fill_max_w = int(bar_w * ratio_w)
                     fill_h = int(bar_h * ratio_h)
                     offset_x = (bar_w - fill_max_w) // 2
                     offset_y = (bar_h - fill_h) // 2
                     
                     current_fill_w = int(fill_max_w * progress)
                     if current_fill_w > 0:
                         fill_scaled = pygame.transform.scale(self.bar_fill_image, (current_fill_w, fill_h))
                         screen.blit(fill_scaled, (bar_rect.x + offset_x, bar_rect.y + offset_y))
                 else:
                     pygame.draw.rect(screen, BLACK, bar_rect)
                     pygame.draw.rect(screen, BLUE, (bar_rect.x, bar_rect.y, bar_rect.width * progress, bar_h))
                     pygame.draw.rect(screen, WHITE, bar_rect, 2)
            else:        
                # Start Button (Only show if NOT researching)
                self.btn_start_research.rect.topleft = (rect.centerx - 60, rect.bottom - 80)
                self.btn_start_research.draw(screen)
            self.btn_close_research.draw(screen)
