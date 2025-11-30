
# Update Log

## [Initial Development]
- Basic scaffolding implemented.
- Player movement (WASD) and collision.
- Infinite map system.
- Inventory and Item collection.
- Basic Shop and Crafting systems (Key-based).
- Visual improvements (Entity names, colors).

## [Update 1]
- **Teleport Reset**: Player position resets to (0,0) when entering Exploration.
- **Mouse UI**: Home menu now uses mouse interactions.
- **Crafting UI**: Detailed view with ingredients, inventory, and "Craft" button.
- **New Potions**: Added Invisibility and Speed potions.
- **Crafting Timer**: Added progress bar for crafting.
- **Teleport Cooldown**: Added 10s cooldown for switching to Exploration.
- **Inventory UI**: Added "Inventory" button in Home to toggle a grid-based inventory window.
- **Drag-and-Drop**: Players can now drag items from the inventory to the toolbar in the Home screen.

## [Experimental]
- **Home State Refinement**:
    - **Camera Follow**: Camera now follows the player in the Home area.
    - **Forest Border**: Added a dark green border around the Home area.
    - **World-Space UI**: Research and Crafting UIs are now anchored to buildings and do not follow the camera.
    - **Fluent Movement**: Player movement in Home is now smoother and consistent with Exploration.
    - **Diagonal Movement**: Player can now move diagonally (W+A, W+D, etc.).
- **Farming & Research Expansion**:
    - **Farming System**: Till soil with a Hoe, plant Herbs (requires Research), water crops, and harvest them.
    - **Forest Fairies**: Rare creatures in Exploration that boost research speed when caught.
    - **Shop Expansion**: Now sells Farming Tools (Hoe, Watering Can) and buys Potions.
    - **Research**: Added "Herbology" and "Rare Herbs" topics to unlock planting.
- **Inventory Improvements**:
    - **Centered UI**: Inventory window is now centered on the screen.
    - **Persistent Toolbar**: Toolbar is now always visible at the bottom of the screen in Home.
    - **Toggle Key**: Press 'E' to toggle Inventory.
    - **Interaction**: Inventory button is clickable at any time.
- **UI UX**:
    - **Close Buttons**: Added "X" buttons to close Research and Crafting windows.
    - **Simultaneous Action**: Player can move while UIs are open.
- **Crafting Station Expansion**:
    - **Tabs**: Added tabs for "Potions", "Seeds", and "Golems" in the Crafting Station.
    - **Seed Crafting**: Players can now craft Seeds using Herbs and Gold.
    - **Gold Cost**: Crafting recipes can now require Gold.
    - **Golem Tab**: Added a placeholder tab for future Golem crafting.

- **New Items**:
    - **Bug Net**: Available in the Shop. Used to catch Insects in the Exploration area.
    - **Axe**: Available in the Shop. Used to create new Safe Zone tiles in the Home area (Durability: 3). Each use converts a 32x32 Forest tile to Safe Zone.
- **Exploration**:
    - Added **Insects**: Slow-moving creatures that can be caught with a Bug Net.
