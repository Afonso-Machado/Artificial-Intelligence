# simulated_anealing.py
import numpy as np
import random
import time

def get_sa_solution(max_time, temp_adjustment, solution_generator, solution_evaluator, neighbor_generator, update_visualization):
    start_time = time.time()
    iteration = 0
    improvement_counter = 0
    temperature = 1000

    cooling_factor_string = ""
    if temp_adjustment == 0:
        cooling_factor_string = "Constant"
    elif temp_adjustment == 1:
        cooling_factor_string = "Linear"
    elif temp_adjustment == 2:
        cooling_factor_string = "Logarithmic"
    
    # Get initial solution and its score
    solution = solution_generator() 
    score, order_status = solution_evaluator(solution, return_status = True)
    
    # Save the best solution found until the moment
    best_solution = solution
    best_score = score

    # Data for graph generation
    data = [[0], [best_score], [], [], [], []]

    if update_visualization:
        # Pass both solution, score, order status, and is_initial=True
        update_visualization(best_solution, best_score, order_status, True)

    with open("output.txt", "w") as f:
        f.write("=" * 60 + "\n")
        f.write(f"{'SIMULATED ANNEALING ALGORITHM RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Initial Solution Score:':<30} {best_score}\n")
        f.write(f"{'Initial Temperature:':<30} {temperature:.2f}\n")
        f.write(f"{'Cooling Factor:':<30} {cooling_factor_string}\n")
        f.write("-" * 60 + "\n")

    print(f"Initial Solution score: {best_score}")

    curr_time = time.time()
    while (curr_time - start_time < max_time):        
        # Generate neighbor
        neighbor = neighbor_generator(solution)
        
        # Check if neighbor was generated
        if neighbor == -1:
            continue

        # Advance iteration (Only for feasible solutions)
        temperature = cooling_schedule(temp_adjustment, max_time, start_time, curr_time)
        iteration += 1
        
        data[4].append(curr_time - start_time)
        data[5].append(temperature)

        neighbor_eval,order_status = solution_evaluator(neighbor, return_status = True)
        delta = -(score - neighbor_eval)

        
        accepted_due_to_temp = (delta < 0 and np.exp(delta/temperature) > random.random()) # Accept worse solution

        if (delta > 0 or accepted_due_to_temp):
            solution = neighbor
            score = neighbor_eval

            data[0].append(curr_time - start_time)
            data[1].append(score)

            if accepted_due_to_temp:
                data[2].append(curr_time - start_time)
                data[3].append(score)

            if score > best_score:
                improvement = score - best_score
                improvement_counter += 1
                best_solution = solution
                best_score = score

                if update_visualization:
                    # Pass solution, score and status to callback
                    update_visualization(best_solution, best_score, order_status)
                
                with open("output.txt", "a") as f:
                    f.write(f"Iteration {iteration:>5}: New better solution found (temp: {temperature:.2f})\n")
                    f.write(f"{'Score:':<30} {best_score}\n")
                    f.write(f"{'Improvement:':<30} +{improvement}\n")
                    f.write(f"{'Temperature:':<30} {temperature:.2f}\n")
                    f.write("-" * 60 + "\n")

                print(f"Found better solution score: {best_score}")

            elif accepted_due_to_temp:
                    # when a worse solution is accepted due to temperature
                    with open("output.txt", "a") as f:
                        f.write(f"Iteration {iteration:>5}: Accepted worse solution (temp: {temperature:.2f})\n")
                        f.write(f"{'Score delta:':<30} {delta}\n")
                        f.write(f"{'Acceptance probability:':<30} {np.exp(delta/temperature):.4f}\n")
                        f.write("-" * 60 + "\n")
        
        # Update time for next loop
        curr_time = time.time()

    data[0].append(max_time)
    data[1].append(best_score)

    with open("output.txt", "a") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"{'FINAL RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Total Iterations:':<30} {iteration:>16}\n")
        f.write(f"{'Improvements Found:':<30} {improvement_counter:>16}\n")
        f.write(f"{'Final Temperature:':<30} {temperature:>16.2f}\n")
        f.write(f"{'Final Solution Score:':<30} {best_score:>16}\n")
        f.write("=" * 60 + "\n")
                
    print(f"Final Solution score: {best_score}")
    return data

def cooling_schedule(temp_adjustment, max_time, start_time, curr_time):
    # Temp_adjustment = 0 -> Constant cooling
    if (temp_adjustment == 0):
        return 500
    # Temp_adjustment = 1 -> Linear cooling
    if (temp_adjustment == 1):
        return 1000 * (1 - ((curr_time - start_time) / max_time))
    # Temp_adjustment = 2 -> Logaritmic cooling
    if (temp_adjustment == 2):
        elapsed_time = curr_time - start_time
        temperature = (1000 / (1 + elapsed_time)) - (1000 / max_time)
        return max(temperature, 0.0001)
