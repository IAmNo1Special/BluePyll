"""
Custom exceptions for BluePyll
"""

from typing import Optional

class BluePyllError(Exception):
    """
    Base exception for BluePyll-related errors.
    
    All BluePyll-specific exceptions should inherit from this class.
    """
    pass

class EmulatorError(BluePyllError):
    """
    Error related to BlueStacks emulator operations.
    
    This exception is raised when there are issues with:
    - Emulator startup/shutdown
    - Emulator state management
    - ADB connection to the emulator
    """
    pass

class AppError(BluePyllError):
    """
    Error related to Android app operations.
    
    This exception is raised when there are issues with:
    - App installation/uninstallation
    - App state management
    - App interaction
    """
    pass

class StateError(BluePyllError):
    """
    Error related to invalid state transitions.
    
    This exception is raised when:
    - An invalid state transition is attempted
    - The current state is unexpected
    - State validation fails
    """
    pass

class ConnectionError(BluePyllError):
    """
    Error related to ADB connection issues.
    
    This exception is raised when:
    - ADB connection cannot be established
    - ADB commands fail
    - ADB server is unreachable
    """
    pass

class TimeoutError(BluePyllError):
    """
    Error related to operation timeouts.
    
    This exception is raised when:
    - An operation takes longer than expected
    - A timeout occurs during waiting for a state
    - A command execution times out
    """
    pass
