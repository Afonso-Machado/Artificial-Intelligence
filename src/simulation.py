# simulation.py
# Problem Parameters

import random
import numpy as np
import copy
from problem_model import Drone, Order, Product
import time

num_rows = 0
num_col = 0
Turns = 0
warehouse_row = 0
warehouse_col = 0
drones = []
orders = []
products = []
update_callback = None

def register_update_callback(callback):
    """Register a callback function to be called whenever a new best solution is found"""
    global update_callback
    update_callback = callback

def parse_input_file(input_file):
    global num_rows, num_col, Turns, products, warehouse_row, warehouse_col, drones, orders
    
    with open(input_file, 'r') as file:
        # General Info
        values = parse_first_line(file)
        num_rows = values[0]
        num_col = values[1]
        drone_number = values[2]
        Turns = values[3]
        
        file.readline()  # Ignore number of product types
        file.readline()  # Ignore product weights
        
        line = int(file.readline().strip())  # Read number of warehouses but ignore
        warehouse_info = list(map(int, file.readline().strip().split())) # Read first warehouse coordinates
        warehouse_row, warehouse_col = warehouse_info[0], warehouse_info[1]
        for _ in range(line * 2 - 1): #ignore warehouse info if not the first one
            file.readline()
        
        # Create drones
        drones = create_drones(drone_number)
        
        # Orders info
        orders = parse_orders(file)

def parse_first_line(file):
    line = next(file)
    return list(map(int, line.split()))

def create_drones(num_drones):
    drone_list = []
    for i in range(num_drones):
        
        start_row = warehouse_row
        start_col = warehouse_col
            
        drone = Drone(i, start_row, start_col)
        drone_list.append(drone)
    return drone_list

def parse_orders(file): 
    global products
    products = []
    num_orders = int(file.readline().strip())
    orders_list = []
    product_id_counter = 0
        
    for i in range(num_orders):
        row, column = map(int, file.readline().strip().split())
        num_items = int(file.readline().strip()) 
        product_types = list(map(int, file.readline().strip().split()))
        order_product_ids = []

        for product_type in product_types:
            product = Product(product_id_counter, product_type)
            products.append(product)
            order_product_ids.append(product_id_counter)
            product_id_counter += 1

        order = Order(i, row, column, order_product_ids)
        orders_list.append(order)
    
    return orders_list


def print_problem_info():
    print(f"Problem Information:")
    print(f"    Number of rows:      {num_rows}")
    print(f"    Number of columns:   {num_col}")
    print(f"    Number of drones:    {len(drones)}")
    print(f"    Max number of turns: {Turns}")
    
    print("\nProducts:")
    for product in products:
        print(f"    {repr(product)}")
    
    print("\nWarehouse:")
    print(f"    Coordinates: ({warehouse_row}, {warehouse_col})")
    
    print("\nDrones:")
    for drone in drones:
        print(f"    {repr(drone)}")
    
    print("\nOrders:")
    for order in orders:
        print(f"    {repr(order)}")

def generate_random_initial_solution():
    
    solution = [[] for _ in range(len(drones))]
    
    all_needed_products = []
    for order in orders:
        all_needed_products.extend(order.product_items)
    
    random.shuffle(all_needed_products)

    # round-robin assignment of products to drones
    drone_index = 0
    
    for product_id in all_needed_products:
        solution[drone_index].append(product_id)
        drone_index = (drone_index + 1) % len(drones)
    
    return solution

