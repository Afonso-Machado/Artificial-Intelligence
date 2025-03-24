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
    improvement_counter = 0
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

    with open("output.txt", "w") as f:
        f.write("=" * 60 + "\n")
        f.write(f"{'SIMULATED ANNEALING ALGORITHM RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Initial Solution Score:':<30} {best_score:.10f}\n")
        f.write(f"{'Initial Temperature:':<30} {temperature:.4f}\n")
        f.write(f"{'Cooling Factor:':<30} {cooling_factor:.4f}\n")
        f.write("-" * 60 + "\n")

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

        accepted_due_to_temp = (delta <= 0 and np.exp(delta/temperature) > random.random())


        if (delta > 0 or np.exp(delta/temperature)>random.random()):
            solution = neighbor
            score, order_status = solution_evaluator(solution, return_status = True)
            if score > best_score:
                improvement = score - best_score
                improvement_counter += 1
                best_solution = solution
                best_score = score
                itNoImp = 0

                if update_visualization:
                    # Pass solution, score and status to callback
                    update_visualization(best_solution, best_score, order_status)
                    time.sleep(0.1)  # Small delay to see changes
                
                with open("output.txt", "a") as f:
                    f.write(f"Iteration {iteration:>5}: New better solution found\n")
                    f.write(f"{'Score:':<30} {best_score:.16f}\n")
                    f.write(f"{'Improvement:':<30} +{improvement:.16f}\n")
                    f.write(f"{'Temperature:':<30} {temperature:.8f}\n")
                    f.write("-" * 60 + "\n")

                print(f"Found better solution score: {best_score}")

            elif accepted_due_to_temp:
                    # when a worse solution is accepted due to temperature
                    with open("output.txt", "a") as f:
                        f.write(f"Iteration {iteration:>5}: Accepted worse solution (temp: {temperature:.8f})\n")
                        f.write(f"{'Score delta:':<30} {delta:.16f}\n")
                        f.write(f"{'Acceptance probability:':<30} {np.exp(delta/temperature):.8f}\n")
                        f.write("-" * 60 + "\n")

    with open("output.txt", "a") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"{'FINAL RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Total Iterations:':<30} {iteration:>16}\n")
        f.write(f"{'Improvements Found:':<30} {improvement_counter:>16}\n")
        f.write(f"{'Final Temperature:':<30} {temperature:>16.8f}\n")
        f.write(f"{'Final Solution Score:':<30} {best_score:>16.10f}\n")
        f.write("=" * 60 + "\n")
                
    print(f"Final Solution score: {best_score}")
    return best_solution
