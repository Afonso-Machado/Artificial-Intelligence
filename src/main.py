# main.py
import tkinter as tk
from problem_model import Product, Warehouse, Order, Drone 
import simulation
from interface import App

# Global variables
num_rows = 0
num_col = 0
deadline = 0
products = []
warehouses = []
drones = []    
orders = []    

def create_interface():
    root = tk.Tk()
    app = App(root, solve_problem)  # Pass the solve_problem function to App
    return root

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

def print_problem_info():
    repr_str = (f"Problem Information:\n"
              f"    Number of rows:      {num_rows}\n"
              f"    Number of columns:   {num_col}\n"
              f"    Number of drones:    {len(drones)}\n"
              f"    Max number of turns: {deadline}\n"
              f"    Max Drone Capacity:  {drones[0].max_load}\n"
              "\n"
              f"    Products:\n")
    
    for product in products:
        repr_str += f"        {repr(product)}\n"
    
    repr_str += f"\n    Warehouses:\n"
    for warehouse in warehouses:
        repr_str += f"        {repr(warehouse)}\n"
    
    # Add drone information
    repr_str += f"\n    Drones:\n"
    for drone in drones:
        repr_str += f"        {repr(drone)}\n"
    
    # Add order information
    repr_str += f"\n    Orders:\n"
    for order in orders:
        repr_str += f"        {repr(order)}\n"
    
    print(repr_str)
    return repr_str  # Return the string for display in UI if needed

def solve_problem(problem, algorithm):
    # Get path to input file
    input_file = "input/" + problem.lower().replace(" ", "_") + ".in"
    
    # Parse the input file
    parse_input_file(input_file)
    
    # Print problem info
    info = print_problem_info()
    
   
    result = simulation.run_algorithm(algorithm, products, warehouses, drones, orders)
    
    return f"Problem Info:\n{info}\n\nResult:\n{result}"

def main():
    root = create_interface()
    root.mainloop()
    

if __name__ == "__main__":
    main()