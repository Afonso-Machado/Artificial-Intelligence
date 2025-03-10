# interface.py
import tkinter as tk
from tkinter import messagebox, scrolledtext

class App:
    def __init__(self, root, solve_function):
        self.root = root
        self.root.title("Drone Delivery Optimization")
        self.solve_function = solve_function

        # Set a minimum window size
        self.root.minsize(600, 500)

        # Create a frame for the top controls
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10, fill=tk.X)

        # Problem selection
        self.problem_label = tk.Label(control_frame, text="Select Problem Instance")
        self.problem_label.grid(row=0, column=0, padx=10)

        self.problem_var = tk.StringVar(value="Example")
        self.problem_menu = tk.OptionMenu(control_frame, self.problem_var, "Example", "Busy Day", "Mother of all warehouses", "Redundancy")
        self.problem_menu.grid(row=0, column=1, padx=10)

        # Algorithm selection
        self.algorithm_label = tk.Label(control_frame, text="Select Algorithm")
        self.algorithm_label.grid(row=0, column=2, padx=10)

        self.algorithm_var = tk.StringVar(value="Hill Climbing")
        self.algorithm_menu = tk.OptionMenu(control_frame, self.algorithm_var, "Hill Climbing", "Simulated Annealing", "Tabu Search", "Genetic Algorithms")
        self.algorithm_menu.grid(row=0, column=3, padx=10)

        # Solve Button
        self.solve_button = tk.Button(control_frame, text="Solve", command=self.solve)
        self.solve_button.grid(row=0, column=4, padx=10)

        # Results area
        self.result_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=30)
        self.result_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def solve(self):
        problem = self.problem_var.get()
        algorithm = self.algorithm_var.get()
        
        try:
            # Clear previous results
            self.result_area.delete(1.0, tk.END)
            self.result_area.insert(tk.END, f"Solving {problem} using {algorithm}...\n\n")
            self.root.update()
            
            # Call the solve function from main
            result = self.solve_function(problem, algorithm)
            
            # Display result
            self.result_area.delete(1.0, tk.END)
            self.result_area.insert(tk.END, result)
        except Exception as e:
            self.result_area.insert(tk.END, f"\nError: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")