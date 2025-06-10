# main.py
from interface import App
import tkinter as tk

def main():
    # Start Interface
    root = tk.Tk()
    
    app = App(root)
 
    root.mainloop()

if __name__ == "__main__":
    main()