# simulated_anealing.py
import numpy as np
import random

def get_sa_solution(num_iterations, starting_temp, cooling_factor, solution_generator, solution_evaluator, neighbor_generator):
    # Algorithm Parameters
    iteration = 0
    itNoImp = 0
    itNoImpMax = num_iterations/10
    temperature = starting_temp

    # Get initial solution and its score
    solution = solution_generator() 
    score = solution_evaluator(solution)
    
    # Save the best solution found until the moment
    best_solution = solution
    best_score = score

    #print(f"Initial Solution: {best_solution}, score: {best_score}")
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
            score = solution_evaluator(solution)
            if score > best_score:
                best_solution = solution
                best_score = score
                itNoImp = 0
                #print(f"Found better solution: {best_solution}, score: {best_score}")
                print(f"Found better solution score: {best_score}")
                
    #print(f"Final Solution: {best_solution}, score: {best_score}")
    print(f"Final Solution score: {best_score}")
    #return best_solution
    return best_score
