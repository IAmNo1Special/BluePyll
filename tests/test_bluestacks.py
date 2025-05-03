"""
Test script for BluestacksController and BluePyllApp functionality.
"""

import logging
import time
import sys
from pathlib import Path

from bluepyll.controller import BluestacksController
from bluepyll.app import BluePyllApp


def setup_logging():
    """
    Configure logging for the test script.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("test_bluestacks.log")
        ]
    )


def main():
    """
    Main test function that demonstrates opening Bluestacks and launching Revomon.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize the controller and wait for Bluestacks to auto-open
        logger.info("Initializing & opening BluestacksController...")
        controller = BluestacksController()
        time.sleep(5)  # Wait for Bluestacks to fully open
        logger.info("Bluestacks opened successfully")
        
        # Create the Revomon app instance
        logger.info("Creating Revomon app instance...")
        revomon_app = BluePyllApp(
            app_name="revomon",
            package_name="com.revomon.vr"
        )
        
        logger.info("Starting test sequence...")
        
        # Verify Bluestacks is open
        if not controller.is_open:
            raise RuntimeError("Bluestacks failed to open")
            
        
        
        # Open Revomon
        logger.info("Opening Revomon...")
        controller.open_app(revomon_app)
            
        # Wait for user to verify
        input("\nPress Enter to close Bluestacks...")
        
        # Clean up
        logger.info("Closing Bluestacks...")
        controller.kill_bluestacks()
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)
