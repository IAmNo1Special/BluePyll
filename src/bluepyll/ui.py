from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

from dataclasses import dataclass


class UIElement:
    """
    Represents a UI element.

    Attributes:
        label (str): Label of the element
        ele_type (str): Type of the element
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
        position: tuple[int, int] | None = None,
        size: tuple[int, int] | None = None,
        path: Path | None = None,
        is_static: bool = True,
        confidence: float | None = None,
        ele_txt: str | None = None,
        pixel_color: tuple[int, int, int] | None = None
    ) -> None:
        """
        Initialize a UIElement.
        
        Args:
            label (str): Label of the element
            ele_type (str): Type of the element
            position (tuple[int, int] | None): Position of the element
            size (tuple[int, int] | None): Size of the element
            path (Path | None): Path to the element image
            is_static (bool): Whether the element is static or not
            confidence (float | None): Confidence of the element
            ele_txt (str | None): Text of the element
            pixel_color (tuple[int, int, int] | None): The color of the element(pixel) if 'ele_type' == 'pixel'
        """
        self.label: str = label.lower()
        self.ele_type: str = ele_type.lower()
        self.position: tuple[int, int] | None = position
        self.size = (1, 1) if ele_type in ["pixel"] else size
        self.path = None if ele_type in ["pixel"] else path
        self.is_static = True if ele_type in ["pixel"] else is_static
        self.confidence = None if ele_type in ["pixel", "text"] else confidence if confidence else 0.7
        self.ele_txt = None if ele_type in ["pixel"] or not ele_txt else ele_txt.lower()
        self.pixel_color = None if ele_type in ["button", "text", "input", "image"] else pixel_color
        self.region: tuple[int, int, int, int] | None = None if ele_type in ["pixel",] or not position else (position[0], position[1], position[0] + size[0], position[1] + size[1]) if position and size else None
        self.center: tuple[int, int] | None = None if ele_type in ["text"] else self.position if ele_type in ["pixel"] else (position[0] + size[0] // 2, position[1] + size[1] // 2) if position and size else None

    def __repr__(self):
        return f"UIElement(label={self.label}, ele_type={self.ele_type}, path={self.path}, position={self.position}, size={self.size}, is_static={self.is_static}, confidence={self.confidence}, ele_txt={self.ele_txt}, pixel_color={self.pixel_color})"

@dataclass(frozen=True)
class BlueStacksUiPaths:
    """
    Paths to UI elements used in the application.
    
    This class organizes UI elements into logical groups for better maintainability.
    """
    
    bluestacks_loading_img: UIElement = UIElement(
        label="bluestacks_loading_img",
        ele_type="image",
        path=files("bluepyll.assets").joinpath("bluestacks_loading_img.png"),
        confidence=0.6,
        ele_txt="Starting BlueStacks"
    )
    
    bluestacks_my_games_button: UIElement = UIElement(
        label="bluestacks_my_games_buttoon",
        ele_type="button",
        path=files("bluepyll.assets").joinpath("bluestacks_my_games_buttoon.png"),
        confidence=0.6,
        ele_txt="My games"
    )
    
    bluestacks_store_search_input: UIElement = UIElement(
            label="bluestacks_store_search_input",
            ele_type="input",
            path=files("bluepyll.assets").joinpath("bluestacks_store_search_input.png"),
            is_static=False,
            confidence=0.6,
            ele_txt="Search for games & apps"
        )
    
    bluestacks_store_button: UIElement = UIElement(
        label="bluestacks_store_button",
        ele_type="button",
        path=files("bluepyll.assets").joinpath("bluestacks_store_button.png"),
        confidence=0.6
    )
    
    bluestacks_playstore_search_inpput: UIElement = UIElement(
        label="bluestacks_playstore_search_input",
        ele_type="input",
        path=files("bluepyll.assets").joinpath("bluestacks_playstore_search_input.png"),
        is_static=False,
        confidence=0.5,
        ele_txt="Search for games & apps"
    )
    
    # Loading elements
    bluestacks_loading_screen_img: UIElement = UIElement(
        label="bluestacks_loading_screen_img",
        ele_type="image",
        path=files("bluepyll.assets").joinpath("bluestacks_loading_screen_img.png"),
        is_static=False,
        confidence=0.99
    )
    
    adb_screenshot_img: UIElement = UIElement(
        label="adb_screenshot_img",
        ele_type="image",
        path=files("bluepyll.assets").joinpath("adb_screenshot_img.png"),
        is_static=False,
        confidence=0.99
    )

