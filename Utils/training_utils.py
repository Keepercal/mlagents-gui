from Utils.utils import logging
from Utils.process_utils import initialise_process, end_process, stream_process_output, stop_event

import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import customtkinter as ctk
import os
import threading

class TrainingPopup(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.run_id = tk.StringVar()
        self.config_file = ""

        self.initialise_setup_ui()

    def initialise_setup_ui(self):
        """ Creates a popup window where the user can enter a name for the training session and select a config file"""

        self.title("Configure new training session")

        self.setup_frame = ctk.CTkFrame(self)
        self.setup_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.label1 = ctk.CTkLabel(
            self.setup_frame,
            text="Enter the Run ID for this training session",
            font=("Arial", 12)
        )
        self.label1.pack(pady=10)

        self.id_entry = ctk.CTkEntry(
            self.setup_frame,
            textvariable=self.run_id,
            width=250
        )
        self.id_entry.pack(pady=10)

        self.label2 = ctk.CTkLabel(
            self.setup_frame,
            text="Select the configuration file for this training session",
            font=("Arial", 12)
        )

        self.label2.pack(pady=10)

        self.label3 = ctk.CTkLabel(
            self.setup_frame,
            text="No config file selected",
            font=("Arial", 12)
        )

        self.label3.pack(pady=10)

        self.select_button = ctk.CTkButton(
            self.setup_frame,
            text="Select Config File",
            command=self.select_config_file
        )
        self.select_button.pack(pady=5)

        self.clear_button = ctk.CTkButton(
            self.setup_frame,
            text="Clear Config File",
            state="disabled",
            command=self.clear_selection
        )
        self.clear_button.pack(pady=5)

        self.start_button = ctk.CTkButton(
            self.setup_frame,
            text="Begin",
            state="disabled",
            command=self.on_start
        )
        self.start_button.pack(pady=10)

    def select_config_file(self):
        """ Prompts the user to select a config.yaml file"""
        # Select config prompt
        config = filedialog.askopenfilename(title="Select a Config file")

        # If there is a config file
        if config:
            self.selected_config = config
            self.label3.configure(text=f"Selected Config File: {self.selected_config}")
            self.start_button.configure(state="normal")
            self.clear_button.configure(state="normal")
            print(f"[INFO] Selected Config File: {self.selected_config}")
        else:
            print("[ALERT] No config file selected.")

    def clear_selection(self):
        """ Clears the selected config file """
        if self.selected_config:
            self.selected_config = ""
            self.label3.configure(text="No config file selected")
            self.clear_button.configure(state="disabled")
            self.start_button.configure(state="disabled")

            print("    [ALERT] Selected config file cleared!")
        else:
            print("    [ALERT] There is no config file to clear")

    def on_start(self):
        """ Executes when the user presses the begin button."""
        try:
            run_id = self.run_id.get() # Retrieve user input
            if not run_id: # Validate the input
                raise ValueError("Run ID is empty. Please provide a valid Run ID.")

            # Begin training
            self.begin_training()

        except ValueError as ve:
            print(f"ValueError: {ve}")

        except AttributeError as ae:
            print(f"AttributeError: {ae}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def initalise_training_ui(self):
        if hasattr(self, "setup_frame"):
            self.setup_frame.destroy()

        self.title(f"Training Session: {self.run_id.get()}")
        self.geometry("600x400")

        label = ctk.CTkLabel(
            self,
            text=f'Training session "{self.run_id.get()}" initialised, press play in the Unity editor to begin training',
            font=("Arial", 14)
        )
        label.pack(pady=10)

        # ScrolledText widget to show output
        self.text_widget = scrolledtext.ScrolledText(
            self, 
            wrap=tk.WORD,
            font=("Courier", 10)
        )
        self.text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        self.end_button = ctk.CTkButton(
        self,
        text="End Training Session",
            command=self.signal_to_end
        )
        self.end_button.pack(pady=5)

        self.close_button = ctk.CTkButton(
            self,
            text="Close",
            state="disabled",
            command=self.close_popup
        )
        self.close_button.pack(pady=5)

    def close_popup(self):
        """ Close the popup and stop streaming process if necessary """
        stop_event.set() # Stop the output streaming thread
        self.destroy() # Destroy the popup window

    def begin_training(self):
        """Begins a new training session in a subprocess

        Args:
            controller (MLAgentsCTRL): The main application instance that acts as the controller for managing the application's state and navigation.
        
        Returns:
            subprocess.Popen: The process object for the training session, or None if an error occurs.
        """
        print(f"\n[ALERT] Attempting to begin training with run-id: {self.run_id.get()}")

        env = self.controller.virtual_env # The user's virtual environment.
        mlagents_dir = self.controller.mlagents_dir # The user's selected ML-Agents directory.
        results_dir = f"{mlagents_dir}/results" # Directory for training results.
        run_id_path = os.path.join(results_dir, self.run_id.get()) # Contruct the full path for the run_id.
        force_flag = "" # OPTIONAL: The flag which forces a training session to begin.

        # Check if the environment is valid.
        if not env:
            logging.error("No environment selected for training.")
            return
        
        # Check if a result already exists with the given run-id
        if os.path.exists(run_id_path) and os.path.isdir(run_id_path):
            logging.warning(f"Previous result found for Run ID '{self.run_id.get()}'. Prompting user for overwrite.")

            # Show an alert window to confirm overwriting
            overwrite = messagebox.askyesno(
                "Existing Run-ID",
                message=f'A result with the Run ID "{self.run_id.get()}" already exists.',
                detail=f'Do you want to force start training and overwrite the previous result?',
            )
            if not overwrite:
                logging.info("Training session cancelled by user.")
                return

            # If user chose to overwrite, add the --force flag.
            logging.info("User confirmed overwrite. Adding --force flag.")
            force_flag = "--force"

            self.initalise_training_ui()

        # Try to begin the training session.
        try:
            logging.info(f"Attempting to start training with Run ID: '{self.run_id.get()}'")

            command = f"source activate base && conda activate {env} && mlagents-learn {self.config_file} --run-id={self.run_id.get()} {force_flag}"

            process = initialise_process(self.controller, command) # Initialise a new process for the training session

            if process is None:
                logging.error(f"Failed to initialise process with command: {command}")
                return None

            # Use a seperate thread to read subprocess output
            threading.Thread(target=stream_process_output, args=(process, self.text_widget), daemon=True).start()

            # Store the process in the controller
            self.controller.current_training_process = process

            return process

        except Exception as e:
            logging.error(f"Failed to begin training: {str(e)}")

            if env:
                #deactivate_env(env, process)
                logging.debug(f'Deactivating virtual environment "{env}" as a consequence.')

            return None

    def signal_to_end(self):
        """Signals to end the training session."""
        if not hasattr(self, 'text_widget'):
            self.text_widget = None
            logging.error("signal_to_end called before text_widget initialisation!")
            return
        
        process = getattr(self.controller, 'current_training_process', None) # Get the current process from the controller

        if process and process.poll() is None:
            try:
                end_process(process)

                # Process terminated successfully
                logging.info("User ended the training session.")
                self.text_widget.after(
                    0,
                    self.text_widget.insert,
                    tk.END,
                    "\n[CTRL Panel] Training session ended by user.\n"
                )

                self.end_button.after(0, lambda: self.end_button.configure(state="disabled"))
                self.close_button.after(0, lambda: self.close_button.configure(state="normal"))

            except Exception as e:
                logging.error(f"Failed to end training session: {e}")
                self.text_widget.after(
                    0,
                    self.text_widget.insert,
                    tk.END,
                    f"\n[ERROR] Encountered a problem ending session: {e}\n"
                )
        else:
            logging.info("No activate training session to end.")
            self.text_widget.insert(
                tk.END,
                "\n[CTRL Panel] No active training session to end.\n"
            )

        return self.text_widget