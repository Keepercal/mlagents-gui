import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, ttk
from utils import get_conda_envs, activate_env, begin_training

class Step1Frame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_directory = ""

        # UI components
        self.greeting = ctk.CTkLabel(
            self,
            text="Select your ML-Agents directory",
            font=("Arial", 14)
        )
        self.greeting.pack(pady=10)

        self.step1_label = ctk.CTkLabel(
            self, 
            text="No directory selected",
            font=("Arial", 10)
        )
        self.step1_label.pack(pady=10)

        self.select_button = ctk.CTkButton(
            self,
            text="Select Directory",
            command=self.select_directory
        )
        self.select_button.pack(pady=5)

        self.clear_button = ctk.CTkButton(
            self,
            text="Clear Directory",
            command=self.clear_selection
        )
        self.clear_button.pack(pady=5)

        self.next_button = ctk.CTkButton(
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
            self.step1_label.configure(text=f"Selected Directory: {self.selected_directory}")
            self.next_button.configure(state="normal")
            print(f"Selected Directory: {self.selected_directory}")
        else:
            print("No directory selected.")

    # Clear the selected directory
    def clear_selection(self):
        if self.selected_directory:
            self.selected_directory = ""
            self.step1_label.configure(text="No directory selected")
            self.clear_button.configure(state="disabled")
            self.next_button.configure(state="disabled")

            print("Selected directory cleared!")
        else:
            print("There is no directory to clear")

class Step2Frame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_env = tk.StringVar()

        self.greeting = ctk.CTkLabel(
            self,
            text="Select Virtual Environment",
            font=("Arial", 14)
        )
        self.greeting.pack(pady=10)

        self.step2_label_instruction = ctk.CTkLabel(
            self, 
            text="Select a Conda environment from the list below",
            font=("Arial", 10)
        )
        self.step2_label_instruction.pack(pady=5)

        conda_envs = get_conda_envs()

        if conda_envs:
            self.env_dropdown = ttk.Combobox(
                self,
                values=conda_envs,
                state="readonly",
                textvariable=self.selected_env
            )
            self.env_dropdown.set("Select Conda Environment")
            self.env_dropdown.pack(pady=10)

            # Bind selection event to enable Next button
            self.env_dropdown.bind("<<ComboboxSelected>>", self.on_env_selected)
        else:
            env_dropdown = ctk.CTkLabel(
                self,
                text="No Conda environments found."
            )
            env_dropdown.pack(pady=10)

        self.next_button = ctk.CTkButton(
            self,
            text = "Next",
            state = "disabled",
            command = self.go_to_next
        )
        self.next_button.pack(pady=5)

        self.back_button = ctk.CTkButton(
            self,
            text="Back",
            command=lambda: controller.show_frame(controller.step1_frame)
        )
        self.back_button.pack(pady=5)

    def on_env_selected(self, event):
        # Enable the next button when a valid env is selected
        selected = self.selected_env.get()
        if selected and selected != "Select Conda Environment":
            self.next_button.configure(state="normal")

    def go_to_next(self):
        """Handle the transition to the next frame"""
        #Save the selected env to the controller
        self.controller.selected_env = self.selected_env.get()
        print(f"Selected Environment: {self.controller.selected_env}")

        # Navigate to next frame
        self.controller.show_frame(self.controller.main_menu)

class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.greeting = ctk.CTkLabel(
            self,
            text="ML-Agents Control Panel",
            font=("Arial", 14)
        )

        self.start_button = ctk.CTkButton(
            self,
            text = "Start Training",
            command = self.enter_run_id
        )
        self.start_button.pack(pady=5)

        self.back_button = ctk.CTkButton(
            self,
            text="Back",
            command=lambda: controller.show_frame(controller.step2_frame)
        )
        self.back_button.pack(pady=5)

    def enter_run_id(self):
        run_id_popup = ctk.CTkToplevel(self)
        run_id_popup.title("Enter Run ID")
        run_id_popup.geometry("300x150")

        label = ctk.CTkLabel(
            run_id_popup,
            text="Enter the run-id for this training session",
            font=("Arial", 12)
        )
        label.pack(pady=10)

        entry = ctk.CTkEntry(
            run_id_popup,
            width=250
        )
        entry.pack(pady=10)

        def on_ok():
            run_id = entry.get() # Retrieve user input
            if run_id:
                run_id_popup.destroy() # Close the popup after processing

                begin_training(self.controller, run_id)

        ok_button = ctk.CTkButton(
            run_id_popup,
            text="OK",
            command=on_ok
        )
        ok_button.pack(pady=10)