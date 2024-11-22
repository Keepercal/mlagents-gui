import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

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
    
def begin_training(controller):
        print("\nAttempting to begin training...")

        env = controller.selected_env

        try:
            activate_env(env)
        except Exception as e:
            print("Error", f"Failed to begin training. \n\n{str(e)}")

            deactivate_env(env)
            print(f'Deactivating virtual environment "{env}"" as a consequence')

            return

        

    
def activate_env(env):
    """Starts the selected virtual environment in a subprocess."""

    if not env:
        print("No environment selected!")
        return
    
    print(f"Attempting to activate virtual environment: {env}\n")

    try:
        command = f"source activate base && conda activate {env} && conda info --envs" # Initialise the Conda env
        subprocess.Popen(command, shell=True)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to activate the environment.\n\n{str(e)}")

def deactivate_env(env):
    "Deactivates the selected virtual environment in a subprocess"

    if not env:
        print("There is no environment to deactivate...")
        return
    
    print(f"Attempting to deactivate virtual environment: {env}\n")

    try:
        command = f"conda deactivate && conda info --envs"
        subprocess.Popen(command, shell=True)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to deactivate the environment.\n\n{str(e)}")