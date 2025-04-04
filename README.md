# Delivery Optimization using Metaheuristics

## Project Overview

This project is part of the Artificial Intelligence course, where we explore the use of **Metaheuristic Algorithms** for solving optimization and decision problems. Specifically, we focus on the **Delivery Optimization** problem, where the objective is to find the most efficient way to manage drone deliveries. The project uses several **metaheuristic optimization algorithms** to solve various delivery-related problems.

### Metaheuristics Used:
- **Hill Climbing**
- **Simulated Annealing**
- **Tabu Search**
- **Genetic Algorithms**

## Installation

To install and run the project locally, follow these steps:

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.x** (Recommended version: 3.8+)
- **pip** (Python package manager)

### Step-by-Step Installation

1. **Move into src folder**:
    ```bash
    cd src/
    ```

2. **Create a Virtual Environment** (Optional but recommended):
    ```bash
    python3 -m venv .venv
    ```

3. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     .\.venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

    This will install all the necessary libraries, such as:
    - `tkinter` (for the GUI)
    - `numpy` (for numerical computations)
    - `matplotlib` (for visualizations)
    - And their dependencies.

5. **Running the Application**:
    After the installation, run the main program to launch the application:
    ```bash
    python3 src/main.py
    ```

    This will start the **Drone Delivery Optimization** app with a simple GUI where you can choose different problem instances and algorithms to solve the delivery optimization problem.