def evaluate_solution(solution, return_status=False):
   
    orders_copy = copy.deepcopy(orders)
    drones_copy = copy.deepcopy(drones)


    # Product to order mapping for quick lookup
    product_to_order = {}
    for order in orders_copy:
        for product_id in order.product_items:
            product_to_order[product_id] = order.id
    
    completed_orders = 0
    max_turn = 0
    
    # Process each drone's assigned products
    for drone_id, assigned_products in enumerate(solution):
        drone = drones_copy[drone_id]
        current_turn = 0
        for product_id in assigned_products:
            
            order_id = product_to_order[product_id]
            order = orders_copy[order_id]
            
            
            # Wait until drone is available
            current_turn = max(current_turn, drone.available_at_turn)
            
            # 1. Go to warehouse to load the product
            distance_to_warehouse = drone.move_to(warehouse_row, warehouse_col, current_turn)
            current_turn += distance_to_warehouse
            
            # 2. Load the product (takes 1 turn)
            drone.load_item(product_id)
            current_turn += 1
            
            # 3. Go to delivery location
            distance_to_delivery = drone.move_to(order.row, order.column, current_turn)
            current_turn += distance_to_delivery
            
            # 4. Deliver the product (takes 1 turn)
            drone.unload_item(product_id)
            order.deliver_product(product_id)
            current_turn += 1
            
            # Check if order is completed
            if order.completed:
                completed_orders += 1

        # Update max turn
        max_turn = max(max_turn, current_turn)
       
    
    # Calculate solution value
    # If no orders were completed, return 0
    if completed_orders == 0:
        solution_value = 0
    else:
        # If all orders were completed, use the formula
        solution_value = completed_orders * Turns - max_turn
    
    # Return additional data if requested
    if return_status:
        order_status = [order.completed for order in orders_copy]
        return solution_value, order_status
    return solution_value



def check_if_feasible(solution):
    orders_copy = copy.deepcopy(orders)
    drones_copy = copy.deepcopy(drones)
    # Product to order mapping for quick lookup
    product_to_order = {}
    for order in orders_copy:
        for product_id in order.product_items:
            product_to_order[product_id] = order.id
    
    completed_orders = 0
    max_turn = 0
    # Process each drone's assigned products
    for drone_id, assigned_products in enumerate(solution):
        drone = drones_copy[drone_id]
        current_turn = 0
        for product_id in assigned_products:
            
            order_id = product_to_order[product_id]
            order = orders_copy[order_id]
                      
            # Wait until drone is available
            current_turn = max(current_turn, drone.available_at_turn)
            
            # 1. Go to warehouse to load the product
            distance_to_warehouse = drone.move_to(warehouse_row, warehouse_col, current_turn)
            current_turn += distance_to_warehouse
            
            # 2. Load the product (takes 1 turn)
            drone.load_item(product_id)
            current_turn += 1
            
            # 3. Go to delivery location
            distance_to_delivery = drone.move_to(order.row, order.column, current_turn)
            current_turn += distance_to_delivery
            
            # 4. Deliver the product (takes 1 turn)
            drone.unload_item(product_id)
            order.deliver_product(product_id)
            current_turn += 1
            
            # Check if order is completed
            if order.completed:
                completed_orders += 1

        # Update max turn
        max_turn = max(max_turn, current_turn)
        if(max_turn > Turns):
            return False
        
    return True



def get_orders_status(solution):

    orders_copy = copy.deepcopy(orders)
    drones_copy = copy.deepcopy(drones)
    
    # Product to order mapping for quick lookup
    product_to_order = {}
    for order in orders_copy:
        for product_id in order.product_items:
            product_to_order[product_id] = order.id
    
    # Process each drone's assigned products
    for drone_id, assigned_products in enumerate(solution):
        drone = drones_copy[drone_id]
        current_turn = 0
        for product_id in assigned_products:
            order_id = product_to_order.get(product_id)
            if order_id is not None:
                order = orders_copy[order_id]
                
                # Wait until drone is available
                current_turn = max(current_turn, drone.available_at_turn)
                
                # 1. Go to warehouse to load the product
                distance_to_warehouse = drone.move_to(warehouse_row, warehouse_col, current_turn)
                current_turn += distance_to_warehouse
                
                # 2. Load the product (takes 1 turn)
                drone.load_item(product_id)
                current_turn += 1
                
                # 3. Go to delivery location
                distance_to_delivery = drone.move_to(order.row, order.column, current_turn)
                current_turn += distance_to_delivery
                
                # 4. Deliver the product (takes 1 turn)
                drone.unload_item(product_id)
                order.deliver_product(product_id)
                current_turn += 1
    
    # Return list of completion status
    return [order.completed for order in orders_copy]

