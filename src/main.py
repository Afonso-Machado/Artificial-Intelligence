from interface import App
import tkinter as tk


from simulation import parse_input_file, print_problem_info
import simulation



def main():
    root = tk.Tk()
    
    app = App(root)
 
    root.mainloop()
    #simulation.run_algorithm("Hill Climbing", "Busy Day")
    

if __name__ == "__main__":
    main()