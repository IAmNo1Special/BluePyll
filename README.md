# BluePyll: BlueStacks Automation Library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://microsoft.com/windows)
[![PyPI Version](https://img.shields.io/badge/pypi-0.1.13-blue.svg)](https://pypi.org/project/bluepyll)
[![Documentation](https://img.shields.io/badge/docs-readthedocs.io-green.svg)](https://bluepyll.readthedocs.io)

> A powerful Python library for automating BlueStacks Android emulator through ADB commands

BluePyll enables seamless automation and management of Android applications on Windows PCs. Built for developers, testers, and automation enthusiasts who need programmatic control over BlueStacks emulator instances.

⚠️ **Disclaimer**: This library involves UI automation and interaction with external software. Use responsibly and ensure compliance with terms of service of applications you interact with.

## 📋 Table of Contents

- [✨ Features](#-features)
- [📦 Prerequisites](#-prerequisites)
- [🚀 Installation](#-installation)
- [🎯 Quick Start](#-quick-start)
- [📖 Usage Examples](#-usage-examples)
- [⚙️ Configuration](#️-configuration)
- [🔧 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## ✨ Features

### 🎮 Emulator Control

- **Launch & Manage**: Start, stop, and monitor BlueStacks instances
- **State Tracking**: Real-time BlueStacks loading and ready state detection
- **Window Management**: Programmatic window focus and positioning

### 📱 App Management

- **App Lifecycle**: Launch, close, and monitor Android applications
- **Package Management**: Handle Android app packages and activities
- **Status Monitoring**: Check app running states and health

### 🖱️ UI Automation

- **Visual Recognition**: Image-based UI element detection and interaction
- **Coordinate Operations**: Precise coordinate-based clicking and navigation
- **Text Recognition**: OCR-powered text detection and verification
- **Input Simulation**: Text input, key presses, and touch events

### 🔌 ADB Integration

- **Shell Commands**: Execute Android shell commands via ADB
- **Connection Management**: Automatic ADB connection handling
- **Screenshot Capture**: High-performance screen capture capabilities

### 🛠️ Advanced Features

- **Multi-Resolution Support**: Automatic scaling for different screen sizes
- **Robust Error Handling**: Comprehensive exception handling and recovery
- **Logging System**: Detailed logging for debugging and monitoring
- **State Machines**: Finite state machines for reliable lifecycle management

## 📦 Prerequisites

- **Python 3.13+** - [Download Python](https://python.org/downloads)
- **BlueStacks** - [Download BlueStacks](https://www.bluestacks.com)
- **Windows OS** - Windows 10/11 (64-bit recommended)
- **uv Package Manager** (recommended) - [Install uv](https://docs.astral.sh/uv/getting-started/installation)

## 🚀 Installation

### Option 1: Using uv (Recommended)

```bash
# Install uv (if not already installed)
pip install uv

# Install BluePyll
uv add bluepyll
```

### Option 2: Using pip

```bash
# Create virtual environment
python -m venv bluepyll-env
bluepyll-env\Scripts\activate  # Windows

# Install BluePyll
pip install bluepyll
```

### Option 3: From Source

```bash
# Clone the repository
git clone https://github.com/IAmNo1Special/BluePyll.git
cd BluePyll

# Install with uv
uv sync

# Or with pip
pip install -e .
```

## 🎯 Quick Start

```python
from bluepyll import BluePyllController, BluePyllApp

# Initialize controller (auto-starts BlueStacks)
controller = BluePyllController()

# Create app instance
app = BluePyllApp(
    app_name="My Android App",
    package_name="com.example.myapp"
)

# Launch app
controller.open_app(app)

# Check if app is running
if controller.is_app_running(app):
    print(f"{app.app_name} is running!")

# Clean up
controller.kill_bluestacks()
```

## 📖 Usage Examples

### Basic Emulator Control

```python
from bluepyll import BluePyllController

controller = BluePyllController()

# Check BlueStacks state
print(f"BlueStacks state: {controller.bluestacks_state.current_state}")

# Take screenshot
screenshot = controller.capture_screenshot()
if screenshot:
    with open('screenshot.png', 'wb') as f:
        f.write(screenshot)
```

### App Management

```python
from bluepyll import BluePyllApp

# Create app instances
whatsapp = BluePyllApp("WhatsApp", "com.whatsapp")
game = BluePyllApp("MyGame", "com.mygame.android")

# Launch apps
controller.open_app(whatsapp)
controller.open_app(game)

# Check running apps
running_apps = [app.app_name for app in controller.running_apps]
print(f"Running apps: {running_apps}")

# Close specific app
controller.close_app(whatsapp)
```

### UI Interaction

```python
from pathlib import Path

from bluepyll import BluePyllController, BluePyllElement

controller: BluePyllController = BluePyllController()

ui_element: BluePyllElement = BluePyllElement(
    label="element_name",
    ele_type="button",
    og_window_size=(1920, 1080),
    position=(100, 200),
    size=(100, 100),
    path=Path("element_image.png"),
    is_static=True,
    confidence=0.8,
    ele_txt="element_text",
    pixel_color=(255, 255, 255),
    controller=controller,
)
# Click on screen coordinates
ui_element.click()

# Type text
controller.type_text("Hello, BlueStacks!")

# Press keys
controller.press_enter()
controller.press_esc()

# Navigate home
controller.go_home()
```

### Advanced Features

```python
# Custom controller configuration
controller = BluePyllController(
    ip="127.0.0.1",
    port=5555,
    ref_window_size=(1920, 1080)
)

# Configure reference window size
controller.ref_window_size = (2560, 1440)

# Check BlueStacks loading status
if controller.is_bluestacks_loading():
    print("BlueStacks is loading...")
```

## ⚙️ Configuration

### BluePyllController Options

- `ip` (str): BlueStacks ADB IP address (default: "127.0.0.1")
- `port` (int): BlueStacks ADB port (default: 5555)
- `ref_window_size` (tuple): Reference window size for UI scaling (default: (1920, 1080))

### Constants

Configure these values in your code or modify `BluestacksConstants`:

- `DEFAULT_TIMEOUT`: Operation timeout in seconds (default: 30)
- `DEFAULT_WAIT_TIME`: Wait time between retries (default: 1)
- `DEFAULT_MAX_RETRIES`: Maximum retry attempts (default: 10)
- `APP_START_TIMEOUT`: App startup timeout (default: 60)

## 🔧 Troubleshooting

### Common Issues

#### BlueStacks not found

- Ensure BlueStacks is installed in default locations
- Manually specify path: `controller.filepath = r"C:\Program Files\BlueStacks_nxt\HD-Player.exe"`

#### ADB connection failed

- Check if BlueStacks is running
- Verify ADB port (default: 5555) is not in use
- Restart BlueStacks and try again

#### UI elements not found

- Verify reference window size matches the resolution of the window the BluePyllElement was taken from
- Check if BluePyllElement is visible on screen
- Adjust confidence threshold in BluePyllElement

#### Permission errors

- Run as administrator
- Check Windows permissions for BlueStacks directory
- Disable antivirus temporarily for testing

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

- 📖 Check the [documentation](https://bluepyll.readthedocs.io)
- 🐛 [Report issues](https://github.com/IAmNo1Special/BluePyll/issues)
- 💬 Create a new issue with detailed error logs

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Setup

```bash
# Clone repository
git clone https://github.com/IAmNo1Special/BluePyll.git
cd BluePyll

# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black src/ tests/
uv run isort src/ tests/
```

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `uv run pytest`
5. Format code:

   ```bash
   uv run black src/ tests/
   uv run isort src/ tests/
   ```

6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Areas for Contribution

- 🐛 Bug fixes and improvements
- 📚 Documentation enhancements
- 🧪 Additional test coverage
- ✨ New features and UI elements
- 🔧 Platform compatibility improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **BlueStacks** for the Android emulator platform
- **EasyOCR** for optical character recognition
- **ADB Shell** for Android Debug Bridge integration
- **PyAutoGUI** for GUI automation capabilities
- **Community contributors** for their valuable feedback and improvements

## 📞 Support

- **Documentation**: [Read the docs](https://bluepyll.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/IAmNo1Special/BluePyll/issues)
- **Discussions**: [GitHub Discussions](https://github.com/IAmNo1Special/BluePyll/discussions)
- **Author**: [IAmNo1Special](https://github.com/IAmNo1Special)

---

---

---

> Made with ❤️ for the automation community
>
> [⭐ Star us on GitHub](https://github.com/IAmNo1Special/BluePyll) • [🐛 Report Bug](https://github.com/IAmNo1Special/BluePyll/issues) • [💡 Request Feature](https://github.com/IAmNo1Special/BluePyll/issues)