def remove_item_from_solution(solution):
    current_solution = copy.deepcopy(solution)
    # Find drones that have at least one product assigned
    non_empty_drones = [i for i, products in enumerate(current_solution) if products]  
    if not non_empty_drones:
        return -1  # No items to remove
    
    # Pick a random drone from   the ones carrying products
    drone_index = random.choice(non_empty_drones)
    # Pick a random product from that drone and remove it 
    product_index = random.randrange(len(current_solution[drone_index]))
    del current_solution[drone_index][product_index]  

    move_info = ("remove", product_index, drone_index)
    return (current_solution, move_info)
            

def add_item_to_solution(solution):
    # Choose a random drone index
    current_solution = copy.deepcopy(solution)
    
    drone_index = random.randrange(len(current_solution))
    
    # Build list of all items currently assigned
    list_of_items = []
    for d in current_solution:  
        list_of_items.extend(d)
    
    # Find an unassigned item
    for item in products:
        if item.product_id not in list_of_items:
            # Add to the randomly selected drone
            current_solution[drone_index].append(item.product_id)
            move_info = ("add", item.product_id, drone_index)
            return (current_solution, move_info)

    return -1

def swap_items_in_solution(solution):
    current_solution = copy.deepcopy(solution)
    drone1 = random.choice(current_solution)
    drone2 = random.choice(current_solution)
    if drone1 == drone2:
        return -1
   
    if len(drone1) == 0 or len(drone2) == 0:
        return -1

    item1 = random.choice(drone1)
    item2 = random.choice(drone2)
    
    drone1.remove(item1)
    drone2.remove(item2)
    drone1.append(item2)
    drone2.append(item1)

    move_info = ("swap", item1, current_solution.index(drone1), item2, current_solution.index(drone2))
    return (current_solution, move_info)

def get_random_neighbor_function(solution):
    function_list = [remove_item_from_solution,add_item_to_solution,swap_items_in_solution]
    choice = random.randint(0,2)

    return function_list[choice](solution)


def run_algorithm(algorithm, problem):
    """
    Run the selected algorithm with the parsed problem data
    """

    problem = problem.lower().replace(" ", "_")

    #print(f"Running {algorithm} on {Problem}...")
    if algorithm == "Hill Climbing":
        parse_input_file(f"input/{problem}.in")
        #print_problem_info()
        return get_hc_solution(10000, True)
    elif algorithm == "Simulated Annealing":
        return get_sa_solution(10000, True)
    elif algorithm == "Tabu Search":
        return get_tabu_solution(10000, 10, True)
    elif algorithm == "Genetic Algorithms":
        return genetic_algorithm(1000,12, True)
    else:
        return f"Unknown algorithm: {algorithm}"

#################
# Hill Climbing #
#################
def get_hc_solution(num_iterations, log=False):
    iteration = 0
    itNoImp = 0
    itNoImpMax = num_iterations/10
    best_solution = generate_random_initial_solution()
    # Get score and order status for initial solution
    best_score, order_status = evaluate_solution(best_solution, return_status=True)
    
    if update_callback:
        # Pass both solution, score, order status, and is_initial=True
        update_callback(best_solution, best_score, order_status, True)
        time.sleep(1)  # Slightly longer delay to see initial solution

    print(f"Initial score: {best_score}\n")
    
    while iteration < num_iterations and itNoImp < itNoImpMax:
        iteration += 1
        itNoImp += 1

        neighbor = get_random_neighbor_function(best_solution)

        if(neighbor == -1):
            continue

        if (not check_if_feasible(neighbor[0])):
            continue

        neighbor_eval, neighbor_status = evaluate_solution(neighbor[0], return_status=True)

        if (neighbor_eval > best_score):
            best_score = neighbor_eval
            best_solution = copy.deepcopy(neighbor[0])
            itNoImp = 0
            print(f"Current best solution: {best_solution}, score: {best_score}")
            if update_callback:
                # Pass solution, score and status to callback
                update_callback(best_solution, best_score, neighbor_status)
                time.sleep(0.1)  # Small delay to see changes
        
            
    print(f"Final score: {best_score}")
    return best_solution

