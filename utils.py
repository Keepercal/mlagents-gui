import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import customtkinter as ctk
import subprocess
import os
import threading
import signal
import select
import json

SETTINGS_FILE = "settings.json"

def load_settings(controller):
    """ Loads user settings from JSON file, if one exists"""

    print("[ALERT] Trying to load saved settings...")

    if os.path.exists(SETTINGS_FILE):
        print("    Settings file found! Skipping setup.")
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)

                controller.working_dir = settings.get("working_dir", "")
                controller.virtual_env = settings.get("virtual_env", "")

                print(f"        working_dir: {controller.working_dir}"),
                print(f"        virtual_env: {controller.virtual_env}")
        except Exception as e:
            messagebox.showerror(
                title="Error!",
                message=f"Failed to load settings: {e}"
            )
    else:
        print("    [INFO] No settings file found. Proceeding with setup.")
        return None

def save_settings(controller):
    settings = {
        "working_dir": controller.working_dir,
        "virtual_env": controller.virtual_env
    }
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        messagebox.showinfo("Saved", "Settings have been saved successfully!")

        print("[SUCCESS] Settings have been saved for future use!")
        print(f"    working_dir: {controller.working_dir}")
        print(f"    virtual_env: {controller.virtual_env}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings: {e}")

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
        print(f"[ERROR] Ran into issue fetching environments: {e}")
        return []
    
def begin_training(controller, run_id, SETTINGS_FILE):
        """Begins a new training session in a subprocess

        Args:
            controller (MLAgentsApp): The main application instance that acts as the controller for managing the application's state and navigation.
            run_id (str): The ID for the training session.
            SETTINGS_FILE (str): The path to the configuation file for the training session.
        
        Returns:
            subprocess.Popen: The process object for the training session, or None if an error occurs.
        """
        print(f"\n[ALERT] Attempting to begin training with run-id: {run_id}")

        env = controller.virtual_env
        working_dir = controller.working_dir # The selected ml-agents working directory
        results_dir = f"{working_dir}/results" # Base directory for results
        run_id_path = os.path.join(results_dir, run_id) # Contruct the full path for the run_id

        if not env: # Check if the environment is valid
            print("[ERROR] No environment selected for training!")
            return
        
        # Check if the directory exists
        force_flag = ""
        if os.path.exists(run_id_path) and os.path.isdir(run_id_path):
            print(f'    [INFO] Previous result found with Run ID "{run_id}". Overwrite?')

            # Show an alert window to confirm overwriting
            overwrite = messagebox.askyesno(
                "Existing Run-ID",
                message=f'A result with the Run ID "{run_id}" already exists.',
                detail=f'Do you want to force start training and overwrite the previous result?',
            )
            if not overwrite:
                print("    [ALERT] Training session cancelled by the user.")
                return

            # User chose to overwrite, add the --force flag
            print("    [INFO] User chose to overwrite. Adding --force flag")
            force_flag = "--force"

        try:
            # Command to run the training session
            command = f"source activate base && conda activate {env} && mlagents-learn {SETTINGS_FILE} --run-id={run_id} {force_flag}"

            # Create the popup to show training output
            output_popup = create_output_popup(controller, run_id)

            process = subprocess.Popen(
                command,
                shell=True,
                cwd=controller.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid
            )

            # Use a seperate thread to read subprocess output
            threading.Thread(target=stream_process_output, args=(process, output_popup), daemon=True).start()

            # Store the process in the controller
            controller.current_training_process = process

            print(f"    [ALERT] Training started with run-id: {run_id}")
            return process

        except Exception as e:
            print(f"    [ERROR] Failed to begin training. \n\n{str(e)}")

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
        text=f'Training session "{run_id}" initialised, press play in the Unity editor to begin training',
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
        print(f"    [ALERT] Attempting to terminate training session, stand by...")

        text_widget.insert(
                    tk.END,
                    "\n[CTRL Panel] Attempting to terminate training session, stand by...\n"
                )
        
        process = getattr(controller, 'current_training_process', None)

        if process and process.poll() is None:
            try:
                # Attempt graceful termination with SIGINT
                try:
                    print("    [INFO] Terminating the process group with SIGINT...")
                    os.killpg(os.getpgid(process.pid), signal.SIGINT) # Send SIGINT to terminate the process
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    print("    [WARNING] Process group did not terminate within timeout, forcing termination...")
                except Exception as e:
                    print(f"    [ERROR] Failed to send SIGINT: {e}")
                
                # If process hasn't ended, forcefully terminate it
                if process.poll() is None:
                    try:
                        print("    [INFO] Sending SIGTERM to process group...")
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM) # Send SIGTERM to terminate gracefully (less aggressive)
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        print("    [WARNING] Process group did not terminate within 5 seconds after SIGTERM.")
                    except Exception as e:
                        print(f"    [ERROR] Failed to send SIGTERM: {e}")

                # If the process still hasn't terminated, kill it
                if process.poll() is None:
                    try:
                        print("    [INFO] Forcing process group termination with SIGKILL...")
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except Exception as e:
                        print(f"    [ERROR] Failed to kill process: {e}")

                # Process terminated successfully
                print(f"    [SUCCESS] Training session terminated.")
                text_widget.after(
                    0,
                    text_widget.insert,
                    tk.END,
                    "\n[CTRL Panel] Training session terminated.\n"
                )

                end_button.after(0, lambda: end_button.configure(state="disabled"))
                close_button.after(0, lambda: close_button.configure(state="normal"))

            except Exception as e:
                print(f"[ERROR] Failed to terminate training session: {e}")
                text_widget.after(
                    0,
                    text_widget.insert,
                    tk.END,
                    f"\n[ERROR] Encountered a problem terminating session: {e}\n"
                )
        else:
            print("[ERROR] No active training session to terminate.")
            text_widget.insert(
                tk.END,
                "\n[CTRL Panel] No active training session to terminate.\n"
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
    text_widget.after(0, append_text, "\n[CTRL Panel] Training Session Ended\n")

def deactivate_env(env, process):
    "Deactivates the selected virtual environment in a subprocess"

    if not env: # If there is no environment inside env
        print("[ERROR] There is no environment to deactivate!")
        return
    
    print(f"[ALERT] Attempting to deactivate virtual environment: {env}\n")

    try:
        command = f"conda deactivate && conda info --envs"
        subprocess.Popen(command, shell=True)

        print(f'[INFO] Virtual environment "{env}" is now deactivated')

    except Exception as e:
        messagebox.showerror(f"[ERROR] Failed to deactivate the environment.\n\n{str(e)}")