"""
Constants for BluePyll configuration
"""

from typing import Tuple


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
    DEFAULT_WAIT_TIME: int = 1
    DEFAULT_TIMEOUT: int = 30
    PROCESS_WAIT_TIMEOUT: int = 10
    APP_START_TIMEOUT: int = 60
