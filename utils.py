import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import customtkinter as ctk
import subprocess
import os
import threading
import signal
import select

def get_conda_envs():
    # Fetch a list of Conda environments
    try:
        result = subprocess.run(["conda", "env", "list"], stdout=subprocess.PIPE, text=True)
        envs = []
        for line in result.stdout.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            env_name = line.split()[0]
            envs.append(env_name)
        return envs
    except Exception as e:
        print(f"Error fetching environments: {e}")
        return []
    
def begin_training(controller, run_id, config_file):
        """Begins a new training session in a subprocess

        Args:
            controller (MLAgentsApp): The main application instance that acts as the controller for managing the application's state and navigation.
            run_id (str): The ID for the training session.
            config_file (str): The path to the configuation file for the training session.
        
        Returns:
            subprocess.Popen: The process object for the training session, or None if an error occurs.
        """
        print(f"\nAttempting to begin training with run-id: {run_id}")

        env = controller.selected_env
        working_dir = controller.working_directory # The selected ml-agents working directory
        results_dir = f"{working_dir}/results" # Base directory for results
        run_id_path = os.path.join(results_dir, run_id) # Contruct the full path for the run_id

        if not env: # Check if the environment is valid
            print("Error: No environment selected for training!")
            return
        
        # Check if the directory exists
        force_flag = ""
        if os.path.exists(run_id_path) and os.path.isdir(run_id_path):
            # Show an alert window to confirm overwriting
            overwrite = messagebox.askyesno(
                "Existing Run-ID",
                message=f'A result with the Run ID "{run_id}" already exists.',
                detail=f'Do you want to force start training and overwrite the previous result?',
            )
            if not overwrite:
                print("Training session cancelled by the user.")
                return

            # User chose to overwrite, add the --force flag
            print("User chose to overwrite. Adding --force flag")
            force_flag = "--force"

        try:
            # Command to run the training session
            command = f"source activate base && conda activate {env} && mlagents-learn {config_file} --run-id={run_id} {force_flag}"

            # Create the popup to show training output
            output_popup = create_output_popup(controller, run_id)

            process = subprocess.Popen(
                command,
                shell=True,
                cwd=controller.working_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Use a seperate thread to read subprocess output
            threading.Thread(target=stream_process_output, args=(process, output_popup), daemon=True).start()

            # Store the process in the controller
            controller.current_training_process = process

            print(f"Training started with run-id: {run_id}")
            return process

        except Exception as e:
            print("Error", f"Failed to begin training. \n\n{str(e)}")

            if env:
                deactivate_env(env, process)
                print(f'Deactivating virtual environment "{env}"" as a consequence')

            return None
        
def create_output_popup(controller, run_id):
    """Creates a popup window to display training output."""
    popup = ctk.CTkToplevel(controller)
    popup.title(f"{run_id}")
    popup.geometry("600x400")

    label = ctk.CTkLabel(
        popup,
        text=f'Training output for session: {run_id}',
        font=("Arial", 14)
    )
    label.pack(pady=10)

    # ScrolledText widget to show output
    text_widget = scrolledtext.ScrolledText(
        popup, 
        wrap=tk.WORD,
        font=("Courier", 10)
    )
    text_widget.pack(expand=True, fill="both", padx=10, pady=10)

    def end_training():
        """Signals to end the training session."""
        process = getattr(controller, 'current_training_process', None) 

        if process and process.poll() is None:
            try:
                process.send_signal(signal.SIGINT) # Send SIGINT to terminate the process
                process.wait(timeout=5) # Allow a short period for graceful termination

                print("Attempting to terminate training session gracefully...")
                
                # If process hasn't ended, forcefully terminate it
                if process.poll() is None:
                    print("Process not terminated gracefully, forcing termination...")
                    process.terminate() # Send SIGTERM to terminate gracefully (less aggressive)
                    process.wait(timeout=15)

                # If the process still hasn't terminated, kill it
                if process.poll() is None:
                    print("Process still running, killing it...")
                    process.kill()

                print("Training session terminated.")

                text_widget.insert(
                    tk.END,
                    "\n Training session terminated.\n"
                )

                end_button.configure(state="disabled")
                close_button.configure(state="normal")

            except Exception as e:
                print(f"Failed to terminate training session: {e}")
                text_widget.insert(
                    tk.END,
                    f"\nError terminating session: {e}\n"
                )
        else:
            print("No active training session to terminate.")
            text_widget.insert(
                tk.END,
                "\nNo active training session to terminate.\n"
            )

    end_button = ctk.CTkButton(
        popup,
        text="End Training Session",
        command=end_training
    )
    end_button.pack(pady=5)

    close_button = ctk.CTkButton(
        popup,
        text="Close",
        state="disabled",
        command=popup.destroy
    )
    close_button.pack(pady=5)

    return text_widget

def stream_process_output(process, text_widget):
    """Streams the subprocess output to the given text widget."""
    def append_text(data):
        text_widget.insert(tk.END, data)
        text_widget.see(tk.END) # Auto-scroll to the end

    while process.poll() is None:
        readable, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
        for stream in readable:
            line = stream.readline()
            if line:
                text_widget.after(0, append_text, line)
    
    # Handle remaining output after process ends
    for stream in (process.stdout, process.stderr):
        for line in stream:
            text_widget.after(0, append_text, line)
    
    # Mark process as finished
    text_widget.after(0, append_text, "\n[Training Session Ended]\n")

def deactivate_env(env, process):
    "Deactivates the selected virtual environment in a subprocess"

    if not env: # If there is no environment inside env
        print("There is no environment to deactivate...")
        return
    
    print(f"Attempting to deactivate virtual environment: {env}\n")

    try:
        command = f"conda deactivate && conda info --envs"
        subprocess.Popen(command, shell=True)

        print(f'Virtual environment "{env}" is now deactivated')

    except Exception as e:
        messagebox.showerror("Error", f"Failed to deactivate the environment.\n\n{str(e)}")