# tabu_search.py

def get_ts_solution(num_iterations, tabu_size, solution_generator, solution_evaluator, neighbor_generator):
    # Algorithm Parameters
    iteration = 0
    itNoImp = 0
    itNoImpMax = num_iterations/10
    
    # Generate initial solution and evaluate it
    current_solution = solution_generator()
    current_score = solution_evaluator(current_solution)
    
    # Set initial best solution
    best_solution = current_solution
    best_score = current_score
    
    # List of tabu moves
    tabu_list = []

    print(f"Initial score: {best_score}\n")
    
    # Main loop
    while iteration < num_iterations and itNoImp < itNoImpMax:
        # Advance iteration
        iteration += 1
        itNoImp += 1
        
        # Generate up to 5 neighbors and store relevant information
        neighbors_info = []
        for _ in range(5):
            generated_neighbor = neighbor_generator(current_solution, True)

            if generated_neighbor == -1:
                continue

            neighbor, move_info = generated_neighbor
            neighbor_score = solution_evaluator(neighbor)
            is_tabu = move_info in tabu_list
            neighbors_info.append((neighbor_score, is_tabu, neighbor, move_info))
        
        # No valid neighbors generated
        if not neighbors_info:
            continue  
        
        # Neighbor selection
        picked_neighbor = None

        # Sort the neighbor list
        neighbors_info.sort()
        
        # Check if best element is not tabu or that it meets the aspiration criteria
        best_neighbor_score, is_tabu, _neighbor, _move_info = neighbors_info[-1]
        if (not is_tabu or best_neighbor_score > best_score):
            picked_neighbor = neighbors_info[-1]
        else:
            non_tabu_neighbors = [neighbor_info for neighbor_info in neighbors_info if neighbor_info[1] == False]

            # If there are non-tabu neighbors pick the best one
            if (non_tabu_neighbors):
                picked_neighbor = non_tabu_neighbors[-1]
            else:
                # Otherwise pick the best tabu solution since they are all tabu
                picked_neighbor = neighbors_info[-1]

        # Process move
        current_solution = picked_neighbor[2]
        current_score = picked_neighbor[0]
        
        # If this is a new best solution, update best solution
        if current_score > best_score:
            best_solution = current_solution
            best_score = current_score
            itNoImp = 0
            print(f"Found better solution score: {best_score}")
        
        # If the move is not tabu then add it to tabu list
        if not picked_neighbor[1]:
            if (len(tabu_list) == tabu_size):
                tabu_list.pop(0)
            tabu_list.append(picked_neighbor[3])

    print(f"Final Solution score: {best_score}")
    #return best_solution
    return best_score