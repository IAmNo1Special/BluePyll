"""
Controller for managing the BlueStacks emulator.
"""

import logging
import os
import glob
from pprint import pprint

from PIL import Image, ImageFile, ImageGrab
import win32gui
import win32con
import psutil
import pyautogui
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.exceptions import TcpTimeoutException
import time

from .constants import BluestacksConstants
from .ui import BlueStacksUiPaths, UIElement
from .app import BluePyllApp
from .utils import ImageTextChecker


# Initialize logger
logger = logging.getLogger(__name__)

# Initialize paths for BlueStacks UI elements
UI_PATHS: BlueStacksUiPaths = BlueStacksUiPaths()


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


class BluestacksController(AdbDeviceTcp):
    """
    Controller for managing the BlueStacks emulator.
    
    This class handles:
    - BlueStacks emulator state management
    - Process control (start/stop)
    - ADB connection management
    - UI automation
    
    Attributes:
        img_txt_checker (ImageTextChecker): Text checker for UI elements
        _ref_window_size (tuple[int, int]): Reference window size
        _filepath (str): Path to BlueStacks executable
        _is_open (bool): Current open state of the emulator
        _is_loaded (bool): Current loaded state of the emulator
        _is_loading (bool): Current loading state of the emulator
    """
    
    def __init__(self, 
                 ip: str = BluestacksConstants.DEFAULT_IP, 
                 port: int = BluestacksConstants.DEFAULT_PORT, 
                 ref_window_size: tuple[int, int] = BluestacksConstants.DEFAULT_REF_WINDOW_SIZE) -> None:
        """
        Initialize the BluestacksController.
        
        Args:
            ip (str): IP address of the ADB server
            port (int): Port of the ADB server
            ref_window_size (tuple[int, int]): Reference window size for UI scaling
        
        Raises:
            ValueError: If invalid parameters are provided
        """
        super().__init__(ip, port)
        logger.info("Initializing BluestacksController")
        self.img_txt_checker: ImageTextChecker = ImageTextChecker()
        self._ref_window_size: tuple[int, int] = ref_window_size
        self._filepath: str | None = None
        self._is_open: bool = False
        self._is_loaded: bool = False
        self._is_loading: bool = False
        
        # Set default timeout
        self._default_transport_timeout_s: int = 10.0
        
        self._update_state()
        self.open_bluestacks()
        logger.debug(f"BluestacksController initialized with the following state:\n{pprint(self.__dict__)}\n")

    def _validate_and_convert_int(self, value: int | str, param_name: str) -> int:
        """Validate and convert value to int if possible"""
        if not isinstance(value, int):
            try:
                value: int = int(value)
            except ValueError as e:
                logger.error(f"ValueError in {param_name}: {e}")
                raise ValueError(f"Error in {param_name}: {e}")
        return value

    def _update_state(self, reset: bool = False) -> None:
        """Update or reset the controller's state"""
        if reset:
            self._filepath: str | None = None
            self._is_open: bool = False
            self._is_loaded: bool = False
            self._is_loading: bool = False
        else:
            self._autoset_filepath()
            self._autoset_is_open()
        logger.debug(f"Bluestacks controller state updated: {pprint(self.__dict__)}\n")


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
                    logger.warning("ValueError while trying to set BlueStacksController 'ref_window_size': Provided width must be positive integers!")
                    raise ValueError("Provided width must be positive integers")
            else:
                logger.warning("ValueError while trying to set BlueStacksController 'ref_window_size': Provided width must be an integer or the string representation of an integer!")
                raise ValueError("Provided width must be integer or the string representation of an integer!")

        if not isinstance(height, int):
            if isinstance(height, str) and height.isdigit():
                height: int = int(height)
                if height <= 0:
                    logger.warning("ValueError while trying to set BlueStacksController 'ref_window_size': Provided height must be positive integers!")
                    raise ValueError("Provided height must be positive integers")
            else:
                logger.warning("ValueError while trying to set BlueStacksController 'ref_window_size': Provided height must be an integer or the string representation of an integer!")
                raise ValueError("Provided height must be integer or the string representation of an integer!")

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
            logger.warning("ValueError while trying to set BlueStacksController 'filepath': Provided filepath must be a string!")
            raise ValueError("Provided filepath must be a string")

        if not os.path.exists(filepath):
            logger.warning("ValueError while trying to set BlueStacksController 'filepath': Provided filepath does not exist!")
            raise ValueError("Provided filepath does not exist")

        self._filepath: str = filepath

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def is_loading(self) -> bool:
        return self._is_loading

    def _autoset_filepath(self):
        logger.debug("Setting filepath...")
        program_files_paths: list[str] = [os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")]
        for path in program_files_paths:
            if path:
                potential_paths: list[str] = glob.glob(os.path.join(path, "BlueStacks_nxt", "HD-Player.exe"))
                self._filepath: str | None = potential_paths[0] if potential_paths else None
            if self._filepath is not None:
                logger.debug(f"HD-Player.exe filepath set to {self._filepath}.")
                break
        if not self._filepath:
            logger.error("Could not find HD-Player.exe. Please ensure BlueStacks is installed or manually specify the filepath.")
            raise FileNotFoundError("Could not find HD-Player.exe. Please ensure BlueStacks is installed or manually specify the filepath.")

    def _autoset_is_open(self) -> None:
        logger.debug("Setting is_open state...")
        self._is_open: bool = any(p.name().lower() == "HD-Player.exe".lower() for p in psutil.process_iter(["name"]))
        logger.debug(f"Bluestacks is open") if self._is_open else logger.debug("Bluestacks is not open")

    def _autoset_is_loading(self):
        """
        Set the loading state based on the loading screen.
        """
        if not self._is_open:
            logger.debug("Cannot check for loading screen if Bluestacks is not open.")
            self._is_loading: bool = False
            self._is_loaded: bool = False
            return
            
        loading_screen = self.find_ui([UI_PATHS.bluestacks_loading_img])
        if loading_screen:
            self._is_loading: bool = True
            self._is_loaded: bool = False
            logger.debug("Bluestacks is loading...")
            return
            
        # If we were loading but can't find the loading screen anymore,
        # we assume Bluestacks has finished loading
        if self._is_loading and not loading_screen:
            self._is_loading: bool = False
            self._is_loaded: bool = True
            logger.debug("Bluestacks has finished loading")
            return
            
        logger.debug("Bluestacks is not loading")
        return

    def _capture_loading_screen(self) -> str | None:
        logger.debug("Capturing loading screen...")
        hwnd: int = win32gui.FindWindow(None, "Bluestacks App Player")
        if hwnd:
            print(f"HWND ------------------------------------------------------------------> {hwnd}")
            try:
                # Restore the window if minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # Pin the window to the foreground
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                pyautogui.sleep(0.5)
                rect: tuple[int, int, int, int] = win32gui.GetWindowRect(hwnd)
                bluestacks_window_image: Image.Image = ImageGrab.grab(bbox=rect)
                pyautogui.sleep(0.5)
                try:
                    # Save loading screen image
                    bluestacks_window_image.save(UI_PATHS.bluestacks_loading_screen_img.path)
                except (ValueError, OSError) as e:
                    logger.error(f"Error saving BlueStacks loading screen image: {e}")
                    return None
                # Unpin the window from the foreground
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)
                logger.debug(f"Loading screen captured and saved to: {UI_PATHS.bluestacks_loading_screen_img.path}")
                return UI_PATHS.bluestacks_loading_screen_img.path
            except Exception as e:
                logger.warning(f"Error capturing loading screen: {e}")
                raise Exception(f"Error capturing loading screen: {e}")
        else:
            logger.warning("Could not find Bluestacks window")
            return None

    def open_bluestacks(self, max_retries: int = BluestacksConstants.DEFAULT_MAX_RETRIES, wait_time: int = BluestacksConstants.DEFAULT_WAIT_TIME, timeout_s: int = BluestacksConstants.DEFAULT_TIMEOUT) -> None:
        """
        Open the Bluestacks controller window.
        
        Args:
            max_retries: Maximum number of attempts to find the window
            wait_time: Delay between retries in seconds
            timeout_s: Total timeout in seconds
            
        Returns:
            None
        """
        max_retries: int = self._validate_and_convert_int(max_retries, "max_retries")
        wait_time: int = self._validate_and_convert_int(wait_time, "wait_time")
        timeout_s: int = self._validate_and_convert_int(timeout_s, "timeout_s")
        
        self._autoset_is_open()
        if self._is_open is False:
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
                self._autoset_is_open()
                if self._is_open:
                    logger.info("Bluestacks controller opened successfully.")
                    self._wait_for_load()
                    return
                
                if time.time() - start_time > timeout_s:
                    logger.error("Timeout waiting for Bluestacks window to appear")
                    raise Exception("Timeout waiting for Bluestacks window to appear")
                    
                logger.warning(f"Attempt {attempt + 1}/{max_retries}: Could not find Bluestacks window.")
                time.sleep(wait_time)
            
            logger.error(f"Failed to find Bluestacks window after all attempts {attempt + 1}/{max_retries}")
            raise Exception(f"Failed to find Bluestacks window after all attempts {attempt + 1}/{max_retries}")
                    
        else:
            logger.info("Bluestacks controller is already open.")
            return

    def _wait_for_load(self):
        logger.debug("Waiting for Bluestacks to load...")
        while not self._is_loaded:
            self._autoset_is_loading()
            if self._is_loading:
                logger.debug("Bluestacks is currently loading...")
                # Wait a bit before checking again
                pyautogui.sleep(1.0)
            else:
                logger.debug("Bluestacks is not loading")
        logger.info("Bluestacks is loaded & ready.")

    def kill_bluestacks(self) -> None:
        """
        Kill the Bluestacks controller process. This will also close the ADB connection.
        """
        logger.info("Killing Bluestacks controller...")
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    info = proc.info
                    if info["name"] == "HD-Player.exe":
                        self.disconnect()
                        proc.kill()
                        proc.wait(timeout=5)  # Wait for process to terminate
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    logger.warning(f"Error killing process: {e}")
        except Exception as e:
            logger.error(f"Error in kill_bluestacks: {e}")
            raise ValueError(f"Failed to kill Bluestacks: {e}")
        
        self._update_state(reset=True)
        logger.info("Bluestacks controller killed.")


    def open_app(self, app: BluePyllApp, timeout: int = BluestacksConstants.APP_START_TIMEOUT, wait_time: int = BluestacksConstants.DEFAULT_WAIT_TIME) -> None:
        # Ensure Bluestacks is loaded before trying to open app
        if not self._is_loaded:
            logger.warning("Cannot open app - Bluestacks is not loaded")
            return
            
        # Ensure ADB connection is established
        if not self.available:
            logger.debug("Connecting ADB device...")
            self.connect()
            if not self.available:
                logger.warning("ADB device not connected. Skipping open_app")
                return
        
        self.shell(f"monkey -p {app.package_name} -v 1")
        # Wait for app to open by checking if it's running
        start_time: float = time.time()
        while time.time() - start_time < timeout:
            if self.is_app_running(app):
                app.is_app_open = True
                app.is_app_loading = True
                print(f"{app.app_name.title()} app opened via ADB")
                return
            else:
                time.sleep(wait_time)
        # If app isn't running after timeout, raise error
        logger.warning(f"App {app.app_name.title()} did not start within {timeout} seconds")
        app.is_app_open = False
        app.is_app_loading = False

    def is_app_running(self, app: BluePyllApp) -> bool:
        """
        Check if an app is running.
        
        Args:
            app: The app to check
            
        Returns:
            bool: True if the app is running, False otherwise
        """
        if not self.available:
            logger.warning("ADB device not connected. Skipping is_app_running")
            return False
            
        try:
            # Try multiple times to detect the app
            for i in range(12):
                try:
                    # Get the list of running processes with a longer timeout
                    output: str = self.shell(f"dumpsys window windows | grep -E 'mCurrentFocus' | grep {app.package_name}", timeout_s=BluestacksConstants.APP_START_TIMEOUT)
                except Exception as e:
                    logger.debug(f"Error checking app process: {e}")
                    time.sleep(BluestacksConstants.DEFAULT_WAIT_TIME)  # Wait a bit before retrying
                if output:
                    logger.debug(f"Found app process: {output}")
                    return True
                else:
                    logger.debug(f"{app.app_name.title()} app process not found. Retrying... {i + 1}/12")
                    time.sleep(BluestacksConstants.DEFAULT_WAIT_TIME)
            return False
        except Exception as e:
            logger.error(f"Error checking if app is running: {e}")
            return False

    def close_app(self, app: BluePyllApp) -> None:
        if not self.available :
            logger.warning("ADB device not connected. Skipping close_app")
            return
        self.shell(f"am force-stop {app.package_name}")
        print(f"{app.app_name.title()} app closed via ADB")

    def go_home(self) -> None:
        if not self.available :
            logger.warning("ADB device not connected. Skipping go_home")
            return
        # Go to home screen
        self.shell("input keyevent 3")
        logger.debug("Home screen opened via ADB")

    def capture_screenshot(self, filename: str = "adb_screenshot_img.png") -> str | None:
        if not self.available :
            logger.warning("ADB device not connected. Skipping capture_screenshot!")
            return None
        try:
            # Capture the screenshot
            self.shell(f"screencap -p /sdcard/{filename}", read_timeout_s=None)
            pyautogui.sleep(0.5)

            # Pull the screenshot from the device
            self.pull(f"/sdcard/{filename}", UI_PATHS.adb_screenshot_img.path)
            pyautogui.sleep(0.5)

            # Delete the screenshot from the device
            self.shell(f"rm /sdcard/{filename}")
            
            pyautogui.sleep(0.5)
            return UI_PATHS.adb_screenshot_img.path
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None

    def find_ui(self, ui_elements: list[UIElement], max_tries: int = 2) -> tuple[int, int] | None:
        logger.debug(f"Finding UI element. Max tries: {max_tries}")
        for ui_element in ui_elements:
            logger.debug(f"Looking for UIElement: {ui_element.label} with confidence of {ui_element.confidence}...")
            find_ui_retries: int = 0
            while (find_ui_retries < max_tries) if max_tries is not None and max_tries > 0 else True:
                try:
                    screen_image: str | None = self._capture_loading_screen() if ui_element.path == UI_PATHS.bluestacks_loading_img.path else self.capture_screenshot()
                    if screen_image:
                        haystack_img: Image.Image = Image.open(screen_image)
                        scaled_img: Image.Image = self.scale_img_to_screen(image_path=ui_element.path, screen_image=screen_image)
                        ui_location: tuple[int, int, int, int] | None = pyautogui.locate(needleImage=scaled_img, haystackImage=haystack_img, confidence=ui_element.confidence, grayscale=True, region=ui_element.region)
                        if ui_location:
                            logger.debug(f"UIElement {ui_element.label} found at: {ui_location}")
                            ui_x_coord, ui_y_coord = pyautogui.center(ui_location)
                            return (ui_x_coord, ui_y_coord)
                except pyautogui.ImageNotFoundException or TcpTimeoutException:
                    find_ui_retries += 1
                    logger.debug(f"UIElement {ui_element.label} not found. Retrying... ({find_ui_retries + 1}/{max_tries})")
                    pyautogui.sleep(1.0)
                    continue
                
        logger.debug(f"Wasn't able to find UIElement(s) {[ui_element.label for ui_element in ui_elements]}")
        return None

    def click_coords(self, coords: tuple[int, int]) -> None:
        if not self.available :
            logger.warning("ADB device not connected. Skipping click_coords!")
            return
        # Send the click using ADB
        self.shell(f"input tap {coords[0]} {coords[1]}", timeout_s=30)
        logger.debug(f"Click event sent via ADB at coords x={coords[0]}, y={coords[1]}")

    def double_click_coords(self, coords: tuple[int, int]) -> None:
        if not self.available :
            logger.warning("ADB device not connected. Skipping double_click_coords!")
            return
        # Send the double click using ADB
        self.shell(f"input tap {coords[0]} {coords[1]} && input tap {coords[0]} {coords[1]}", timeout_s=30)
        logger.debug(f"Double click event sent via ADB at coords x={coords[0]}, y={coords[1]}")

    def click_ui(self, ui_elements: list[UIElement], max_tries: int = 2) -> None:
        if not self.available :
            logger.warning("ADB device not connected. Skipping click_ui!")
            return
        coords: tuple[int, int] | None = self.find_ui(ui_elements=ui_elements, max_tries=max_tries)
        if coords:
            self.click_coords(coords)
            logger.debug(f"Click event sent via ADB at coords x={coords[0]}, y={coords[1]}")
        else:
            logger.debug(f"UI element(s) {[ui_element.label for ui_element in ui_elements]} not found")

    def double_click_ui(self, ui_elements: list[UIElement], max_tries: int = 2) -> None:
        if not self.available :
            logger.warning("ADB device not connected. Skipping double_click_ui!")
            return
        coords: tuple[int, int] | None = self.find_ui(ui_elements=ui_elements, max_tries=max_tries)
        if coords:
            self.double_click_coords(coords)
            logger.debug(f"Double click event sent via ADB at coords x={coords[0]}, y={coords[1]}")
        else:
            logger.debug("UI element(s) not found")

    def type_text(self, text: str) -> None:
        if not self.available :
            logger.warning("ADB device not connected. Skipping type_text!")
            return
        # Send the text using ADB
        self.shell(f"input text {text}", timeout_s=30)
        logger.debug(f"Text '{text}' sent via ADB")

    def press_enter(self) -> None:
        if not self.available :
            logger.warning("ADB device not connected. Skipping press_enter!")
            return
        # Send the enter key using ADB
        self.shell("input keyevent 66", timeout_s=30)
        logger.debug("Enter key sent via ADB")

    def press_esc(self) -> None:
        if not self.available :
            logger.warning("ADB device not connected. Skipping press_esc!")
            return
        # Send the esc key using ADB
        self.shell("input keyevent 4", timeout_s=30)
        logger.debug("Esc key sent via ADB")

    def scale_img_to_screen(self, image_path: str, screen_image) -> Image.Image:
        game_screen_width, game_screen_height = Image.open(screen_image).size
        
        original_image: ImageFile.ImageFile = Image.open(image_path)
        original_image_size: tuple[int, int] = original_image.size

        original_window_size: tuple[int, int] = self._ref_window_size

        ratio_width: float = game_screen_width / original_window_size[0]
        ratio_height: float = game_screen_height / original_window_size[1]

        scaled_image_size: tuple[int, int] = (int(original_image_size[0] * ratio_width), int(original_image_size[1] * ratio_height))
        scaled_image: Image.Image = original_image.resize(scaled_image_size)
        return scaled_image

    def connect_adb(self) -> None:
        if not self.available :
            logger.debug("Connecting ADB device...")
            self.connect()
            logger.debug("ADB device connected.")
        else:
            logger.debug("ADB device is already connected.")

    def disconnect(self) -> None:
        if self.available :
            logger.debug("Disconnecting ADB device...")
            self.close()
            logger.debug("ADB device disconnected.")

    def check_pixel_color(self, coords: tuple[int, int], target_color: tuple[int, int, int], tolerance: int = 0) -> bool:
        """Check if the pixel at (x, y) in the given image matches the target color within a tolerance."""
        
        def check_color_with_tolerance(color1: tuple[int, int, int], color2: tuple[int, int, int], tolerance: int) -> bool:
            """Check if two colors are within a certain tolerance."""
            return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))
        
        try:
            # Convert coordinates to integers
            coords = tuple(int(x) for x in coords)
            # Convert target color to integers
            target_color = tuple(int(x) for x in target_color)
            # Convert tolerance to integer
            tolerance = int(tolerance)
            
            if len(coords) != 2:
                raise ValueError("Coords must be a tuple of two values")
            if len(target_color) != 3:
                raise ValueError("Target color must be a tuple of three values")
            if tolerance < 0:
                raise ValueError("Tolerance must be a non-negative integer")
            
            screenshot = self.capture_screenshot()
            if not screenshot:
                raise ValueError("Failed to capture screenshot")
                
            with Image.open(screenshot) as image:
                pixel_color = image.getpixel(coords)
                return check_color_with_tolerance(pixel_color, target_color, tolerance)
                
        except ValueError as e:
            logger.error(f"ValueError in check_pixel_color: {e}")
            raise ValueError(f"Error checking pixel color: {e}")
        except Exception as e:
            logger.error(f"Error in check_pixel_color: {e}")
            raise ValueError(f"Error checking pixel color: {e}")

    def show_recent_apps(self) -> None:
        """Show the recent apps drawer"""
        logger.info("Showing recent apps...")
        self.shell('input keyevent KEYCODE_APP_SWITCH')
        logger.debug("Recent apps drawer successfully opened")
    
    
