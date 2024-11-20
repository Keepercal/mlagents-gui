import tkinter as tk
from tkinter import filedialog, ttk
from utils import get_conda_envs

class Step1Frame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_directory = ""

        # UI components
        self.greeting = tk.Label(
            self,
            text="Select your ML-Agents directory",
            font=("Arial", 14)
        )
        self.greeting.pack(pady=10)

        self.step1_label = tk.Label(
            self, 
            text="No directory selected",
            font=("Arial", 10)
        )
        self.step1_label.pack(pady=10)

        self.select_button = tk.Button(
            self,
            text="Select Directory",
            command=self.select_directory
        )
        self.select_button.pack(pady=5)

        self.clear_button = tk.Button(
            self,
            text="Clear Directory",
            command=self.clear_selection
        )
        self.clear_button.pack(pady=5)

        self.next_button = tk.Button(
            self,
            text = "Next",
            state = "disabled",
            command = lambda: controller.show_frame(controller.step2_frame)
        )
        self.next_button.pack(pady=5)
    
    # Open directory selection dialog
    def select_directory(self):
        # Select directory prompt
        directory = filedialog.askdirectory(title="Select a Directory")

        # If there is a directory
        if directory:
            self.selected_directory = directory
            self.step1_label.config(text=f"Selected Directory: {self.selected_directory}")
            self.next_button.config(state="normal")
            print(f"Selected Directory: {self.selected_directory}")
        else:
            print("No directory selected.")

    # Clear the selected directory
    def clear_selection(self):
        if self.selected_directory:
            selected_directory = ""
            self.step1_label.config(text="No directory selected")
            self.clear_button.config(state="disabled")
            self.next_button.config(state="disabled")

            print("Selected directory cleared!")
        else:
            print("There is no directory to clear")

class Step2Frame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.greeting = tk.Label(
            self,
            text="Select Virtual Environment",
            font=("Arial", 14)
        )
        self.greeting.pack(pady=10)

        self.step2_label_instruction = tk.Label(
            self, 
            text="Select a Conda environment from the list below",
            font=("Arial", 10)
        )
        self.step2_label_instruction.pack(pady=5)

        conda_envs = get_conda_envs()

        if conda_envs:
            env_dropdown = ttk.Combobox(
                self,
                values=conda_envs,
                state="readonly"
            )
            env_dropdown.set("Select Conda Environment")
            env_dropdown.pack(pady=10)
        else:
            env_dropdown = tk.Label(
                self,
                text="No Conda environments found."
            )
            env_dropdown.pack(pady=10)

        self.back_button = tk.Button(
            self,
            text="Back",
            command=lambda: controller.show_frame(controller.step1_frame)
        )
        self.back_button.pack(pady=5)