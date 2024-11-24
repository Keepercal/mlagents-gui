import tkinter as tk
import customtkinter as ctk
from frames import Step1Frame, Step2Frame, MainMenu

class MLAgentsApp(ctk.CTk):
    def __init__(self):
        # Main window setup
        super().__init__()
        self.title("ML-Agents Control Panel")
        #self.geometry("500x400")

        # Stores selected virtual env
        self.working_directory = None
        self.selected_env = None

        # Initialise frames
        self.step1_frame = Step1Frame(self, self)
        self.step2_frame = Step2Frame(self, self)
        self.main_menu = MainMenu(self, self)

        # Place frames
        for frame in (self.step1_frame, self.step2_frame, self.main_menu):
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the first frame
        self.show_frame(self.step1_frame)

    # Switch between frames
    def show_frame(self, frame):
        frame.tkraise()

if __name__ == "__main__":
    app = MLAgentsApp()
    app.mainloop()
