#problem_model.py

class ProblemModel:

    # Class Constructor
    def __init__(self, input_file):

        # Open File
        with open(input_file, 'r') as file:
            
            values = self.parse_first_line(file)

            # General Info
            self.num_rows = values[0]
            self.num_col = values[1]
            self.drone_number = values[2]
            self.deadline = values[3]
            self.max_drone_load = values[4]

            # Products Type
            self.products = self.parse_products(file)

            # Warehouses info
            self.warehouses = self.parse_warehouses(file)
    
    # Get problem's parameters
    def parse_first_line(self, file):
        line = next(file)
        return list(map(int, line.split()))
    
    # Get product types
    def parse_products(self, file):
        num_products = int(file.readline().strip())
        values = list(map(int, file.readline().strip().split()))

        return [Product(i, weight) for i, weight in enumerate(values)]

    # Get warehouse info
    def parse_warehouses(self, file):
        num_warehouses = int(file.readline().strip())

        warehouses = []

        for i in range(num_warehouses):
            row, column = map(int, file.readline().strip().split())
            
            quantities = list(map(int, file.readline().strip().split()))

            warehouse = Warehouse(i, row, column, quantities)
            warehouses.append(warehouse)
        
        return warehouses

    # Define a printing function
    def __repr__(self):
        repr_str = (f"ProblemModel:\n"
                f"    Number of rows:      {self.num_rows}\n"
                f"    Number of columns:   {self.num_col}\n"
                f"    Number of drones:    {self.drone_number}\n"
                f"    Max number of turns: {self.deadline}\n"
                f"    Max Drone Capacity:  {self.max_drone_load}\n"
                "\n"
                f"    Products:\n")
        
        for product in self.products:
            repr_str += f"        {repr(product)}\n"
        
        repr_str += f"\n    Warehouses:\n"
        for warehouse in self.warehouses:
            repr_str += f"{repr(warehouse)}\n"
        
        return repr_str


class Product:
    # Class Constructor
    def __init__(self, product_id, weight):
        self.product_id = product_id
        self.weight = weight

    # Define a printing function
    def __repr__(self):
        return f"Product: id={self.product_id}, weight={self.weight}"


class Warehouse:
    def __init__(self, id, row, column, quantities):
        self.id = id
        self.row = row
        self.column = column
        self.quantities = quantities
    
    def __repr__(self):
        return (f"        Warehouse {self.id}: row={self.row}, column={self.column}\n"
                f"            Quantities: {self.quantities}")

