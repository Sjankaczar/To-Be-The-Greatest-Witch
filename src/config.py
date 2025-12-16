import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_TITLE = "To Be The Greatest Witch"
FPS = 30
SCREEN_HEIGHT = 600
TILE_SIZE = 32
CAMERA_ZOOM = 2.7 

# Game Settings
SHOW_OPENING_SCREEN = True

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (100, 100, 100)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144) # Light Green
BROWN = (139, 69, 19) # Farmland color
DARK_GREEN_BG = (20, 50, 20) # Very dark green for exploration

# Game Settings
# FPS = 30 # Removed redundant
# ZOOM_LEVEL = 2.0 # Removed redundant
TELEPORT_COOLDOWN = 5 # Seconds
LANTERN_RADIUS = 75
LANTERN_MAX_ALPHA = 200

# Shop Prices
PRICES = {
    "Health Potion": 10,
    "Mana Potion": 15,
    "Speed Potion": 20,
    "Invisibility Potion": 30,
    "Intelligence Potion": 50,
    "Rank Up Potion": 100,
    "Hoe": 50,
    "Watering Can": 30,
    "Water": 1,
    "Red Herb": 2,
    "Blue Herb": 2,
    "Rare Herb": 10,
    "Bug Net": 100,
    "Axe": 150,
    "Beetle": 5
}

# Farming Settings
CROP_GROWTH_TIME = 600 # Frames (10 seconds)
FAIRY_SPAWN_CHANCE = 0.001 # 0.1% chance per frame
FAIRY_RESEARCH_BOOST = 0.1 # 10% speed boost per fairy
INSECT_SPAWN_CHANCE = 0.005 # 0.5% chance per frame
AXE_DURABILITY = 3
SAFE_ZONE_EXPANSION_AMOUNT = TILE_SIZE

# Golem Settings
GOLEM_SPEED = 2
GOLEM_MAX_ENERGY = 100
GOLEM_WATER_COST = 5
GOLEM_EXPAND_COST = 20
GOLEM_RECHARGE_RATE = 0.1

# Rank Unlocks
RANK_UNLOCKS = {
    1: {
        "features": ["Crafting", "Shop"],
        "recipes": ["Health Potion", "Mana Potion", "Intelligence Potion", "Rank Up Potion"],
        "shop": ["Health Potion", "Mana Potion", "Red Herb", "Blue Herb"] # Basic herbs sellable
    },
    2: {
        "features": ["Farming"],
        "recipes": ["Speed Potion", "Red Seed", "Blue Seed"],
        "shop": ["Speed Potion", "Hoe", "Watering Can", "Bug Net"]
    },
    3: {
        "features": ["Golems"],
        "recipes": ["Invisibility Potion", "Wood Golem"],
        "shop": ["Axe"]
    },
    4: {
        "features": ["Research", "Fairies"],
        "recipes": ["Rare Seed"], # Rare Seed requires research + Rank 4
        "shop": ["Intelligence Potion", "Rank Up Potion"] # Advanced potions in shop
    }
}

RANK_INTEL_CAPS = {
    1: 25,
    2: 50,
    3: 90
    # Rank 4+ has dynamic cap (equal to current)
}