######################
# Simulated Anealing #
######################
def get_sa_solution(num_iterations, log=False):
    iteration = 0
    itNoImp = 0
    itNoImpMax = num_iterations/10
    temperature = 1000
    solution = generate_random_initial_solution() 
    score, order_status = evaluate_solution(solution, return_status=True)
    
    best_solution = copy.deepcopy(solution)
    best_score = score
    
    if update_callback:
        # Pass both solution, score, order status, and is_initial=True
        update_callback(best_solution, best_score, order_status, True)
        time.sleep(1)  # Slightly longer delay to see initial solution

    print(f"Initial score: {best_score}\n")
    
    while iteration < num_iterations and itNoImp < itNoImpMax:
        temperature = temperature * 0.999  
        iteration += 1
        itNoImp += 1
        
        neighbor = get_random_neighbor_function(solution)
        if neighbor == -1:
            continue  # Skip invalid neighbors
            
        # Check if the solution is feasible
        if not check_if_feasible(neighbor[0]):
            continue

        neighbor_eval, neighbor_status = evaluate_solution(neighbor[0], return_status=True)
        delta = -(score - neighbor_eval)

        if (delta > 0 or np.exp(delta/temperature)>random.random()):
            solution = copy.deepcopy(neighbor[0])
            score, order_status = evaluate_solution(solution, return_status=True)
            if score > best_score:
                best_solution = solution
                best_score = score
                itNoImp = 0
                if log:
                    print(f"Solution:       {best_solution}, score: {best_score},  Temp: {temperature}")
                if update_callback:
                    # Pass solution, score and status to callback
                    update_callback(best_solution, best_score, order_status)
                    time.sleep(0.1)  # Small delay to see changes
        
        
                
    print(f"Final Solution: {best_solution}, score: {best_score}")
    return best_solution 

#TODO
###############
# Tabu Search #
###############
def get_tabu_solution(num_iterations, tabu_size=10, log=False):
  
    # Initialize parameters
    iteration = 0
    itNoImp = 0
    itNoImpMax = num_iterations/10
    
    # Generate initial solution and evaluate it
    current_solution = generate_random_initial_solution()
    current_score, current_status = evaluate_solution(current_solution, return_status=True)
    
    # Set initial best solution
    best_solution = copy.deepcopy(current_solution)
    best_score = current_score
    
    tabu_list = []
    
    # For visualization
    if update_callback:
        update_callback(best_solution, best_score, current_status, True)
        time.sleep(1)  # Longer delay to see initial solution

    print(f"Initial score: {best_score}\n")
    
    # Main loop
    while iteration < num_iterations and itNoImp < itNoImpMax:
        iteration += 1
        itNoImp += 1
        
        neighbors = []
        for _ in range(5):  
            neighbor = get_random_neighbor_function(current_solution)
            
            if neighbor != -1 and check_if_feasible(neighbor[0]):
                neighbors.append(neighbor)
        
        if not neighbors:
            continue  # No valid neighbors found
        
        # Evaluate all neighbors
        best_neighbor = None
        best_neighbor_score = float('-inf')
        best_neighbor_status = None
        best_neighbor_is_tabu = False
        
        for neighbor in neighbors:
            neighbor_score, neighbor_status = evaluate_solution(neighbor[0], return_status=True)
            is_tabu = neighbor[1] in tabu_list
            
            # Check if this is the best neighbor so far (tabu status considered later)
            if neighbor_score > best_neighbor_score:
                best_neighbor = neighbor
                best_neighbor_status = neighbor_status
                best_neighbor_score = neighbor_score
                best_neighbor_is_tabu = is_tabu
        
        # Check aspiration criteria for the best neighbor
        aspiration_criteria = best_neighbor_score > best_score
        # Decide whether to accept this move
        accept_move = False
        
        if not best_neighbor_is_tabu or(best_neighbor_is_tabu and aspiration_criteria):
            # Accept the move if it's not tabu or meets aspiration criteria
            accept_move = True
            
            # For non-tabu moves, add to tabu list only if accepted
            if not is_tabu:
                tabu_list.append(best_neighbor[1])
                # Keep tabu list at the desired size
                while len(tabu_list) > tabu_size:
                    tabu_list.pop(0)
        
        # Process the accepted move
        if accept_move:
            current_solution = copy.deepcopy(best_neighbor[0])
            current_score = neighbor_score
            
            # If this is a new best solution, update best solution
            if current_score > best_score:
                best_solution = copy.deepcopy(best_neighbor[0])
                best_score = current_score
                best_status = copy.deepcopy(best_neighbor_status)
                itNoImp = 0
                
                if log:
                    print(f"Iteration {iteration}, new best score: {best_score}")
                
                if update_callback:
                    update_callback(best_solution, best_score, best_status, False)
                    time.sleep(0.1)  # Small delay to see changes
                
            print(f"Iteration {iteration}, Current solution score: {current_score}") 
        '''
        else:
            # Every 10 iterations or so, try a random diversification move
            if iteration % 10 == 0:
                diversification_solution = generate_diversification_move(current_solution)
                if (diversification_solution != -1 and 
                    check_if_feasible(diversification_solution)):
                    current_solution = diversification_solution
                    current_score = evaluate_solution(current_solution)
                    if log and random.random() < 0.2:  # Only log occasionally
                        print(f"Iteration {iteration}, diversification move: {current_score}")'
        '''

    print(f"Final score: {best_score}")
    return best_solution


