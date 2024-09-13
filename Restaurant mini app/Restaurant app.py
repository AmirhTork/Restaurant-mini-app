import json
from datetime import datetime
import os
import sys


file_name = ['menu.json', 'adminInfo.json', 'appLog.json']


class Menu_handler:
    def __init__(self):
        self.menu = self.load_menu()
        self.categories_list = []
        for category in self.menu:
            self.categories_list.append(category)
            
    def load_menu(self):
        try:
            with open(file_name[0], 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Menu file not found. The menu is empty.")
            return {
                "appetizers": {},
                "main_meals": {},
                "drinks": {}
            }
    
    def show_menu(self):
        if not self.menu:
            print("The menu is currently empty.")
        else:
            print("Here is the menu:")
            for category, items in self.menu.items():
                print(f"\n{category.capitalize()}:")
                for item, price in sorted(items.items()):
                    print(f"  {item}: {price}")
                    
    def find_category(self, item):
        for category, items in self.menu_handler.menu.items():
            if item in items:
                return category
        return None    
    
    def update_menu(self, new_item, price):
        print("Please enter the category you like to update or make:")
        print("Categories: ", self.categories_list)
        category = input("")
        if category in self.menu:
            self.menu[category][new_item] = price
        else:
            self.menu[category] = {new_item: price}
        with open(file_name[0], 'w') as f:
            json.dump(self.menu, f, indent=4)
        print(f"Menu updated: Added {new_item} price {price} in {category}.")
        prompt = f"Menu updated: Added {new_item} price {price} in {category}."
        Log(prompt).set_log()
                
    def delete_menu_item(self, item):
        category = self.find_category(item)
        if category:
            del self.menu[category][item]
            with open(file_name[0], 'w') as f:
                json.dump(self.menu, f, indent=4)
            print(f"Menu updated: Deleted {item} from {category}.")
            prompt = f"Menu updated: Deleted {item} from {category}."
            Log(prompt).set_log()
        else:
            print(f"{item} is not in the menu.")
            

class Authentication:
    def __init__(self):
        self._admin_password = None
        self.load_admin_password()

    def load_admin_password(self):
        try:
            with open(file_name[1], 'r') as f:
                self._admin_password = json.load(f)
        except FileNotFoundError:
            print("Admin password not set. Please create one.")
            self._set_admin_password()

    def _set_admin_password(self):
        password = input("Enter new admin password: ")
        with open(file_name[1], 'w') as f:
            json.dump(password, f, indent=4)
        self._admin_password = password
        print("Admin password updated.")
        prompt = "Admin password updated."
        Log(prompt).set_log()
        
    def authenticate_admin(self):
        incoming_pass = input("Please enter your admin password: ")
        if self._admin_password == incoming_pass:
            print("Admin authenticated successfully.")
            return True
        else:
            print("Incorrect password.")
            self.authenticate_admin()
            return False
        

class Customer:
    def __init__(self, menu_handler):
        self.menu_handler = menu_handler
        self.temp_receipt = {}
        if not self.menu_handler.menu:
            print("The menu is currently empty. No orders can be taken.")
        else:
            self.set_receipt()
    
    def set_receipt(self):
        self.menu_handler.show_menu()
        while True:
            order = input('\nWhat would you like to order? (e.g., "pizza 3")\nor type "done" to finish:\n').strip().lower()
            if order == 'done':
                break
            try:
                item, quantity = order.split()
                quantity = int(quantity)
                category = self.find_category(item, self.menu_handler.menu)
                if category:
                    if category in self.temp_receipt:
                        if item in self.temp_receipt[category]:
                            self.temp_receipt[category][item] += quantity
                        else:
                            self.temp_receipt[category][item] = quantity
                    else:
                        self.temp_receipt[category] = {item: quantity}
                    print(f'{item} has been added to your order.')
                else:
                    print(f"{item} not available in the {category}.")
            except ValueError:
                print("Invalid input. Please use the format 'item quantity'.")

        self._generate_receipt()
        
    def find_category(self, item, data):
        for category, items in data.items():
            if item in items:
                return category
        return None
    
    def _generate_receipt(self):
        total_price = 0
        print("\nYour order:")
        for category, items in self.temp_receipt.items():
            for item, quantity in items.items():
                price = int(self.menu_handler.menu.get(category, {}).get(item, 0))
                total = price * quantity
                total_price += total
                print(f"{category.capitalize()} - {item}: {quantity} x {price} = {total}")
        print(f"Total: {total_price}")
        self.confirm_receipt()
        
    def confirm_receipt(self):
        next_action = input("\nDo you confirm your order?\n [Yes]\t[No]\n").strip().lower()
        if next_action == 'yes':
            prompt = f'Order placed: {self.temp_receipt}'
            Log(prompt).set_log()
            print("Thank you for your purchase.")
            sys.exit(0)
        elif next_action == 'no':
            self.change_receipt_action()
        else:
            print("\nInvalid answer. Please choose one of the options.")
            self.confirm_receipt()
            
    def change_receipt_action(self):
        action = input("\nWould you like add or delete an item?\n[delete]\t[add]\n").strip().lower()
        if action == 'add':
            self.add_to_receipt()
        elif action == 'delete':
            self.delete_from_receipt()
        else:
            print("\nInvalid answer. Please choose one of the options.")
            self.change_receipt_action()
            
    def add_to_receipt(self):
        while True:
            order = input('\nWhich food and how many would you like to add?(e.g., "pizza 2")\nother options:\n[change action]\t[done]\n').strip().lower()
            if order == 'done':
                self._generate_receipt()
                break
            elif order == 'change action':
                self._generate_receipt()
                self.change_receipt_action()
                pass
            try:
                item, quantity = order.split()
                quantity = int(quantity)
                category = self.find_category(item, self.menu_handler.menu)
                if category:
                    if category in self.temp_receipt:
                        if item in self.temp_receipt[category]:
                            self.temp_receipt[category][item] += quantity
                        else:
                            self.temp_receipt[category][item] = quantity
                    else:
                        self.temp_receipt[category] = {item: quantity}
                else:
                    print("Item not on the menu.")
            except ValueError:
                print("Invalid input. Please use the format 'item quantity'.")
        
        self.change_receipt_action()
                
    def delete_from_receipt(self):
        while True:
            item_to_delete = input('\nWhat would you like to delete?(e.g., "pizza")\nother options:\n[change action]\t[done]\n').strip().lower()
            if item_to_delete == 'done':
                self._generate_receipt()
                break
            elif item_to_delete == 'change action':
                self._generate_receipt()
                self.change_receipt_action()
                break
            
            try:
                category = self.find_category(item_to_delete, self.temp_receipt)
                if category and item_to_delete in self.temp_receipt[category]:
                    del self.temp_receipt[category][item_to_delete]
                    if not self.temp_receipt[category]:
                        del self.temp_receipt[category]
                    print(f"{item_to_delete} has been removed from your order.")
                else:
                    print(f"{item_to_delete} is not in your order.")

            except ValueError:
                print("Invalid input. Please enter the item name.")
        
        self.change_receipt_action()
 
        
class Admin_menu:
    def __init__(self, auth, menu_handler, log):
        self.auth = auth
        self.log = log
        self.menu_handler = menu_handler
        if self.auth.authenticate_admin():
            self.run()

    def run(self):
        while True:
            action = input("\nOptions:\n[change password] [show menu] [update menu]\n[delete menu item] [log] [exit]:\n").strip().lower()
            if action == "exit":
                print("Goodbye!")
                sys.exit(0)
            elif action == "change password":
                self.auth._set_admin_password()
            elif action == "update menu":
                self._update_menu()
            elif action == "delete menu item":
                self._delete_menu_item()
            elif action == "log":
                self.log.choose_log()
            else:
                print("Invalid option.")
                
    def _update_menu(self):
        while True:
            new_item = input('Enter the name of the new item or type "done" to finish:\n ').strip().lower()
            if new_item == 'done':
                break
            
            try:
                price = input(f"Enter the price for {new_item}: ")
                self.menu_handler.update_menu(new_item, price)
            except ValueError:
                print("Invalid price. Please enter a numeric value.")
        
        self.run()

    def _delete_menu_item(self):
        while True:
            item = input('Enter the name of the item to delete or type "done" to finish:\n').strip().lower()
            if item == 'done':
                break
            self.menu_handler.delete_menu_item(item)
        
        self.run()
        

class Log:
    def __init__(self, prompt=None):
        self.prompt = prompt
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logg = self.load_log()
    
    def load_log(self):
        try:
            with open(file_name[2], 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        
    def set_log(self):
        self.logg[self.current_time] = self.prompt
        
        with open(file_name[2], 'w') as f:
            json.dump(self.logg, f, indent=4)
      
    def show_log(self):
        for time, action in self.logg.items():
            print(time, ': ', action)
            
    def choose_log(self):
        order = input("\nOptions:\n[Log adress]\t[view log]\n").strip().lower()
        if order == 'log adress':
            print(os.getcwd())
        elif order == 'view log':
            self.show_log()
        else:
            print("\nInvalid answer. Please choose one of the options.")
            self.choose_log()
            
            
class User:
    def __init__(self):
        print("Welcome to our restaurant menu system.")
        self.menu_handler = Menu_handler()
        self.choose_role()

    def choose_role(self):
        while True:
            role = input("Please enter your role:\n[Admin]\t[Customer]\n").strip().lower()
            if role == 'admin':
                self.admin_flow()
                break
            elif role == 'customer':
                self.customer_flow()
                break
            else:
                print("Invalid role. Please try again.")

    def admin_flow(self):
        auth = Authentication()
        log = Log()
        Admin_menu(auth, self.menu_handler, log)

    def customer_flow(self):
        Customer(self.menu_handler)



User()
