import time

# Start timing importing the ImageTextChecker module
import_start_time = time.time()

from bluepyll.utils import ImageTextChecker

import_end_time = time.time()
# End timing importing the ImageTextChecker module


def check_text_test():
    # Start timing the initialization
    init_start_time = time.time()
    try:
        # Initialize ImageTextChecker as early as possible as it takes time to initialize
        checker = ImageTextChecker()
    except Exception as e:
        print(f"Error initializing ImageTextChecker: {str(e)}")
        return "FAIL"

    # End timing the initialization
    init_end_time = time.time()

    # Start timing the check
    check_start_time = time.time()
    try:
        # Test image path
        image_path = "src/bluepyll/assets/bluestacks_my_games_button.png"
        # Text to search for
        text_to_check = "my games"
        # Check if text is present in the image
        result = checker.check_text(text_to_check, image_path)
    except Exception as e:
        print(f"Error checking text in image: {str(e)}")
        return "FAIL"

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
    return result


def read_text_test():
    # Start timing the initialization
    init_start_time = time.time()
    try:
        # Initialize ImageTextChecker as early as possible as it takes time to initialize
        checker = ImageTextChecker()
    except Exception as e:
        print(f"Error initializing ImageTextChecker: {str(e)}")
        return "FAIL"

    # End timing the initialization
    init_end_time = time.time()

    # Start timing the check
    check_start_time = time.time()
    try:
        # Test image path
        image_path = "src/bluepyll/assets/bluestacks_my_games_button.png"
        # Read text from the image
        result = checker.read_text(image_path)
    except Exception as e:
        print(f"Error reading text from image: {str(e)}")
        return "FAIL"

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
    print(f"Text read from image: {result}")
    return result


if __name__ == "__main__":
    # Run the tests

    # Run check_text_test
    print("Running check_text_test...")
    result = check_text_test()
    print(f"check_text_test result: {result}")

    # Run read_text_test
    print("Running read_text_test...")
    result = read_text_test()
    print(f"read_text_test result: {result}")
