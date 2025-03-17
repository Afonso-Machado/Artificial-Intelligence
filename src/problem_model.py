#problem_model.py

class Product:
    # Class Constructor
    def __init__(self, product_id,product_type):
        self.product_id = product_id
        self.product_type = product_type

    # Define a printing function
    def __repr__(self):
        return f"Product: id={self.product_id}"

class Drone:
    def __init__(self, id, start_row, start_col):
        self.id = id
        self.row = start_row  
        self.column = start_col
        self.current_item = None
        self.available_at_turn = 0 
    
    def load_item(self, product_id): 
        if self.current_item is None:
            self.current_item = product_id
            return True
        return False
    
    def unload_item(self, product_id):
      
        if self.current_item is not None:
            product_id = self.current_item
            self.current_item = None
            return product_id
        return None
    
    def move_to(self, row, column, turn):
        
        distance = int(((row - self.row) ** 2 + (column - self.column) ** 2) ** 0.5)
        self.row = row
        self.column = column
        self.available_at_turn = turn + distance + 1
        return distance + 1
    
    def __repr__(self):
        item_info = f"carrying product {self.current_item}" if self.current_item is not None else "empty"
        return (f"Drone {self.id}: position=({self.row}, {self.column}), "
                f"{item_info}, available_at_turn={self.available_at_turn}")


class Order:
    def __init__(self, id, row, column, product_items):
        self.id = id
        self.row = row
        self.column = column
        self.product_items = product_items  
        self.completed = False
        self.completion_turn = -1
    
    def is_product_needed(self, product_id):
       
        return product_id in self.product_items
    
    def deliver_product(self, product_id):
        
        if product_id in self.product_items:
            self.product_items.remove(product_id)
            if len(self.product_items) == 0:
                self.completed = True
            return True
        return False
    
    def __repr__(self):
        status = "Completed" if self.completed else "Pending"
        return (f"Order {self.id}: delivery_location=({self.row}, {self.column}), "
                f"status={status}, remaining_items={len(self.product_items)}")