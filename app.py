import tkinter as tk
import customtkinter as ctk
from frames import Step1Frame, Step2Frame, MainMenu
from utils import load_settings
import os

CONFIG_FILE = "config.json"

class MLAgentsApp(ctk.CTk):
    def __init__(self):
        # Main window setup
        super().__init__()
        self.title("ML-Agents Control Panel")
        #self.geometry("500x400")

        print("[ALERT] Starting app!")

        # Stores selected virtual env
        self.working_dir = None
        self.virtual_env = None
        self.current_training_process = None

        print(f"    working_dir: {self.working_dir}")
        print(f"    virtual_env: {self.virtual_env}")

        # Initialise frames
        self.step1_frame = Step1Frame(self, self)
        self.step2_frame = Step2Frame(self, self)
        self.main_menu = MainMenu(self, self)

        # Place frames
        for frame in (self.step1_frame, self.step2_frame, self.main_menu):
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the frame
        if os.path.exists(CONFIG_FILE): # Show the main menu if config file exists
            load_settings(self)
            self.show_frame(self.main_menu)
        else: # Proceed to setup if config file does not exist
            print("[INFO] Cannot find config file, proceeding to setup.")
            self.show_frame(self.step1_frame)

    # Switch between frames
    def show_frame(self, frame):
        frame.tkraise()

if __name__ == "__main__":
    app = MLAgentsApp()
    app.mainloop()
