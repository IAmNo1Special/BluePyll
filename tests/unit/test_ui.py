"""
Unit tests for UI components.
"""

import pytest
from unittest.mock import Mock, patch

from bluepyll.ui import BluePyllElement, BluePyllElements
from bluepyll.exceptions import BluePyllError


class TestBluePyllElement:
    """Test cases for BluePyllElement class."""

    def test_element_creation_minimal(self):
        """Test element creation with minimal required parameters."""
        element = BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080)
        )

        assert element.label == "test_button"
        assert element.ele_type == "button"
        assert element.og_window_size == (1920, 1080)
        assert element.position is None
        assert element.size is None
        assert element.path is None
        assert element.confidence == 0.7
        assert element.is_static is True

    def test_element_creation_with_position(self):
        """Test element creation with position."""
        element = BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080),
            position=(100, 200)
        )

        assert element.position == (100, 200)

    def test_element_creation_with_size(self):
        """Test element creation with size."""
        element = BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080),
            size=(50, 30)
        )

        assert element.size == (50, 30)

    def test_element_pixel_type_defaults(self):
        """Test pixel element type has correct defaults."""
        element = BluePyllElement(
            label="test_pixel",
            ele_type="pixel",
            og_window_size=(1920, 1080),
            position=(100, 200)
        )

        assert element.size == (1, 1)  # Pixel elements default to 1x1
        assert element.path is None  # Pixel elements don't have paths
        assert element.is_static is True  # Pixel elements are static
        assert element.confidence is None  # Pixel elements don't have confidence

    def test_element_text_type_defaults(self):
        """Test text element type has correct defaults."""
        element = BluePyllElement(
            label="test_text",
            ele_type="text",
            og_window_size=(1920, 1080),
            ele_txt="Hello World"
        )

        assert element.confidence is None  # Text elements don't have confidence
        assert element.ele_txt == "hello world"  # Text is lowercased

    def test_element_confidence_default(self):
        """Test confidence default for non-pixel, non-text elements."""
        element = BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080)
        )

        assert element.confidence == 0.7

    def test_element_confidence_custom(self):
        """Test custom confidence value."""
        element = BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080),
            confidence=0.9
        )

        assert element.confidence == 0.9

    def test_element_text_lowercasing(self):
        """Test that element text is lowercased."""
        element = BluePyllElement(
            label="test_text",
            ele_type="text",
            og_window_size=(1920, 1080),
            ele_txt="Hello World"
        )

        assert element.ele_txt == "hello world"

    def test_element_label_lowercasing(self):
        """Test that element label is lowercased."""
        element = BluePyllElement(
            label="TestButton",
            ele_type="button",
            og_window_size=(1920, 1080)
        )

        assert element.label == "testbutton"

    def test_element_type_lowercasing(self):
        """Test that element type is lowercased."""
        element = BluePyllElement(
            label="test_element",
            ele_type="Button",
            og_window_size=(1920, 1080)
        )

        assert element.ele_type == "button"

    def test_element_pixel_color_validation(self):
        """Test pixel color validation for pixel elements."""
        element = BluePyllElement(
            label="test_pixel",
            ele_type="pixel",
            og_window_size=(1920, 1080),
            pixel_color=(255, 128, 0)
        )

        assert element.pixel_color == (255, 128, 0)

    def test_element_pixel_color_none_for_non_pixel(self):
        """Test pixel color is None for non-pixel elements."""
        element = BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080),
            pixel_color=(255, 128, 0)
        )

        assert element.pixel_color is None

    def test_element_region_calculation(self):
        """Test region calculation based on position and size."""
        element = BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080),
            position=(100, 200),
            size=(50, 30)
        )

        assert element.region == (100, 200, 150, 230)  # x, y, x+width, y+height

    def test_element_region_none_without_position(self):
        """Test region is None when position is not set."""
        element = BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080)
        )

        assert element.region is None

    def test_element_center_calculation(self):
        """Test center calculation based on position and size."""
        element = BluePyllElement(
            label="test_button",
            ele_type="button",
            og_window_size=(1920, 1080),
            position=(100, 200),
            size=(50, 30)
        )

        assert element.center == (125, 215)  # x+width//2, y+height//2

    def test_element_center_pixel_type(self):
        """Test center for pixel type elements."""
        element = BluePyllElement(
            label="test_pixel",
            ele_type="pixel",
            og_window_size=(1920, 1080),
            position=(100, 200)
        )

        assert element.center == (100, 200)  # Same as position for pixel

    def test_element_center_text_type(self):
        """Test center is None for text type elements."""
        element = BluePyllElement(
            label="test_text",
            ele_type="text",
            og_window_size=(1920, 1080)
        )

        assert element.center is None

    @patch('bluepyll.ui.ImageGrab.grab')
    def test_capture_screenshot(self, mock_grab):
        """Test screenshot capture functionality."""
        mock_controller = Mock()
        mock_screenshot = Mock()
        mock_grab.return_value = mock_screenshot

        element = BluePyllElement(
            label="test_element",
            ele_type="button",
            og_window_size=(1920, 1080),
            controller=mock_controller
        )

        result = element.capture_screenshot()

        mock_grab.assert_called_once()
        assert result == mock_screenshot

    def test_check_pixel_color_invalid_coords(self, caplog):
        """Test pixel color check with invalid coordinates."""
        element = BluePyllElement(
            label="test_pixel",
            ele_type="pixel",
            og_window_size=(1920, 1080),
            position=(100, 200),
            pixel_color=(255, 0, 0)
        )

        # Mock invalid coordinates (not a 2-tuple)
        element.center = (100,)  # Invalid: only one coordinate

        with pytest.raises(BluePyllError, match="Coords must be a tuple of two values"):
            element.check_pixel_color((255, 0, 0), b"fake_image")

    def test_check_pixel_color_invalid_target_color(self, caplog):
        """Test pixel color check with invalid target color."""
        element = BluePyllElement(
            label="test_pixel",
            ele_type="pixel",
            og_window_size=(1920, 1080),
            position=(100, 200),
            pixel_color=(255, 0, 0)
        )

        # Mock invalid target color (not a 3-tuple)
        element.pixel_color = (255, 0)  # Invalid: only two values

        with pytest.raises(BluePyllError, match="Target color must be a tuple of three values"):
            element.check_pixel_color((255, 0), b"fake_image")

    def test_check_pixel_color_negative_tolerance(self, caplog):
        """Test pixel color check with negative tolerance."""
        element = BluePyllElement(
            label="test_pixel",
            ele_type="pixel",
            og_window_size=(1920, 1080),
            position=(100, 200),
            pixel_color=(255, 0, 0)
        )

        with pytest.raises(BluePyllError, match="Tolerance must be a non-negative integer"):
            element.check_pixel_color((255, 0, 0), b"fake_image", tolerance=-1)


