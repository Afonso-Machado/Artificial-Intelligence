# ui.py
import tkinter as tk
from tkinter import messagebox
import calculations

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Delivery Optimization")

        # Set a minimum window size
        self.root.minsize(400, 300)

        # Problem selection
        self.problem_label = tk.Label(root, text="Select Problem Instance")
        self.problem_label.pack(pady=(20, 5))

        self.problem_var = tk.StringVar(value="Example")
        self.problem_menu = tk.OptionMenu(root, self.problem_var, "Example", "Busy Day", "Mother of all warehouses", "Redundancy")
        self.problem_menu.pack(pady=(5, 20))

        # Algorithm selection
        self.algorithm_label = tk.Label(root, text="Select Algorithm")
        self.algorithm_label.pack(pady=(20, 5))

        self.algorithm_var = tk.StringVar(value="Hill Climbing")
        self.algorithm_menu = tk.OptionMenu(root, self.algorithm_var, "Hill Climbing", "Simulated Annealing", "Tabu Search", "Genetic Algorithms")
        self.algorithm_menu.pack(pady=(5, 20))

        # Solve Button
        self.solve_button = tk.Button(root, text="Solve", command=self.solve)
        self.solve_button.pack(pady=(20, 10))

    def solve(self):
        problem = self.problem_var.get()
        algorithm = self.algorithm_var.get()
        
        try:
            result = calculations.solve_problem(problem, algorithm)
            messagebox.showinfo("Result", result)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
