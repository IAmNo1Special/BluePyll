import cv2
import easyocr

class ImageTextChecker:
    def __init__(self):
        """
        Initialize the ImageTextChecker with the path to the image.
        """
        self.reader = easyocr.Reader(lang_list=["en"], verbose=False)  # Specify the language

    def check_text(self, text_to_find, image_path):
        """
        Check if the specified text is present in the image.

        :param text_to_find: Text to search for in the image.
        :param image_path: Path to the image file.
        :return: True if the text is found, False otherwise.
        """
        # Read the image using OpenCV
        image = cv2.imread(image_path)

        # Use EasyOCR to do text detection
        results = self.reader.readtext(image)

        # Extract the text from the results
        extracted_texts = [result[1].lower() for result in results]

        # Check if the specified text is in the extracted texts
        return any(text_to_find in text for text in extracted_texts)

    def read_text(self, image_path):
        """
        Read text from the image.

        :param image_path: Path to the image file.
        :return: List of detected texts.
        """
        # Read the image using OpenCV
        image = cv2.imread(image_path)

        # Use EasyOCR to do text detection
        results = self.reader.readtext(image)

        # Extract the text from the results
        extracted_texts = [result[1].lower() for result in results]

        return extracted_texts