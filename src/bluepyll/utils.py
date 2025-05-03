import cv2
import easyocr
from pathlib import Path
from typing import List, Any

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

    def check_text(self, text_to_find: str, image_path: Path, **kwargs) -> bool:
        """
        Check if the specified text is present in the image.
        
        Args:
            text_to_find (str): Text to search for in the image
            image_path (Path): Path to the image file
            **kwargs: Additional arguments to pass to EasyOCR
            
        Returns:
            bool: True if the text is found, False otherwise
            
        Raises:
            ValueError: If the image cannot be read
            TypeError: If invalid arguments are provided
        """
        try:
            # Read the image using OpenCV
            image: cv2.typing.MatLike = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not read image from {image_path}")

            # Convert image to grayscale
            image: cv2.typing.MatLike = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Use EasyOCR to do text detection
            results: List[List[Any]] = self.reader.readtext(image, **kwargs)

            # Extract the text from the results
            extracted_texts: List[str] = [str(result[1]).lower() for result in results]

            # Check if the specified text is in the extracted texts
            return any(text_to_find.lower() in text for text in extracted_texts)

        except Exception as e:
            raise ValueError(f"Error checking text in image: {e}")

    def read_text(self, image_path: Path, **kwargs) -> List[str]:
        """
        Read text from the image.
        
        Args:
            image_path (Path): Path to the image file
            **kwargs: Additional arguments to pass to EasyOCR
            
        Returns:
            List[str]: List of detected texts
            
        Raises:
            ValueError: If the image cannot be read
            TypeError: If invalid arguments are provided
        """
        try:
            # Read the image using OpenCV
            image: cv2.typing.MatLike = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not read image from {image_path}")

            # Convert image to grayscale
            image: cv2.typing.MatLike = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Use EasyOCR to do text detection
            results: List[List[Any]] = self.reader.readtext(image, **kwargs)

            # Extract the text from the results
            extracted_texts: List[str] = [str(result[1]).lower() for result in results]

            return extracted_texts

        except Exception as e:
            raise ValueError(f"Error reading text from image: {e}")