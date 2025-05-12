# BluePyll: Automating BlueStacks

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.13+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

BluePyll is a Python library designed to control BlueStacks through ADB commands, enabling seamless automation and management of Android applications on a PC.

**Warning:** This project involves automating UI interactions and interacting with external software. Use it responsibly and ensure it complies with the terms of service of any applications you interact with.

## Features

* **Emulator Control:**
  * Launch and close BlueStacks
  * Check BlueStacks running and loading status
* **App Management:**
  * Launch and close Android applications
  * Check application running status
* **UI Interaction:**
  * Coordinate-based & image-based clicking
  * Image recognition interactions
  * Text input and key presses
* **ADB Integration:**
  * Execute shell commands
  * Device connection management
* **Image and Text Recognition:**
  * Screen text location
  * Region-based text verification
* **Utility Functions:**
  * Execution delays
  * Image scaling
  * Logging support

## Prerequisites

* **Python 3.13+**
* **BlueStacks**
* **uv** (Package Manager)

## Why uv?

* 🚀 **All-in-One Tool:** Replaces pip, pip-tools, pipx, poetry, pyenv, twine, and virtualenv
* ⚡️ **Blazing Fast:** 10-100x faster than pip
* 🗂️ **Comprehensive Project Management:** Universal lockfile and workspace support
* 💾 **Efficient Storage:** Global cache for dependency deduplication
* 🐍 **Python Version Management:** Easily install and manage Python versions
* 🛠️ **Flexible Tooling:** Runs and installs tools published as Python packages
* 🖥️ **Cross-Platform:** Supports macOS, Linux, and Windows

[Learn more about uv](https://docs.astral.sh/uv/)

## Installation

1. **Install uv:**(If not already installed)
    ```bash
    pip install uv
    ```

2. **Create Project and Install BluePyll:**
    ```bash
    # Initialize a new project
    uv init bluepyll-project
    cd bluepyll-project

    # Add BluePyll
    uv add bluepyll
    ```

**Note:** We recommend using uv for the most efficient and reliable package management.

## Usage

### Quick Start

```python
from bluepyll.controller import BluepyllController
from bluepyll.app import BluePyllApp
from bluepyll.state_machine import BluestacksState


def main():
  """
  Main test function that demonstrates opening Bluestacks and launching an app.
  """
    
  try:
    # Initialize the controller and wait for Bluestacks to auto-open
    print("Initializing & opening BluepyllController...")
    controller = BluepyllController()
    print("Bluestacks opened successfully")

    # Create the app instance
    print("Creating app instance...")
    app = BluePyllApp(
        app_name="Example App",
        package_name="com.example.app"
    )

    print("Starting test sequence...")

    # Verify Bluestacks is open
    if not controller.bluestacks_state.current_state == BluestacksState.READY:
        raise RuntimeError("Bluestacks failed to be ready!")

    # Open app
    print("Opening app...")
    controller.open_app(app)
        
    # Wait for user to verify
    input("\nPress Enter to close Bluestacks...")

    # Clean up
    print("Closing Bluestacks...")
    controller.kill_bluestacks()
    print("Test completed successfully!")
  except Exception as e:
    print(f"Test failed: {e}")
    raise


if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print(f"\nTest failed with error: {e}")
    sys.exit(1)


```

For more detailed usage and examples, please refer to the individual module documentation and the example scripts (if any).

### Project Structure

The project is organized as follows:

* bluepyll/` - Contains the source code for BluePyll.
  * `__init__.py` - Initializes the BluePyll package.
  * `app.py` - Module for managing Android apps within BlueStacks.
  * `constants.py` - Module containing constants for BluePyll.
  * `controller.py` - Module for controlling the BlueStacks emulator.
  * `exceptions.py` - Module containing BluePyll-specific exceptions.
  * `ui.py` - Module for interacting with the BlueStacks user interface.
  * `utils.py` - Module containing utility functions for BluePyll.
