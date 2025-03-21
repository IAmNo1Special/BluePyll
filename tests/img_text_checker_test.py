import time
# Start timing importing the ImageTextChecker module
import_start_time = time.time()

from bluepyll.utils import ImageTextChecker

import_end_time = time.time()
# End timing importing the ImageTextChecker module


if __name__ == "__main__":
    # Start timing the initialization
    init_start_time = time.time()
    
    # Initialize ImageTextChecker as early as possible as it takes time to initialize
    checker = ImageTextChecker()
    
    # End timing the initialization
    init_end_time = time.time()
    
    # Start timing the check
    check_start_time = time.time()

    # Test image path
    image_path = "src/bluepyll/assets/my_games_icon.png"
    # Text to search for
    text_to_check = "my games"
    # Check if text is present in the image
    result = checker.check_text(text_to_check, image_path)

    # End timing the check
    check_end_time = time.time()

    # Calculate the duration
    import_time = import_end_time - import_start_time
    initialization_time = init_end_time - init_start_time
    check_time = check_end_time - check_start_time

    # Print import time
    print(f"ImageTextChecker module imported in {import_time:.4f} seconds.")
    # Print initialization time
    print(f"ImageTextChecker obj initialized in {initialization_time:.4f} seconds.")
    # Print check time
    print(f"Text check completed in {check_time:.4f} seconds.")
    # Print total time
    total_time = import_time + initialization_time + check_time
    print(f"Total time: {total_time:.4f} seconds.")

    # Print result
    print(f"Text '{text_to_check}' found in image: {result}")