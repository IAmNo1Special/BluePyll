"""
Controller for managing the BlueStacks emulator.
"""

import io
import logging
import os
import time
from pprint import pprint

import psutil
import win32con
import win32gui
from adb_shell.adb_device import AdbDeviceTcp
from PIL import Image, ImageGrab

from .app import BluePyllApp
from .constants import BluestacksConstants
from .state_machine import AppLifecycleState, BluestacksState, StateMachine
from .ui import BluePyllElement, BluePyllElements
from .utils import ImageTextChecker

# Initialize logger
logger = logging.getLogger(__name__)


def log_property_setter(func):
    """
    Decorator to log property setter operations.

    Args:
        func: The property setter function to decorate

    Returns:
        The decorated function
    """

    def wrapper(self, value: object | None):
        logger.debug(f"Setting {func.__name__}...")
        result = func(self, value)
        logger.debug(f"{func.__name__} set to {value}")
        return result

    return wrapper


class BluePyllController(AdbDeviceTcp):
    def __init__(
        self,
        ip: str = BluestacksConstants.DEFAULT_IP,
        port: str | int = BluestacksConstants.DEFAULT_PORT,
        ref_window_size: tuple[int, int] = BluestacksConstants.DEFAULT_REF_WINDOW_SIZE,
    ) -> None:
        port: int = self._validate_and_convert_int(port, "port")
        super().__init__(ip, port)
        logger.info("Initializing BluePyllController")
        self.img_txt_checker: ImageTextChecker = ImageTextChecker()
        self._ref_window_size: tuple[int, int] = ref_window_size
        self._filepath: str | None = None
        self._default_transport_timeout_s: int = 60.0
        self.running_apps: list[BluePyllApp] | list = list()
        self.bluestacks_state = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions(),
        )
        self.bluestacks_state.register_handler(
            BluestacksState.LOADING, self.wait_for_load, None
        )
        self.bluestacks_state.register_handler(
            BluestacksState.READY, self.connect_adb, None
        )
        self.elements: BluePyllElements = BluePyllElements(self)
        self._autoset_filepath()
        self.open_bluestacks()
        logger.debug(
            f"BluePyllController initialized with the following state:\n{pprint(self.bluestacks_state)}\n"
        )

    def _validate_and_convert_int(self, value: int | str, param_name: str) -> int:
        """Validate and convert value to int if possible"""
        if not isinstance(value, int):
            try:
                value: int = int(value)
            except ValueError as e:
                logger.error(f"ValueError in {param_name}: {e}")
                raise ValueError(f"Error in {param_name}: {e}")
        return value

    @property
    def ref_window_size(self) -> tuple[int, int] | None:
        return self._ref_window_size

    @ref_window_size.setter
    @log_property_setter
    def ref_window_size(self, width: int | str, height: int | str) -> None:
        if not isinstance(width, int):
            if isinstance(width, str) and width.isdigit():
                width: int = int(width)
                if width <= 0:
                    logger.warning(
                        "ValueError while trying to set BluePyllController 'ref_window_size': Provided width must be positive integers!"
                    )
                    raise ValueError("Provided width must be positive integers")
            else:
                logger.warning(
                    "ValueError while trying to set BluePyllController 'ref_window_size': Provided width must be an integer or the string representation of an integer!"
                )
                raise ValueError(
                    "Provided width must be integer or the string representation of an integer!"
                )

        if not isinstance(height, int):
            if isinstance(height, str) and height.isdigit():
                height: int = int(height)
                if height <= 0:
                    logger.warning(
                        "ValueError while trying to set BluePyllController 'ref_window_size': Provided height must be positive integers!"
                    )
                    raise ValueError("Provided height must be positive integers")
            else:
                logger.warning(
                    "ValueError while trying to set BluePyllController 'ref_window_size': Provided height must be an integer or the string representation of an integer!"
                )
                raise ValueError(
                    "Provided height must be integer or the string representation of an integer!"
                )

        self._ref_window_size = (width, height)

    @property
    def filepath(self) -> str | None:
        return self._filepath

    @filepath.setter
    @log_property_setter
    def filepath(self, filepath: str) -> None:
        """
        If the provided filepath is a string and it exist,
        sets the filepath to the BlueStacks Emulator.
        Otherwise, returns a ValueError
        """

        if not isinstance(filepath, str):
            logger.warning(
                "ValueError while trying to set BluePyllController 'filepath': Provided filepath must be a string!"
            )
            raise ValueError("Provided filepath must be a string")

        if not os.path.exists(filepath):
            logger.warning(
                "ValueError while trying to set BluePyllController 'filepath': Provided filepath does not exist!"
            )
            raise ValueError("Provided filepath does not exist")

        self._filepath: str = filepath

    def _autoset_filepath(self):
        logger.debug("Setting filepath...")

        # Common installation paths for BlueStacks
        search_paths = [
            # Standard Program Files locations
            os.path.join(
                os.environ.get("ProgramFiles", ""), "BlueStacks_nxt", "HD-Player.exe"
            ),
            os.path.join(
                os.environ.get("ProgramFiles(x86)", ""),
                "BlueStacks_nxt",
                "HD-Player.exe",
            ),
            # Alternative BlueStacks versions
            os.path.join(
                os.environ.get("ProgramFiles", ""), "BlueStacks", "HD-Player.exe"
            ),
            os.path.join(
                os.environ.get("ProgramFiles(x86)", ""), "BlueStacks", "HD-Player.exe"
            ),
            # Common custom installation paths
            "C:\\Program Files\\BlueStacks_nxt\\HD-Player.exe",
            "C:\\Program Files (x86)\\BlueStacks_nxt\\HD-Player.exe",
            "C:\\BlueStacks\\HD-Player.exe",
            "C:\\BlueStacks_nxt\\HD-Player.exe",
            # Check if file exists in current directory or subdirectories
            "HD-Player.exe",
        ]

        # Remove empty paths from environment variables
        search_paths = [
            path for path in search_paths if path and path != "HD-Player.exe"
        ]

        # Add current working directory relative paths
        cwd = os.getcwd()
        search_paths.extend(
            [
                os.path.join(cwd, "BlueStacks_nxt", "HD-Player.exe"),
                os.path.join(cwd, "BlueStacks", "HD-Player.exe"),
            ]
        )

        logger.debug(f"Searching for HD-Player.exe in {len(search_paths)} locations")

        for potential_path in search_paths:
            if os.path.exists(potential_path) and os.path.isfile(potential_path):
                self._filepath = potential_path
                logger.debug(f"HD-Player.exe filepath set to {self._filepath}.")
                return
            else:
                logger.debug(f"Checked path (does not exist): {potential_path}")

        # If we still haven't found it, try a broader search
        logger.debug("Performing broader search for HD-Player.exe...")
        try:
            for root, dirs, files in os.walk("C:\\"):
                if "HD-Player.exe" in files:
                    potential_path = os.path.join(root, "HD-Player.exe")
                    if "bluestacks" in root.lower():
                        self._filepath = potential_path
                        logger.debug(
                            f"HD-Player.exe found via broad search: {self._filepath}"
                        )
                        return
        except Exception as e:
            logger.debug(f"Broad search failed: {e}")

        logger.error(
            "Could not find HD-Player.exe. Please ensure BlueStacks is installed or manually specify the filepath."
        )
        logger.error(f"Searched paths: {search_paths}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"ProgramFiles: {os.environ.get('ProgramFiles')}")
        logger.error(f"ProgramFiles(x86): {os.environ.get('ProgramFiles(x86)')}")
        raise FileNotFoundError(
            "Could not find HD-Player.exe. Please ensure BlueStacks is installed or manually specify the filepath."
        )

    def _capture_loading_screen(self) -> bytes | None:
        """Capture the loading screen of BlueStacks."""
        time.sleep(1.0)
        hwnd: int = win32gui.FindWindow(None, "Bluestacks App Player")
        if hwnd:
            try:
                # Restore the window if minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # Pin the window to the foreground
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOPMOST,
                    0,
                    0,
                    0,
                    0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
                )
                time.sleep(0.5)
                rect: tuple[int, int, int, int] = win32gui.GetWindowRect(hwnd)
                bluestacks_window_image: Image.Image = ImageGrab.grab(bbox=rect)
                time.sleep(0.5)

                # Convert image to bytes
                img_byte_arr = io.BytesIO()
                bluestacks_window_image.save(img_byte_arr, format="PNG")
                img_byte_arr = img_byte_arr.getvalue()

                # Unpin the window from the foreground
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE
                )
                logger.debug("Loading screen captured as bytes")
                return img_byte_arr
            except Exception as e:
                logger.warning(f"Error capturing loading screen: {e}")
                raise Exception(f"Error capturing loading screen: {e}")
        else:
            logger.warning("Could not find 'Bluestacks App Player' window")
            return None

    def open_bluestacks(
        self,
        max_retries: int = BluestacksConstants.DEFAULT_MAX_RETRIES,
        wait_time: int = BluestacksConstants.DEFAULT_WAIT_TIME,
        timeout_s: int = BluestacksConstants.DEFAULT_TIMEOUT,
    ) -> None:
        max_retries: int = self._validate_and_convert_int(max_retries, "max_retries")
        wait_time: int = self._validate_and_convert_int(wait_time, "wait_time")
        timeout_s: int = self._validate_and_convert_int(timeout_s, "timeout_s")
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED:
                logger.info("Opening Bluestacks controller...")
                if not self._filepath:
                    self._autoset_filepath()
                try:
                    os.startfile(self._filepath)
                except Exception as e:
                    logger.error(f"Failed to start Bluestacks: {e}")
                    raise ValueError(f"Failed to start Bluestacks: {e}")

                start_time: float = time.time()

                for attempt in range(max_retries):
                    is_open: bool = any(
                        p.name().lower() == "HD-Player.exe".lower()
                        for p in psutil.process_iter(["name"])
                    )
                    if is_open:
                        logger.info("Bluestacks controller opened successfully.")
                        self.bluestacks_state.transition_to(BluestacksState.LOADING)
                        return

                    if time.time() - start_time > timeout_s:
                        logger.error("Timeout waiting for Bluestacks window to appear")
                        raise Exception(
                            "Timeout waiting for Bluestacks window to appear"
                        )

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries}: Could not find Bluestacks window."
                    )
                    time.sleep(wait_time)

                logger.error(
                    f"Failed to find Bluestacks window after all attempts {attempt + 1}/{max_retries}"
                )
                raise Exception(
                    f"Failed to find Bluestacks window after all attempts {attempt + 1}/{max_retries}"
                )
            case BluestacksState.LOADING:
                logger.info(
                    "Bluestacks controller is already open and currently loading."
                )
                return
            case BluestacksState.READY:
                logger.info("Bluestacks controller is already open and ready.")
                return

    def is_bluestacks_loading(self) -> bool:
        """
        Checks if the emulator is currently loading by searching for the loading screen image.
        - If the emulator is loading(loading screen image is found):
            - If the 'BluestacksState' state is in the loading state:
                - The 'BluestacksState' state will stay in the loading state.
            - Otherwise:
                - The 'BluestacksState' state will transition to the loading state.
        - If the emulator is not loading(loading screen image is not found):
            - If the 'BluestacksState' state is in the closed state:
                - The 'BluestacksState' state will stay in the closed state.
            - If the 'BluestacksState' state is in the loading state:
                - The 'BluestacksState' state will transition to the ready state.
            - If the 'BluestacksState' state is in the ready state:
                - The 'BluestacksState' state will stay in the ready state.

        Returns:
            bool: Whether the emulator is loading.
        """

        loading_screen: tuple[int, int] | None = (
            self.elements.bluestacks_loading_img.where()
        )
        match isinstance(loading_screen, tuple):
            case True:
                match self.bluestacks_state.current_state:
                    case BluestacksState.LOADING:
                        logger.debug("Bluestacks is loading...")
                        return True
                    case _:
                        self.bluestacks_state.transition_to(BluestacksState.LOADING)
                        logger.debug("Bluestacks is loading...")
                        return True
            case False:
                match self.bluestacks_state.current_state:
                    case BluestacksState.CLOSED:
                        logger.debug("Bluestacks is closed")
                        return False
                    case BluestacksState.LOADING:
                        self.bluestacks_state.transition_to(BluestacksState.READY)
                        logger.debug("Bluestacks has finished loading")
                        return False
                    case BluestacksState.READY:
                        logger.debug("Bluestacks is ready")
                        return False

    def wait_for_load(self):
        logger.debug("Waiting for Bluestacks to load...")
        while self.bluestacks_state.current_state == BluestacksState.LOADING:
            if self.is_bluestacks_loading():
                logger.debug("Bluestacks is currently loading...")
                # Wait a bit before checking again
                time.sleep(BluestacksConstants.DEFAULT_WAIT_TIME)
            else:
                logger.debug("Bluestacks is not loading")
        logger.info("Bluestacks is loaded & ready.")

    def kill_bluestacks(self) -> bool:
        """
        Kill the Bluestacks controller process. This will also close the ADB connection.

        Returns:
            bool: True if Bluestacks was successfully killed, False otherwise
        """
        logger.info("Killing Bluestacks controller...")

        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED:
                logger.debug("Bluestacks is already closed.")
                return True
            case BluestacksState.LOADING | BluestacksState.READY:
                try:
                    for proc in psutil.process_iter(["pid", "name"]):
                        info = proc.info
                        if info["name"] == "HD-Player.exe":
                            is_disconnected = self.disconnect_adb()
                            if is_disconnected:
                                proc.kill()
                                proc.wait(
                                    timeout=BluestacksConstants.PROCESS_WAIT_TIMEOUT
                                )  # Wait for process to terminate
                                self.bluestacks_state.transition_to(
                                    BluestacksState.CLOSED
                                )
                                logger.info("Bluestacks controller killed.")
                                return True
                            else:
                                raise ValueError("Failed to disconnect ADB device.")
                    return False
                except Exception as e:
                    logger.error(f"Error in kill_bluestacks: {e}")
                    raise ValueError(f"Failed to kill Bluestacks: {e}")

    def open_app(
        self,
        app: BluePyllApp,
        timeout: int = BluestacksConstants.APP_START_TIMEOUT,
        wait_time: int = BluestacksConstants.DEFAULT_WAIT_TIME,
    ) -> None:
        # Ensure Bluestacks is ready before trying to open app
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot open app - Bluestacks is not ready")
                return
            case BluestacksState.READY:
                # Ensure ADB connection is established
                is_connected = self.connect_adb()
                if not is_connected:
                    logger.warning(
                        "ADB device could not connect. Skipping 'open_app' method call."
                    )
                    return

                # Wait for app to open by checking if it's running
                start_time: float = time.time()
                while time.time() - start_time < timeout:
                    self.shell(
                        f"monkey -p {app.package_name} -v 1",
                        timeout_s=timeout,
                        read_timeout_s=timeout,
                        transport_timeout_s=timeout,
                    )
                    match self.is_app_running(app):
                        case True:
                            app.app_state.transition_to(AppLifecycleState.LOADING)
                            self.running_apps.append(app)
                            print(f"{app.app_name.title()} app opened via ADB")
                            return
                        case False:
                            time.sleep(wait_time)
                # If app isn't running after timeout, raise error
                logger.warning(
                    f"App {app.app_name.title()} did not start within {timeout} seconds"
                )

    def is_app_running(self, app: BluePyllApp, max_retries: int = 3) -> bool:
        """
        Check if an app is running.

        Args:
            app: The app to check

        Returns:
            bool: True if the app is running, False otherwise
        """
        # Ensure Bluestacks is ready before trying to check if app is running
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning(
                    "Cannot check if app is running - Bluestacks is not ready"
                )
                return
            case BluestacksState.READY:
                is_connected = self.connect_adb()
                if not is_connected:
                    logger.warning(
                        "ADB device not connected. Skipping 'is_app_running' method call."
                    )
                    return False

                try:
                    # Try multiple times to detect the app
                    for i in range(max_retries):
                        try:
                            # Get the list of running processes with a longer timeout
                            output: str = self.shell(
                                f"dumpsys window windows | grep -E 'mCurrentFocus' | grep {app.package_name}",
                                timeout_s=BluestacksConstants.APP_START_TIMEOUT,
                            )
                        except Exception as e:
                            logger.debug(f"Error checking app process: {e}")
                            time.sleep(
                                BluestacksConstants.DEFAULT_WAIT_TIME
                            )  # Wait a bit before retrying
                        if output:
                            logger.debug(f"Found app process: {output}")
                            return True
                        else:
                            logger.debug(
                                f"{app.app_name.title()} app process not found. Retrying... {i + 1}/{max_retries}"
                            )
                            time.sleep(BluestacksConstants.DEFAULT_WAIT_TIME)
                    return False
                except Exception as e:
                    logger.error(f"Error checking if app is running: {e}")
                    return False

    def close_app(
        self,
        app: BluePyllApp,
        timeout: int = BluestacksConstants.APP_START_TIMEOUT,
        wait_time: int = BluestacksConstants.DEFAULT_WAIT_TIME,
    ) -> None:
        # Ensure Bluestacks is ready before trying to close app
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot close app - Bluestacks is not ready")
                return
            case BluestacksState.READY:
                # Ensure ADB connection is established
                is_connectd = self.connect_adb()
                if not is_connectd:
                    logger.warning(
                        "ADB device could not connect. Skipping 'close_app' method call."
                    )
                    return

                start_time: float = time.time()
                while time.time() - start_time < timeout:
                    self.shell(
                        f"am force-stop {app.package_name}",
                        timeout_s=BluestacksConstants.DEFAULT_TIMEOUT,
                    )
                    match self.is_app_running(app):
                        case True:
                            time.sleep(wait_time)
                        case False:
                            app.app_state.transition_to(AppLifecycleState.CLOSED)
                            self.running_apps = [
                                existing_app
                                for existing_app in self.running_apps
                                if existing_app != app
                            ]
                            print(f"{app.app_name.title()} app closed via ADB")
                            return
                # If app is still running after timeout, raise error
                logger.warning(
                    f"App {app.app_name.title()} did not close within {timeout} seconds"
                )

    def go_home(self) -> None:
        # Ensure Bluestacks is ready before trying to go home
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot go home - Bluestacks is not ready")
                return
            case BluestacksState.READY:
                # Ensure ADB connection is established
                is_connected = self.connect_adb()
                if not is_connected:
                    logger.warning(
                        "ADB device could not connect. Skipping 'go_home' method call."
                    )
                    return
                # Go to home screen
                self.shell(
                    "input keyevent 3", timeout_s=BluestacksConstants.DEFAULT_TIMEOUT
                )
                logger.debug("Home screen opened via ADB")

    def capture_screenshot(self) -> bytes | None:
        # Ensure Bluestacks is ready before trying to capture screenshot
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot capture screenshot - Bluestacks is not ready")
                return
            case BluestacksState.READY:
                # Ensure ADB connection is established
                is_connected = self.connect_adb()
                if not is_connected:
                    logger.warning(
                        "ADB device could not connect. Skipping 'capture_screenshot' method call."
                    )
                    return None
                try:
                    # Capture the screenshot
                    screenshot_bytes: bytes = self.shell(
                        "screencap -p",
                        decode=False,
                        timeout_s=BluestacksConstants.DEFAULT_TIMEOUT,
                    )

                    return screenshot_bytes
                except Exception as e:
                    logger.error(f"Error capturing screenshot: {e}")
                    return None

    def where_elements(
        self,
        ui_elements: list[BluePyllElement],
        screenshot_img_bytes: bytes = None,
        max_tries: int = 2,
    ) -> tuple[int, int] | None:
        coord: tuple[int, int] | None = None
        for ui_element in ui_elements:
            coord = ui_element.where(
                bluepyll_controller=self,
                screenshot_img_bytes=screenshot_img_bytes,
                max_retries=max_tries,
            )
            if coord:
                return coord

    def click_elements(
        self,
        ui_elements: list[BluePyllElement],
        screenshot_img_bytes: bytes = None,
        max_tries: int = 2,
    ) -> bool:
        return any(
            ui_element.click(screenshot_img_bytes=screenshot_img_bytes, max_tries=max_tries)
            for ui_element in ui_elements
        )

    def type_text(self, text: str) -> None:
        # Ensure Bluestacks is ready before trying to type text
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot type text - Bluestacks is not ready")
                return
            case BluestacksState.READY:
                is_connected = self.connect_adb()
                if not is_connected:
                    logger.warning(
                        "ADB device not connected. Skipping 'type_text' method call."
                    )
                    return
                # Send the text using ADB
                self.shell(
                    f"input text {text}", timeout_s=BluestacksConstants.DEFAULT_TIMEOUT
                )
                logger.debug(f"Text '{text}' sent via ADB")

    def press_enter(self) -> None:
        # Ensure Bluestacks is ready before trying to press enter
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot press enter - Bluestacks is not ready")
                return
            case BluestacksState.READY:
                is_connected = self.connect_adb()
                if not is_connected:
                    logger.warning(
                        "ADB device not connected. Skipping 'press_enter' method call."
                    )
                    return
                # Send the enter key using ADB
                self.shell(
                    "input keyevent 66", timeout_s=BluestacksConstants.DEFAULT_TIMEOUT
                )
                logger.debug("Enter key sent via ADB")

    def press_esc(self) -> None:
        # Ensure Bluestacks is ready before trying to press esc
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot press esc - Bluestacks is not ready")
                return
            case BluestacksState.READY:
                is_connected = self.connect_adb()
                if not is_connected:
                    logger.warning(
                        "ADB device not connected. Skipping 'press_esc' method call."
                    )
                    return
                # Send the esc key using ADB
                self.shell(
                    "input keyevent 4", timeout_s=BluestacksConstants.DEFAULT_TIMEOUT
                )
                logger.debug("Esc key sent via ADB")

    def connect_adb(self) -> bool:
        match self.available:
            case True:
                return True
            case False:
                logger.debug(
                    "ADB device not connected. Attempting to Connect ADB device..."
                )
                self.connect()
                time.sleep(BluestacksConstants.DEFAULT_WAIT_TIME)
                match self.available:
                    case True:
                        logger.debug("ADB device connected.")
                        return True
                    case False:
                        logger.warning("ADB device could not connect.")
                        return False

    def disconnect_adb(self) -> bool:
        match self.available:
            case False:
                return True
            case True:
                logger.debug(
                    "ADB device is connected. Attempting to disconnect ADB device..."
                )
                self.close()
                time.sleep(BluestacksConstants.DEFAULT_WAIT_TIME)
                match self.available:
                    case True:
                        logger.debug("ADB device not disconnected.")
                        return False
                    case False:
                        logger.debug("ADB device disconnected.")
                        return True

    def show_recent_apps(self) -> None:
        """Show the recent apps drawer"""
        logger.info("Showing recent apps...")
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot show recent apps - Bluestacks is not ready")
                return
            case BluestacksState.READY:
                self.shell(
                    "input keyevent KEYCODE_APP_SWITCH",
                    timeout_s=BluestacksConstants.DEFAULT_TIMEOUT,
                )
                logger.debug("Recent apps drawer successfully opened")
