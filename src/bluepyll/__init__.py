"""
BluePyll - A Python library for controlling BlueStacks emulator
"""

from .app import BluePyllApp
from .constants import BluestacksConstants
from .controller import BluePyllController
from .exceptions import (
    AppError,
    BluePyllError,
    ConnectionError,
    EmulatorError,
    StateError,
    TimeoutError,
)
from .state_machine import AppLifecycleState, BluestacksState, StateMachine
from .ui import BluePyllElement, BluePyllElements
from .utils import ImageTextChecker

__all__ = [
    "BluePyllController",
    "BluePyllApp",
    "BluePyllError",
    "EmulatorError",
    "AppError",
    "StateError",
    "ConnectionError",
    "TimeoutError",
    "BluestacksConstants",
    "AppLifecycleState",
    "StateMachine",
    "BluestacksState",
    "BluePyllElements",
    "BluePyllElement",
    "ImageTextChecker",
]

__version__ = "0.1.13"
