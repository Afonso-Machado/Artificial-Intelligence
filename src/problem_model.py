# order.py
import math

class Order:
    def __init__(self, id, row, column, product_list):
        self.id = id
        self.row = row
        self.column = column
        self.product_list = product_list

    def calculate_fly_distance(self, x_coord, y_coord):
        # Cost of flying to target
        distance = math.sqrt((self.row - x_coord)**2 + (self.column - y_coord)**2)
        distance = math.ceil(distance)
        
        self.fly_cost = distance

        return distance

    def calculate_delivery_cost(self, warehouse_row, warehouse_col):
        delivery_cost = 0

        # Cost of loading item
        delivery_cost += 1

        # Cost of flying to target
        distance = self.calculate_fly_distance(warehouse_row, warehouse_col)
        delivery_cost += distance

        # Cost of delivering item
        delivery_cost += 1

        # Cost of flying back to warehouse
        delivery_cost += distance

        self.delivery_cost = delivery_cost
    
    def clear_deliveries(self):
        for product in self.product_list:
            product.delivered = False
    
    def clear_assignements(self):
        for product in self.product_list:
            product.assigned = False
    
    def is_completed(self) -> bool:
        return all(product.delivered for product in self.product_list)
    
    def get_unassigned_products(self):
        return [product for product in self.product_list if not product.assigned]

    def __repr__(self):
        return (f"Order {self.id} (delivery_location=({self.row}, {self.column}), "
                f"number_of_items={len(self.product_list)}, item_delivery_cost={self.delivery_cost})")

class Product:
    def __init__(self, id, order_id):
        self.id = id
        self.order_id = order_id
        self.delivered = False
        self.assigned = False
    
    def set_delivered(self):
        self.delivered = True
    
    def set_assigned(self):
        self.assigned = True

    def __repr__(self):
        return (f"Product {self.id} (belongs_to={self.order_id})")
    