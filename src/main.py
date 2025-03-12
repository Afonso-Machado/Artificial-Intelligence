import random
import copy
from problem_model import Product, Warehouse, Order, Drone

# Global variables
num_rows = 0
num_col = 0
deadline = 0
products = []
warehouses = []
drones = []    
orders = []

def parse_input_file(input_file):
    global num_rows, num_col, deadline, products, warehouses, drones, orders
    
    with open(input_file, 'r') as file:
        # General Info
        values = parse_first_line(file)
        num_rows = values[0]
        num_col = values[1]
        drone_number = values[2]
        deadline = values[3]
        max_drone_load = values[4]

        # Products Type
        products = parse_products(file)

        # Warehouses info
        warehouses = parse_warehouses(file)
        
        # Create drones
        drones = create_drones(drone_number, max_drone_load)
        
        # Orders info
        orders = parse_orders(file)

def parse_first_line(file):
    line = next(file)
    return list(map(int, line.split()))

def parse_products(file):
    num_products = int(file.readline().strip())
    values = list(map(int, file.readline().strip().split()))
    return [Product(i, weight) for i, weight in enumerate(values)]

def parse_orders(file): 
    num_orders = int(file.readline().strip())
    orders_list = []
    
    for i in range(num_orders):
        row, column = map(int, file.readline().strip().split())
        num_items = int(file.readline().strip())
        product_items = list(map(int, file.readline().strip().split()))
        order = Order(i, row, column, product_items)
        orders_list.append(order)
    
    return orders_list

def parse_warehouses(file):
    num_warehouses = int(file.readline().strip())
    warehouses_list = []

    for i in range(num_warehouses):
        row, column = map(int, file.readline().strip().split())
        quantities = list(map(int, file.readline().strip().split()))
        warehouse = Warehouse(i, row, column, quantities)
        warehouses_list.append(warehouse)
    
    return warehouses_list

def create_drones(num_drones, max_load):
    drone_list = []
    for i in range(num_drones):
        # All drones start at the location of warehouse 0
        if warehouses:
            start_row = warehouses[0].row
            start_col = warehouses[0].column
        else:
            start_row, start_col = 0, 0
            
        drone = Drone(i, max_load)
        drone.row = start_row
        drone.column = start_col
        drone_list.append(drone)
    return drone_list

def print_problem_info():
    print(f"Problem Information:")
    print(f"    Number of rows:      {num_rows}")
    print(f"    Number of columns:   {num_col}")
    print(f"    Number of drones:    {len(drones)}")
    print(f"    Max number of turns: {deadline}")
    print(f"    Max Drone Capacity:  {drones[0].max_load}")
    
    print("\nProducts:")
    for product in products:
        print(f"    {repr(product)}")
    
    print("\nWarehouses:")
    for warehouse in warehouses:
        print(f"    {repr(warehouse)}")
    
    print("\nDrones:")
    for drone in drones:
        print(f"    {repr(drone)}")
    
    print("\nOrders:")
    for order in orders:
        print(f"    {repr(order)}")

