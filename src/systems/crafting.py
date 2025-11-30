class CraftingSystem:
    def __init__(self):
        # Categories
        self.recipes = {
            "Potions": {
                "Health Potion": ({"Red Herb": 2, "Water": 1}, 3),
                "Mana Potion": ({"Blue Herb": 2, "Water": 1}, 3),
                "Invisibility Potion": ({"Blue Herb": 3, "Water": 1}, 5),
                "Speed Potion": ({"Red Herb": 3, "Water": 1}, 5),
                "Intelligence Potion": ({"Blue Herb": 2, "Red Herb": 1}, 5),
                "Rank Up Potion": ({"Blue Herb": 5, "Red Herb": 5, "Water": 5}, 10)
            },
            "Seeds": {
                "Red Seed": ({"Red Herb": 1, "Gold": 10}, 2),
                "Blue Seed": ({"Blue Herb": 1, "Gold": 10}, 2),
                "Rare Seed": ({"Rare Herb": 1, "Gold": 50}, 5)
            },
            "Golems": {
                # Placeholder for now
                "Wood Golem": ({"Red Herb": 10, "Gold": 100}, 10) 
            }
        }

    def get_recipe(self, category, item_name):
        if category in self.recipes and item_name in self.recipes[category]:
            return self.recipes[category][item_name]
        return None

    def can_craft(self, player, category, item_name):
        recipe = self.get_recipe(category, item_name)
        if not recipe:
            return False
        
        ingredients, _ = recipe
        for item, count in ingredients.items():
            if item == "Gold":
                if player.gold < count:
                    return False
            else:
                if player.inventory.get(item, 0) < count:
                    return False
        return True

    def craft(self, player, category, item_name):
        if not self.can_craft(player, category, item_name):
            return False
        
        ingredients, _ = self.get_recipe(category, item_name)
        
        # Consume ingredients
        for item, count in ingredients.items():
            if item == "Gold":
                player.gold -= count
            else:
                player.inventory[item] -= count
                if player.inventory[item] == 0:
                    del player.inventory[item]
        
        # Add item
        # Seeds and Golems might need special handling if they are not just inventory items
        # For now, assume they are items
        if item_name in player.inventory:
            player.inventory[item_name] += 1
        else:
            player.inventory[item_name] = 1
            
        print(f"Crafted {item_name}!")
        return True
