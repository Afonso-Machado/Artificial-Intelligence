# interface.py

# Built-in libraries
import tkinter as tk
from tkinter import messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter

# Custom libraries
import simulation

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Delivery Optimization")

        self.last_solution = None
        self.last_score = None
        self.last_order_status = None
        self.is_last_initial = False

        # Set a minimum window size
        self.root.minsize(900, 700)

        # Create a main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        
        # Top control frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=5, fill=tk.X)

        # Problem selection
        self.problem_label = tk.Label(control_frame, text="Problem:")
        self.problem_label.grid(row=0, column=0, padx=5)

        self.problem_var = tk.StringVar(value="Example")
        self.problem_menu = tk.OptionMenu(control_frame, self.problem_var, "Example", "Busy Day", "Mother of all warehouses", "Redundancy")
        self.problem_menu.grid(row=0, column=1, padx=5)

        # Algorithm selection
        self.algorithm_label = tk.Label(control_frame, text="Algorithm:")
        self.algorithm_label.grid(row=0, column=2, padx=5)

        self.algorithm_var = tk.StringVar(value="Hill Climbing")
        self.algorithm_menu = tk.OptionMenu(control_frame, self.algorithm_var, "Hill Climbing", "Simulated Annealing", "Tabu Search", "Genetic Algorithms")
        self.algorithm_menu.grid(row=0, column=3, padx=5)

        # Solve Button
        self.solve_button = tk.Button(control_frame, text="Solve", command=self.solve)
        self.solve_button.grid(row=0, column=4, padx=10)

        self.param_frame = tk.LabelFrame(main_frame, text="Algorithm Parameters")
        self.param_frame.pack(fill=tk.X, padx=10, pady=5)

        # Common parameter (Max duration)
        self.iter_frame = tk.Frame(self.param_frame)
        self.iter_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(self.iter_frame, text="Maximum duration (in seconds):").pack(side=tk.LEFT, padx=5)
        self.max_duration_var = tk.StringVar(value="10")
        tk.Entry(self.iter_frame, textvariable=self.max_duration_var, width=10).pack(side=tk.LEFT, padx=5)

        # Hill Climbing parameters (none additional)
        self.hc_frame = tk.Frame(self.param_frame)
        # No additional parameters for Hill Climbing

        # Simulated Annealing parameters
        self.sa_frame = tk.Frame(self.param_frame)
        tk.Label(self.sa_frame, text="Starting Temperature Adjustment:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.sa_temp_adjustment_var = tk.StringVar(value="Logarithmic")
        tk.OptionMenu(self.sa_frame, self.sa_temp_adjustment_var, "Constant", "Linear", "Logarithmic").grid(row=0, column=1, padx=5, pady=2)

        # Tabu Search parameters
        self.ts_frame = tk.Frame(self.param_frame)
        tk.Label(self.ts_frame, text="Tabu List Size:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.ts_tabu_adjustment_var = tk.StringVar(value="Small")
        tk.OptionMenu(self.ts_frame, self.ts_tabu_adjustment_var, "Small", "Medium", "Large").grid(row=0, column=1, padx=5, pady=2)

        # Genetic Algorithm parameters
        self.ga_frame = tk.Frame(self.param_frame)
        tk.Label(self.ga_frame, text="Population Size:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.ga_pop_adjustment_var = tk.StringVar(value="Small")
        tk.OptionMenu(self.ga_frame, self.ga_pop_adjustment_var, "Small", "Medium", "Large").grid(row=0, column=1, padx=5, pady=2)

        # Register callback when algorithm changes to update parameter display
        self.algorithm_var.trace_add("write", self.update_param_display)
        # Initialize parameter display based on default algorithm
        self.update_param_display()
        # Text output area (smaller, at the top)
        text_frame = tk.Frame(main_frame, height=100)
        text_frame.pack(fill=tk.X, padx=10, pady=5)
        text_frame.pack_propagate(False)  # Prevent the frame from resizing to fit content

        self.result_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=5)
        self.result_area.pack(fill=tk.BOTH, expand=True)
        
        # Separator line
        separator = tk.Frame(main_frame, height=2, bg="gray")
        separator.pack(fill=tk.X, padx=5, pady=5)

        # Create a frame to hold the grid and graph side by side
        visualization_frame = tk.Frame(main_frame)
        visualization_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Canvas for visualization (grid)
        self.canvas_frame = tk.Frame(visualization_frame, bd=2, relief=tk.SUNKEN)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Set up visualization properties
        self.margin = 20

        # Frame for the graph (to the right of the canvas)
        self.graph_frame = tk.Frame(visualization_frame, bd=2, relief=tk.SUNKEN)
        self.graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a matplotlib figure and canvas (initially empty)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax2 = None
        self.canvas_graph = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas_graph.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add zoom controls below the visualization
        zoom_frame = tk.Frame(main_frame)
        zoom_frame.pack(fill=tk.X, pady=5)

        self.zoom_in_btn = tk.Button(zoom_frame, text="Zoom In (+)", command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=10)

        self.zoom_out_btn = tk.Button(zoom_frame, text="Zoom Out (-)", command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=10)

        self.reset_zoom_btn = tk.Button(zoom_frame, text="Reset Zoom", command=self.reset_zoom)
        self.reset_zoom_btn.pack(side=tk.LEFT, padx=10)

        # Add status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(main_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")
        
        # Zoom factor
        self.zoom_factor = 1.0

    def solve(self):
        problem = self.problem_var.get()
        algorithm = self.algorithm_var.get()
        
        try:
            # Validate and get parameters
            params = self.validate_and_get_params()
            
            # Clear previous results
            self.result_area.delete(1.0, tk.END)
            self.result_area.insert(tk.END, f"Solving {problem} using {algorithm}...\n\n")
            
            # Display the parameters being used
            self.result_area.insert(tk.END, f"Parameters: {params}\n\n")
            self.root.update()
            
            # Clear the graph before starting a new computation
            self.clear_graph()

            # Initialize problem
            simulation.init_problem_info(problem)
            
            # Reset zoom for new problem
            self.zoom_factor = 1.0
            self.status_var.set(f"Grid size: {simulation.num_rows}x{simulation.num_col}")

            # Initialize visualization
            self.init_visualization()

            # Register update callback with simulation module
            simulation.register_update_callback(self.update_visualization)

            # Call the solve function with validated parameters
            recorded_data = simulation.run_algorithm(algorithm, **params)
            
            self.result_area.insert(tk.END, f"\n\nOptimization complete!")

            # Update the graph with the results
            self.update_graph(recorded_data, algorithm)
            
        except ValueError as ve:
            self.result_area.insert(tk.END, f"\nParameter Error: {ve}")
            messagebox.showerror("Parameter Error", f"Please enter valid parameters: {ve}")
        except Exception as e:
            self.result_area.insert(tk.END, f"\nError: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.update_visualization_with_zoom()
        
    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.update_visualization_with_zoom()
        
    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.update_visualization_with_zoom()
    
    def update_visualization_with_zoom(self):
        """Redraw visualization with new zoom level using last known state"""
        # Only redraw if we have a solution
        if self.last_solution is not None:
            self.update_visualization(
                self.last_solution, 
                self.last_score, 
                self.last_order_status, 
                self.is_last_initial,
                update_text=False  # Don't update text area when just zooming
            )
        else:
            # Just redraw grid if no solution yet
            self.init_visualization()

    def init_visualization(self):
        """Initialize the visualization canvas"""
        self.canvas.delete("all")  # Clear canvas
        
        # Calculate cell size based on grid dimensions
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600

        grid_width = simulation.num_col
        grid_height = simulation.num_rows
        
        base_cell_size = min(
            (canvas_width - 2 * self.margin) / grid_width,
            (canvas_height - 2 * self.margin) / grid_height
        )
        self.cell_size = base_cell_size * self.zoom_factor
        
        # Calculate total grid size with current zoom
        total_width = grid_width * self.cell_size + 2 * self.margin
        total_height = grid_height * self.cell_size + 2 * self.margin
        
        # Configure canvas scrollregion to accommodate zoomed content
        self.canvas.config(scrollregion=(0, 0, total_width, total_height))
        
        # Remove old scrollbars if they exist
        if hasattr(self, 'h_scrollbar'):
            self.h_scrollbar.pack_forget()
            self.v_scrollbar.pack_forget()
        
        # Add scrollbars if needed
        if total_width > canvas_width or total_height > canvas_height:
            # Create vertical scrollbar first (right side)
            self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
            self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.v_scrollbar.config(command=self.canvas.yview)
            
            # Then create horizontal scrollbar (bottom)
            self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
            self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            self.h_scrollbar.config(command=self.canvas.xview)
            
            self.canvas.config(
                xscrollcommand=self.h_scrollbar.set,
                yscrollcommand=self.v_scrollbar.set
            )
        
        # Draw grid
        for i in range(grid_width + 1):
            x = self.margin + i * self.cell_size
            self.canvas.create_line(
                x, self.margin, 
                x, self.margin + grid_height * self.cell_size, 
                fill="lightgray" if i % 10 != 0 else "gray", 
                width=1 if i % 10 != 0 else 2
            )
        
        for i in range(grid_height + 1):
            y = self.margin + i * self.cell_size
            self.canvas.create_line(
                self.margin, y,
                self.margin + grid_width * self.cell_size, y,
                fill="lightgray" if i % 10 != 0 else "gray", 
                width=1 if i % 10 != 0 else 2
            )
    
    def update_visualization(self, solution, score=None, order_status=None, is_initial=False, update_text=True):
        """Update the visualization with current solution state"""
        # Save state for future redraws (e.g., when zooming)
        self.last_solution = solution
        self.last_score = score
        self.last_order_status = order_status
        self.is_last_initial = is_initial

        self.canvas.delete("all")  # Clear canvas
        self.init_visualization()  # Redraw grid
        
        # If order_status was provided, use it, otherwise calculate it
        if order_status is None:
            order_status = simulation.get_orders_status(solution)
                
        # If score was provided and update_text is True, update the score display
        if score is not None and update_text:
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
        
        warehouse_size = max(self.cell_size * 0.8, 8)  # Don't let it get too small

        self.canvas.create_rectangle(
            w_x - warehouse_size/2, w_y - warehouse_size/2,
            w_x + warehouse_size/2, w_y + warehouse_size/2,
            fill="blue", outline="black", tags="warehouse"
        )
        
        # Only add text if cell is large enough
        if self.cell_size >= 15:
            self.canvas.create_text(w_x, w_y, text="W", fill="white")

        # Draw orders based on provided completion status
        for i, order in enumerate(simulation.orders):
            o_x = self.margin + order.column * self.cell_size + self.cell_size/2
            o_y = self.margin + order.row * self.cell_size + self.cell_size/2
            
            # Use the provided status
            color = "green" if order_status[i] else "red"
            
            order_size = max(self.cell_size * 0.7, 6)  # Don't let it get too small

            self.canvas.create_oval(
                o_x - order_size/2, o_y - order_size/2,
                o_x + order_size/2, o_y + order_size/2,
                fill=color, outline="black", tags=f"order_{i}"
            )

            # Only add text if cell is large enough
            if self.cell_size >= 15:
                self.canvas.create_text(o_x, o_y, text=f"{i}", fill="white")
        
        # Update status bar
        completed = sum(1 for status in order_status if status)
        total = len(order_status)
        self.status_var.set(f"Grid: {simulation.num_rows}x{simulation.num_col} | Orders completed: {completed}/{total} | Zoom: {self.zoom_factor:.1f}x")
        
        # Force UI update
        self.root.update()

    def validate_and_get_params(self):
        """Validate parameters and return them as a dictionary"""
        try:
            # Common parameters
            params = {"max_time": int(self.max_duration_var.get())}
            if params["max_time"] <= 0:
                raise ValueError("Max duration must be greater than 0")
            
            # Algorithm-specific parameters
            algorithm = self.algorithm_var.get()
            if algorithm == "Simulated Annealing":
                adjustment_type = self.sa_temp_adjustment_var.get()
                params["temp_adjustment"] = {"Constant": 0, "Linear": 1, "Logarithmic": 2}[adjustment_type]
                
            elif algorithm == "Tabu Search":
                    adjustment_type = self.ts_tabu_adjustment_var.get()
                    params["tabu_adjustment"] = {"Small": 0, "Medium": 1, "Large": 2}[adjustment_type]

            elif algorithm == "Genetic Algorithms":
                    adjustment_type = self.ga_pop_adjustment_var.get()
                    params["pop_adjustment"] = {"Small": 0, "Medium": 1, "Large": 2}[adjustment_type]
                
            return params
        
        except ValueError as e:
            raise ValueError(f"Invalid parameter: {str(e)}")
        
    def update_param_display(self, *args):
        """Update which parameter controls are displayed based on selected algorithm"""
        algorithm = self.algorithm_var.get()
        
        # Hide all parameter frames
        self.hc_frame.pack_forget()
        self.sa_frame.pack_forget()
        self.ts_frame.pack_forget()
        self.ga_frame.pack_forget()
        
        # Show the appropriate parameter frame
        if algorithm == "Hill Climbing":
            self.hc_frame.pack(fill=tk.X, padx=5, pady=5)
        elif algorithm == "Simulated Annealing":
            self.sa_frame.pack(fill=tk.X, padx=5, pady=5)
        elif algorithm == "Tabu Search":
            self.ts_frame.pack(fill=tk.X, padx=5, pady=5)
        elif algorithm == "Genetic Algorithms":
            self.ga_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def clear_graph(self):
        """Clear the graph."""
        self.ax.clear()
        self.ax.tick_params(axis="y", labelcolor="black")
        if self.ax2:
            self.ax2.remove()
            self.ax2 = None
        self.canvas_graph.draw()
    
    def update_graph(self, data, algorithm):
        """Update the graph with new data."""
        self.ax.clear()
        if self.ax2:
            self.ax2.remove()
            self.ax2 = None

        if algorithm == "Hill Climbing":
            # Retrive data
            x_data = data[0]
            y_data = data[1]

            # Set up labels and plot graph
            self.ax.set_title("Score Improvement Over Time")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Score")
            self.ax.plot(x_data, y_data, label="Score")
            # Use scientific notation for the y-axis
            self.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            self.ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        
        if algorithm == "Tabu Search":
            # Retrive data
            x_data = data[0]
            y_data = data[1]
            x_tabu = data[2]
            y_tabu = data[3]

            # Set up labels and plot graph
            self.ax.set_title("Score Improvement Over Time")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Score")
            self.ax.plot(x_data, y_data, label="Score")
            self.ax.scatter(x_tabu, y_tabu, label="Tabu Hits", color="red", s=20)
            # Use scientific notation for the y-axis
            self.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            self.ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        
        if algorithm == "Simulated Annealing":
            # Retrive data
            x_data = data[0]
            y_data = data[1]
            x_worse = data[2]
            y_worse = data[3]
            x_temp = data[4]
            y_temp = data[5]

            # Set up labels and plot graph
            self.ax.set_title("Algorithm Results Over Time")
            self.ax.set_xlabel("Time (s)")
            
            # Plot score on the primary y-axis
            self.ax.set_ylabel("Score", color="blue")
            self.ax.plot(x_data, y_data, label="Score", color="blue")
            self.ax.tick_params(axis="y", labelcolor="blue")

            # Create a secondary y-axis for temperature
            self.ax2 = self.ax.twinx()
            self.ax2.set_ylabel("Temperature", color="orange")
            self.ax2.plot(x_temp, y_temp, label="Temperature", color="orange")
            self.ax2.tick_params(axis="y", labelcolor="orange")

            # Plot accepted worse solutions as scatter points on the primary axis
            self.ax.scatter(x_worse, y_worse, label="Accepted Worse", color="red", s=5)

            # Add legends for both axes
            self.ax.legend(loc="upper left")
            self.ax2.legend(loc="center right")

            # Use scientific notation for the primary y-axis (score)
            self.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            self.ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

            # Redraw the graph
            self.canvas_graph.draw()
        
        if algorithm == "Genetic Algorithms":
            # Retrive data
            x_data = data[0]
            y_data = data[1]
            x_avg = data[2]
            y_avg = data[3]

            # Set up labels and plot graph
            self.ax.set_title("Score Improvement Over Time")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Score")
            self.ax.plot(x_data, y_data, label="Best Score")
            self.ax.plot(x_avg, y_avg, label="Average Score")

            # Use scientific notation for the y-axis
            self.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            self.ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

        # Add legend and redraw the graph
        self.ax.legend()
        self.canvas_graph.draw()