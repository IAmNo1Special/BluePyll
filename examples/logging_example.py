"""
Example script demonstrating proper logging configuration for BluePyll.

This script shows users how to configure logging to control BluePyll's output.
"""

import logging
from bluepyll import BluePyllController, BluePyllApp


def setup_logging(level: str = "INFO") -> None:
    """
    Configure logging for BluePyll usage.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure basic logging
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console output
            # logging.FileHandler('bluepyll.log'),  # Optional file output
        ]
    )

    # Set specific levels for noisy modules if needed
    logging.getLogger('easyocr').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)


def example_basic_usage():
    """Example of basic BluePyll usage with logging."""
    print("BluePyll Logging Example")
    print("=" * 50)

    # Configure logging
    setup_logging("DEBUG")  # Use DEBUG for detailed output during development

    try:
        print("\n1. Initializing BluePyllController...")
        controller = BluePyllController()

        print("\n2. Creating app instance...")
        app = BluePyllApp("Example App", "com.example.app")

        print("\n3. Checking BlueStacks state...")
        print(f"BlueStacks state: {controller.bluestacks_state.current_state}")

        print("\n4. App information...")
        print(f"App: {app}")
        print(f"Running apps: {len(controller.running_apps)}")

        print("\n5. Controller properties...")
        print(f"Reference window size: {controller.ref_window_size}")
        print(f"ADB available: {controller.available}")

        print("\n6. Cleaning up...")
        controller.kill_bluestacks()

    except Exception as e:
        print(f"Error during execution: {e}")
        return False

    return True


def example_error_handling():
    """Example of proper error handling with BluePyll exceptions."""
    print("\n\nError Handling Example")
    print("=" * 50)

    setup_logging("WARNING")  # Use WARNING to reduce noise

    try:
        # Try to create app with invalid parameters
        print("\n1. Testing invalid app creation...")
        try:
            invalid_app = BluePyllApp("", "com.test.app")  # Empty app name
        except Exception as e:
            print(f"Caught expected error: {type(e).__name__}: {e}")
            # The error was caught and handled properly

    except Exception as e:
        print(f"Caught expected error: {type(e).__name__}: {e}")

    try:
        print("\n2. Testing controller property validation...")
        controller = BluePyllController()
        controller.ref_window_size = (-1, 1080)  # Invalid negative width

    except Exception as e:
        print(f"Caught expected error: {type(e).__name__}: {e}")


def example_production_logging():
    """Example of production-ready logging configuration."""
    print("\n\nProduction Logging Example")
    print("=" * 50)

    # Production logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bluepyll_production.log')
        ]
    )

    print("Production logging configured. Check 'bluepyll_production.log' for detailed logs.")


if __name__ == "__main__":
    print("BluePyll Logging Examples")
    print("This script demonstrates proper logging configuration.")

    # Run examples
    example_basic_usage()
    example_error_handling()
    example_production_logging()

    print("\nLogging examples completed!")
    print("\nTips:")
    print("- Use DEBUG level during development for detailed information")
    print("- Use INFO level for normal operation")
    print("- Use WARNING level to reduce noise in production")
    print("- Use ERROR level for critical issues only")
    print("- Configure file handlers for persistent logging")
    print("- Adjust third-party library logging levels as needed")