def generate_random_initial_solution():
    """
    Generate a random initial solution for the drone delivery problem.
    
    Returns:
        List of instructions where each instruction is:
        - Load: [drone_id, 'L', warehouse_id, product_id, quantity]
        - Deliver: [drone_id, 'D', order_id, product_id, quantity]
    """
    # Make copies to avoid modifying originals
    warehouses_copy = copy.deepcopy(warehouses)
    
    solution = []  # Will store all instructions
    
    # Track what products each order needs
    order_needs = {}
    for order in orders:
        order_needs[order.id] = {}
        for product_id in order.product_items:
            order_needs[order.id][product_id] = order_needs[order.id].get(product_id, 0) + 1
    
    # Track drone state
    drone_positions = {drone.id: (warehouses[0].row, warehouses[0].column) for drone in drones}
    drone_loads = {drone.id: {} for drone in drones}  # {drone_id: {product_id: quantity}}
    drone_available_turn = {drone.id: 0 for drone in drones}
    
    # Process orders in random order
    order_ids = list(range(len(orders)))
    random.shuffle(order_ids)
    
    for order_idx in order_ids:
        order = orders[order_idx]
        
        # Process each product type needed for this order
        for product_id, quantity_needed in order_needs[order.id].items():
            remaining = quantity_needed
            
            while remaining > 0:
                # Choose a random available drone with lowest available_turn
                available_drones = [(d.id, drone_available_turn[d.id]) for d in drones]
                if not available_drones:
                    break
                
                # Choose drone with earliest availability
                available_drones.sort(key=lambda x: x[1])
                drone_id = available_drones[0][0]
                drone = next(d for d in drones if d.id == drone_id)
                
                # Choose a warehouse that has this product
                available_warehouses = [w for w in warehouses_copy 
                                       if product_id < len(w.quantities) and w.quantities[product_id] > 0]
                if not available_warehouses:
                    break  # No warehouse has this product
                
                # Choose nearest warehouse
                warehouse = min(available_warehouses, 
                               key=lambda w: calculate_distance(drone_positions[drone_id], (w.row, w.column)))
                
                # Calculate max quantity we can load
                max_by_drone_capacity = (drone.max_load - sum(
                    products[p].weight * qty for p, qty in drone_loads[drone_id].items()
                )) // products[product_id].weight
                
                quantity = min(remaining, warehouse.quantities[product_id], max_by_drone_capacity)
                
                if quantity <= 0:
                    break  # Can't load any more
                
                # Calculate time for loading
                drone_pos = drone_positions[drone_id]
                warehouse_pos = (warehouse.row, warehouse.column)
                distance_to_warehouse = calculate_distance(drone_pos, warehouse_pos)
                
                # Current turn is when the drone is available
                current_turn = drone_available_turn[drone_id]
                
                # Add flight time to warehouse + 1 turn for loading
                load_turn = current_turn + int(distance_to_warehouse) + 1
                
                # Update warehouse inventory
                warehouse.quantities[product_id] -= quantity
                
                # Update drone load
                drone_loads[drone_id][product_id] = drone_loads[drone_id].get(product_id, 0) + quantity
                
                # Update drone position
                drone_positions[drone_id] = warehouse_pos
                
                # Add load instruction: [drone_id, 'L', warehouse_id, product_id, quantity]
                solution.append([drone_id, 'L', warehouse.id, product_id, quantity])
                
                # Calculate delivery
                order_pos = (order.row, order.column)
                distance_to_order = calculate_distance(warehouse_pos, order_pos)
                
                # Add flight time to order + 1 turn for delivery
                deliver_turn = load_turn + int(distance_to_order) + 1
                
                # Update drone availability time
                drone_available_turn[drone_id] = deliver_turn
                
                # Update drone position
                drone_positions[drone_id] = order_pos
                
                # Update drone load
                drone_loads[drone_id][product_id] -= quantity
                if drone_loads[drone_id][product_id] == 0:
                    del drone_loads[drone_id][product_id]
                
                # Add deliver instruction: [drone_id, 'D', order_id, product_id, quantity]
                solution.append([drone_id, 'D', order.id, product_id, quantity])
                
                # Update remaining quantity
                remaining -= quantity
                
                # Check if we've exceeded the deadline
                if deliver_turn >= deadline:
                    return solution
    
    return solution

def calculate_distance(pos1, pos2):
    """Calculate Euclidean distance between two points"""
    return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

def print_solution(solution):
    """Print solution in the required format for submission"""
    print(len(solution))
    for instruction in solution:
        if instruction[1] == 'L':
            # Load instruction
            print(f"{instruction[0]} L {instruction[2]} {instruction[3]} {instruction[4]}")
        elif instruction[1] == 'D':
            # Deliver instruction
            print(f"{instruction[0]} D {instruction[2]} {instruction[3]} {instruction[4]}")


def main():
    # Parse input file
    problem_name = "example"  # Change this to the problem you want to solve
    input_file = f"input/{problem_name}.in"
    
    parse_input_file(input_file)
    
    # Print problem information
    print_problem_info()
    
    # Generate and print a random initial solution
    solution = generate_random_initial_solution()
    
    print("\nRandom Initial Solution:")
    print_solution(solution)

if __name__ == "__main__":
    main()