import tkinter as tk
from tkinter import filedialog

selected_directory = ""

# Open directory selection dialog
def select_directory():
    global selected_directory # Refer to the directory's global variable

    # Select directory prompt
    directory = filedialog.askdirectory(title="Select a Directory")

    if directory:
        selected_directory = directory
        print(f"Selected Directory: {selected_directory}")
        label.config(text=f"Selected Directory: {selected_directory}")
        clear_button.config(state="normal")
    else:
        print("No directory selected.")

def clear_selection():
    global selected_directory

    if selected_directory:
        selected_directory = ""

        label.config(text="No directory selected")

        clear_button.config(state="disabled")

        print("Selected directory cleared!")
        print(f"{selected_directory}")
    else:
        print("There is no directory to clear")

# Main windows
root = tk.Tk()
root.title("ML-Agents")

# Greeting label
label = tk.Label(root, text="This is an application that intergrates the ML-Agents command line into a gui")
label.pack()

label = tk.Label(root, text="No directory selected")
label.pack(pady=10)

select_button = tk.Button(root, text="Select Directory", command=select_directory)
select_button.pack(pady=5)

clear_button = tk.Button(root, text="Clear Directory", command=clear_selection)
clear_button.pack(pady=5)

# Start the Tkinter event loop
root.mainloop()