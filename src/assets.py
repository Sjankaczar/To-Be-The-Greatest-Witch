import os

# Base Directories
# Assuming this file is in src/assets.py, so we go up one level to src, then one more to project root
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
UI_DIR = os.path.join(PROJECT_ROOT, "UI The Greatest Witch")
MAPS_DIR = os.path.join(ASSETS_DIR, "maps")

# UI Images
IMG_HOTKEY_BOX = os.path.join(UI_DIR, "HotkeyBox.png")
IMG_STATS_BG = os.path.join(UI_DIR, "RectangleBox_96x96-1.png.png")
IMG_LETTER_PISKEL_4 = os.path.join(UI_DIR, "Letter Piskel 4.png")
IMG_NEW_PISKEL_7 = os.path.join(UI_DIR, "New Piskel 7.png")
IMG_HIGHLIGHT_SLOT = os.path.join(UI_DIR, "cutout-1765779993.png")
IMG_HOME_ICON = os.path.join(UI_DIR, "balikrumah.png")
IMG_TEMPLATE_BOX = os.path.join(UI_DIR, "template box.png")
IMG_QUIT_ICON = os.path.join(UI_DIR, "QuitIcon.png")
IMG_BUTTON = os.path.join(UI_DIR, "Button.png")
IMG_BUTTON = os.path.join(UI_DIR, "Button.png")
IMG_BUTTON_PRESSED = os.path.join(UI_DIR, "ButtonPressed.png")
IMG_SLIDER = os.path.join(UI_DIR, "slider.png")
IMG_VALUE_BAR = os.path.join(UI_DIR, "ValueBar_128x16.png")
IMG_VALUE_BLUE = os.path.join(UI_DIR, "ValueBlue_120x8.png")
IMG_PLAY_BTN = os.path.join(UI_DIR, "play button.png")
IMG_EXIT_BTN = os.path.join(UI_DIR, "exit button.png")
IMG_BUTTERFLY = os.path.join(UI_DIR, "butterfly.png")

# Maps
MAP_HOME = os.path.join(MAPS_DIR, "halaman.tmx")
MAP_ROOM = os.path.join(MAPS_DIR, "room.tmx")
MAP_FOREST = os.path.join(MAPS_DIR, "forest.tmx")

# Audio
AUDIO_DIR = os.path.join(ASSETS_DIR, "sounds")
AUDIO_BGM = os.path.join(AUDIO_DIR, "bgm1.mp3")

# Fonts (Aliases for clarity)
FONT_NUMBERS_PATH = IMG_LETTER_PISKEL_4
FONT_LETTERS_PATH = IMG_NEW_PISKEL_7
