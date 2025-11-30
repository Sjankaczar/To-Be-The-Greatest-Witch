from src.config import PRICES

class ShopSystem:
    def __init__(self):
        self.items = {
            "Health Potion": PRICES["Health Potion"],
            "Mana Potion": PRICES["Mana Potion"],
            "Speed Potion": PRICES["Speed Potion"],
            "Invisibility Potion": PRICES["Invisibility Potion"],
            "Intelligence Potion": PRICES["Intelligence Potion"],
            "Rank Up Potion": PRICES["Rank Up Potion"],
            "Hoe": PRICES["Hoe"],
            "Watering Can": PRICES["Watering Can"]
        }
        self.lantern_upgrade_cost = 50
        
    def buy_item(self, inventory, item_name, gold):
        if item_name in self.items:
            price = self.items[item_name]
            if gold >= price:
                gold -= price
                if item_name in inventory:
                    inventory[item_name] += 1
                else:
                    inventory[item_name] = 1
                print(f"Bought {item_name} for {price} Gold.")
                return gold
            else:
                print("Not enough gold.")
        return gold

    def sell_item(self, inventory, item_name, gold):
        # Generic sell logic
        if item_name in inventory:
            # Sell price is half of buy price, or defined
            price = PRICES.get(item_name, 0) // 2
            count = inventory[item_name]
            total_price = price * count
            
            gold += total_price
            del inventory[item_name]
            print(f"Sold {count} {item_name} for {total_price} Gold.")
            return gold
        return gold

    def buy_upgrade(self, lantern, gold):
        if gold >= self.lantern_upgrade_cost:
            gold -= self.lantern_upgrade_cost
            lantern.upgrade()
            self.lantern_upgrade_cost += 50 # Increase cost for next upgrade
            print("Lantern upgraded!")
            return gold
        else:
            print("Not enough gold.")
            return gold
