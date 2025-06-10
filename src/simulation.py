# simulation.py

# Built-in libraries
import random
from typing import List, Union

# Custom libraries
from parsing import parse_input_file
from problem_model import Order, Product
from algorithms.hill_climbing import get_hc_solution
from algorithms.simulated_anealing import get_sa_solution
from algorithms.genetic_algorithms import get_ga_solution
from algorithms.tabu_search import get_ts_solution

##########################
#    Global Variables    #
# - Problem Parameters - #
##########################

num_rows: int = 0
num_col: int = 0
max_turns: int = 0
warehouse_row: int = 0
warehouse_col: int = 0
drone_number: int = 0
orders: List[Order] = []
update_callback = None


###########################
# Interface's entry point #
###########################

def run_algorithm(algorithm: str, **params):
    """
    Run selected algorithm with customizable parameters
    """
    # Get maximum duration parameter
    max_time = params.get("max_time", 10)

    # Run algorithm with provided parameters
    if algorithm == "Hill Climbing":
        print(f"Running Hill Climbing with a maximum time of {max_time} seconds")
        return get_hc_solution(max_time, generate_random_solution, evaluate_solution, 
                              get_random_neighbor_function, update_callback)
    
    elif algorithm == "Simulated Annealing":
        temp_adjustment = params.get("temp_adjustment", 0)
        print(f"Running Simulated Annealing with max time {max_time} and temp adjustment {temp_adjustment}")
        return get_sa_solution(max_time, temp_adjustment, generate_random_solution, evaluate_solution, 
                                get_random_neighbor_function, update_callback)
    
    elif algorithm == "Tabu Search":
        tabu_adjustment = params.get("tabu_adjustment", 0)
        print(f"Running Tabu Search with max time {max_time} and tabu adjustment {tabu_adjustment}")
        return get_ts_solution(max_time, tabu_adjustment, generate_random_solution, evaluate_solution, 
                                get_random_neighbor_function, update_callback, drone_number, orders)
    
    elif algorithm == "Genetic Algorithms":
        pop_adjustment = params.get("pop_adjustment", 0)
        print(f"Running Genetic Algorithms with max time {max_time} and population adjustment {pop_adjustment}")
        return get_ga_solution(max_time, pop_adjustment, generate_random_solution, evaluate_solution, 
                                order_based_crossover, get_random_neighbor_function, update_callback)
    
    else:
        return f"Unknown algorithm: {algorithm}"

############################
#        Simulation        #
# - Auxiliary  Functions - #
############################
"""---------------------
- Initializing Problem -
---------------------"""
def init_problem_info(problem: str):
    # Prepare to change problem's parameters
    global num_rows, num_col, max_turns, warehouse_row, warehouse_col, drone_number, orders
    
    # Transform problem string to match file
    problem = problem.lower().replace(" ", "_")

    # Parse input
    num_rows, num_col, max_turns, warehouse_row, warehouse_col, drone_number, orders = parse_input_file(f"input/{problem}.in")

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
    
    for product in all_needed_products:
        # Add item to drone if it is feasible otherwise skip item
        if (get_drone_cost(solution[drone_index]) + orders[product.order_id].delivery_cost <= max_turns):
            solution[drone_index].append(product)
            drone_index = (drone_index + 1) % drone_number
        else:
            continue
    
    return solution

"""--------------------
- Evaluation function -
--------------------"""
def evaluate_solution(solution: List[List[Product]], return_status: bool = False) -> int:
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

    if return_status:
        order_status = [order.is_completed() for order in orders]
        return solution_value, order_status
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
def add_product_to_solution(solution: List[List[Product]], get_move_info: bool = False) -> List[List[Product]]:
    """
    This neighboor function picks a random drone from a solution, checks which items are not being delivered and randomly assings one of them to the drone.
    This function returns a new solution with the added product or it returns -1 if:
    - There are no products not being delivered
    - Picked product can not be added to the picked drone's workload (adding it would make the solution unfeasible)
    """
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

    # Pick a random unassigned product
    product = random.choice(unassigned_products)

    # Check if product can be added to drone
    if (get_drone_cost(new_solution[drone_index]) + orders[product.order_id].delivery_cost > max_turns):
        return -1

    # Add product to drone
    new_solution[drone_index].append(product)

    # Return info about chosen move (Tabu Search related)
    if get_move_info:
        return (new_solution, ("add", product.id, drone_index))

    return new_solution

def remove_product_from_solution(solution: List[List[Product]], get_move_info: bool = False) -> Union[List[List[Product]], int]:
    """
    This neighboor function picks a random drone from a solution and removes one of the products it is responsible for delivering.
    This function returns a new solution with the removed product or it returns -1 if:
    - The picked drone has no products to remove
    """
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
    product = random.choice(new_solution[drone_index])
    new_solution[drone_index].remove(product)

    # Return info about chosen move (Tabu Search related)
    if get_move_info:
        return (new_solution, ("remove", product.id, drone_index))

    return new_solution

