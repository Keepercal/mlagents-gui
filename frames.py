import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, ttk
from utils import get_conda_envs, begin_training

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
            state="disabled",
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
            self.controller.working_directory = directory

            self.step1_label.configure(text=f"Selected Directory: {self.controller.working_directory}")
            self.next_button.configure(state="normal")
            self.clear_button.configure(state="normal")

            print(f"Working Directory: {self.controller.working_directory}")
        else:
            print("No directory selected.")

    # Clear the selected directory
    def clear_selection(self):
        if self.controller.working_directory:
            self.contoller.working_directory = ""

            self.step1_label.configure(text="No directory selected")
            self.clear_button.configure(state="disabled")
            self.next_button.configure(state="disabled")

            print("Working directory cleared!")
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
        print(f"Using Virtual Environment: {self.controller.selected_env}")

        # Navigate to next frame
        self.controller.show_frame(self.controller.main_menu)

class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_config = ""
        
        self.greeting = ctk.CTkLabel(
            self,
            text="ML-Agents Control Panel",
            font=("Arial", 14)
        )

        self.start_button = ctk.CTkButton(
            self,
            text = "Start New Training Session",
            command = self.training_setup
        )
        self.start_button.pack(pady=5)

        self.back_button = ctk.CTkButton(
            self,
            text="Back",
            command=lambda: controller.show_frame(controller.step2_frame)
        )
        self.back_button.pack(pady=5)

    def training_setup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Enter Run ID")

        label1 = ctk.CTkLabel(
            popup,
            text="Enter the Run ID for this training session",
            font=("Arial", 12)
        )
        label1.pack(pady=10)

        id_entry = ctk.CTkEntry(
            popup,
            width=250
        )
        id_entry.pack(pady=10)

        label2 = ctk.CTkLabel(
            popup,
            text="Select the configuration file for this training session",
            font=("Arial", 12)
        )

        label2.pack(pady=10)

        label3 = ctk.CTkLabel(
            popup,
            text="No config file selected",
            font=("Arial", 12)
        )

        label3.pack(pady=10)

        # Open config selection dialog
        def select_config_file():
            # Select config prompt
            config = filedialog.askopenfilename(title="Select a Config file")

            # If there is a config file
            if config:
                self.selected_config = config
                label3.configure(text=f"Selected Config File: {self.selected_config}")
                start_button.configure(state="normal")
                clear_button.configure(state="normal")
                print(f"Selected Config File: {self.selected_config}")
            else:
                print("No config file selected.")

        select_button = ctk.CTkButton(
            popup,
            text="Select Config File",
            command=select_config_file
        )
        select_button.pack(pady=5)

        # Clear the selected config file
        def clear_selection():
            if self.selected_config:
                self.selected_config = ""
                label3.configure(text="No config file selected")
                clear_button.configure(state="disabled")
                start_button.configure(state="disabled")

                print("Selected config file cleared!")
            else:
                print("There is no config file to clear")

        clear_button = ctk.CTkButton(
            popup,
            text="Clear Config File",
            state="disabled",
            command=clear_selection
        )
        clear_button.pack(pady=5)

        def on_start():
            try:
                run_id = id_entry.get() # Retrieve user input
                if not run_id: # Validate the input
                    raise ValueError("Run ID is empty. Please provide a valid Run ID.")
                
                # Close the popup after processing
                if popup: # Ensure popup exists before destroying it
                    popup.destroy()

                # Begin training
                begin_training(self.controller, run_id, self.selected_config)

            except ValueError as ve:
                print(f"ValueError: {ve}")

            except AttributeError as ae:
                print(f"AttributeError: {ae}")

            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        start_button = ctk.CTkButton(
            popup,
            text="Begin",
            state="disabled",
            command=on_start
        )
        start_button.pack(pady=10)