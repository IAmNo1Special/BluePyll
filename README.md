# BluePyll: Automating BlueStacks for Fun and Profit (and Maybe Some Testing)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-%3E=3.8-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

BluePyll is a Python library designed to automate interactions within the BlueStacks Android emulator on Windows. It provides a set of tools and functionalities to control the emulator, interact with applications, and perform various automated tasks.

**Warning:** This project involves automating UI interactions and interacting with external software. Use it responsibly and ensure it complies with the terms of service of any applications you interact with.

## Features

* **Emulator Control:**
  * Launch and close BlueStacks.
  * Check if BlueStacks is running and loaded.
  * Handle potential loading screens.
* **App Management:**
  * Launch and close Android applications within BlueStacks.
  * Check if an application is running.
* **UI Interaction:**
  * Click and double-click on specific coordinates.
  * Locate and interact with UI elements based on image recognition (using `pyautogui`).
  * Type text into UI elements.
  * Press Enter and Escape keys.
* **ADB Integration:**
  * Execute ADB shell commands.
  * Check the connection status of the ADB device.
* **Image and Text Recognition:**
  * Locate text within specific regions of the emulator screen (using `easyocr`).
  * Verify the presence of specific text on the screen.
* **Utility Functions:**
  * Delay execution for specified times.
  * Handle image scaling for different BlueStacks resolutions.
  * Basic logging for debugging and monitoring.
* **Custom Exceptions:** Provides specific exception types for easier error handling related to emulator and app interactions.

## Installation

1. **Prerequisites:**
    * **Python 3.8 or higher:** Ensure you have a compatible Python version installed.
    * **BlueStacks:** You need to have BlueStacks installed on your Windows system.
    * **ADB (Android Debug Bridge):** BluePyll relies on ADB. Ensure ADB is correctly configured and accessible in your system's PATH. BluePyll attempts to locate it, but manual configuration might be necessary.

2. **Install via pip:**

    ```bash
    pip install -r requirements.txt
    ```

    *(Note: You'll need to create a `requirements.txt` file with the necessary dependencies. Based on the code, it should include at least `pyautogui`, `adb-shell`, `easyocr`, `Pillow`, `psutil`, and `pywin32`).*

    Example `requirements.txt`:

    ```python
    pyautogui
    adb-shell
    easyocr
    Pillow
    psutil
    pywin32
    ```

## Usage

Here's a basic example of how to use BluePyll to launch an app:

```python
from bluepyll.controller import BluestacksController
from bluepyll.app import BluePyllApp
import time
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    controller = BluestacksController()
    my_app = BluePyllApp(package_name="com.example.android.app", app_name="My Awesome App") # Replace with the actual package name and app name

    try:
        if not controller.is_open():
            controller.open()
            controller.wait_for_loading()

        if not controller.is_app_running(my_app):
            controller.launch_app(my_app)
            print(f"Launched {my_app.app_name}")
            time.sleep(10) # Give the app some time to load

        if controller.is_app_running(my_app):
            print(f"{my_app.app_name} is running.")
        else:
            print(f"Failed to launch {my_app.app_name}.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Optional: Close BlueStacks after your tasks
        # controller.close()
        pass
```

For more detailed usage and examples, please refer to the individual module documentation and the example scripts (if any).

### Project Structure

The project is organized as follows:

* `BluePyll/` - Contains the source code for BluePyll.
  * `src/bluepyll/` - Contains the source code for BluePyll.
    * `__init__.py` - Initializes the BluePyll package.
    * `app.py` - Module for managing Android apps within BlueStacks.
    * `constants.py` - Module containing constants for BluePyll.
    * `controller.py` - Module for controlling the BlueStacks emulator.
    * `exceptions.py` - Module containing BluePyll-specific exceptions.
    * `ui.py` - Module for interacting with the BlueStacks user interface.
    * `utils.py` - Module containing utility functions for BluePyll.
    * `LICENSE` - The license file for the project.
  * `pyproject.toml` - Configuration file for containing project metadata and dependencies.
  * `README.md` - This README file.
  * `uv.lock` - The lock file containing the resolved dependencies.