def swap_products_in_solution(solution: List[List[Product]], get_move_info: bool = False) -> List[List[Product]]:
    """
    This neighboor function picks two random drone from a solution and swaps two randomly picked items between them.
    This function returns a new solution with the swapped products or it returns -1 if:
    - The problem instance doens't have more than one drone
    - If any of the randomly picked drones doesn't have products
    - If the swap would make any drone's workload be infeasible
    """
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

    # Remove original products
    drone_products_1.remove(product_1)
    drone_products_2.remove(product_2)
    
    # Check if new products can be added
    if (get_drone_cost(drone_products_1) + orders[product_2.order_id].delivery_cost > max_turns):
        return -1
    if (get_drone_cost(drone_products_2) + orders[product_1.order_id].delivery_cost > max_turns):
        return -1

    # Add new products
    drone_products_1.append(product_2)
    drone_products_2.append(product_1)
    
    # Return info about chosen move (Tabu Search related)
    if get_move_info:
        return (new_solution, ("swap", product_1.id, new_solution.index(drone_products_1), product_2.id, new_solution.index(drone_products_2)))

    return new_solution

def get_random_neighbor_function(solution, get_move_info = False):
    function_list = [add_product_to_solution, remove_product_from_solution, swap_products_in_solution]
    choosen_function = random.choice(function_list)

    # Return info about chosen move (Tabu Search related)
    if get_move_info:
        return choosen_function(solution, True)

    return choosen_function(solution)

"""--------------------
- Crossover Functions -
--------------------"""
def order_based_crossover(parent1, parent2):
    """
    Crossover Logic: Start with empty children, child1 will pick a drone from parent 1, then a drone from parent 2 and so on, until it has picked all the drones.
    However, with this approach dupplicated products are a problem. Therefore, after picking a parent's drone, the child will remove all the items from it that are duplicated.
    This way no child solution will have duplicated products, however, to avoid culling products from the parent soltuions the erased items are stored.
    At the end of the algorithm, removed products are added to the drone with the least workload in the other child.
    This ensures that child solutions have all the products from the parents and that no child solution has duplicated products.
    """
    # Make shallow copy of solution 1 and shuffle it
    parent1_aux = parent1.copy()
    random.shuffle(parent1_aux)

    # Make shallow copy of solution 2 and shuffle it
    parent2_aux = parent2.copy()
    random.shuffle(parent2_aux)

    # Create child 1
    child1, excluded_products_1 = make_child(parent1_aux, parent2_aux)

    # Create child 2
    child2, excluded_products_2 = make_child(parent2_aux, parent1_aux)

    # Apply Excluded products
    child1 = apply_excluded(child1, excluded_products_2)

    child2 = apply_excluded(child2, excluded_products_1)

    return child1, child2

def make_child(parent1, parent2):
    # Initialize Child
    child = []

    # Mark all pertinent products as "non assigned"
    for parent in [parent1, parent2]:
        for drone_products in parent:
            for product in drone_products:
                product.assigned = False

    # Create child
    excluded_products = []
    for i in range(drone_number):
        # Determine from which parent to pick
        parent = parent2 if i % 2 == 0 else parent1
        # Get the drone from parent
        drone_products = parent.pop()
        # Make child inherit valid products
        assignable_products = [product for product in drone_products if not product.assigned]
        excluded_products.extend([product for product in drone_products if product.assigned])
        child.append(assignable_products)
        # Mark products as assigned
        for product in assignable_products:
            product.assigned = True
    
    return child, excluded_products

def apply_excluded(child, excluded_products):
    # Get drone cost
    drones_cost = list(map(get_drone_cost, child))

    for product in excluded_products:
        # Get drone with least cost
        drone_cost = min(drones_cost)
        drone_index = drones_cost.index(drone_cost)
        # If possible, assign current product to it
        if (drone_cost + orders[product.order_id].delivery_cost <= max_turns):
            child[drone_index].append(product)
            drones_cost[drone_index] += orders[product.order_id].delivery_cost

    return child

"""------------------
- Interface related -
------------------"""
def get_orders_status(solution: List[List[Product]]) -> List[int]:
    # Set every product to "not delivered"
    for order in orders:
        order.clear_deliveries()

    # Mark every delivered product
    for drone_products in solution:
        # Marking delivered products
        for product in drone_products:
            product.set_delivered()

    return [order.is_completed() for order in orders]

def register_update_callback(callback):
    """Register a callback function to be called whenever a new best solution is found"""
    global update_callback
    update_callback = callback

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
