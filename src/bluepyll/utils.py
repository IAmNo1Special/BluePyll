import cv2
import easyocr
from typing import Any

class ImageTextChecker:
    def __init__(self):
        """
        Initialize the ImageTextChecker with the path to the image.
        """
        self.reader: easyocr.Reader = easyocr.Reader(lang_list=["en"], verbose=False)  # Specify the language

    def check_text(self, text_to_find: str, image_path: str, **kwargs) -> bool:
        """
        Check if the specified text is present in the image.

        :param text_to_find: Text to search for in the image.
        :param image_path: Path to the image file.
        :return: True if the text is found, False otherwise.
        """
        # Read the image using OpenCV
        image: cv2.typing.Matlike = cv2.imread(image_path)

        # Use EasyOCR to do text detection
        results: list | list[dict[str, Any]] | list[str] | list[list] = self.reader.readtext(image, **kwargs)

        # Extract the text from the results
        extracted_texts: list[str] = [result[1].lower() if isinstance(result[1], str) else result[1] for result in results]

        # Check if the specified text is in the extracted texts
        return any(text_to_find in text for text in extracted_texts)

    def read_text(self, image_path: str, **kwargs) -> list[str]:
        """
        Read text from the image.

        :param image_path: Path to the image file.
        :return: List of detected texts.
        """
        # Read the image using OpenCV
        image: cv2.typing.Matlike = cv2.imread(image_path)

        # Use EasyOCR to do text detection
        results: list | list[dict[str, Any]] | list[str] | list[list] = self.reader.readtext(image, **kwargs)

        # Extract the text from the results
        extracted_texts: list[Any] = [result[1].lower() if isinstance(result[1], str) else result[1] for result in results]

        return extracted_texts