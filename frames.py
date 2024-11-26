import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, ttk
from utils import get_conda_envs, begin_training, save_settings

class Step1Frame(ctk.CTkFrame):
    """ Step 1 of setting up the CTRL panel. User chooses their working directory (their ML-Agents clone)

    Args:
        ctk (CTkFrame): The base class for creating a CustomTkinter frame, providing the functionality 
        to organize and manage widgets within a frame in the application.
    """
    def __init__(self, parent, controller):
        """ Initialises the frame and its components

        Args:
            parent (tk.Widget): The parent widget which the frame belongs to.
            controller (MLAgentsApp): The application controller, used for navigating between frames
        """
        super().__init__(parent)
        self.controller = controller
        self.selected_directory = ""

        self.initialise_ui(controller)

    def initialise_ui(self, controller):
        """ Initialises the UI components of this frame.

        Args:
            controller (MLAgentsApp): The application's controller, used for navigating between frames.
        """
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
    
    def select_directory(self):
        """ Prompts the user to select their ML-Agents working directory """
        directory = filedialog.askdirectory(title="Select a Directory")

        # If there is a directory
        if directory:
            self.controller.working_dir = directory

            self.step1_label.configure(text=f"Selected Directory: {self.controller.working_dir}")
            self.next_button.configure(state="normal")
            self.clear_button.configure(state="normal")

            print(f"    Selected Directory: {self.controller.working_dir}")
        else:
            print("[ALERT] No directory selected.")

    def clear_selection(self):
        """ Clears the given working directory """
        if self.controller.working_dir:
            self.controller.working_dir = ""

            self.step1_label.configure(text="No directory selected")
            self.clear_button.configure(state="disabled")
            self.next_button.configure(state="disabled")

            print("    [ALERT] Working directory cleared!")
        else:
            print("    [ALERT] There is no directory to clear")

class Step2Frame(ctk.CTkFrame):
    """ Step 2 of setting up the CTRL panel. User chooses their working virtual environment

    Args:
        ctk (CTkFrame): The base class for creating a CustomTkinter frame, providing the functionality 
        to organize and manage widgets within a frame in the application.
    """
    def __init__(self, parent, controller):
        """ Initialises the frame and its components

        Args:
            parent (tk.Widget): The parent widget which the frame belongs to.
            controller (MLAgentsApp): The application controller, used for navigating between frames
        """
        super().__init__(parent)
        self.controller = controller

        self.virtual_env = tk.StringVar()

        self.initialise_ui(controller)

    def initialise_ui(self, controller):
        """ Initialises the UI components of this frame.

        Args:
            controller (MLAgentsApp): The application's controller, used for navigating between frames.
        """
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
                textvariable=self.virtual_env
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

        self.save_button = ctk.CTkButton(
            self,
            text = "Save & Continue",
            state = "disabled",
            command = self.go_to_next
        )
        self.save_button.pack(pady=5)

        self.back_button = ctk.CTkButton(
            self,
            text="Back",
            command=lambda: controller.show_frame(controller.step1_frame)
        )
        self.back_button.pack(pady=5)

    def on_env_selected(self):
        """ Enables the save button to be clickable when a virtual environment is selected. """
        selected = self.virtual_env.get()
        if selected and selected != "Select Conda Environment":
            self.save_button.configure(state="normal")

    def go_to_next(self):
        """Save the user settings and handle the transition to the next frame"""
        self.controller.virtual_env = self.virtual_env.get() #Save the selected env to the controller
        print(f"    Selected Virtual Environment: {self.controller.virtual_env}")
        
        save_settings(self.controller)

        # Navigate to next frame
        self.controller.show_frame(self.controller.main_menu)

class MainMenu(ctk.CTkFrame):
    """ The main menu of the application.

    Args:
        ctk (CTkFrame): The base class for creating a CustomTkinter frame, providing the functionality 
        to organize and manage widgets within a frame in the application.
    """
    def __init__(self, parent, controller):
        """ Initialises the frame and its components

        Args:
            parent (tk.Widget): The parent widget which the frame belongs to.
            controller (MLAgentsApp): The application controller, used for navigating between frames
        """
        super().__init__(parent)
        self.controller = controller
        self.selected_config = ""

        self.initialise_ui(controller)
        
    def initialise_ui(self, controller):
        """ Initialises the UI components of this frame.

        Args:
            controller (MLAgentsApp): The application's controller, used for navigating between frames.
        """
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
        """ Creates a popup window where the user can enter a name for the training session and select a config file"""
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

        def select_config_file():
            """ Prompts the user to select a config.yaml file"""
            # Select config prompt
            config = filedialog.askopenfilename(title="Select a Config file")

            # If there is a config file
            if config:
                self.selected_config = config
                label3.configure(text=f"Selected Config File: {self.selected_config}")
                start_button.configure(state="normal")
                clear_button.configure(state="normal")
                print(f"[INFO] Selected Config File: {self.selected_config}")
            else:
                print("[ALERT] No config file selected.")

        select_button = ctk.CTkButton(
            popup,
            text="Select Config File",
            command=select_config_file
        )
        select_button.pack(pady=5)

        def clear_selection():
            """ Clears the selected config file """
            if self.selected_config:
                self.selected_config = ""
                label3.configure(text="No config file selected")
                clear_button.configure(state="disabled")
                start_button.configure(state="disabled")

                print("    [ALERT] Selected config file cleared!")
            else:
                print("    [ALERT] There is no config file to clear")

        clear_button = ctk.CTkButton(
            popup,
            text="Clear Config File",
            state="disabled",
            command=clear_selection
        )
        clear_button.pack(pady=5)

        def on_start():
            """ Executes when the user presses the begin button."""
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