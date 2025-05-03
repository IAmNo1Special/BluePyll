"""
Constants for BluePyll configuration
"""

from typing import Tuple, Literal


class BluestacksConstants:
    """
    Constants for BlueStacks emulator configuration.
    
    These constants define default values and timeouts for the emulator.
    """
    
    # Network configuration
    DEFAULT_IP: str = "127.0.0.1"
    DEFAULT_PORT: int = 5555
    
    # Display configuration
    DEFAULT_REF_WINDOW_SIZE: Tuple[int, int] = (1920, 1080)
    
    # Operation timeouts
    DEFAULT_MAX_RETRIES: int = 10
    DEFAULT_WAIT_TIME: int = 5
    DEFAULT_TIMEOUT: int = 30
    PROCESS_WAIT_TIMEOUT: int = 5
    APP_START_TIMEOUT: int = 60


class AppConstants:
    """
    Constants for Android app configuration.
    
    These constants define default values and states for Android apps.
    """
    
    class State:
        """
        App state constants.
        
        These constants represent the possible states of an Android app.
        """
        LOADING: Literal["loading"] = "loading"
        OPEN: Literal["open"] = "open"
        CLOSED: Literal["closed"] = "closed"

    # Default app values
    DEFAULT_PACKAGE_NAME: str = "com.example.app"
    DEFAULT_APP_NAME: str = "Example App"
