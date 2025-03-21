# simulation.py

# Built-in libraries
import random
from typing import List, Union

# Custom libraries
from parsing import parse_input_file
from problem_model import Order, Product
from algorithms.hill_climbing import get_hc_solution

##########################
#    Global Variables    #
# - Problem Parameters - #
##########################

max_turns: int = 0
warehouse_row: int = 0
warehouse_col: int = 0
drone_number: int = 0
orders: List[Order] = []


###########################
# Interface's entry point #
###########################

def run_algorithm(problem: str, algorithm: str) -> str:
    """
    Parse problem and run selected algorithm
    """
    # Prepare to change problem's parameters
    global max_turns, warehouse_row, warehouse_col, drone_number, orders
    
    # Transform problem string to match file
    problem = problem.lower().replace(" ", "_")

    # Parse input
    max_turns, warehouse_row, warehouse_col, drone_number, orders = parse_input_file(f"input/{problem}.in")

    # Run algorithm
    if algorithm == "Hill Climbing":
        return get_hc_solution(1000, generate_random_solution, evaluate_solution, get_random_neighbor_function)
    elif algorithm == "Simulated Annealing":
        return "Not yet implemented"
        #return algorithm2()
    elif algorithm == "Tabu Search":
        return "Not yet implemented"
        #return get_sa_solution()
    elif algorithm == "Genetic Algorithms":
        return "Not yet implemented"
        #return genetic_algorithm()
    else:
        return f"Unknown algorithm: {algorithm}"


############################
#        Simulation        #
# - Auxiliary  Functions - #
############################

"""--------------------
- Solution Generation -
--------------------"""
def generate_random_solution() -> List[List[Product]]:
    # Initialize empty solution
    solution: List[List[Product]] = [[] for _ in range(drone_number)]
    
    # Gather all produtcs to be delivered
    all_needed_products: List[Product] = []
    for order in orders:
        all_needed_products.extend(order.product_list)
    
    # Randomize product listing
    random.shuffle(all_needed_products)

    # Round-robin assignment of products to drones
    drone_index: int = 0
    
    for product_id in all_needed_products:
        solution[drone_index].append(product_id)
        drone_index = (drone_index + 1) % drone_number
    
    return solution

"""--------------------
- Evaluation function -
--------------------"""
def evaluate_solution(solution: List[List[Product]]) -> int:
    # Set every product to "not delivered"
    for order in orders:
        order.clear_deliveries()
    
    # Mark every delivered product and check turns taken
    turns_taken = 0
    for drone_products in solution:
        # Checking turns taken
        drone_cost = get_drone_cost(drone_products)
        turns_taken = max(turns_taken, drone_cost)

        # Marking delivered products
        for product in drone_products:
            product.set_delivered()

    # Check the number of completed orders
    completed_orders = 0
    for order in orders:
        if order.is_completed():
            completed_orders += 1
    
    # Calculate solution score
    if completed_orders == 0:
        solution_value = 0
    else:
        solution_value = completed_orders * max_turns - turns_taken

    return solution_value

"""--------------------
- Constraint checking -
--------------------"""
def get_drone_cost(drone_products: List[Product]) -> int:
    drone_cost: int = 0

    for product in drone_products:
        drone_cost += orders[product.order_id].delivery_cost

    return drone_cost

def check_if_feasible(solution: List[List[Product]]) -> bool:
    # Check drone cost and ensure its smaller than max turns
    for drone_products in solution:
        cost: int = get_drone_cost(drone_products)
        if cost > max_turns:
            return False
    
    return True

"""-----------------------
- Neighboorhood/Mutation -
-       Functions        -
-----------------------"""
def add_product_to_solution(solution: List[List[Product]]) -> List[List[Product]]:
    # Make a shallow copy of the given solution
    new_solution = [drone_products.copy() for drone_products in solution]

    # Choose a random drone index
    drone_index = random.randrange(drone_number)

    # Set every product to "not assigned"
    for order in orders:
        order.clear_assignements()

    # Mark every assigned product
    for drone_products in new_solution:
        # Marking assigned products
        for product in drone_products:
            product.set_assigned()
    
    # Get all unassigned products
    unassigned_products = []
    for order in orders:
        unassigned_products.extend(order.get_unassigned_products())

    # Check if there are unassigned items
    if not unassigned_products:
        return -1

    # Pick a random unassigned product and add it to choosen drone
    product_index = random.randrange(len(unassigned_products))
    new_solution[drone_index].append(unassigned_products[product_index])

    return new_solution

def remove_product_from_solution(solution: List[List[Product]]) -> Union[List[List[Product]], int]:
    # Make a shallow copy of the given solution
    new_solution = [drone_products.copy() for drone_products in solution]

    # Find drones that have at least one product assigned
    non_empty_drones = [i for i, products in enumerate(new_solution) if products]  
    if not non_empty_drones:
        # No items to remove
        return -1
    
    # Pick a random drone that is not empty
    drone_index = random.choice(non_empty_drones)

    # Pick a random product from that drone and remove it
    product_index = random.randrange(len(new_solution[drone_index]))
    del new_solution[drone_index][product_index]

    return new_solution

def swap_products_in_solution(solution: List[List[Product]]) -> List[List[Product]]:
    # Check if there are more than 1 drone
    if drone_number <= 1:
        return -1
    
    # Make a shallow copy of the given solution
    new_solution = [drone_products.copy() for drone_products in solution]

    # Pick two random drones
    drone_products_1, drone_products_2  = random.sample(new_solution, 2)

    # Check if both drones have products assigned
    if len(drone_products_1) == 0 or len(drone_products_2) == 0:
        return -1

    # Pick two random products
    product_1 = random.choice(drone_products_1)
    product_2 = random.choice(drone_products_2)

    # Swap products
    drone_products_1.remove(product_1)
    drone_products_2.remove(product_2)

    drone_products_1.append(product_2)
    drone_products_2.append(product_1)

    return new_solution

def get_random_neighbor_function(solution):
    function_list = [add_product_to_solution, remove_product_from_solution, swap_products_in_solution]
    choosen_function = random.choice(function_list)

    return choosen_function(solution)

"""-----------------------
- Problem representation -
-----------------------"""
def print_problem_info():
    print(f"Problem Information:")
    print(f"    Number of drones:    {drone_number}")
    print(f"    Max number of turns: {max_turns}")
    
    print("\nWarehouse:")
    print(f"    Coordinates: ({warehouse_row}, {warehouse_col})")
    
    print("\nOrders:")
    print(f"    {orders}\n")
