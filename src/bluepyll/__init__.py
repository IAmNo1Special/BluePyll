"""
BluePyll - A Python library for controlling BlueStacks emulator
"""

from .app import BluePyllApp
from .constants import BluestacksConstants
from .controller import BluepyllController
from .exceptions import (
    AppError,
    BluePyllError,
    ConnectionError,
    EmulatorError,
    StateError,
    TimeoutError,
)
from .state_machine import AppLifecycleState, BluestacksState, StateMachine
from .ui import BlueStacksUiPaths, UIElement
from .utils import ImageTextChecker

__all__ = [
    "BluepyllController",
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
    "BlueStacksUiPaths",
    "UIElement",
    "ImageTextChecker",
]

__version__ = "0.0.5"
