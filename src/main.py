import tkinter as tk
from GUI import DatabaseGUI

if __name__ == "__main__":
    root = tk.Tk()
    gui = DatabaseGUI(root)
    root.mainloop()