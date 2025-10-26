from pathlib import Path
from typing import Any

import cv2
import easyocr
import numpy as np

from .exceptions import BluePyllError


class ImageTextChecker:
    """
    A utility class for text detection in images using EasyOCR.

    This class provides methods to:
    - Check for specific text in images
    - Extract all text from images
    """

    def __init__(self) -> None:
        """
        Initialize the ImageTextChecker.

        Uses EasyOCR with English language support for text detection.
        """
        self.reader: easyocr.Reader = easyocr.Reader(lang_list=["en"], verbose=False)

    def check_text(
        self, text_to_find: str, image_path: Path | bytes | str, **kwargs
    ) -> bool:
        """
        Check if the specified text is present in the image.

        Args:
            text_to_find (str): Text to search for in the image
            image_path (Path): Path to the image file
            **kwargs: Additional arguments to pass to EasyOCR

        Returns:
            bool: True if the text is found, False otherwise

        Raises:
            BluePyllError: If the image cannot be read
            TypeError: If invalid arguments are provided
        """
        try:
            # Handle different input types
            if isinstance(image_path, bytes):
                # Convert bytes to numpy array
                nparr = np.frombuffer(image_path, np.uint8)
                image: cv2.typing.MatLike = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                # Read the image using OpenCV
                image: cv2.typing.MatLike = cv2.imread(str(image_path))

            if image is None:
                raise BluePyllError(f"Could not read image from {image_path}")

            # Convert image to grayscale
            image: cv2.typing.MatLike = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Use EasyOCR to do text detection
            results: list[list[Any]] = self.reader.readtext(image, **kwargs)

            # Extract the text from the results
            extracted_texts: list[str] = [str(result[1]).lower() for result in results]

            # Check if the specified text is in the extracted texts
            return any(text_to_find.lower() in text for text in extracted_texts)

        except Exception as e:
            raise BluePyllError(f"Error checking text in image: {e}")

    def read_text(self, image_path: Path | bytes | str, **kwargs) -> list[str]:
        """
        Read text from the image.

        Args:
            image_path (Path | bytes | str): Path to the image file, or image bytes, or image path
            **kwargs: Additional arguments to pass to EasyOCR

        Returns:
            list[str]: list of detected texts

        Raises:
            BluePyllError: If the image cannot be read
            TypeError: If invalid arguments are provided
        """
        try:
            # Handle different input types
            if isinstance(image_path, bytes):
                # Convert bytes to numpy array
                nparr = np.frombuffer(image_path, np.uint8)
                image: cv2.typing.MatLike = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                # Read the image using OpenCV
                image: cv2.typing.MatLike = cv2.imread(str(image_path))

            if image is None:
                raise BluePyllError(f"Could not read image from {image_path}")

            # Convert image to grayscale
            image: cv2.typing.MatLike = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Use EasyOCR to do text detection
            results: list[list[Any]] = self.reader.readtext(image, **kwargs)

            # Extract the text from the results
            extracted_texts: list[str] = [str(result[1]).lower() for result in results]

            return extracted_texts

        except Exception as e:
            raise BluePyllError(f"Error reading text from image: {e}")