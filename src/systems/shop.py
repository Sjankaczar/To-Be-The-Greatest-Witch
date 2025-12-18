from src.config import PRICES, RANK_UNLOCKS

class ShopSystem:
    def __init__(self):
        self.lantern_upgrade_cost = 50

    def get_available_items(self, player_rank):
        # Deprecated for UI list, but useful if we want to filter for some reason.
        # Now we show all.
        return self.get_all_items()

    def get_all_items(self):
        all_items = []
        for r in RANK_UNLOCKS:
            all_items.extend(RANK_UNLOCKS[r].get("shop", []))
        return list(set(all_items)) # Unique items

    def get_required_rank(self, item_name):
        for rank, data in RANK_UNLOCKS.items():
            if item_name in data.get("shop", []):
                return rank
        return 1 # Default
        
    def buy_item(self, inventory, item_name, gold):
        if item_name in PRICES:
            price = PRICES[item_name]
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
