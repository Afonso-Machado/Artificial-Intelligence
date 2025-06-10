# tabu_search.py
import time
import math

def get_ts_solution(max_time, tabu_adjustment, solution_generator, solution_evaluator, neighbor_generator, update_visualization, drone_number, orders):
    start_time = time.time()    
    iteration = 0
    improvement_counter = 0
    tabu_size = 10

    # Tabu size is calculated according to problem size
    product_number = orders[-1].product_list[-1].id + 1
    # Problem Size approximates the maximum number of possible neighbor moves
    problem_size = product_number * drone_number + product_number//2 * product_number//2
    if tabu_adjustment==0:
        tabu_size = math.ceil(0.00005 * problem_size)
    elif tabu_adjustment==1:
        tabu_size = math.ceil(0.00025 * problem_size)
    elif tabu_adjustment==2:
        tabu_size = math.ceil(0.00050 * problem_size)
    
    # Generate initial solution and evaluate it
    current_solution = solution_generator()
    current_score, order_status = solution_evaluator(current_solution, return_status = True)
    
    # Set initial best solution
    best_solution = current_solution
    best_score = current_score
    
    # Data for graph generation
    data = [[0], [best_score], [], []]

    if update_visualization:
        # Pass both solution, score, order status, and is_initial=True
        update_visualization(best_solution, best_score, order_status, True)

    # List of tabu moves
    tabu_list = []

    with open("output.txt", "w") as f:
        f.write("=" *60 + "\n")
        f.write(f"{'TABU SEARCH ALGORITHM RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Initial Solution Score:':<30} {best_score}\n")
        f.write(f"{'Tabu List Size:':<30} {tabu_size}\n")
        f.write("-" * 60 + "\n")

    print(f"Initial score: {best_score}\n")
    
    # Main loop
    curr_time = time.time()
    while (curr_time - start_time < max_time):        
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

        # Advance iteration (Only for feasible neighbors)
        iteration += 1
        
        # Neighbor selection
        picked_neighbor = None

        # Sort the neighbor list
        neighbors_info.sort()
        
        # Check if best element is not tabu or that it meets the aspiration criteria
        best_neighbor_score, is_tabu, _neighbor, _move_info, _order_status = neighbors_info[-1]

        if (is_tabu):
            data[2].append(curr_time - start_time)
            data[3].append(best_neighbor_score)

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

            data[0].append(curr_time - start_time)
            data[1].append(best_score)

            if update_visualization:
                # Pass solution, score and status to callback
                update_visualization(best_solution, best_score, picked_neighbor[4])

            with open("output.txt", "a") as f:
                f.write(f"Iteration {iteration:>5}: New better solution found\n")
                f.write(f"{'Score:':<30} {best_score}\n")
                f.write(f"{'Improvement:':<30} +{improvement}\n")
                f.write(f"{'Current tabu list size:':<30} {len(tabu_list)}/{tabu_size}\n")
                f.write("-" * 60 + "\n")

            print(f"Found better solution score: {best_score}")
        
        # If the move is not tabu then add it to tabu list
        if not picked_neighbor[1]:
            if (len(tabu_list) == tabu_size):
                tabu_list.pop(0)
            tabu_list.append(picked_neighbor[3])
        
        curr_time = time.time()
    
    data[0].append(max_time)
    data[1].append(best_score)

    with open("output.txt", "a") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"{'FINAL RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Total Iterations:':<30} {iteration:>16}\n")
        f.write(f"{'Improvements Found:':<30} {improvement_counter:>16}\n")
        f.write(f"{'Final Tabu List Size:':<30} {len(tabu_list):>16}/{tabu_size}\n")
        f.write(f"{'Final Solution Score:':<30} {best_score:>16}\n")
        f.write("=" * 60 + "\n")

    # Save solution to file
    with open("solution.txt", "w") as f:
        f.write("=" * 60 + "\n")
        f.write(f"{'SOLUTION DETAILS':^60}\n")
        f.write("=" * 60 + "\n\n")

        for drone_id, drone_products in enumerate(best_solution):
            # Write drone details
            f.write(f"Drone {drone_id + 1}:\n")
            f.write(f"{'Products:':<15}")

            # Wrap the product list into chunks of a fixed size
            chunk_size = 1
            for i in range(0, len(drone_products), chunk_size):
                chunk = drone_products[i:i + chunk_size]
                if i > 0:
                    f.write(f"{'':<15}")  # Indent subsequent lines
                f.write(f"{', '.join(map(str, chunk))}\n")

            f.write("-" * 60 + "\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write(f"{'END OF SOLUTION':^60}\n")
        f.write("=" * 60 + "\n")

    print(f"Final Solution score: {best_score}")
    return data