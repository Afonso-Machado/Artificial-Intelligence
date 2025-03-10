# simulation.py


def run_algorithm(algorithm, products, warehouses, drones, orders):
    """
    Run the selected algorithm with the parsed problem data
    """
    if algorithm == "Hill Climbing":
        return algorithm1()
    elif algorithm == "Simulated Annealing":
        return algorithm2()
    elif algorithm == "Tabu Search":
        return algorithm3()
    elif algorithm == "Genetic Algorithms":
        return algorithm4()
    else:
        return f"Unknown algorithm: {algorithm}"

def algorithm1():
    return f"Processed problem with Hill Climbing"

def algorithm2():
    return f"Processed problem with Simulated Annealing"

def algorithm3():
    return f"Processed problem with Tabu Search"

def algorithm4():
    return f"Processed problem with Genetic Algorithms"

