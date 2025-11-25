class CraftingSystem:
    def __init__(self):
        # Recipe format: {Ingredient: Count}, CraftTime (seconds)
        self.recipes = {
            "Health Potion": ({"Red Herb": 2, "Water": 1}, 3),
            "Mana Potion": ({"Blue Herb": 2, "Water": 1}, 3),
            "Invisibility Potion": ({"Blue Herb": 3, "Water": 1}, 5),
            "Speed Potion": ({"Red Herb": 3, "Water": 1}, 5)
        }

    def can_craft(self, inventory, potion_name):
        if potion_name not in self.recipes:
            return False
        
        ingredients, _ = self.recipes[potion_name]
        for item, count in ingredients.items():
            if inventory.get(item, 0) < count:
                return False
        return True

    def craft(self, inventory, potion_name):
        if not self.can_craft(inventory, potion_name):
            return False
        
        ingredients, _ = self.recipes[potion_name]
        
        # Consume ingredients
        for item, count in ingredients.items():
            inventory[item] -= count
            if inventory[item] == 0:
                del inventory[item]
        
        # Add potion
        if potion_name in inventory:
            inventory[potion_name] += 1
        else:
            inventory[potion_name] = 1
            
        print(f"Crafted {potion_name}!")
        return True
