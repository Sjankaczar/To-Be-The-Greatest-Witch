class CraftingSystem:
    def __init__(self):
        self.recipes = {
            "Health Potion": {"Red Herb": 2, "Water": 1},
            "Mana Potion": {"Blue Herb": 2, "Water": 1}
        }

    def craft(self, inventory, potion_name):
        if potion_name not in self.recipes:
            print("Unknown recipe")
            return False
        
        ingredients = self.recipes[potion_name]
        
        # Check if player has ingredients
        for item, count in ingredients.items():
            if inventory.get(item, 0) < count:
                print(f"Not enough {item}")
                return False
        
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
