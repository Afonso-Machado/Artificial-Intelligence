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
    
    # Create a beautiful output file header
    with open("output.txt", "w") as f:
        f.write("=" * 60 + "\n")
        f.write(f"{'HILL CLIMBING ALGORITHM RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Initial Solution Score:':<30} {best_score}\n")
        f.write("-" * 60 + "\n")

    print(f"Initial Solution score: {best_score}")
    improvement_counter = 0

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
            improvement = neighbor_eval - best_score
            best_score = neighbor_eval
            best_solution = neighbor
            itNoImp = 0
            improvement_counter += 1

            if update_visualization:
                # Pass solution, score and status to callback
                update_visualization(best_solution, best_score, order_status)
                time.sleep(0.1)  # Small delay to see changes

            with open("output.txt", "a") as f:
                f.write(f"Iteration {iteration:>5}: New better solution found\n")
                f.write(f"{'Score:':<30} {best_score}\n")
                f.write(f"{'Improvement:':<30} +{improvement}\n")
                f.write("-" * 60 + "\n")

            print(f"Found better solution score: {best_score}")

    # Write final results
    with open("output.txt", "a") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"{'FINAL RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Total Iterations:':<30} {iteration:>16}\n")
        f.write(f"{'Improvements Found:':<30} {improvement_counter:>16}\n")
        f.write(f"{'Final Solution Score:':<30} {best_score:>16}\n")
        f.write("=" * 60 + "\n")

    print(f"Final Solution score: {best_score}")
    return best_solution