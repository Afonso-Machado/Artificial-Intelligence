# calculations.py

def algorithm1():
    return f"Processed problem with Hill Climbing"

def algorithm2():
    return f"Processed problem with Simulated Annealing"

def algorithm3():
    return f"Processed problem with Tabu Search"

def algorithm4():
    return f"Processed problem with Genetic Algorithms"

def solve_problem(problem, algorithm):
    # Based on problem and algorithm selected, return the result
    if algorithm == "Hill Climbing":
        return algorithm1()
    elif algorithm == "Simulated Annealing":
        return algorithm2()
    elif algorithm == "Tabu Search":
        return algorithm3()
    elif algorithm == "Genetic Algorithms":
        return algorithm4()
