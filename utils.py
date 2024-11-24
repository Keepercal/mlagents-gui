import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

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
        else:
            force_flag = "" # No need for flag if result doesn't exist

        try:
            command = f"source activate base && conda activate {env} && mlagents-learn {config_file} --run-id={run_id} {force_flag}"
            process = subprocess.Popen(command, shell=True, cwd=controller.working_directory)
            print(f"Training started with run-id: {run_id}")
            return process

        except Exception as e:
            print("Error", f"Failed to begin training. \n\n{str(e)}")

            if env:
                deactivate_env(env, process)
                print(f'Deactivating virtual environment "{env}"" as a consequence')

            return None

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