#####################
# Genetic Algorithm #
#####################
def generate_population(population_size):
    solutions = []
    for i in range(population_size):
        solutions.append(generate_random_initial_solution())
    return solutions

def get_greatest_fit(population):
    best_solution = population[0]
    best_score = evaluate_solution(population[0])
    for i in range(1, len(population)):
        score = evaluate_solution(population[i])
        if score > best_score:
            best_score = score
            best_solution = population[i]
    return best_solution, best_score

def tournament_select(population, tournament_size):
    if tournament_size > len(population):
        raise ValueError("Error: Tournament size larger than population")

    participants = random.sample(population, tournament_size)

    best_solution, _best_score = get_greatest_fit(participants)
    
    return best_solution

def roulette_select(population):
    
    total_fitness = sum(evaluate_solution(individual) for individual in population)

    random_value = random.uniform(0, total_fitness)

    accumulated_fitness = 0
    for individual in population:
        accumulated_fitness += evaluate_solution(individual)
        if accumulated_fitness >= random_value:
            return individual

def replace_least_fittest(population, offspring):
    least_fittest_index = 0
    least_fittest_value = evaluate_solution(population[0])
    for i in range(1, len(population)):
        score = evaluate_solution(population[i])
        if score < least_fittest_value:
            least_fittest_value = score
            least_fittest_index = i
    population[least_fittest_index] = offspring

def order_based_crossover(parent1, parent2):

    #Still needs to be ixed becuase is leading to many parents being thesame as the children and also equal children'''

    # Create deep copies to avoid modifying original solutions
    p1 = copy.deepcopy(parent1)
    p2 = copy.deepcopy(parent2)
    
    # If either parent is empty, return originals
    if not p1 or not p2:
        return -1, -1
    
    # Step 1: Flatten both parents into single lists of items
    p1_flat = []
    for drone in p1:
        p1_flat.extend(drone)

    print(f"Parent 1 flat: {p1_flat}")
    
    p2_flat = []
    for drone in p2:
        p2_flat.extend(drone)

    print(f"Parent 2 flat: {p2_flat}")
    
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
    print(f"Child 1 flat: {child1_flat}")
    # Create child 2: Reverse the process
    cut1_p2 = random.randint(0, len(p2_flat) - 1)
    cut2_p2 = random.randint(cut1_p2, len(p2_flat))
    
    # Get middle segment from parent 2
    middle_segment_p2 = p2_flat[cut1_p2:cut2_p2]
    
    # Fill rest with items from parent 1 that aren't in middle segment
    remaining_items_p2 = [item for item in p1_flat if item not in middle_segment_p2]
    
    # Create child 2's flat representation
    child2_flat = remaining_items_p2[:cut1_p2] + middle_segment_p2 + remaining_items_p2[cut1_p2:]
    print(f"Child 2 flat: {child2_flat}")
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

