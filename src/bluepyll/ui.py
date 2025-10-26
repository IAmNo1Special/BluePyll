import logging
from importlib.resources import files
from io import BytesIO
from pathlib import Path
from time import sleep

from adb_shell.exceptions import TcpTimeoutException
from PIL import Image
from pyautogui import ImageNotFoundException, center, locate

from .constants import BluestacksConstants
from .state_machine import BluestacksState

logger = logging.getLogger(__name__)


class BluePyllElement:
    """
    Represents a UI element.

    Attributes:
        label (str): Label of the element
        ele_type (str): Type of the element
        og_window_size (tuple[int, int]): The original size of the window the element was created from
        position (tuple[int, int] | None): Position of the element
        size (tuple[int, int] | None): Size of the element
        path (Path | None): Path to the element image
        is_static (bool): Whether the element is static or not
        confidence (float | None): Confidence of the element
        ele_txt (str | None): Text of the element
        pixel_color (tuple[int, int, int] | None): The color of the element(pixel) if 'ele_type' == 'pixel'
        region (tuple[int, int, int, int] | None): The region of the screenshot to look for the element
        center (tuple[int, int] | None): The coords of the center of the element
    """

    def __init__(
        self,
        label: str,
        ele_type: str,
        og_window_size: tuple[int, int],
        position: tuple[int, int] | None = None,
        size: tuple[int, int] | None = None,
        path: Path | None = None,
        is_static: bool = True,
        confidence: float | None = None,
        ele_txt: str | None = None,
        pixel_color: tuple[int, int, int] | None = None,
        controller=None,
    ) -> None:
        """
        Initialize a BluePyllElement.

        Args:
            label (str): Label of the element
            ele_type (str): Type of the element
            og_window_size (tuple[int, int]): The original size of the window the element was created from
            position (tuple[int, int] | None): Position of the element
            size (tuple[int, int] | None): Size of the element
            path (Path | None): Path to the element image
            is_static (bool): Whether the element is static or not
            confidence (float | None): Confidence of the element
            ele_txt (str | None): Text of the element
            pixel_color (tuple[int, int, int] | None): The color of the element(pixel) if 'ele_type' == 'pixel'
            controller: The BluePyllController instance
        """

        self.label: str = str(label).lower()
        self.ele_type: str = str(ele_type).lower()
        self.og_window_size: tuple[int, int] = int(og_window_size[0]), int(
            og_window_size[1]
        )
        self.position: tuple[int, int] | None = (
            (int(position[0]), int(position[1])) if position else None
        )
        self.size: tuple[int, int] | None = (
            (1, 1)
            if self.ele_type in ["pixel"]
            else (int(size[0]), int(size[1])) if size else None
        )
        self.path = None if self.ele_type in ["pixel"] else path
        self.is_static: bool = True if self.ele_type in ["pixel"] else is_static
        self.confidence: float | None = (
            None
            if self.ele_type in ["pixel", "text"]
            else float(confidence) if confidence else 0.7
        )
        self.ele_txt: str | None = (
            None if self.ele_type in ["pixel"] or not ele_txt else str(ele_txt).lower()
        )
        self.pixel_color: tuple[int, int, int] | None = (
            None
            if self.ele_type in ["button", "text", "input", "image"]
            else (
                (int(pixel_color[0]), int(pixel_color[1]), int(pixel_color[2]))
                if pixel_color
                else None
            )
        )
        self.region: tuple[int, int, int, int] | None = (
            None
            if self.ele_type in ["pixel"] or not self.position
            else (
                self.position[0],
                self.position[1],
                self.position[0] + self.size[0],
                self.position[1] + self.size[1],
            )
        )
        self.center: tuple[int, int] | None = (
            None
            if self.ele_type in ["text"]
            else (
                self.position
                if self.ele_type in ["pixel"]
                else (
                    (
                        self.position[0] + self.size[0] // 2,
                        self.position[1] + self.size[1] // 2,
                    )
                    if self.position and self.size
                    else None
                )
            )
        )
        self.controller = controller

    def __repr__(self):
        return f"BluePyllElement(label={self.label}, ele_type={self.ele_type}, og_window_size={self.og_window_size}, position={self.position}, size={self.size}, path={self.path}, is_static={self.is_static}, confidence={self.confidence}, ele_txt={self.ele_txt}, pixel_color={self.pixel_color}, region={self.region}, center={self.center}, controller={self.controller})"

    def scale_img_to_screen(
        self, image_path: str, screen_image: str | Image.Image | bytes
    ) -> Image.Image:
        # If screen_image is bytes, convert to PIL Image
        if isinstance(screen_image, bytes):
            screen_image = Image.open(BytesIO(screen_image))

        # If screen_image is a string (file path), open it
        elif isinstance(screen_image, str):
            screen_image = Image.open(screen_image)

        # At this point, screen_image should be a PIL Image
        game_screen_width, game_screen_height = screen_image.size

        needle_img: Image.Image = Image.open(image_path)

        needle_img_size: tuple[int, int] = needle_img.size

        original_window_size: tuple[int, int] = self.og_window_size

        ratio_width: float = game_screen_width / original_window_size[0]
        ratio_height: float = game_screen_height / original_window_size[1]

        scaled_image_size: tuple[int, int] = (
            int(needle_img_size[0] * ratio_width),
            int(needle_img_size[1] * ratio_height),
        )
        scaled_image: Image.Image = needle_img.resize(scaled_image_size)
        return scaled_image

    def capture_screenshot(self):
        """Captures a screenshot using the controller."""
        return self.controller.capture_screenshot()

    def check_pixel_color(
        self,
        target_color: tuple[int, int, int],
        image: bytes | str,
        tolerance: int = 0,
    ) -> bool:
        """Check if the pixel at (x, y) in the given image matches the target color within a tolerance."""

        def check_color_with_tolerance(
            color1: tuple[int, int, int], color2: tuple[int, int, int], tolerance: int
        ) -> bool:
            """Check if two colors are within a certain tolerance."""
            return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

        try:

            coords = self.center
            target_color = self.pixel_color
            tolerance = int(tolerance)

            if len(coords) != 2:
                raise ValueError("Coords must be a tuple of two values")
            if len(target_color) != 3:
                raise ValueError("Target color must be a tuple of three values")
            if tolerance < 0:
                raise ValueError("Tolerance must be a non-negative integer")

            screenshot = image if image else self.capture_screenshot()
            if not screenshot:
                raise ValueError("Failed to capture screenshot")

            if isinstance(screenshot, bytes):
                with Image.open(BytesIO(screenshot)) as image:
                    pixel_color = image.getpixel(coords)
                    return check_color_with_tolerance(
                        pixel_color, target_color, tolerance
                    )
            elif isinstance(screenshot, str):
                with Image.open(screenshot) as image:
                    pixel_color = image.getpixel(coords)
                    return check_color_with_tolerance(
                        pixel_color, target_color, tolerance
                    )
            else:
                raise ValueError("Image must be a bytes or str")

        except ValueError as e:
            logger.error(f"ValueError in check_pixel_color: {e}")
            raise ValueError(f"Error checking pixel color: {e}")
        except Exception as e:
            logger.error(f"Error in check_pixel_color: {e}")
            raise ValueError(f"Error checking pixel color: {e}")

    def where(
        self,
        screenshot_img_bytes: bytes = None,
        max_retries: int = 2,
    ) -> tuple[int, int] | None:
        # Ensure Bluestacks is loading or ready before trying to find UI element
        if not self.path:
            logger.warning("Cannot find UI element - BluePyllElement path is not set")
            return None
        match self.controller.bluestacks_state.current_state:
            case BluestacksState.CLOSED:
                logger.warning("Cannot find UI element - Bluestacks is closed")
                return None
            case BluestacksState.LOADING | BluestacksState.READY:
                logger.debug(f"Finding UI element. Max retries: {max_retries}")
                logger.debug(
                    f"Looking for BluePyllElement: {self.label} with confidence of {self.confidence}..."
                )
                find_ui_retries: int = 0
                while (
                    (find_ui_retries < max_retries)
                    if max_retries is not None and max_retries > 0
                    else True
                ):
                    try:
                        screen_image: bytes | None = (
                            screenshot_img_bytes
                            if screenshot_img_bytes
                            else (
                                self.controller._capture_loading_screen()
                                if self.path
                                == self.controller.elements.bluestacks_loading_img.path
                                else self.capture_screenshot()
                            )
                        )
                        if screen_image:
                            haystack_img: Image.Image = Image.open(
                                BytesIO(screen_image)
                            )
                            scaled_img: Image.Image = self.scale_img_to_screen(
                                image_path=self.path,
                                screen_image=haystack_img,
                            )
                            ui_location: tuple[int, int, int, int] | None = locate(
                                needleImage=scaled_img,
                                haystackImage=haystack_img,
                                confidence=self.confidence,
                                grayscale=True,
                                region=self.region,
                            )
                            if ui_location:
                                logger.debug(
                                    f"BluePyllElement {self.label} found at: {ui_location}"
                                )
                                ui_x_coord, ui_y_coord = center(ui_location)
                                return (ui_x_coord, ui_y_coord)
                    except ImageNotFoundException or TcpTimeoutException:
                        find_ui_retries += 1
                        logger.debug(
                            f"BluePyllElement {self.label} not found. Retrying... ({find_ui_retries}/{max_retries})"
                        )
                        sleep(BluestacksConstants.DEFAULT_WAIT_TIME)
                        continue

                logger.debug(f"Wasn't able to find BluePyllElement: {self.label}")
                return None

    def click_coord(
        self,
        coords: tuple[int, int],
        times: int = 1,
    ) -> bool:
        # Ensure Bluestacks is ready before trying to click coords
        match self.controller.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot click coords - Bluestacks is not ready")
                return False
            case BluestacksState.READY:
                is_connected = self.controller.connect_adb()
                if not is_connected:
                    logger.warning(
                        "ADB device not connected. Skipping 'click_coords' method call."
                    )
                    return False
                tap_command: str = f"input tap {coords[0]} {coords[1]}"
                for _ in range(times - 1):
                    tap_command += f" && input tap {coords[0]} {coords[1]}"

                self.controller.shell(
                    tap_command,
                    timeout_s=BluestacksConstants.DEFAULT_TIMEOUT,
                )
                logger.debug(
                    f"Click event sent via ADB at coords x={coords[0]}, y={coords[1]}"
                )
                return True

    def click(
        self,
        times: int = 1,
        screenshot_img_bytes: bytes | None = None,
        max_tries: int = 2,
    ) -> bool:
        # Ensure Bluestacks is ready before trying to click ui
        match self.controller.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot click coords - Bluestacks is not ready")
                return False
            case BluestacksState.READY:
                is_connected = self.controller.connect_adb()
                if not is_connected:
                    logger.warning(
                        "ADB device not connected. Skipping 'click_ui' method call."
                    )
                    return False
                coord: tuple[int, int] | None = self.where(
                    screenshot_img_bytes=screenshot_img_bytes, max_retries=max_tries
                )
                if not coord:
                    logger.debug(f"UI element {self.label} not found")
                    return False
                if self.click_coord(coord, times=times):
                    logger.debug(
                        f"Click event sent via ADB at coords x={coord[0]}, y={coord[1]}"
                    )
                    return True
                return False
            case _:
                logger.warning(
                    "Cannot click coords - BluePyllController.bluestacks_state.current_state is not in a valid state."
                    " Make sure it is in the 'BluestacksState.READY' state."
                )
                return False


