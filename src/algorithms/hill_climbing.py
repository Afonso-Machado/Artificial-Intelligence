# hill_climbing.py

def get_hc_solution(num_iterations, solution_generator, solution_evaluator, neighbor_generator):
    # Algorithm Parameters
    iteration = 0
    itNoImp = 0
    itNoImpMax = num_iterations/10

    # Get initial solution and its score
    best_solution = solution_generator()
    best_score = solution_evaluator(best_solution)
    
    print(f"Initial Solution: {best_solution}, score: {best_score}")

    while iteration < num_iterations and itNoImp < itNoImpMax:
        # Advance Iteration
        iteration += 1
        itNoImp += 1

        # Generate Neighbor
        neighbor = neighbor_generator(best_solution)

        # Check if neighbor was generated
        if(neighbor == -1):
            continue

        neighbor_eval = solution_evaluator(neighbor)

        if (neighbor_eval > best_score):
            best_score = neighbor_eval
            best_solution = neighbor
            itNoImp = 0
            print(f"Found better solution: {best_solution}, score: {best_score}")

    print(f"Final Solution: {best_solution}, score: {best_score}")
    return best_solution