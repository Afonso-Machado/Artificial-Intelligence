# tabu_search.py
import time

def get_ts_solution(num_iterations, tabu_size, solution_generator, solution_evaluator, neighbor_generator, update_visualization):
    # Algorithm Parameters
    iteration = 0
    itNoImp = 0
    itNoImpMax = num_iterations/10
    improvement_counter = 0
    
    # Generate initial solution and evaluate it
    current_solution = solution_generator()
    current_score, order_status = solution_evaluator(current_solution, return_status = True)
    
    # Set initial best solution
    best_solution = current_solution
    best_score = current_score
    
    if update_visualization:
        # Pass both solution, score, order status, and is_initial=True
        update_visualization(best_solution, best_score, order_status, True)
        time.sleep(1)  # Slightly longer delay to see initial solution

    # List of tabu moves
    tabu_list = []

    with open("output.txt", "w") as f:
        f.write("=" *60 + "\n")
        f.write(f"{'TABU SEARCH ALGORITHM RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Initial Solution Score:':<30} {best_score:.10f}\n")
        f.write(f"{'Tabu List Size:':<30} {tabu_size}\n")
        f.write("-" * 60 + "\n")

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
            neighbor_score, order_status = solution_evaluator(neighbor, return_status = True)
            is_tabu = move_info in tabu_list
            neighbors_info.append((neighbor_score, is_tabu, neighbor, move_info, order_status))
        
        # No valid neighbors generated
        if not neighbors_info:
            continue  
        
        # Neighbor selection
        picked_neighbor = None

        # Sort the neighbor list
        neighbors_info.sort()
        
        # Check if best element is not tabu or that it meets the aspiration criteria
        best_neighbor_score, is_tabu, _neighbor, _move_info, _order_status = neighbors_info[-1]

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
            improvement = current_score - best_score
            improvement_counter += 1
            best_solution = current_solution
            best_score = current_score
            itNoImp = 0

            if update_visualization:
                    # Pass solution, score and status to callback
                    update_visualization(best_solution, best_score, picked_neighbor[4])
                    time.sleep(0.1)  # Small delay to see changes

            with open("output.txt", "a") as f:
                f.write(f"Iteration {iteration:>5}: New better solution found\n")
                f.write(f"{'Score:':<30} {best_score:.16f}\n")
                f.write(f"{'Improvement:':<30} +{improvement:.16f}\n")
                f.write(f"{'Current tabu list size:':<30} {len(tabu_list)}/{tabu_size}\n")
                f.write("-" * 60 + "\n")

            print(f"Found better solution score: {best_score}")
        
        # If the move is not tabu then add it to tabu list
        if not picked_neighbor[1]:
            if (len(tabu_list) == tabu_size):
                tabu_list.pop(0)
            tabu_list.append(picked_neighbor[3])

    with open("output.txt", "a") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"{'FINAL RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Total Iterations:':<30} {iteration:>16}\n")
        f.write(f"{'Improvements Found:':<30} {improvement_counter:>16}\n")
        f.write(f"{'Final Tabu List Size:':<30} {len(tabu_list):>16}/{tabu_size}\n")
        f.write(f"{'Final Solution Score:':<30} {best_score:>16.10f}\n")
        f.write("=" * 60 + "\n")

    print(f"Final Solution score: {best_score}")
    return best_solution