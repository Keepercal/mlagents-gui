import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, ttk
from utils.utils import get_conda_envs, save_settings, get_conda_exe, logging

class Step1Frame(ctk.CTkFrame):
    """ Step 1 of setting up the CTRL panel. User chooses their working directory (their ML-Agents clone)

    Args:
        ctk (CTkFrame): The base class for creating a CustomTkinter frame, providing the functionality 
        to organize and manage widgets within a frame in the application.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_directory = "" # Stores the user's choice in this instance.

        self.initialise_ui()

    def initialise_ui(self):
        """ Initialises the UI components of this frame. """
        self.greeting = ctk.CTkLabel(
            self,
            text="Select your ML-Agents directory",
            font=("Arial", 14)
        )
        self.greeting.pack(pady=10)

        self.info_label = ctk.CTkLabel(
            self, 
            text="No directory selected",
            font=("Arial", 10)
        )
        self.info_label.pack(pady=10)

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
            command = lambda: self.controller.show_frame(self.controller.step2_frame)
        )
        self.next_button.pack(pady=5)
    
    def select_directory(self):
        """ Prompts the user to select their ML-Agents working directory. """
        mlagents_directory = filedialog.askdirectory(title="Select a Directory")

        # If there is a directory
        if mlagents_directory:
            self.controller.mlagents_dir = mlagents_directory # Set the user's ML-Agents working directory in the main application

            # Enable buttons
            self.info_label.configure(text=f"Selected Directory: {self.controller.mlagents_dir}")
            self.next_button.configure(state="normal")
            self.clear_button.configure(state="normal")

            logging.info(f"Selected Directory: {self.controller.mlagents_dir}")
        else:
            logging.warning("No directory selected.")

    def clear_selection(self):
        """ Clears the given working directory """
        if self.controller.mlagents_dir:
            self.controller.mlagents_dir = "" # Clear the user's ML-Agents working directory in the main application

            # Disable buttons
            self.info_label.configure(text="No directory selected")
            self.clear_button.configure(state="disabled")
            self.next_button.configure(state="disabled")

            logging.info("Working directory cleared.")
        else:
            logging.info("There is no directory to clear.")

class Step2Frame(ctk.CTkFrame):
    """ Step 2 of setting up the CTRL panel. User chooses their Anaconda installation

    Args:
        ctk (CTkFrame): The base class for creating a CustomTkinter frame, providing the functionality 
        to organize and manage widgets within a frame in the application.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_conda_dir = ""

        self.initialise_ui()

    def initialise_ui(self):
        """ Initialises the UI components of this frame.

        Args:
            controller (MLAgentsCTRL): The application's controller, used for navigating between frames.
        """
        self.greeting = ctk.CTkLabel(
            self,
            text="Select your Anaconda installation",
            font=("Arial", 14)
        )
        self.greeting.pack(pady=10)

        self.info_label = ctk.CTkLabel(
            self, 
            text="No installation selected",
            font=("Arial", 10)
        )
        self.info_label.pack(pady=10)

        self.select_button = ctk.CTkButton(
            self,
            text="Select Installation",
            command=self.select_installation
        )
        self.select_button.pack(pady=5)

        self.clear_button = ctk.CTkButton(
            self,
            text="Clear Installation",
            state="disabled",
            command=self.clear_selection
        )
        self.clear_button.pack(pady=5)

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
            command=lambda: self.controller.show_frame(self.controller.step1_frame)
        )
        self.back_button.pack(pady=5)

    def select_installation(self):
        """ Prompts the user to select their Anaconda installion directory. """
        conda_directory = filedialog.askdirectory(title="Select your Anaconda Installation")

        # If there is a directory
        if conda_directory:
            self.controller.conda_dir = conda_directory # Set the user's Conda installation in the main application.

            # Enable buttons
            self.info_label.configure(text=f" Selected Installation: {self.controller.conda_dir}")
            self.next_button.configure(state="normal")
            self.clear_button.configure(state="normal")

            logging.info(f"Selected Conda Installation Directory: {self.controller.conda_dir}")
        else:
            logging.info("No conda installation selected.")

    def clear_selection(self):
        """ Clears the given Anaconda installation """
        if self.controller.conda_dir:
            self.controller.conda_dir = "" # Clear the user's Conda installation in the main application

            self.info_label.configure(text="No installation selected")
            self.clear_button.configure(state="disabled")
            self.next_button.configure(state="disabled")

            print("    [ALERT] Anaconda installation cleared!")
            logging.info("Anaconda installation cleared!")
        else:
            logging.info("There is no Anaconda installation to clear.")

    def go_to_next(self):
        """ Moves to the next frame. """
        try:
            conda_exe = get_conda_exe(self.controller.conda_dir) # Get the path of the Anaconda executable
            if conda_exe:
                self.controller.conda_exe = conda_exe # Store the executable in the main application 
                try:
                    self.controller.conda_envs = get_conda_envs(conda_exe) # Get a list of Conda environments from the given .exe
                    logging.info(f"Retrieved Conda envirobments: {self.controller.conda_envs}")
                    self.controller.step3_frame.env_dropdown['values'] = self.controller.conda_envs # Populate the Step 3 dropdown with envs
                except Exception as e:
                    logging.error(f"Encountered an issue when retrieving Conda environments: {e}")
        except Exception as e:
            logging.error(f"Failed to retrieve Anaconda executable: {e}")

        self.controller.show_frame(self.controller.step3_frame)

class Step3Frame(ctk.CTkFrame):
    """ Step 3 of setting up the CTRL panel. User chooses their working virtual environment

    Args:
        ctk (CTkFrame): The base class for creating a CustomTkinter frame, providing the functionality 
        to organize and manage widgets within a frame in the application.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.virtual_env = tk.StringVar() # The chosen virtual environment to use.
        self.conda_envs = self.controller.conda_envs # A list of avaliable Conda environments.

        self.initialise_ui()

    def initialise_ui(self):
        """ Initialises the UI components of this frame.

        Args:
            controller (MLAgentsCTRL): The application's controller, used for navigating between frames.
        """
        
        self.greeting = ctk.CTkLabel(
            self,
            text="Select Virtual Environment",
            font=("Arial", 14)
        )
        self.greeting.pack(pady=10)

        self.info_label = ctk.CTkLabel(
            self, 
            text="Select a Conda environment from the list below",
            font=("Arial", 10)
        )
        self.info_label.pack(pady=5)

        self.env_dropdown = ttk.Combobox(
            self,
            values=[],
            state="readonly",
            textvariable=self.virtual_env
        )
        self.env_dropdown.set("Select Conda Environment")
        self.env_dropdown.pack(pady=10)

        # Bind selection event to enable Next button
        self.env_dropdown.bind("<<ComboboxSelected>>", self.on_env_selected)
        self.env_dropdown.pack(pady=10)

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
            command=lambda: self.controller.show_frame(self.controller.step2_frame)
        )
        self.back_button.pack(pady=5)

    def on_env_selected(self, event=None):
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