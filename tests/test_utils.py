"""
Unit tests for BluePyll utils module.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

from bluepyll.utils import ImageTextChecker


class TestImageTextChecker:
    """Test the ImageTextChecker class."""

    @pytest.fixture
    def checker(self):
        """Create an ImageTextChecker instance for testing."""
        return ImageTextChecker()

    @pytest.fixture
    def mock_cv2_image(self):
        """Create a mock OpenCV image for testing."""
        # Create a simple 100x100 grayscale image
        return np.random.randint(0, 255, (100, 100), dtype=np.uint8)

    @pytest.fixture
    def mock_image_bytes(self):
        """Create mock image bytes for testing."""
        # Create a simple image and convert to bytes
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        _, encoded_img = cv2.imencode('.png', image)
        return encoded_img.tobytes()

    def test_checker_initialization(self, checker):
        """Test ImageTextChecker initialization."""
        assert checker is not None
        assert hasattr(checker, 'reader')
        assert checker.reader is not None

    @patch('bluepyll.utils.easyocr.Reader')
    def test_checker_initialization_with_mock(self, mock_reader_class):
        """Test ImageTextChecker initialization with mocked EasyOCR."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        checker = ImageTextChecker()

        # Verify EasyOCR was initialized with correct parameters
        mock_reader_class.assert_called_once_with(lang_list=["en"], verbose=False)
        assert checker.reader == mock_reader

    @patch('bluepyll.utils.cv2.imread')
    @patch('bluepyll.utils.cv2.cvtColor')
    def test_check_text_valid_image_path(self, checker, mock_cvtColor, mock_imread):
        """Test check_text with valid image path."""
        # Setup mocks
        mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_cvtColor.return_value = mock_image[:, :, 0]  # Grayscale

        # Mock EasyOCR results
        with patch.object(checker.reader, 'readtext', return_value=[['hello', 'hello', [0, 0, 50, 50]]]):
            result = checker.check_text("hello", "test_image.png")

            assert result is True
            mock_imread.assert_called_once_with("test_image.png")
            mock_cvtColor.assert_called_once()

    @patch('bluepyll.utils.cv2.imread')
    def test_check_text_image_not_found(self, checker, mock_imread):
        """Test check_text with non-existent image path."""
        mock_imread.return_value = None

        with pytest.raises(ValueError, match="Could not read image"):
            checker.check_text("hello", "nonexistent_image.png")

    def test_check_text_with_bytes(self, checker, mock_image_bytes):
        """Test check_text with image bytes."""
        with patch('bluepyll.utils.cv2.imdecode') as mock_imdecode, \
             patch('bluepyll.utils.cv2.cvtColor') as mock_cvtColor, \
             patch.object(checker.reader, 'readtext', return_value=[['test', 'test', [0, 0, 50, 50]]]):

            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imdecode.return_value = mock_image
            mock_cvtColor.return_value = mock_image[:, :, 0]

            result = checker.check_text("test", mock_image_bytes)

            assert result is True
            mock_imdecode.assert_called_once()

    def test_check_text_case_insensitive(self, checker):
        """Test check_text is case insensitive."""
        with patch('bluepyll.utils.cv2.imread') as mock_imread, \
             patch('bluepyll.utils.cv2.cvtColor') as mock_cvtColor, \
             patch.object(checker.reader, 'readtext', return_value=[['HELLO', 'HELLO', [0, 0, 50, 50]]]):

            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imread.return_value = mock_image
            mock_cvtColor.return_value = mock_image[:, :, 0]

            # Search for lowercase, should find uppercase
            result = checker.check_text("hello", "test_image.png")
            assert result is True

    def test_check_text_not_found(self, checker):
        """Test check_text when text is not found."""
        with patch('bluepyll.utils.cv2.imread') as mock_imread, \
             patch('bluepyll.utils.cv2.cvtColor') as mock_cvtColor, \
             patch.object(checker.reader, 'readtext', return_value=[['world', 'world', [0, 0, 50, 50]]]):

            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imread.return_value = mock_image
            mock_cvtColor.return_value = mock_image[:, :, 0]

            result = checker.check_text("hello", "test_image.png")
            assert result is False

    def test_check_text_partial_match(self, checker):
        """Test check_text with partial text match."""
        with patch('bluepyll.utils.cv2.imread') as mock_imread, \
             patch('bluepyll.utils.cv2.cvtColor') as mock_cvtColor, \
             patch.object(checker.reader, 'readtext', return_value=[['hello world', 'hello world', [0, 0, 50, 50]]]):

            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imread.return_value = mock_image
            mock_cvtColor.return_value = mock_image[:, :, 0]

            # Should find partial match
            result = checker.check_text("hello", "test_image.png")
            assert result is True

            result = checker.check_text("world", "test_image.png")
            assert result is True

    def test_check_text_with_kwargs(self, checker):
        """Test check_text passes kwargs to EasyOCR."""
        with patch('bluepyll.utils.cv2.imread') as mock_imread, \
             patch('bluepyll.utils.cv2.cvtColor') as mock_cvtColor, \
             patch.object(checker.reader, 'readtext', return_value=[['test', 'test', [0, 0, 50, 50]]]) as mock_readtext:

            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imread.return_value = mock_image
            mock_cvtColor.return_value = mock_image[:, :, 0]

            kwargs = {'width_ths': 0.5, 'height_ths': 0.5}
            checker.check_text("test", "test_image.png", **kwargs)

            mock_readtext.assert_called_once_with(mock_image[:, :, 0], **kwargs)

    @patch('bluepyll.utils.cv2.imread')
    @patch('bluepyll.utils.cv2.cvtColor')
    def test_read_text_valid_image_path(self, checker, mock_cvtColor, mock_imread):
        """Test read_text with valid image path."""
        # Setup mocks
        mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_cvtColor.return_value = mock_image[:, :, 0]  # Grayscale

        # Mock EasyOCR results
        with patch.object(checker.reader, 'readtext', return_value=[
            ['hello', 'hello', [0, 0, 50, 50]],
            ['world', 'world', [50, 50, 100, 100]]
        ]):
            result = checker.read_text("test_image.png")

            assert result == ['hello', 'world']
            mock_imread.assert_called_once_with("test_image.png")
            mock_cvtColor.assert_called_once()

    def test_read_text_with_bytes(self, checker, mock_image_bytes):
        """Test read_text with image bytes."""
        with patch('bluepyll.utils.cv2.imdecode') as mock_imdecode, \
             patch('bluepyll.utils.cv2.cvtColor') as mock_cvtColor, \
             patch.object(checker.reader, 'readtext', return_value=[
                 ['test', 'test', [0, 0, 50, 50]],
                 ['data', 'data', [50, 50, 100, 100]]
             ]):

            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imdecode.return_value = mock_image
            mock_cvtColor.return_value = mock_image[:, :, 0]

            result = checker.read_text(mock_image_bytes)

            assert result == ['test', 'data']
            mock_imdecode.assert_called_once()

    def test_read_text_case_conversion(self, checker):
        """Test read_text converts text to lowercase."""
        with patch('bluepyll.utils.cv2.imread') as mock_imread, \
             patch('bluepyll.utils.cv2.cvtColor') as mock_cvtColor, \
             patch.object(checker.reader, 'readtext', return_value=[
                 ['HELLO', 'HELLO', [0, 0, 50, 50]],
                 ['WORLD', 'WORLD', [50, 50, 100, 100]]
             ]):

            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imread.return_value = mock_image
            mock_cvtColor.return_value = mock_image[:, :, 0]

            result = checker.read_text("test_image.png")

            # Should be lowercase
            assert result == ['hello', 'world']

    def test_read_text_empty_results(self, checker):
        """Test read_text with no text detected."""
        with patch('bluepyll.utils.cv2.imread') as mock_imread, \
             patch('bluepyll.utils.cv2.cvtColor') as mock_cvtColor, \
             patch.object(checker.reader, 'readtext', return_value=[]):

            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imread.return_value = mock_image
            mock_cvtColor.return_value = mock_image[:, :, 0]

            result = checker.read_text("test_image.png")

            assert result == []

    def test_read_text_with_kwargs(self, checker):
        """Test read_text passes kwargs to EasyOCR."""
        with patch('bluepyll.utils.cv2.imread') as mock_imread, \
             patch('bluepyll.utils.cv2.cvtColor') as mock_cvtColor, \
             patch.object(checker.reader, 'readtext', return_value=[['test', 'test', [0, 0, 50, 50]]]) as mock_readtext:

            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imread.return_value = mock_image
            mock_cvtColor.return_value = mock_image[:, :, 0]

            kwargs = {'width_ths': 0.5, 'height_ths': 0.5}
            checker.read_text("test_image.png", **kwargs)

            mock_readtext.assert_called_once_with(mock_image[:, :, 0], **kwargs)

    def test_check_text_exception_handling(self, checker):
        """Test check_text handles exceptions properly."""
        with patch('bluepyll.utils.cv2.imread', side_effect=Exception("OpenCV error")):
            with pytest.raises(ValueError, match="Error checking text in image"):
                checker.check_text("hello", "test_image.png")

    def test_read_text_exception_handling(self, checker):
        """Test read_text handles exceptions properly."""
        with patch('bluepyll.utils.cv2.imread', side_effect=Exception("OpenCV error")):
            with pytest.raises(ValueError, match="Error reading text from image"):
                checker.read_text("test_image.png")

    def test_check_text_pathlib_path(self, checker):
        """Test check_text works with Path objects."""
        test_path = Path("test_image.png")

        with patch('bluepyll.utils.cv2.imread') as mock_imread, \
             patch('bluepyll.utils.cv2.cvtColor') as mock_cvtColor, \
             patch.object(checker.reader, 'readtext', return_value=[['test', 'test', [0, 0, 50, 50]]]):

            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imread.return_value = mock_image
            mock_cvtColor.return_value = mock_image[:, :, 0]

            result = checker.check_text("test", test_path)

            assert result is True
            mock_imread.assert_called_once_with(str(test_path))

    def test_read_text_pathlib_path(self, checker):
        """Test read_text works with Path objects."""
        test_path = Path("test_image.png")

        with patch('bluepyll.utils.cv2.imread') as mock_imread, \
             patch('bluepyll.utils.cv2.cvtColor') as mock_cvtColor, \
             patch.object(checker.reader, 'readtext', return_value=[['test', 'test', [0, 0, 50, 50]]]):

            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imread.return_value = mock_image
            mock_cvtColor.return_value = mock_image[:, :, 0]

            result = checker.read_text(test_path)

            assert result == ['test']
            mock_imread.assert_called_once_with(str(test_path))
