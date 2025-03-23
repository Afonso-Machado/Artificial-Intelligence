# hill_climbing.py

import time

def get_hc_solution(num_iterations, solution_generator, solution_evaluator, neighbor_generator, update_visualization):
    # Algorithm Parameters
    iteration = 0
    itNoImp = 0
    itNoImpMax = num_iterations/10

    # Get initial solution and its score
    best_solution = solution_generator()
    best_score, order_status = solution_evaluator(best_solution, return_status = True)

    if update_visualization:
        # Pass both solution, score, order status, and is_initial=True
        update_visualization(best_solution, best_score, order_status, True)
        time.sleep(1)  # Slightly longer delay to see initial solution
    
    print(f"Initial Solution score: {best_score}")

    while iteration < num_iterations and itNoImp < itNoImpMax:
        # Advance Iteration
        iteration += 1
        itNoImp += 1

        # Generate Neighbor
        neighbor = neighbor_generator(best_solution)

        # Check if neighbor was generated
        if(neighbor == -1):
            continue

        neighbor_eval, order_status = solution_evaluator(neighbor, return_status = True)

        if (neighbor_eval > best_score):
            best_score = neighbor_eval
            best_solution = neighbor
            itNoImp = 0

            if update_visualization:
                # Pass solution, score and status to callback
                update_visualization(best_solution, best_score, order_status)
                time.sleep(0.1)  # Small delay to see changes

            print(f"Found better solution score: {best_score}")

    print(f"Final Solution score: {best_score}")
    return best_solution