"""
Unit tests for utility components.
"""

import pytest
from unittest.mock import Mock, patch

from bluepyll.utils import ImageTextChecker
from bluepyll.exceptions import BluePyllError


class TestImageTextChecker:
    """Test cases for ImageTextChecker class."""

    def test_checker_initialization(self):
        """Test ImageTextChecker initialization."""
        checker = ImageTextChecker()

        assert hasattr(checker, 'reader')
        assert checker.reader is not None

    @patch('bluepyll.utils.easyocr.Reader')
    def test_checker_initialization_with_mock(self, mock_reader_class):
        """Test ImageTextChecker initialization with mocked reader."""
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader

        checker = ImageTextChecker()

        mock_reader_class.assert_called_once_with(lang_list=["en"], verbose=False)
        assert checker.reader == mock_reader

    @patch('bluepyll.utils.cv2.imread')
    @patch('bluepyll.utils.easyocr.Reader')
    def test_check_text_valid_image_path(self, mock_reader_class, mock_imread):
        """Test text checking with valid image path."""
        # Setup mocks
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        mock_imread.return_value = Mock()  # Valid image

        mock_reader.readtext.return_value = [
            [[], "Hello World", 0.9],
            [[], "Test Text", 0.8]
        ]

        checker = ImageTextChecker()

        result = checker.check_text("hello", "test_image.png")

        assert result is True
        mock_imread.assert_called_once_with("test_image.png")
        mock_reader.readtext.assert_called_once()

    @patch('bluepyll.utils.cv2.imread')
    @patch('bluepyll.utils.easyocr.Reader')
    def test_check_text_no_match(self, mock_reader_class, mock_imread):
        """Test text checking when target text is not found."""
        # Setup mocks
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        mock_imread.return_value = Mock()  # Valid image

        mock_reader.readtext.return_value = [
            [[], "Some Other Text", 0.9],
            [[], "Different Text", 0.8]
        ]

        checker = ImageTextChecker()

        result = checker.check_text("hello", "test_image.png")

        assert result is False

    @patch('bluepyll.utils.cv2.imread')
    def test_check_text_invalid_image_path(self, mock_imread):
        """Test text checking with invalid image path."""
        mock_imread.return_value = None  # Invalid image

        checker = ImageTextChecker()

        with pytest.raises(BluePyllError, match="Could not read image"):
            checker.check_text("hello", "invalid_image.png")

    @patch('bluepyll.utils.cv2.imread')
    @patch('bluepyll.utils.easyocr.Reader')
    def test_check_text_with_bytes_image(self, mock_reader_class, mock_imread):
        """Test text checking with bytes image."""
        # Setup mocks
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader

        # Mock cv2.imdecode for bytes handling
        with patch('bluepyll.utils.cv2.imdecode') as mock_imdecode:
            mock_imdecode.return_value = Mock()  # Valid decoded image
            mock_reader.readtext.return_value = [
                [[], "Hello World", 0.9]
            ]

            checker = ImageTextChecker()

            result = checker.check_text("hello", b"fake_image_bytes")

            assert result is True
            mock_imdecode.assert_called_once()

    @patch('bluepyll.utils.cv2.imread')
    @patch('bluepyll.utils.easyocr.Reader')
    def test_read_text_valid_image(self, mock_reader_class, mock_imread):
        """Test text reading from valid image."""
        # Setup mocks
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        mock_imread.return_value = Mock()  # Valid image

        mock_reader.readtext.return_value = [
            [[], "Hello World", 0.9],
            [[], "Test Text", 0.8]
        ]

        checker = ImageTextChecker()

        result = checker.read_text("test_image.png")

        assert len(result) == 2
        assert "hello world" in result
        assert "test text" in result

    @patch('bluepyll.utils.cv2.imread')
    def test_read_text_invalid_image(self, mock_imread):
        """Test text reading from invalid image."""
        mock_imread.return_value = None  # Invalid image

        checker = ImageTextChecker()

        with pytest.raises(BluePyllError, match="Could not read image"):
            checker.read_text("invalid_image.png")

    @patch('bluepyll.utils.cv2.imread')
    @patch('bluepyll.utils.easyocr.Reader')
    def test_read_text_empty_results(self, mock_reader_class, mock_imread):
        """Test text reading when no text is detected."""
        # Setup mocks
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        mock_imread.return_value = Mock()  # Valid image

        mock_reader.readtext.return_value = []  # No text detected

        checker = ImageTextChecker()

        result = checker.read_text("test_image.png")

        assert result == []

    @patch('bluepyll.utils.cv2.imread')
    @patch('bluepyll.utils.easyocr.Reader')
    def test_check_text_case_insensitive(self, mock_reader_class, mock_imread):
        """Test text checking is case insensitive."""
        # Setup mocks
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        mock_imread.return_value = Mock()  # Valid image

        mock_reader.readtext.return_value = [
            [[], "HELLO WORLD", 0.9],  # Uppercase in image
        ]

        checker = ImageTextChecker()

        # Search for lowercase
        result = checker.check_text("hello", "test_image.png")

        assert result is True

    @patch('bluepyll.utils.cv2.imread')
    @patch('bluepyll.utils.easyocr.Reader')
    def test_check_text_partial_match(self, mock_reader_class, mock_imread):
        """Test text checking with partial matches."""
        # Setup mocks
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        mock_imread.return_value = Mock()  # Valid image

        mock_reader.readtext.return_value = [
            [[], "Hello World Test", 0.9],
            [[], "Some Text", 0.8]
        ]

        checker = ImageTextChecker()

        # Search for substring
        result = checker.check_text("world", "test_image.png")

        assert result is True

    @patch('bluepyll.utils.cv2.imread')
    @patch('bluepyll.utils.easyocr.Reader')
    def test_read_text_with_kwargs(self, mock_reader_class, mock_imread):
        """Test text reading with additional EasyOCR arguments."""
        # Setup mocks
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        mock_imread.return_value = Mock()  # Valid image

        mock_reader.readtext.return_value = [
            [[], "Hello World", 0.9]
        ]

        checker = ImageTextChecker()

        result = checker.read_text("test_image.png", width_ths=0.5, height_ths=0.5)

        # Verify kwargs were passed to readtext
        mock_reader.readtext.assert_called_once_with(Mock(), width_ths=0.5, height_ths=0.5)
        assert result == ["hello world"]