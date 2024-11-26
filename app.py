import tkinter as tk
import customtkinter as ctk
from frames import Step1Frame, Step2Frame, MainMenu
from utils import load_settings
from tkinter import PhotoImage
import os

SETTINGS_FILE = "settings.json"

class MLAgentsApp(ctk.CTk):
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

        self.title("ML-Agents Control Panel")
        self.iconphoto(False, PhotoImage(file="icon.png"))
        #self.geometry("500x400")

    def initialise_variables(self):
        """ Initialises application variables. """
        self.working_dir = None
        self.virtual_env = None
        self.current_training_process = None

        print(f"    working_dir: {self.working_dir}")
        print(f"    virtual_env: {self.virtual_env}")

    def initialise_frames(self):
        """ Initialises the different frames for the application """
        self.step1_frame = Step1Frame(self, self)
        self.step2_frame = Step2Frame(self, self)
        self.main_menu = MainMenu(self, self)

    def place_frames(self):
        """ Place the frames in the window using a grid layout. """
        for frame in (self.step1_frame, self.step2_frame, self.main_menu):
            frame.grid(row=0, column=0, sticky="nsew")

    def handle_settings_file(self):
        """" Handles the loading of settings from the settings.json file """
        if os.path.exists(SETTINGS_FILE): # Show the main menu if settings file exists
            load_settings(self)
            self.show_frame(self.main_menu)
        else: # Proceed to setup if settings file does not exist
            print("[INFO] Cannot find settings file, proceeding to setup.")
            self.show_frame(self.step1_frame)

    def show_frame(self, frame):
        """ Handles switching between frames """
        frame.tkraise()

if __name__ == "__main__":
    app = MLAgentsApp()
    app.mainloop()
