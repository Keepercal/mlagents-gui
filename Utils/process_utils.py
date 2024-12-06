from Utils.utils import logging

import tkinter as tk
import subprocess
import os
import signal
import select
import threading

stop_event = threading.Event()

def initialise_process(controller, command):
    """ Intialises a new training session process

    Args:
        controller (MLAgentsCTRL): The application controller, used for accessing application variables.
        command (str): The command to execute in the process.

    Returns:
        process: Returns a new process
    """

    try:
        process = subprocess.Popen(
                    command,
                    shell=True,
                    executable="/bin/bash",
                    cwd=controller.mlagents_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid
        )

        return process
    except Exception as e:
        logging.error(f"Failed to start new process: {e}")

def end_process(process):
    """ Ends a given process, firsty trying gracefully, then forcefully.

    Args:
        process(subprocess.Popen): The process to end.
    """
    try:
        print.info("Interrupting the process group with SIGINT...")
        os.killpg(os.getpgid(process.pid), signal.SIGINT) # Send SIGINT to terminate the process
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        logging.warning("Process group did not interrupt within timeout, forcing termination...")
    except Exception as e:
        logging.error(f"Failed to send SIGINT to process: {e}")
    
    # If process hasn't ended, forcefully terminate it
    if process.poll() is None:
        try:
            logging.info("Sending SIGTERM to process group...")
            os.killpg(os.getpgid(process.pid), signal.SIGTERM) # Send SIGTERM to terminate gracefully (less aggressive)
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logging.warning("Process group did not terminate within timout, killing process...")
        except Exception as e:
            logging.error(f"Failed to send SIGTERM to process: {e}")

    # If the process still hasn't terminated, kill it
    if process.poll() is None:
        try:
            logging.info("Killing process group with SIGKILL...")
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except Exception as e:
            print(f"    [ERROR] Failed to kill process: {e}")
            logging.error(f"Failed to kill process: {e} ")

def stream_process_output(process, text_widget):
    """ Streams the subprocess output to a passed text widget. """
    def append_text(data):
        try:
            if text_widget.winfo_exists():
                text_widget.insert(tk.END, data)
                text_widget.see(tk.END) # Auto-scroll to the end
            else:
                logging.warning("Text widget no longer exists. Stopping updates.")
                stop_event.set()
        except tk.TclError as e:
            logging.error(f"Widget destroyed or invalid: {e}")
            stop_event.set()

    while process.poll() is None:
        if stop_event.is_set(): # Check if the thread should stop
            logging.info("Stopping output streaming due to stop_event.")
            return
        
        readable, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
        for stream in readable:
            line = stream.readline()
            if line:
                text_widget.after(0, append_text, line)
    
    # Handle remaining output after process ends
    for stream in (process.stdout, process.stderr):
        for line in stream:
            if stop_event.is_set():
                logging.warning("Stopping output streaming due to stop_event")
                return
            if text_widget.winfo_exists():
                text_widget.after(0, append_text, line)
    
    # Mark process as finished
    if text_widget.winfo_exists():
        text_widget.after(0, append_text, "\n[CTRL Panel] Training Session Ended\n")