class TestBluePyllElements:
    """Test cases for BluePyllElements class."""

    @patch('bluepyll.ui.files')
    def test_elements_initialization(self, mock_files):
        """Test BluePyllElements initialization."""
        mock_controller = Mock()
        mock_controller.ref_window_size = (1920, 1080)

        # Mock the files function to return mock paths
        mock_files.return_value.joinpath.return_value = Mock()

        elements = BluePyllElements(mock_controller)

        # Verify controller assignment
        assert elements.bluepyll_controller == mock_controller

        # Verify all expected elements are created
        assert hasattr(elements, 'bluestacks_loading_img')
        assert hasattr(elements, 'bluestacks_my_games_button')
        assert hasattr(elements, 'bluestacks_store_search_input')
        assert hasattr(elements, 'bluestacks_store_button')
        assert hasattr(elements, 'bluestacks_playstore_search_input')
        assert hasattr(elements, 'bluestacks_loading_screen_img')
        assert hasattr(elements, 'adb_screenshot_img')

    @patch('bluepyll.ui.files')
    def test_elements_paths(self, mock_files):
        """Test that elements have correct paths."""
        mock_controller = Mock()
        mock_controller.ref_window_size = (1920, 1080)

        # Mock the files function
        mock_files.return_value.joinpath.return_value = Mock()

        elements = BluePyllElements(mock_controller)

        # Verify that files.joinpath was called for each element
        expected_calls = [
            'bluestacks_loading_img.png',
            'bluestacks_my_games_button.png',
            'bluestacks_store_search_input.png',
            'bluestacks_store_button.png',
            'bluestacks_playstore_search_input.png',
            'bluestacks_loading_screen_img.png',
            'adb_screenshot_img.png'
        ]

        for expected_path in expected_calls:
            mock_files.return_value.joinpath.assert_any_call(expected_path)