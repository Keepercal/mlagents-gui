import tkinter as tk
import customtkinter as ctk
from Utils.training_utils import TrainingPopup

class MainMenuFrame(ctk.CTkFrame):
    """ The main menu of the application.

    Args:
        ctk (CTkFrame): The base class for creating a CustomTkinter frame, providing the functionality 
        to organize and manage widgets within a frame in the application.
    """
    def __init__(self, parent, controller):
        """ Initialises the frame and its components

        Args:
            parent (tk.Widget): The parent widget which the frame belongs to.
            controller (MLAgentsCTRL): The application controller, used for navigating between frames
        """
        super().__init__(parent)
        self.controller = controller
        self.selected_config = ""

        self.initialise_ui(controller)
        
    def initialise_ui(self, controller):
        """ Initialises the UI components of this frame.

        Args:
            controller (MLAgentsCTRL): The application's controller, used for navigating between frames.
        """
        self.greeting = ctk.CTkLabel(
            self,
            text="ML-Agents Control Panel",
            font=("Arial", 14)
        )

        self.start_button = ctk.CTkButton(
            self,
            text = "Start New Training Session",
            command = self.create_popup
        )
        self.start_button.pack(pady=5)

        self.back_button = ctk.CTkButton(
            self,
            text="Back",
            command=lambda: controller.show_frame(controller.step3_frame)
        )
        self.back_button.pack(pady=5)

    def create_popup(self):
        TrainingPopup(self, self.controller)