from dataclasses import dataclass, field
from importlib.resources import files

from pyautogui import screenshot

# OG BLUESTACKS SIZE 1920x1080
@dataclass(frozen=True)
class BlueStacksUiPaths():
    bluestacks_ads_enabled: tuple[str, float] = (str(files("bluepyll.assets").joinpath("bluestacks_ads_enabled.png")), 0.6)
    bluestacks_ads_disabled: tuple[str, float] = (str(files("bluepyll.assets").joinpath("bluestacks_ads_disabled.png")), 0.6)
    bluestacks_controller_loading: tuple[str, float] = (str(files("bluepyll.assets").joinpath("bluestacks_loading.png")), 0.74)
    bluestacks_my_games_icon: tuple[str, float] = (str(files("bluepyll.assets").joinpath("my_games_icon.png")), 0.53)
    bluestacks_revomon_logo_icon: tuple[str, float] = (str(files("bluepyll.assets").joinpath("revomon_logo_icon.png")), 0.5)
    bluestacks_store_search_bar: tuple[str, float] = (str(files("bluepyll.assets").joinpath("bluestacks_store_search_bar.png")), 0.4)
    bluestacks_store_icon: tuple[str, float] = (str(files("bluepyll.assets").joinpath("bluestacks_store_icon.png")), 0.6)
    bluestacks_playstore_search_bar: tuple[str, float] = (str(files("bluepyll.assets").joinpath("bluestacks_playstore_search_bar.png")), 0.5)
    bluestacks_loading_screen: tuple[str, float] = (str(files("bluepyll.assets").joinpath("loading_screen.png")), 0.99)
    screenshot: tuple[str, float] = (str(files("bluepyll.assets").joinpath("screenshot.png")), 0.99)

