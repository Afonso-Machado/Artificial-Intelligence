#problem_model.py


class Product:
    # Class Constructor
    def __init__(self, product_id, weight):
        self.product_id = product_id
        self.weight = weight

    # Define a printing function
    def __repr__(self):
        return f"Product: id={self.product_id}, weight={self.weight}"


class Warehouse:
    def __init__(self, id, row, column, quantities):
        self.id = id
        self.row = row
        self.column = column
        self.quantities = quantities
    
    def __repr__(self):
        # Create a nicely formatted representation
        base_info = f"Warehouse {self.id}: Location ({self.row}, {self.column})"
        
        # Format product quantities
        qty_lines = []
        for product_id, quantity in enumerate(self.quantities):
            if quantity > 0:  # Only show products that are available
                qty_lines.append(f"Product {product_id}: {quantity} units")
        
        # If there are products, format them nicely
        if qty_lines:
            products_info = "\n            ".join(qty_lines)
            return f"{base_info}\n            {products_info}"
        else:
            return f"{base_info}\n            No products available"

class Drone:
    def __init__(self, id, max_load):
        self.id = id
        self.max_load = max_load
        self.row = 0  
        self.column = 0
        self.current_load = 0
        self.items = {}  # Dictionary mapping product_id to quantity
        self.available_at_turn = 0  # When the drone becomes available
    
    def load_item(self, product_id, quantity, product_weight):
      
        total_weight = product_weight * quantity
        if self.current_load + total_weight <= self.max_load:
            if product_id in self.items:
                self.items[product_id] += quantity
            else:
                self.items[product_id] = quantity
            self.current_load += total_weight
            return True
        return False
    
    def unload_item(self, product_id, quantity, product_weight):
      
        if product_id in self.items and self.items[product_id] >= quantity:
            self.items[product_id] -= quantity
            if self.items[product_id] == 0:
                del self.items[product_id]
            self.current_load -= product_weight * quantity
            return True
        return False
    
    def move_to(self, row, column, turn):
        
        distance = int(((row - self.row) ** 2 + (column - self.column) ** 2) ** 0.5)
        self.row = row
        self.column = column
        self.available_at_turn = turn + distance + 1
        return distance + 1
    
    def __repr__(self):
        return (f"Drone {self.id}: position=({self.row}, {self.column}), "
                f"load={self.current_load}/{self.max_load}, "
                f"available_at_turn={self.available_at_turn}, "
                f"items={self.items}")


class Order:
    def __init__(self, id, row, column, product_items):
        self.id = id
        self.row = row
        self.column = column
        self.product_items = product_items  # List of product IDs needed
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
        return (f"Order {self.id}: location=({self.row}, {self.column}), "
                f"status={status}, remaining_items={len(self.product_items)}")