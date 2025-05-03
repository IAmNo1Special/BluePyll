"""
BluePyll - A Python library for controlling BlueStacks emulator
"""

from .controller import BluestacksController
from .app import BluePyllApp
from .exceptions import BluePyllError, EmulatorError, AppError, StateError, ConnectionError, TimeoutError

__all__ = [
    "BluestacksController",
    "BluePyllApp",
    "BluePyllError",
    "EmulatorError",
    "AppError",
    "StateError",
    "ConnectionError",
    "TimeoutError"
]

__version__ = "0.2.0"