# parsing.py
from problem_model import Order, Product

def parse_input_file(input_file):
    
    with open(input_file, 'r') as file:
        # General Info
        values = list(map(int, file.readline().split()))
        num_row = values[0]
        num_col = values[1]
        drone_number = values[2]
        max_turns = values[3]
        
        file.readline()  # Ignore number of product types
        file.readline()  # Ignore product weights
        
        # Read number of warehouses but ignore
        line = int(file.readline().strip())
        # Read first warehouse coordinates
        warehouse_row, warehouse_col = list(map(int, file.readline().strip().split())) 
        #ignore warehouse info if not the first one
        for _ in range(line * 2 - 1):
            file.readline()
        
        # Orders info
        orders = parse_orders(file, warehouse_row, warehouse_col)
    
    return num_row, num_col, max_turns, warehouse_row, warehouse_col, drone_number, orders

def parse_orders(file, warehouse_row, warehouse_col):
    orders = []
    num_orders = int(file.readline().strip())
    product_id_counter = 0

    for i in range(num_orders):
        # Parse general info about order
        row, column = map(int, file.readline().strip().split())
        num_products = int(file.readline().strip())
        product_list = [Product(product_id_counter + j, i) for j in range(num_products)]

        # Parse info regarding order's items (Discarded)
        product_types = list(map(int, file.readline().strip().split()))

        # Save order info
        order = Order(i, row, column, product_list)
        order.calculate_delivery_cost(warehouse_row, warehouse_col)
        orders.append(order)
        product_id_counter += num_products
    
    return orders