class BluePyllElements:
    """
    Paths to UI elements used in the application.

    This class organizes UI elements into logical groups for better maintainability.
    """

    def __init__(self, bluepyll_controller):
        self.bluepyll_controller = bluepyll_controller

        self.bluestacks_loading_img: BluePyllElement = BluePyllElement(
            label="bluestacks_loading_img",
            ele_type="image",
            og_window_size=self.bluepyll_controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("bluestacks_loading_img.png"),
            confidence=0.6,
            ele_txt="Starting BlueStacks",
            controller=self.bluepyll_controller,
        )

        self.bluestacks_my_games_button: BluePyllElement = BluePyllElement(
            label="bluestacks_my_games_buttoon",
            ele_type="button",
            og_window_size=self.bluepyll_controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("bluestacks_my_games_buttoon.png"),
            confidence=0.6,
            ele_txt="My games",
            controller=self.bluepyll_controller,
        )

        self.bluestacks_store_search_input: BluePyllElement = BluePyllElement(
            label="bluestacks_store_search_input",
            ele_type="input",
            og_window_size=self.bluepyll_controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("bluestacks_store_search_input.png"),
            is_static=False,
            confidence=0.6,
            ele_txt="Search for games & apps",
            controller=self.bluepyll_controller,
        )

        self.bluestacks_store_button: BluePyllElement = BluePyllElement(
            label="bluestacks_store_button",
            ele_type="button",
            og_window_size=self.bluepyll_controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("bluestacks_store_button.png"),
            confidence=0.6,
            controller=self.bluepyll_controller,
        )

        self.bluestacks_playstore_search_inpput: BluePyllElement = BluePyllElement(
            label="bluestacks_playstore_search_input",
            ele_type="input",
            og_window_size=self.bluepyll_controller.ref_window_size,
            path=files("bluepyll.assets").joinpath(
                "bluestacks_playstore_search_input.png"
            ),
            is_static=False,
            confidence=0.5,
            ele_txt="Search for games & apps",
            controller=self.bluepyll_controller,
        )

        # Loading elements
        self.bluestacks_loading_screen_img: BluePyllElement = BluePyllElement(
            label="bluestacks_loading_screen_img",
            ele_type="image",
            og_window_size=self.bluepyll_controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("bluestacks_loading_screen_img.png"),
            is_static=False,
            confidence=0.99,
            controller=self.bluepyll_controller,
        )

        self.adb_screenshot_img: BluePyllElement = BluePyllElement(
            label="adb_screenshot_img",
            ele_type="image",
            og_window_size=self.bluepyll_controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("adb_screenshot_img.png"),
            is_static=False,
            confidence=0.99,
            controller=self.bluepyll_controller,
        )
