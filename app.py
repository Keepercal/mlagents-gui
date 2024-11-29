import tkinter as tk
import customtkinter as ctk
from frames import Step1Frame, Step2Frame, Step3Frame, MainMenu
from utils import load_settings
from tkinter import PhotoImage
import os
import sys

SETTINGS_FILE = "settings.json"

def get_resource_path(realative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller. """
    try:
        #PyInstaller creates a temp folder and stores the app in it
        base_path = sys._MEIPASS
    except Exception as e:
        # If not running in PyInstaller, use the normal file system
        base_path = os.path.dirname(__file__)
    
    return os.path.join(base_path, realative_path)

class MLAgentsCTRL(ctk.CTk):
    """ Main application class for managing the ML Agents user interface.

    Args:
        ctk (CTk): The base class for CustomTkinter applications, providing functionality for 
        creating modern and customisable GUI applications.
    """
    def __init__(self):
        super().__init__()
        self.setup_main_window()
        self.initialise_variables()
        self.initialise_frames()
        self.place_frames()
        self.handle_settings_file()

    def setup_main_window(self):
        """ Setup the main application window, including the title and icon. """
        print("[ALERT] Starting app!")

        self.title("ML-Agents CTRL")

        # Use the get_resource_path function to get the correct icon path
        #icon_path = get_resource_path("icon.png")
        #self.iconphoto(False, PhotoImage(file=icon_path))

        # self.geometry("500x400")

    def initialise_variables(self):
        """ Initialises application variables. """
        self.mlagents_dir = None
        self.conda_dir = None
        self.conda_exe = None
        self.conda_envs = []
        self.virtual_env = None
        self.current_training_process = None

    def print_variables(self):
        print(f"    mlagents_dir: {self.mlagents_dir}")
        print(f"    conda_dir: {self.conda_dir}")
        print(f"    conda_exe: {self.conda_exe}")
        print(f"    conda_envs: {self.conda_envs}")
        print(f"    virtual_env: {self.virtual_env}")

    def initialise_frames(self):
        try:
            print("[INFO] Initialising frames...")  # Debugging line
            """ Initialises the different frames for the application """
            self.step1_frame = Step1Frame(self, self)
            self.step2_frame = Step2Frame(self, self)
            self.step3_frame = Step3Frame(self, self)
            self.main_menu = MainMenu(self, self)
        except Exception as e:
            print(f"[ERROR] Encountered an issue initialising frames: {e}")

    def place_frames(self):
        """ Place the frames in the window using a grid layout. """
        for frame in (self.step1_frame, self.step2_frame, self.step3_frame, self.main_menu):
            frame.grid(row=0, column=0, sticky="nsew")

    def handle_settings_file(self):
        """" Handles the loading of settings from the settings.json file """
        if os.path.exists(SETTINGS_FILE): # Show the main menu if settings file exists
            print("    Settings file found! Skipping setup.")
            load_settings(self)
            self.show_frame(self.main_menu)
        else: # Proceed to setup if settings file does not exist
            print("    [INFO] No settings file found, proceeding to setup.")
            self.show_frame(self.step1_frame)

    def show_frame(self, frame):
        """ Handles switching between frames """
        frame.tkraise()
        print(f"[ALERT] Frame {frame} should be displayed now")
        self.print_variables()

if __name__ == "__main__":
    app = MLAgentsCTRL()
    app.mainloop()
