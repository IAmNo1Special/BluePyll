"""
Unit tests for BluePyll UI module.
"""

from unittest.mock import MagicMock

import pytest

from bluepyll.ui import BluePyllElement, BluePyllElements


class TestBluePyllElement:
    """Test the BluePyllElement class."""

    @pytest.fixture
    def mock_controller(self):
        """Create a mock controller for testing."""
        controller = MagicMock()
        controller.bluestacks_state.current_state = "READY"
        controller.ref_window_size = (1920, 1080)
        return controller

    @pytest.fixture
    def sample_element(self, mock_controller):
        """Create a sample BluePyllElement for testing."""
        return BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080),
            position=(100, 100),
            size=(200, 50),
            path="test/path/button.png",
            confidence=0.8,
            ele_txt="Test Button",
            controller=mock_controller
        )

    def test_element_initialization(self, sample_element, mock_controller):
        """Test BluePyllElement initialization."""
        assert sample_element.label == "test_button"
        assert sample_element.ele_type == "button"
        assert sample_element.og_window_size == (1920, 1080)
        assert sample_element.position == (100, 100)
        assert sample_element.size == (200, 50)
        assert sample_element.path == "test/path/button.png"
        assert sample_element.confidence == 0.8
        assert sample_element.ele_txt == "test button"  # Should be lowercase
        assert sample_element.controller == mock_controller

    def test_element_initialization_pixel_type(self):
        """Test BluePyllElement initialization for pixel type."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_pixel",
            ele_type="pixel",
            og_window_size=(1920, 1080),
            position=(50, 50),
            pixel_color=(255, 0, 0),
            controller=controller
        )

        assert element.label == "test_pixel"
        assert element.ele_type == "pixel"
        assert element.size == (1, 1)  # Pixel type should have size (1, 1)
        assert element.path is None  # Pixel type should not have path
        assert element.is_static is True  # Pixel type should be static
        assert element.confidence is None  # Pixel type should not have confidence
        assert element.ele_txt is None  # Pixel type should not have text
        assert element.pixel_color == (255, 0, 0)
        assert element.center == (50, 50)  # Center should be same as position for pixel

    def test_element_initialization_text_type(self):
        """Test BluePyllElement initialization for text type."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_text",
            ele_type="text",
            og_window_size=(1920, 1080),
            position=(100, 100),
            size=(200, 50),
            ele_txt="Test Text",
            controller=controller
        )

        assert element.label == "test_text"
        assert element.ele_type == "text"
        assert element.confidence is None  # Text type should not have confidence
        assert element.ele_txt == "test text"  # Should be lowercase
        assert element.center is None  # Text type should not have center

    def test_element_initialization_defaults(self):
        """Test BluePyllElement initialization with default values."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_element",
            ele_type="button",
            og_window_size=(1920, 1080),
            controller=controller
        )

        assert element.position is None
        assert element.size is None
        assert element.path is None
        assert element.is_static is True  # Default for non-pixel
        assert element.confidence == 0.7  # Default confidence
        assert element.ele_txt is None
        assert element.pixel_color is None
        assert element.region is None
        assert element.center is None

    def test_element_initialization_size_defaults(self):
        """Test BluePyllElement size defaults for different types."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        # Button without size should get None
        button_element = BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080),
            position=(100, 100),
            controller=controller
        )
        assert button_element.size is None

        # Pixel without size should get (1, 1)
        pixel_element = BluePyllElement(
            label="test_pixel",
            ele_type="pixel",
            og_window_size=(1920, 1080),
            position=(50, 50),
            controller=controller
        )
        assert pixel_element.size == (1, 1)

    def test_element_initialization_confidence_defaults(self):
        """Test BluePyllElement confidence defaults for different types."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        # Button without confidence should get 0.7
        button_element = BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080),
            position=(100, 100),
            size=(200, 50),
            path="test.png",
            controller=controller
        )
        assert button_element.confidence == 0.7

        # Pixel without confidence should get None
        pixel_element = BluePyllElement(
            label="test_pixel",
            ele_type="pixel",
            og_window_size=(1920, 1080),
            position=(50, 50),
            controller=controller
        )
        assert pixel_element.confidence is None

        # Text without confidence should get None
        text_element = BluePyllElement(
            label="test_text",
            ele_type="text",
            og_window_size=(1920, 1080),
            position=(100, 100),
            size=(200, 50),
            ele_txt="Test",
            controller=controller
        )
        assert text_element.confidence is None

    def test_element_region_calculation(self):
        """Test BluePyllElement region calculation."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_element",
            ele_type="button",
            og_window_size=(1920, 1080),
            position=(100, 100),
            size=(200, 50),
            controller=controller
        )

        # Region should be (left, top, right, bottom)
        assert element.region == (100, 100, 300, 150)

    def test_element_region_calculation_no_position(self):
        """Test BluePyllElement region calculation without position."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_element",
            ele_type="button",
            og_window_size=(1920, 1080),
            controller=controller
        )

        # Region should be None if no position
        assert element.region is None

    def test_element_center_calculation(self):
        """Test BluePyllElement center calculation."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_element",
            ele_type="button",
            og_window_size=(1920, 1080),
            position=(100, 100),
            size=(200, 50),
            controller=controller
        )

        # Center should be (left + width/2, top + height/2)
        assert element.center == (200, 125)

    def test_element_center_calculation_pixel(self):
        """Test BluePyllElement center calculation for pixel type."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_pixel",
            ele_type="pixel",
            og_window_size=(1920, 1080),
            position=(50, 50),
            controller=controller
        )

        # Pixel center should be same as position
        assert element.center == (50, 50)

    def test_element_center_calculation_no_position_size(self):
        """Test BluePyllElement center calculation without position or size."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_element",
            ele_type="button",
            og_window_size=(1920, 1080),
            controller=controller
        )

        # Center should be None if no position or size
        assert element.center is None

    def test_element_center_calculation_text_type(self):
        """Test BluePyllElement center calculation for text type."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_text",
            ele_type="text",
            og_window_size=(1920, 1080),
            position=(100, 100),
            size=(200, 50),
            controller=controller
        )

        # Text type should not have center
        assert element.center is None

    def test_element_string_conversion(self):
        """Test BluePyllElement string representations."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_element",
            ele_type="button",
            og_window_size=(1920, 1080),
            position=(100, 100),
            size=(200, 50),
            path="test.png",
            confidence=0.8,
            controller=controller
        )

        # Test __repr__
        repr_str = repr(element)
        assert "BluePyllElement" in repr_str
        assert "test_element" in repr_str
        assert "button" in repr_str
        assert "(1920, 1080)" in repr_str
        assert "(100, 100)" in repr_str
        assert "(200, 50)" in repr_str

    def test_element_label_lowercase(self):
        """Test that element label is converted to lowercase."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="TestButton",
            ele_type="button",
            og_window_size=(1920, 1080),
            controller=controller
        )

        assert element.label == "testbutton"

    def test_element_type_lowercase(self):
        """Test that element type is converted to lowercase."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_element",
            ele_type="Button",
            og_window_size=(1920, 1080),
            controller=controller
        )

        assert element.ele_type == "button"

    def test_element_text_lowercase(self):
        """Test that element text is converted to lowercase."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_element",
            ele_type="button",
            og_window_size=(1920, 1080),
            ele_txt="Test Text",
            controller=controller
        )

        assert element.ele_txt == "test text"

    def test_element_position_integer_conversion(self):
        """Test that position coordinates are converted to integers."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_element",
            ele_type="button",
            og_window_size=(1920, 1080),
            position=(100.5, 100.7),
            size=(200.2, 50.9),
            controller=controller
        )

        assert element.position == (100, 100)
        assert element.size == (200, 50)

    def test_element_pixel_color_integer_conversion(self):
        """Test that pixel color values are converted to integers."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)

        element = BluePyllElement(
            label="test_pixel",
            ele_type="pixel",
            og_window_size=(1920, 1080),
            position=(50, 50),
            pixel_color=(255.5, 0.7, 128.9),
            controller=controller
        )

        assert element.pixel_color == (255, 0, 128)


class TestBluePyllElements:
    """Test the BluePyllElements class."""

    @pytest.fixture
    def mock_controller(self):
        """Create a mock controller for testing."""
        controller = MagicMock()
        controller.ref_window_size = (1920, 1080)
        controller.elements = MagicMock()
        return controller

    def test_elements_initialization(self, mock_controller):
        """Test BluePyllElements initialization."""
        elements = BluePyllElements(mock_controller)

        assert elements.bluepyll_controller == mock_controller
        assert hasattr(elements, 'bluestacks_loading_img')
        assert hasattr(elements, 'bluestacks_my_games_button')
        assert hasattr(elements, 'bluestacks_store_search_input')
        assert hasattr(elements, 'bluestacks_store_button')
        assert hasattr(elements, 'bluestacks_playstore_search_input')
        assert hasattr(elements, 'bluestacks_loading_screen_img')
        assert hasattr(elements, 'adb_screenshot_img')

    def test_loading_img_element(self, mock_controller):
        """Test bluestacks_loading_img element configuration."""
        elements = BluePyllElements(mock_controller)

        loading_img = elements.bluestacks_loading_img
        assert loading_img.label == "bluestacks_loading_img"
        assert loading_img.ele_type == "image"
        assert loading_img.og_window_size == (1920, 1080)
        assert loading_img.confidence == 0.6
        assert loading_img.ele_txt == "starting bluestacks"
        assert loading_img.controller == mock_controller

    def test_my_games_button_element(self, mock_controller):
        """Test bluestacks_my_games_button element configuration."""
        elements = BluePyllElements(mock_controller)

        button = elements.bluestacks_my_games_button
        assert button.label == "bluestacks_my_games_buttoon"  # Note: typo in original
        assert button.ele_type == "button"
        assert button.og_window_size == (1920, 1080)
        assert button.confidence == 0.6
        assert button.ele_txt == "my games"
        assert button.controller == mock_controller

    def test_store_search_input_element(self, mock_controller):
        """Test bluestacks_store_search_input element configuration."""
        elements = BluePyllElements(mock_controller)

        input_element = elements.bluestacks_store_search_input
        assert input_element.label == "bluestacks_store_search_input"
        assert input_element.ele_type == "input"
        assert input_element.og_window_size == (1920, 1080)
        assert input_element.is_static is False
        assert input_element.confidence == 0.6
        assert input_element.ele_txt == "search for games & apps"
        assert input_element.controller == mock_controller

    def test_store_button_element(self, mock_controller):
        """Test bluestacks_store_button element configuration."""
        elements = BluePyllElements(mock_controller)

        button = elements.bluestacks_store_button
        assert button.label == "bluestacks_store_button"
        assert button.ele_type == "button"
        assert button.og_window_size == (1920, 1080)
        assert button.confidence == 0.6
        assert button.controller == mock_controller

    def test_playstore_search_input_element(self, mock_controller):
        """Test bluestacks_playstore_search_input element configuration."""
        elements = BluePyllElements(mock_controller)

        input_element = elements.bluestacks_playstore_search_input
        assert input_element.label == "bluestacks_playstore_search_input"
        assert input_element.ele_type == "input"
        assert input_element.og_window_size == (1920, 1080)
        assert input_element.is_static is False
        assert input_element.confidence == 0.5
        assert input_element.ele_txt == "search for games & apps"
        assert input_element.controller == mock_controller

    def test_loading_screen_img_element(self, mock_controller):
        """Test bluestacks_loading_screen_img element configuration."""
        elements = BluePyllElements(mock_controller)

        loading_screen = elements.bluestacks_loading_screen_img
        assert loading_screen.label == "bluestacks_loading_screen_img"
        assert loading_screen.ele_type == "image"
        assert loading_screen.og_window_size == (1920, 1080)
        assert loading_screen.is_static is False
        assert loading_screen.confidence == 0.99
        assert loading_screen.controller == mock_controller

    def test_adb_screenshot_img_element(self, mock_controller):
        """Test adb_screenshot_img element configuration."""
        elements = BluePyllElements(mock_controller)

        screenshot_img = elements.adb_screenshot_img
        assert screenshot_img.label == "adb_screenshot_img"
        assert screenshot_img.ele_type == "image"
        assert screenshot_img.og_window_size == (1920, 1080)
        assert screenshot_img.is_static is False
        assert screenshot_img.confidence == 0.99
        assert screenshot_img.controller == mock_controller
