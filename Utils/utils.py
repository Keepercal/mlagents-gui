import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import threading
import signal
import select
import json
import sys
import logging
#from colorlog import ColoredFormatter

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ]
)

"""formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    }
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)"""

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def print_variables(self):
        logging.info("Configuration Details:")
        print(f"    - ML-Agents Directory: {self.mlagents_dir}")
        print(f"    - Conda Installation Directory: {self.conda_dir}")
        print(f"    - Conda Executable: {self.conda_exe}")
        print(f"    - Avaliable Conda Environments: {self.conda_envs}")
        print(f"    - Selected Conda Environment: {self.virtual_env}")

def get_resource_path(realative_path):
    """ Get the absolute path to a resource when it is stored temporarily. """
    try:
        base_path = sys._MEIPASS # Points to the special temporary folder
    except Exception:
        # If not running in PyInstaller, use the normal file system
        base_path = os.path.dirname(__file__)

        if base_path.endswith('Utils'):
            base_path = os.path.dirname(base_path)
    
    return os.path.join(base_path, realative_path)

# =====================================================================
# SETTINGS: Load and save user settings.
# =====================================================================
SETTINGS_FILE = "settings.json"

def load_settings(controller):
    """ Loads user settings from JSON file, if one exists"""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)

            controller.mlagents_dir = settings.get("mlagents_dir", "")
            controller.virtual_env = settings.get("virtual_env", "")
    except Exception as e:
        logging.error(f"Failed to load saved settings: {e}")
        messagebox.showerror(
            title="Error!",
            message=f"Failed to load settings: {e}"
        )

def save_settings(controller):
    """ Saves the neccesary settings for loading a training session.

    Args:
        controller (MLAgentsCTRL): The application controller, used for accessing application variables.
    """
    settings = {
        "mlagents_dir": controller.mlagents_dir,
        "virtual_env": controller.virtual_env
    }
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        messagebox.showinfo("Saved", "Settings have been saved successfully!")

        logging.info("Settings have been saved for future use")
    except Exception as e:
        logging.error(f"Failed to save settings: {e}")
        messagebox.showerror("Error", f"Failed to save settings: {e}")
    
# =====================================================================
# VIRTUAL ENVIRONMENT HANDLING: Handles logic relating to virtual environments.
# =====================================================================
def get_conda_exe(conda_dir):
    """ Given the selected Anaconda installation directory, return the full path to the conda executable.

    Args:
        conda_dir (str): A string of the path to the user's conda installation.
    """
    # Check for conda in common subdirectories
    if os.name == 'nt': # Windows
        conda_exe = os.path.join(conda_dir, "Scripts", "conda.exe")
        logging.info("User's system identified as Windows")
    else: # macOS/Linux
        conda_exe = os.path.join(conda_dir, "bin", "conda")
        logging.info("User's system identified as MacOS or Linux")
    
    if not os.path.isfile(conda_exe):
        raise FileNotFoundError(f"  - Conda executable not found at {conda_exe}")
    else:
        print(f"    - Found Conda executable at {conda_exe}")
        return conda_exe

def get_conda_envs(conda_exe):
    """ Given a Conda executable, retrieves a list of avaliable Conda virtual environments.

    Args:
        conda_exe (str): The path to a given Conda executable.

    Raises:
        RuntimeError: Raises if there are issues fetching Conda environments from the given executable.

    Returns:
        list: A list of avaliable conda virtual environments
    """
    try:
        result = subprocess.run([conda_exe, "env", "list"], capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"[ERROR] Error fetching Conda Environments: {result.stderr}")
        
        envs = []
        for line in result.stdout.splitlines():
            if line.startswith("#") or not line.strip():
                continue

            # Split the line into columns to get the environxwments
            parts = line.split()
            if len(parts) >= 2:
                env_name = parts[0]
                envs.append(env_name)
        return envs
    
    except Exception as e:
        logging.error(f"Ran into issues fetching environments: {e}")
        return []
    
'''def deactivate_env(env, process):
    if not env: # If there is no environment inside env
        print("[ERROR] There is no environment to deactivate!")
        return
    
    print(f"[ALERT] Attempting to deactivate virtual environment: {env}\n")

    try:
        command = f"conda deactivate && conda info --envs"
        subprocess.Popen(command, shell=True)

        print(f'[INFO] Virtual environment "{env}" is now deactivated')

    except Exception as e:
        messagebox.showerror(f"[ERROR] Failed to deactivate the environment.\n\n{str(e)}")'''