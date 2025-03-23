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
        return get_hc_solution(10000, generate_random_solution, evaluate_solution, get_random_neighbor_function)
    elif algorithm == "Simulated Annealing":
        return get_sa_solution(10000, 1000, 0.999, generate_random_solution, evaluate_solution, get_random_neighbor_function)
    elif algorithm == "Tabu Search":
        return get_ts_solution(10000, 10, generate_random_solution, evaluate_solution, get_random_neighbor_function)
    elif algorithm == "Genetic Algorithms":
        return get_ga_solution(1000, 30, generate_random_solution, evaluate_solution, order_based_crossover, get_random_neighbor_function)
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
def add_product_to_solution(solution: List[List[Product]], get_move_info: bool = False) -> List[List[Product]]:
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
    # Make shallow copy of parents
    p1 = parent1.copy()
    p2 = parent2.copy()

    # If either parent is empty, return originals
    if not p1 or not p2:
        return -1, -1
    
    # Step 1: Flatten both parents into single lists of items
    p1_flat = []
    for drone in p1:
        p1_flat.extend(drone)
    
    p2_flat = []
    for drone in p2:
        p2_flat.extend(drone)
    
    # If either flattened list is empty, return originals
    if not p1_flat or not p2_flat:
        return p1, p2
    
    # Step 2: Perform crossover on the flattened lists
    # Create child 1: Take a random segment from parent 1, fill rest from parent 2
    cut1 = random.randint(0, len(p1_flat) - 1)
    cut2 = random.randint(cut1, len(p1_flat))
    
    # Get middle segment from parent 1
    middle_segment = p1_flat[cut1:cut2]
    
    # Fill rest with items from parent 2 that aren't in middle segment
    remaining_items = [item for item in p2_flat if item not in middle_segment]
    
    # Create child 1's flat representation
    child1_flat = remaining_items[:cut1] + middle_segment + remaining_items[cut1:]
    # Create child 2: Reverse the process
    cut1_p2 = random.randint(0, len(p2_flat) - 1)
    cut2_p2 = random.randint(cut1_p2, len(p2_flat))
    
    # Get middle segment from parent 2
    middle_segment_p2 = p2_flat[cut1_p2:cut2_p2]
    
    # Fill rest with items from parent 1 that aren't in middle segment
    remaining_items_p2 = [item for item in p1_flat if item not in middle_segment_p2]
    
    # Create child 2's flat representation
    child2_flat = remaining_items_p2[:cut1_p2] + middle_segment_p2 + remaining_items_p2[cut1_p2:]
    # Step 3: Redistribute items to drones using round-robin
    num_drones = max(len(p1), len(p2))
    
    # Create empty drone lists for each child
    child1 = [[] for _ in range(num_drones)]
    child2 = [[] for _ in range(num_drones)]
    
    # Distribute items for child 1
    drone_idx = 0
    for item in child1_flat:
        child1[drone_idx].append(item)
        drone_idx = (drone_idx + 1) % num_drones
    
    # Distribute items for child 2
    drone_idx = 0
    for item in child2_flat:
        child2[drone_idx].append(item)
        drone_idx = (drone_idx + 1) % num_drones

    if(child1 == child2) :
        return -1, -1
    
    return child1, child2

def order_based_crossover_2(parent1, parent2):
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

    return child

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
