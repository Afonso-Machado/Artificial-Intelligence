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

    """
    Returns an array of order completion status based on a solution
    without modifying the original orders
    """
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
    
    # Find drones that have at least one product assigned
    non_empty_drones = [i for i, products in enumerate(solution) if products]  
    if not non_empty_drones:
        return -1  # No items to remove
    
    # Pick a random drone from   the ones carrying products
    drone_index = random.choice(non_empty_drones)
    # Pick a random product from that drone and remove it 
    product_index = random.randrange(len(solution[drone_index]))
    del solution[drone_index][product_index]  

    return solution
            

def add_item_to_solution(solution):
    # Choose a random drone index
    
    drone_index = random.randrange(len(solution))
    
    # Build list of all items currently assigned
    list_of_items = []
    for d in solution:  
        list_of_items.extend(d)
    
    # Find an unassigned item
    for item in products:
        if item.product_id not in list_of_items:
            # Add to the randomly selected drone
            solution[drone_index].append(item.product_id)
            return solution

    return -1

def swap_items_in_solution(solution):
    drone1 = random.choice(solution)
    drone2 = random.choice(solution)
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

    return solution

def get_random_neighbor_function(solution):
    function_list = [remove_item_from_solution]
    choice = random.randint(0,0)


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
        return get_hc_solution(1000, True)
    elif algorithm == "Simulated Annealing":
        return get_sa_solution(10000, True)
    elif algorithm == "Tabu Search":
        return get_sa_solution()
    elif algorithm == "Genetic Algorithms":
        return genetic_algorithm()
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
        print(f"Best Solution before get_neighbor in iter: {iteration} - {best_solution}\n\n")

        neighbor = get_random_neighbor_function(best_solution)
        print(f"Best Solution after get_neighbor in iter: {iteration} - {best_solution}\n\n")

        if(neighbor == -1):
            continue
        print(f"Best Solution before is feasible in iter: {iteration} - {best_solution}\n\n")

        if (not check_if_feasible(neighbor)):
            continue
        print(f"Best Solution after is feasible in iter: {iteration} - {best_solution}\n\n")

        neighbor_eval, neighbor_status = evaluate_solution(neighbor, return_status=True)
        print(f"Best Solution after evaluate solution in iter: {iteration} - {best_solution}\n\n")

        if (neighbor_eval > best_score):
            best_score = neighbor_eval
            #print(f"Neighbor b4 copy: {best_solution}")
            best_solution = copy.deepcopy(neighbor)
            #print(f"Neighbor after copy: {best_solution}\n\n")
            itNoImp = 0
            #print(f"Current best solution: {best_solution}, score: {best_score}")
            #if update_callback:
                # Pass solution, score and status to callback
                #update_callback(best_solution, best_score, neighbor_status)
                #time.sleep(0.1)  # Small delay to see changes
        
        print(f"Last Best Solution before iter: {iteration} - {best_solution}\n\n")

           
            
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
    solution = generate_random_initial_solution() # Best solution after 'num_iterations' iterations without improvement
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
        if not check_if_feasible(neighbor):
            continue

        neighbor_eval, neighbor_status = evaluate_solution(neighbor, return_status=True)
        delta = -(score - neighbor_eval)

        if (delta > 0 or np.exp(delta/temperature)>random.random()):
            solution = copy.deepcopy(neighbor)
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
def get_tabu_solution(num_iterations=1000, tabu_size=10, log=False):
    """
    Implements Tabu Search algorithm
    
    Parameters:
    - num_iterations: maximum number of iterations
    - tabu_size: size of the tabu list (how many recent moves to remember)
    - log: whether to print progress information
    
    Returns:
    - best solution found
    """
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
    
    # Initialize tabu list as a list of (drone_index, product_id, operation_type) tuples
    # operation_type: 1=add, 2=remove, 3=swap_from, 4=swap_to
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
        
        
        neighbor_solution = get_random_neighbor_function(current_solution)
        
        if neighbor_solution == -1:
            continue  # Skip invalid neighbors
            
        # Check if the solution is feasible
        if not check_if_feasible(neighbor_solution):
            continue
        
        neighbor_score, neighbor_status = evaluate_solution(neighbor_solution, return_status=True)

        # Check if this move is in the tabu list
        
        if(neighbor_solution in tabu_list):
            is_tabu = True
        else:
            is_tabu = False
        
        
        # If we found a better neighbor
        if neighbor_score > current_score and not is_tabu:
          
            best_score = current_score
            itNoImp = 0
            
            if update_callback:
                update_callback(best_solution, best_score, best_neighbor_status, False)
                time.sleep(0.1)  # Small delay to see changes
            
            if log:
                print(f"Iteration {iteration}, new best score: {best_score}")
            
            # Add move to tabu list
            for move_part in best_neighbor_move:
                tabu_list.append(move_part)
                
            # Keep tabu list at the desired size
            while len(tabu_list) > tabu_size:
                tabu_list.pop(0)
        else:
            # If no feasible neighbor was found, try a random one
            random_neighbor = get_random_neighbor_function(current_solution)
            if random_neighbor != -1 and check_if_feasible(random_neighbor):
                current_solution = random_neighbor
                current_score = evaluate_solution(current_solution)
    
        #Aspiration criteria
        if is_tabu and neighbor_score > best_score: #
            best_solution = copy.deepcopy(current_solution)
            best_score = neighbor_score
            itNoImp = 0

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
    
    total_fitness = sum(-evaluate_solution(individual) for individual in population)

    random_value = random.uniform(0, total_fitness)

    accumulated_fitness = 0
    for individual in population:
        accumulated_fitness += -evaluate_solution(individual)
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

def genetic_algorithm(stop_criteria, population_size, crossover_func, mutation_func, log=False):
    population = generate_population(population_size)
    
    best_solution = population[0] # Initial solution
    best_score = evaluate_solution(population[0])
    best_solution_generation = 0 # Generation on which the best solution was found
    
    generation_no = 0
    num_iterations = stop_criteria
    
    print(f"Initial solution: {best_solution}, score: {best_score}")
    
    while(num_iterations > 0):
        
        generation_no += 1
        
        tournment_winner_sol = tournament_select(population, 4)
        roulette_winner_sol = roulette_select(population)

        # Next generation Crossover and Mutation
        
        child_1, child_2 = crossover_func(tournment_winner_sol, roulette_winner_sol)
        
        # Chance of mutation for child_1
        if random.randint(1, 101) == 1:
            child_1 = mutation_func(child_1)

        # Chance of mutation for child_2
        if random.randint(1, 101) == 1:
            child_2 = mutation_func(child_2)

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
