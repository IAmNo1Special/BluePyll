"""
TODO:
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

from .ui import BlueStacksUiPaths
from .app import BluePyllApp


# Initialize logger
logger = logging.getLogger(__name__)

# Initialize paths for BlueStacks UI elements
UI_PATHS: BlueStacksUiPaths = BlueStacksUiPaths()


class AdbController:
    def __init__(self, ip: str, port: int, ref_window_size: tuple[int, int]) -> None:
        logger.info("Initializing AdbController...")
        self._ip = ip
        self._port = port
        self._ref_window_size: tuple[int, int] = ref_window_size

        self._adb_device: AdbDeviceTcp = AdbDeviceTcp(ip, port)
        self._is_connected: bool = False
        logger.info("AdbController initialized.")

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def port(self) -> int:
        return self._port

    @property
    def adb_device(self) -> AdbDeviceTcp | None:
        return self._adb_device

    @property
    def ref_window_size(self) -> tuple[int, int] | None:
        return self._ref_window_size

    @ip.setter
    def ip(self, new_ip: str) -> None:
        self._ip = new_ip
    
    @ip.getter
    def ip(self) -> str:
        return self._ip

    @port.setter
    def port(self, new_port: int) -> None:
        self._port = new_port
    
    @port.getter
    def port(self) -> int:
        return self._port

    @ref_window_size.setter
    def ref_window_size(self, width: int, height: int) -> None:
        logger.debug(f"Setting reference window size, from {self._ref_window_size} to ({width}, {height})...")
        self._ref_window_size = (width, height)
        logger.debug(f"Reference window size set to {self._ref_window_size}.")

    @ref_window_size.getter
    def ref_window_size(self) -> tuple[int, int]:
        return self._ref_window_size

    @adb_device.setter
    def adb_device(self, new_adb_device: AdbDeviceTcp) -> None:
        self._adb_device = new_adb_device

    @adb_device.getter
    def adb_device(self) -> AdbDeviceTcp:
        return self._adb_device

    def open_app(self, app: BluePyllApp) -> None:
        if not self._is_connected:
            logger.warning("ADB device not connected. Skipping open_app")
            return
        self._adb_device.shell(f"monkey -p {app.package_name} -v 1")
        # TODO: Find a better way to wait for the app to open
        pyautogui.sleep(4.0)
        print(f"{app.app_name.title()} app opened via ADB")

    def close_app(self, app: BluePyllApp) -> None:
        if not self._is_connected:
            logger.warning("ADB device not connected. Skipping close_app")
            return
        self._adb_device.shell(f"am force-stop {app.package_name}")
        print(f"{app.app_name.title()} app closed via ADB")

    def go_home(self) -> None:
        if not self._is_connected:
            logger.warning("ADB device not connected. Skipping go_home")
            return
        # Go to home screen
        self._adb_device.shell("input keyevent 3")
        logger.debug("Home screen opened via ADB")

    def capture_screenshot(self, filename: str = "screenshot.png") -> str | None:
        if not self._is_connected:
            logger.warning("ADB device not connected. Skipping capture_screenshot!")
            return None
        try:
            # Capture the screenshot
            self._adb_device.shell(f"screencap -p /sdcard/{filename}", read_timeout_s=None)
            pyautogui.sleep(0.5)

            # Pull the screenshot from the device
            self._adb_device.pull(f"/sdcard/{filename}", UI_PATHS.screenshot[0])
            pyautogui.sleep(0.5)

            # Delete the screenshot from the device
            self._adb_device.shell(f"rm /sdcard/{filename}")
            
            pyautogui.sleep(0.5)
            return UI_PATHS.screenshot[0]
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None

    def find_ui(self, ui_img_paths: list[tuple[str, float]], max_tries: int = 2) -> tuple[int, int] | None:
        logger.debug(f"Finding UI element. Max tries: {max_tries}")
        for ui_img_path in ui_img_paths:
            logger.debug(f"Processing UI image path: {ui_img_path[0]}")
            find_ui_retries = 0
            while (find_ui_retries < max_tries) if max_tries is not None and max_tries > 0 else True:
                try:
                    logger.debug(f"Locating UI element {ui_img_path[0]} with confidence {ui_img_path[1]}...")
                    screen_image = self._capture_loading_screen() if ui_img_path == UI_PATHS.bluestacks_controller_loading else self.capture_screenshot()
                    scaled_img: Image.Image = self.scale_img_to_screen(image_path=ui_img_path[0], screen_image=screen_image)
                    ui_location = pyautogui.locate(needleImage=scaled_img, haystackImage=screen_image, confidence=ui_img_path[1], grayscale=True)
                except pyautogui.ImageNotFoundException or TcpTimeoutException:
                    find_ui_retries += 1
                    logger.debug(f"UI element {ui_img_path[0]} not found. Retrying... ({find_ui_retries}/{max_tries})")
                    pyautogui.sleep(1.0)
                    continue
                if ui_location:
                    logger.debug(f"UI element {ui_img_path[0]} found at: {ui_location}")
                    ui_x_coord, ui_y_coord = pyautogui.center(ui_location)
                    return ui_x_coord, ui_y_coord
        logger.debug(f"Wasn't able to find UI element(s) {[ui_img_path for ui_img_path in ui_img_paths]}")
        return None

    def click_coords(self, coords: tuple[int, int]) -> None:
        if not self._is_connected:
            logger.warning("ADB device not connected. Skipping click_coords!")
            return
        # Send the click using ADB
        self._adb_device.shell(f"input tap {coords[0]} {coords[1]}", timeout_s=30)
        logger.debug(f"Click event sent via ADB at coords x={coords[0]}, y={coords[1]}")

    def double_click_coords(self, coords: tuple[int, int]) -> None:
        if not self._is_connected:
            logger.warning("ADB device not connected. Skipping double_click_coords!")
            return
        # Send the double click using ADB
        self._adb_device.shell(f"input tap {coords[0]} {coords[1]} && input tap {coords[0]} {coords[1]}", timeout_s=30)
        logger.debug(f"Double click event sent via ADB at coords x={coords[0]}, y={coords[1]}")

    def click_ui(self, ui_img_paths: list[tuple[str, float]], max_tries: int = 2) -> None:
        if not self._is_connected:
            logger.warning("ADB device not connected. Skipping click_ui!")
            return
        coords = self.find_ui(ui_img_paths=ui_img_paths, max_tries=max_tries)
        if coords:
            self.click_coords(coords)
            logger.debug(f"Click event sent via ADB at coords x={coords[0]}, y={coords[1]}")
        else:
            logger.debug("UI element(s) not found")

    def double_click_ui(self, ui_img_paths: list[tuple[str, float]], max_tries: int = 2) -> None:
        if not self._is_connected:
            logger.warning("ADB device not connected. Skipping double_click_ui!")
            return
        coords = self.find_ui(ui_img_paths=ui_img_paths, max_tries=max_tries)
        if coords:
            self.double_click_coords(coords)
            logger.debug(f"Double click event sent via ADB at coords x={coords[0]}, y={coords[1]}")
        else:
            logger.debug("UI element(s) not found")

    def type_text(self, text: str) -> None:
        if not self._is_connected:
            logger.warning("ADB device not connected. Skipping type_text!")
            return
        # Send the text using ADB
        self._adb_device.shell(f"input text {text}", timeout_s=30)
        logger.debug(f"Text '{text}' sent via ADB")

    def press_enter(self) -> None:
        if not self._is_connected:
            logger.warning("ADB device not connected. Skipping press_enter!")
            return
        # Send the enter key using ADB
        self._adb_device.shell("input keyevent 66", timeout_s=30)
        logger.debug("Enter key sent via ADB")

    def press_esc(self) -> None:
        if not self._is_connected:
            logger.warning("ADB device not connected. Skipping press_esc!")
            return
        # Send the esc key using ADB
        self._adb_device.shell("input keyevent 4", timeout_s=30)
        logger.debug("Esc key sent via ADB")

    def scale_img_to_screen(self, image_path: str, screen_image) -> Image.Image:
        game_screen_width, game_screen_height = Image.open(screen_image).size
        original_image: ImageFile.ImageFile = Image.open(image_path)
        original_image_size: tuple[int, int] = original_image.size

        original_window_size: tuple[int, int] = self._ref_window_size

        ratio_width: float = game_screen_width / original_window_size[0]
        ratio_height: float= game_screen_height / original_window_size[1]

        scaled_image_size: tuple[int, int] = (int(original_image_size[0] * ratio_width), int(original_image_size[1] * ratio_height))
        scaled_image: Image.Image = original_image.resize(scaled_image_size)
        return scaled_image

    def connect(self) -> None:
        if not self._is_connected:
            logger.debug("Connecting ADB device...")
            self._adb_device.connect()
            self._is_connected = True
            logger.debug("ADB device connected.")

    def disconnect(self) -> None:
        if self._adb_device and self._is_connected:
            logger.debug("Disconnecting ADB device...")
            self._adb_device.close()
            self._is_connected = False
            logger.debug("ADB device disconnected.")

    def check_pixel_color(self, coords: tuple[int, int], target_color: tuple[int, int, int], tolerance: int = 0) -> bool:
        """Check if the pixel at (x, y) in the given image matches the target color within a tolerance."""

        def check_color_with_tolerance(color1, color2, tolerance):
            """Check if two colors are within a certain tolerance."""
            return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

        screenshot = self.capture_screenshot()
        image = Image.open(screenshot)
        pixel_color = image.getpixel(coords)
        return check_color_with_tolerance(pixel_color, target_color, tolerance)

    def __str__(self) -> str:
        return f"AdbController(ip={self._ip}, port={self._port}, ref_window_size={self._ref_window_size})"

    def __repr__(self) -> str:
        return f"AdbController(ip={self._ip}, port={self._port}, ref_window_size={self._ref_window_size})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AdbController):
            return False
        return self._ip == other._ip and self._port == other._port and self._ref_window_size == other._ref_window_size


class BluestacksController(AdbController):
    def __init__(self, ip="127.0.0.1", port=5555, ref_window_size=(1920, 1080)) -> None:
        super().__init__(ip, port, ref_window_size)
        logger.info("Initializing BluestacksController")
        self._filepath: str = None
        self._is_open: bool = False
        self._is_loaded: bool = False
        self._is_loading: bool = False
        
        self._set_state()
        self._open_controller()
        logger.debug(f"BluestacksController initialized with the following state:\n{pprint(self.__dict__)}\n")

    @property
    def filepath(self) -> str:
        return self._filepath
    
    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def is_loading(self) -> bool:
        return self._is_loading

    @filepath.setter
    def filepath(self, value: str) -> None:
        """Setter for filepath"""
        if value and os.path.exists(value):
            logger.debug(f"Setting filepath to {value}.")
            self._filepath = value
            logger.debug(f"Filepath manually set to {self._filepath}.")
        else:
            logger.warning("Invalid filepath provided or file does not exist!")

    @filepath.getter
    def filepath(self) -> str:
        return self._filepath
    
    @is_open.setter
    def is_open(self, value: bool) -> None:
        self._is_open = value

    def _set_filepath(self):
        logger.debug("Setting filepath...")
        program_files_paths = [os.environ.get("ProgramFiles"), ]
        for path in program_files_paths:
            if path:
                potential_paths = glob.glob(os.path.join(path, "BlueStacks_nxt", "HD-Player.exe"))
                self._filepath = potential_paths[0] if potential_paths else None
            if self._filepath is not None:
                logger.debug(f"HD-Player.exe filepath set to {self._filepath}.")
                break
            else:
                #TODO: Handle case where HD-Player.exe is not found. User may need to manually specify the filepath or install BlueStacks
                logger.warning("Could not find HD-Player.exe filepath!")

    def _set_is_open(self) -> None:
        logger.debug("Setting is_open state...")
        self._is_open = "HD-Player.exe".lower() in [p.name().lower() for p in psutil.process_iter(["name"])]
        logger.debug(f"Bluestacks is open") if self._is_open else logger.debug("Bluestacks is not open")
        
    def _set_is_loading(self) -> None:
        logger.debug("Setting is_loading state...")
        if self._is_loaded is True:
            self._is_loading = False
            return
        while self._is_open is True and self._is_loaded is False:
            bluestacks_loading_bar_position = self.find_ui(ui_img_paths=[UI_PATHS.bluestacks_controller_loading], max_tries=2)
            self._is_loading = True if bluestacks_loading_bar_position else False
            if self._is_loading is True:
                logger.debug("Bluestacks is still loading")
                pyautogui.sleep(1.0)
                continue
            else:
                self._is_loaded = True
                self.connect()
                logger.debug("Bluestacks has finished loading")

    def _set_state(self):
        logger.debug("Setting Bluestacks controller state...")
        self._set_filepath()
        self._set_is_open()
        self._set_is_loading()
        logger.debug(f"Bluestacks controller state set: {pprint(self.__dict__)}\n")

    def _refresh_state(self):
        logger.debug("refreshing Bluestacks controller state...")
        self._set_is_open()
        self._set_is_loading()
        logger.debug(f"Bluestacks controller state refreshed: {pprint(self.__dict__)}\n")

    def _reset_state(self):
        logger.debug("Resetting Bluestacks controller state...")
        self._filepath = None
        self._is_open = False
        self._is_loaded = False
        self._is_loading = False
        logger.debug(f"Bluestacks controller state reset: {pprint(self.__dict__)}\n")

    def _capture_loading_screen(self) -> str | None:
        logger.debug("Capturing loading screen...")
        hwnd = win32gui.FindWindow(None, "Bluestacks App Player")
        if hwnd:
            try:
                # Restore the window if minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # Pin the window to the foreground
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                pyautogui.sleep(0.5)
                rect = win32gui.GetWindowRect(hwnd)
                image = ImageGrab.grab(bbox=rect)
                image.save(UI_PATHS.bluestacks_loading_screen[0])
                # Unpin the window from the foreground
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)
                logger.debug(f"Loading screen captured and saved to: {UI_PATHS.bluestacks_loading_screen[0]}")
                return UI_PATHS.bluestacks_loading_screen[0]
            except Exception as e:
                logger.warning(f"A handler for this exception needs to be made: {e}")
                raise Exception(f"A handler for this exception needs to be made: {e}")
        else:
            logger.warning("Could not find Bluestacks window")
            return None

    def _open_controller(self):
        if self._is_open is False:
            logger.info("Opening Bluestacks controller...")
            os.startfile(self._filepath)
            pyautogui.sleep(8.0)
            self._refresh_state()
            logger.debug(f"Bluestacks controller opened.")
        elif self._is_open is True:
            self._refresh_state()
            logger.info("Bluestacks controller is already open.")

    def kill_controller(self):
        """
        Kill the Bluestacks controller process. This will also close the ADB connection.
        """
        logger.info("Killing Bluestacks controller...")
        for proc in psutil.process_iter(["pid", "name"]):
            info = proc.info
            if info["name"] == "HD-Player.exe":
                self._adb_device.disconnect()
                proc.kill()
        self._refresh_state()
        logger.debug("Bluestacks controller killed.")

    def show_recent_apps(self) -> None:
        hwnd = win32gui.FindWindow(None, "Bluestacks App Player")
        if hwnd:
            logger.info("Showing recent apps...")
            # Restore the window if minimized
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            # Pin the window to the foreground
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            pyautogui.sleep(0.5)
            
            pyautogui.keyDown("ctrl")
            pyautogui.keyDown("shift")
            pyautogui.keyDown("5")
            pyautogui.sleep(0.25)
            pyautogui.keyUp("ctrl")
            pyautogui.keyUp("shift")
            pyautogui.keyUp("5")

            # Unpin the window from the foreground
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)
            logger.debug("Recent apps showing.")
    
    