def order_based_crossover(parent1, parent2):

    #Still needs to be ixed becuase is leading to many parents being thesame as the children and also equal children'''

    # Create deep copies to avoid modifying original solutions
    p1 = copy.deepcopy(parent1)
    p2 = copy.deepcopy(parent2)
    
    # If either parent is empty, return originals
    if not p1 or not p2:
        return -1, -1
    
    # Step 1: Flatten both parents into single lists of items
    p1_flat = []
    for drone in p1:
        p1_flat.extend(drone)

    print(f"Parent 1 flat: {p1_flat}")
    
    p2_flat = []
    for drone in p2:
        p2_flat.extend(drone)

    print(f"Parent 2 flat: {p2_flat}")
    
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
    print(f"Child 1 flat: {child1_flat}")
    # Create child 2: Reverse the process
    cut1_p2 = random.randint(0, len(p2_flat) - 1)
    cut2_p2 = random.randint(cut1_p2, len(p2_flat))
    
    # Get middle segment from parent 2
    middle_segment_p2 = p2_flat[cut1_p2:cut2_p2]
    
    # Fill rest with items from parent 1 that aren't in middle segment
    remaining_items_p2 = [item for item in p1_flat if item not in middle_segment_p2]
    
    # Create child 2's flat representation
    child2_flat = remaining_items_p2[:cut1_p2] + middle_segment_p2 + remaining_items_p2[cut1_p2:]
    print(f"Child 2 flat: {child2_flat}")
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

def genetic_algorithm(stop_criteria, population_size, log=False):
    population = generate_population(population_size)
    
    best_solution = random.choice(population) # Initial solution
    best_score = evaluate_solution(best_solution) # Initial score
    best_solution_generation = 0 # Generation on which the best solution was found
    
    generation_no = 0
    num_iterations = stop_criteria
    
    print(f"Initial solution: {best_solution}, score: {best_score}")
    
    while(num_iterations > 0):
        
        generation_no += 1
        
        tournment_winner_sol = tournament_select(population, 4)
        roulette_winner_sol = roulette_select(population)
        print(f"Parent 1: {tournment_winner_sol}")
        print(f"Parent 2: {roulette_winner_sol}")
        # Next generation Crossover and Mutation
        
        child_1, child_2 = order_based_crossover(tournment_winner_sol, roulette_winner_sol)
        if child_1 == -1 or child_2 == -1:
            continue
        print(f"Child 1: {child_1}")
        print(f"Child 2: {child_2}\n\n")
        # Chance of mutation for child_1
        if random.randint(1, 101) == 1:
            child_1 = get_random_neighbor_function(child_1)[0]

        # Chance of mutation for child_2
        if random.randint(1, 101) == 1:
            child_2 = get_random_neighbor_function(child_2)[0]

        # Pick best offspring
        score_1 = evaluate_solution(child_1)
        score_2 = evaluate_solution(child_2)
        if score_1 > score_2:
            offspring = child_1
        else:
            offspring = child_2
        
        replace_least_fittest(population, offspring)
        
        # Checking the greatest fit among the current population
        greatest_fit, greatest_fit_score = get_greatest_fit(population)
        if greatest_fit_score > best_score:
            best_solution = greatest_fit
            best_score = greatest_fit_score
            best_solution_generation = generation_no
            num_iterations = stop_criteria
            if log:
                print(f"\nGeneration: {generation_no }")
                print(f"Solution: {best_solution}, score: {best_score}")
                
        else:
            num_iterations -= 1
        
    print(f"  Final solution: {best_solution}, score: {best_score}")
    print(f"  Found on generation {best_solution_generation}")
    
    return best_solution
