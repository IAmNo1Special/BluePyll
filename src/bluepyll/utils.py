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


if __name__ == "__main__":
    image_path = "revomon/game_ui/overworld/in-battle/batttle_screen1.png"
    text_to_check = "run"  # Text to search for
    checker = ImageTextChecker()
    result = checker.check_text(text_to_check, image_path)
    print(f"Text '{text_to_check}' found in image: {result}")