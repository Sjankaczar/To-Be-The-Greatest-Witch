class ShopSystem:
    def __init__(self):
        self.prices = {
            "Health Potion": 10,
            "Mana Potion": 15
        }
        self.lantern_upgrade_cost = 50

    def sell_item(self, inventory, item_name, gold):
        if item_name in inventory and inventory[item_name] > 0:
            if item_name in self.prices:
                inventory[item_name] -= 1
                if inventory[item_name] == 0:
                    del inventory[item_name]
                gold += self.prices[item_name]
                print(f"Sold {item_name} for {self.prices[item_name]} gold.")
                return gold
            else:
                print("This item cannot be sold.")
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
