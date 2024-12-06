from Frames.setup_frames import Step1Frame, Step2Frame, Step3Frame
from Frames.main_frames import MainMenuFrame
from Utils.utils import load_settings, get_resource_path, logging, print_variables

import tkinter as tk
import customtkinter as ctk
from tkinter import PhotoImage
import os

SETTINGS_FILE = "settings.json"

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
        logging.info("Starting application.")

        self.title("ML-Agents CTRL")

        # Use the get_resource_path function to get the correct icon path
        icon_path = get_resource_path("Images/icon.png")
        self.iconphoto(False, PhotoImage(file=icon_path))

        # self.geometry("500x400")

    def initialise_variables(self):
        """ Initialises application variables. """
        try:
            logging.debug("Initialising environment configuration.")
            self.mlagents_dir = None
            self.conda_dir = None

            self.conda_exe = None
            self.conda_envs = []
            self.virtual_env = None

            self.current_training_process = None
        except Exception as e:
            logging.error(f"Failed to initalise variables: {e}")

    def initialise_frames(self):
        """ Initialises the different frames for the application. """
        try:
            logging.debug("Initialising frames.")

            self.step1_frame = Step1Frame(self, self)
            self.step2_frame = Step2Frame(self, self)
            self.step3_frame = Step3Frame(self, self)
            self.main_menu = MainMenuFrame(self, self)
        except Exception as e:
            logging.error(f"Encountered an issue initialising frames: {e}")

    def place_frames(self):
        """ Place the frames in the window using a grid layout. """
        try:
            logging.debug("Placing frames in the grid.")
            for frame in (self.step1_frame, self.step2_frame, self.step3_frame, self.main_menu):
                frame.grid(row=0, column=0, sticky="nsew")
        except Exception as e:
            logging.error(f"Encountered an issue placing frames: {e}")

    def handle_settings_file(self):
        """" Handles the loading of settings from the settings.json file """
        if os.path.exists(SETTINGS_FILE): # Show the main menu if settings file exists
            logging.info("Settings file found. Skipping setup process.")
            load_settings(self)
            self.show_frame(self.main_menu)
        else: # Proceed to setup if settings file does not exist
            logging.info("No settings file found. Proceeding to environment setup.")
            self.show_frame(self.step1_frame)

    def show_frame(self, frame):
        """ Handles switching between frames """
        frame.tkraise()
        logging.info(f"Frame {frame} should be displayed now.")
        print_variables(self)

if __name__ == "__main__":
    app = MLAgentsCTRL()
    app.mainloop()
