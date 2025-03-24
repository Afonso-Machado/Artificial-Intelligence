# simulated_anealing.py
import numpy as np
import random
import time

def get_sa_solution(num_iterations, starting_temp, cooling_factor, solution_generator, solution_evaluator, neighbor_generator, update_visualization):
    # Algorithm Parameters
    iteration = 0
    itNoImp = 0
    itNoImpMax = num_iterations/10
    temperature = starting_temp

    # Get initial solution and its score
    solution = solution_generator() 
    score, order_status = solution_evaluator(solution, return_status = True)
    
    # Save the best solution found until the moment
    best_solution = solution
    best_score = score

    if update_visualization:
        # Pass both solution, score, order status, and is_initial=True
        update_visualization(best_solution, best_score, order_status, True)
        time.sleep(1)  # Slightly longer delay to see initial solution

    print(f"Initial Solution score: {best_score}")
    
    while iteration < num_iterations and itNoImp < itNoImpMax:
        # Advance iteration
        temperature = temperature * cooling_factor
        iteration += 1
        itNoImp += 1
        
        # Generate neighbor
        neighbor = neighbor_generator(solution)
        
        # Check if neighbor was generated
        if neighbor == -1:
            continue

        neighbor_eval = solution_evaluator(neighbor)
        delta = -(score - neighbor_eval)

        if (delta > 0 or np.exp(delta/temperature)>random.random()):
            solution = neighbor
            score, order_status = solution_evaluator(solution, return_status = True)
            if score > best_score:
                best_solution = solution
                best_score = score
                itNoImp = 0

                if update_visualization:
                    # Pass solution, score and status to callback
                    update_visualization(best_solution, best_score, order_status)
                    time.sleep(0.1)  # Small delay to see changes

                print(f"Found better solution score: {best_score}")
                
    print(f"Final Solution score: {best_score}")
    return best_solution
