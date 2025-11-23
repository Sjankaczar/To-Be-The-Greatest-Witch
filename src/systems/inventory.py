class InventorySystem:
    def __init__(self):
        pass

    def add_item(self, inventory, item_name):
        if item_name in inventory:
            inventory[item_name] += 1
        else:
            inventory[item_name] = 1
    
    def remove_item(self, inventory, item_name):
        if item_name in inventory and inventory[item_name] > 0:
            inventory[item_name] -= 1
            if inventory[item_name] == 0:
                del inventory[item_name]
            return True
        return False
