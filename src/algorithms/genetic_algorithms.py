# genetic_algorithms.py
import random

#######################
# Algorithm Structure #
#######################

def get_ga_solution(num_iterations, population_size, solution_generator, solution_evaluator, crossover_generator, mutation_generator):
    # Algorithm Parameters
    generation_no = 0
    num_iterations = num_iterations
    
    # Generate initial population
    population = generate_population(population_size, solution_generator)
    
    # Save the best solution found until the moment
    best_solution = random.choice(population)
    best_score = solution_evaluator(best_solution)
    best_solution_generation = 0
    
    #print(f"Initial solution: {best_solution}, score: {best_score}")
    print(f"Initial solution score: {best_score}")
    
    while(num_iterations > 0):
        # Advance iteration
        print(f"Generation {generation_no}")
        
        #DEBUG
        total = 0
        for solution in population:
            total += solution_evaluator(solution)
        print(total/population_size)
        #END DEBUG
            
        generation_no += 1
        
        # Selected parents for crossover
        tournment_winner_sol = tournament_select(population, 4, solution_evaluator)
        roulette_winner_sol = roulette_select(population, solution_evaluator)

        # Next generation Crossover and Mutation
        child_1, child_2 = crossover_generator(tournment_winner_sol, roulette_winner_sol)

        # Check if croosover was successful
        if child_1 == -1 or child_2 == -1:
            num_iterations -= 1
            continue

        # Chance of mutation for child_1
        if random.randint(1, 100) == 1:
            child_1 = mutation_generator(child_1)

        # Chance of mutation for child_2
        if random.randint(1, 100) == 1:
            child_2 = mutation_generator(child_2)
        
        # Check if mutation was successful
        if child_1 == -1 or child_2 == -1:
            num_iterations -= 1
            continue

        # Pick best offspring
        score_1 = solution_evaluator(child_1)
        score_2 = solution_evaluator(child_2)

        if score_1 > score_2:
            offspring = child_1
        else:
            offspring = child_2

        # Modify population
        replace_least_fittest(population, offspring, solution_evaluator)

        # Checking the greatest fit among the current population
        greatest_fit, greatest_fit_score = get_greatest_fit(population, solution_evaluator)
        if greatest_fit_score > best_score:
            best_solution = greatest_fit
            best_score = greatest_fit_score
            best_solution_generation = generation_no
            num_iterations = num_iterations
            #print(f"Solution: {best_solution}, score: {best_score}")
            print(f"Solution score: {best_score}")
            print(f"Generation: {generation_no }")
        else:
            num_iterations -= 1
        
    #print(f"  Final solution: {best_solution}, score: {best_score}")
    print(f"Final solution score: {best_score}")
    print(f"Found on generation {best_solution_generation}")

    #return best_solution
    return best_score

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

    best_solution, _best_score = get_greatest_fit(participants, solution_evaluator)
    
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
    best_score = solution_evaluator(population[0])
    for i in range(1, len(population)):
        score = solution_evaluator(population[i])
        if score > best_score:
            best_score = score
            best_solution = population[i]
    return best_solution, best_score