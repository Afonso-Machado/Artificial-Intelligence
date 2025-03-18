# interface.py
import tkinter as tk
from tkinter import messagebox, scrolledtext
import simulation
import time

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Delivery Optimization")

        # Set a minimum window size
        self.root.minsize(800, 600)
        
        # Create a main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left frame for controls and text output
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a frame for the top controls
        control_frame = tk.Frame(left_frame)
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
        self.result_area = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, width=60, height=20)
        self.result_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Right frame for visualization
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas for visualization
        self.canvas_frame = tk.Frame(right_frame, bd=2, relief=tk.SUNKEN)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Set up visualization properties
        self.cell_size = 20  # Default, will be adjusted based on grid size
        self.margin = 20
        
        # Register update callback with simulation module
        simulation.register_update_callback(self.update_visualization)

    def solve(self):
        problem = self.problem_var.get()
        algorithm = self.algorithm_var.get()
        
        try:
            # Clear previous results
            self.result_area.delete(1.0, tk.END)
            self.result_area.insert(tk.END, f"Solving {problem} using {algorithm}...\n\n")
            self.root.update()
            
            # Parse input file to set up the problem
            simulation.parse_input_file(f"input/{problem.lower().replace(' ', '_')}.in")
            
            # Initialize visualization
            self.init_visualization()

            simulation.register_update_callback(self.update_visualization)

            # Call the solve function
            simulation.run_algorithm(algorithm, problem)
            
            self.result_area.insert(tk.END, f"\n\nOptimization complete!")

            
            
            
        except Exception as e:
            self.result_area.insert(tk.END, f"\nError: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def init_visualization(self):
        """Initialize the visualization canvas"""
        self.canvas.delete("all")  # Clear canvas
        
        # Calculate cell size based on grid dimensions
        canvas_width = self.canvas.winfo_width() or 400
        canvas_height = self.canvas.winfo_height() or 400
        
        grid_width = simulation.num_col
        grid_height = simulation.num_rows
        
        self.cell_size = min(
            (canvas_width - 2 * self.margin) / grid_width,
            (canvas_height - 2 * self.margin) / grid_height
        )
        
        # Draw grid
        for i in range(grid_width + 1):
            x = self.margin + i * self.cell_size
            self.canvas.create_line(
                x, self.margin, 
                x, self.margin + grid_height * self.cell_size, 
                fill="gray"
            )
        
        for i in range(grid_height + 1):
            y = self.margin + i * self.cell_size
            self.canvas.create_line(
                self.margin, y,
                self.margin + grid_width * self.cell_size, y,
                fill="gray"
            )
    
    def update_visualization(self, solution, score=None, order_status=None, is_initial=False):
        """Update the visualization with current solution state"""
        self.canvas.delete("all")  # Clear canvas
        self.init_visualization()  # Redraw grid
        
        # If order_status was provided, use it, otherwise calculate it
        if order_status is None:
            order_status = simulation.get_orders_status(solution)
                
        # If score was provided, update the score display
        if score is not None:
            if is_initial:
                # Special formatting for initial solution
                self.result_area.insert(tk.END, f"INITIAL SOLUTION\n")
                self.result_area.insert(tk.END, f"Initial score: {score}\n")
                self.result_area.insert(tk.END, f"-----------------------------\n\n")
            else:
                # Normal formatting for improvement solutions
                self.result_area.insert(tk.END, f"Improved solution: {score}\n")
            
            # Auto-scroll to show the latest score
            self.result_area.see(tk.END)
        
        # Draw warehouse
        w_x = self.margin + simulation.warehouse_col * self.cell_size + self.cell_size/2
        w_y = self.margin + simulation.warehouse_row * self.cell_size + self.cell_size/2
        
        self.canvas.create_rectangle(
            w_x - self.cell_size/2, w_y - self.cell_size/2,
            w_x + self.cell_size/2, w_y + self.cell_size/2,
            fill="blue", outline="black", tags="warehouse"
        )
        self.canvas.create_text(w_x, w_y, text="W", fill="white")
        
        # Draw orders based on provided completion status
        for i, order in enumerate(simulation.orders):
            o_x = self.margin + order.column * self.cell_size + self.cell_size/2
            o_y = self.margin + order.row * self.cell_size + self.cell_size/2
            
            # Use the provided status
            color = "green" if order_status[i] else "red"
            
            self.canvas.create_oval(
                o_x - self.cell_size/2, o_y - self.cell_size/2,
                o_x + self.cell_size/2, o_y + self.cell_size/2,
                fill=color, outline="black", tags=f"order_{i}"
            )
            self.canvas.create_text(o_x, o_y, text=f"{i}", fill="white")
        
        # Force UI update
        self.root.update()