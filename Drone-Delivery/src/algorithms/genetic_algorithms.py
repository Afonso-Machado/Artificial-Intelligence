# genetic_algorithms.py
import random
import time

#######################
# Algorithm Structure #
#######################

def get_ga_solution(max_time, pop_adjustment, solution_generator, solution_evaluator, crossover_generator, mutation_generator, update_visualization):
    start_time = time.time()
    generation_no = 0
    improvement_counter = 0
    population_size = 30
    if pop_adjustment==0:
        population_size = 20
    elif pop_adjustment==1:
        population_size = 30
    elif pop_adjustment==2:
        population_size = 50

    # Generate initial population
    population = generate_population(population_size, solution_generator)
    
    # Save the best solution found until the moment
    best_solution, best_score, order_status = get_greatest_fit(population, solution_evaluator)
    best_solution_generation = 0

    # Data for graph generation
    data = [[0], [best_score], [0], [get_average(population, solution_evaluator)]]

    if update_visualization:
        # Pass both solution, score, order status, and is_initial=True
        update_visualization(best_solution, best_score, order_status, True)

    with open("output.txt", "w") as f:
        f.write("=" * 60 + "\n")
        f.write(f"{'GENETIC ALGORITHM RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Initial Solution Score:':<30} {best_score}\n")
        f.write(f"{'Population Size:':<30} {population_size}\n")
        f.write(f"{'Mutation Rate:':<30} {'1% chance per child'}\n")
        f.write("-" * 60 + "\n")
    
    print(f"Initial solution score: {best_score}")
    
    curr_time = time.time()
    while (curr_time - start_time < max_time):
        # Selected parents for crossover
        tournment_winner_sol = tournament_select(population, 4, solution_evaluator)
        roulette_winner_sol = roulette_select(population, solution_evaluator)

        # Next generation Crossover and Mutation
        child_1, child_2 = crossover_generator(tournment_winner_sol, roulette_winner_sol)

        # Check if croosover was successful
        if child_1 == -1 or child_2 == -1:
            continue
        
        # Chance of mutation for child_1
        if random.randint(1, 100) == 1:
            child_1 = mutation_generator(child_1)

        # Chance of mutation for child_2
        if random.randint(1, 100) == 1:
            child_2 = mutation_generator(child_2)
        
        # Check if mutation was successful
        if child_1 == -1 or child_2 == -1:
            continue

        # Advance iteration (Only if children solutions are feasible)
        generation_no += 1

        # Pick best offspring
        score_1 = solution_evaluator(child_1)
        score_2 = solution_evaluator(child_2)

        if score_1 > score_2:
            offspring = child_1
        else:
            offspring = child_2

        # Modify population
        replace_least_fittest(population, offspring, solution_evaluator)

        data[2].append(curr_time - start_time)
        data[3].append(get_average(population, solution_evaluator))

        # Checking the greatest fit among the current population
        greatest_fit, greatest_fit_score, order_status = get_greatest_fit(population, solution_evaluator)
        if greatest_fit_score > best_score:
            improvement = greatest_fit_score - best_score
            improvement_counter += 1
            best_solution = greatest_fit
            best_score = greatest_fit_score
            best_solution_generation = generation_no

            data[0].append(curr_time - start_time)
            data[1].append(best_score)

            if update_visualization:
                # Pass solution, score and status to callback
                update_visualization(best_solution, best_score, order_status)

            with open("output.txt", "a") as f:
                f.write(f"Generation {generation_no:>5}: New best solution found\n")
                f.write(f"{'Score:':<30} {best_score}\n")
                f.write(f"{'Improvement:':<30} +{improvement}\n")
                f.write("-" * 60 + "\n")

            print(f"Found better solution score: {best_score}")
            print(f"Generation: {generation_no}")
        
        curr_time = time.time()

    data[0].append(max_time)
    data[1].append(best_score)

    with open("output.txt", "a") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"{'FINAL RESULTS':^60}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Total Generations:':<30} {generation_no:>16}\n")
        f.write(f"{'Improvements Found:':<30} {improvement_counter:>16}\n")
        f.write(f"{'Best Generation:':<30} {best_solution_generation:>16}\n")
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

    print(f"Final solution score: {best_score}")
    print(f"Found on generation {best_solution_generation}")

    return data

#########################
# Population Generation #
#########################

def generate_population(population_size, solution_generator):
    solutions = []
    for i in range(population_size):
        solutions.append(solution_generator())
    return solutions

####################
# Parent Selection #
####################

def tournament_select(population, tournament_size, solution_evaluator):
    if tournament_size > len(population):
        raise ValueError("Error: Tournament size larger than population")

    participants = random.sample(population, tournament_size)

    best_solution, _best_score, _order_status = get_greatest_fit(participants, solution_evaluator)
    
    return best_solution

def roulette_select(population, solution_evaluator):
    total_fitness = sum(solution_evaluator(individual) for individual in population)

    random_value = random.uniform(0, total_fitness)

    accumulated_fitness = 0
    for individual in population:
        accumulated_fitness += solution_evaluator(individual)
        if accumulated_fitness >= random_value:
            return individual

###########################
# Population Modification #
###########################

def replace_least_fittest(population, offspring, solution_evaluator):
    least_fittest_index = 0
    least_fittest_value = solution_evaluator(population[0])
    for i in range(1, len(population)):
        score = solution_evaluator(population[i])
        if score < least_fittest_value:
            least_fittest_value = score
            least_fittest_index = i
    population[least_fittest_index] = offspring

#######################
# Auxiliary Functions #
#######################

def get_greatest_fit(population, solution_evaluator):
    best_solution = population[0]
    best_score, order_status = solution_evaluator(population[0], return_status = True)
    for i in range(1, len(population)):
        score, temp_order_status = solution_evaluator(population[i], return_status = True)
        if score > best_score:
            best_score = score
            best_solution = population[i]
            order_status = temp_order_status
    return best_solution, best_score, order_status

def get_average(population, solution_evaluator):
    total = 0
    for i in range(len(population)):
        total += solution_evaluator(population[i])
    return total / len(population)
