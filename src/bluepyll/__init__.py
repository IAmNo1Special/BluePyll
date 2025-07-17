"""
BluePyll - A Python library for controlling BlueStacks emulator
"""

from .controller import BluepyllController
from .app import BluePyllApp
from .exceptions import BluePyllError, EmulatorError, AppError, StateError, ConnectionError, TimeoutError
from .constants import BluestacksConstants
from .state_machine import AppLifecycleState, StateMachine, BluestacksState
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
    "ImageTextChecker"
]

__version__ = "0.0.5"