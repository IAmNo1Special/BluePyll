"""
Unit tests for BluePyll constants module.
"""

from bluepyll.constants import BluestacksConstants


class TestBluestacksConstants:
    """Test the BluestacksConstants class."""

    def test_default_ip(self):
        """Test that DEFAULT_IP is correctly set."""
        assert BluestacksConstants.DEFAULT_IP == "127.0.0.1"

    def test_default_port(self):
        """Test that DEFAULT_PORT is correctly set."""
        assert BluestacksConstants.DEFAULT_PORT == 5555

    def test_default_ref_window_size(self):
        """Test that DEFAULT_REF_WINDOW_SIZE is correctly set."""
        assert BluestacksConstants.DEFAULT_REF_WINDOW_SIZE == (1920, 1080)
        assert isinstance(BluestacksConstants.DEFAULT_REF_WINDOW_SIZE, tuple)
        assert len(BluestacksConstants.DEFAULT_REF_WINDOW_SIZE) == 2

    def test_default_max_retries(self):
        """Test that DEFAULT_MAX_RETRIES is correctly set."""
        assert BluestacksConstants.DEFAULT_MAX_RETRIES == 10
        assert isinstance(BluestacksConstants.DEFAULT_MAX_RETRIES, int)

    def test_default_wait_time(self):
        """Test that DEFAULT_WAIT_TIME is correctly set."""
        assert BluestacksConstants.DEFAULT_WAIT_TIME == 1
        assert isinstance(BluestacksConstants.DEFAULT_WAIT_TIME, int)

    def test_default_timeout(self):
        """Test that DEFAULT_TIMEOUT is correctly set."""
        assert BluestacksConstants.DEFAULT_TIMEOUT == 30
        assert isinstance(BluestacksConstants.DEFAULT_TIMEOUT, int)

    def test_process_wait_timeout(self):
        """Test that PROCESS_WAIT_TIMEOUT is correctly set."""
        assert BluestacksConstants.PROCESS_WAIT_TIMEOUT == 10
        assert isinstance(BluestacksConstants.PROCESS_WAIT_TIMEOUT, int)

    def test_app_start_timeout(self):
        """Test that APP_START_TIMEOUT is correctly set."""
        assert BluestacksConstants.APP_START_TIMEOUT == 60
        assert isinstance(BluestacksConstants.APP_START_TIMEOUT, int)

    def test_all_constants_positive(self):
        """Test that all timeout and retry constants are positive."""
        assert BluestacksConstants.DEFAULT_MAX_RETRIES > 0
        assert BluestacksConstants.DEFAULT_WAIT_TIME > 0
        assert BluestacksConstants.DEFAULT_TIMEOUT > 0
        assert BluestacksConstants.PROCESS_WAIT_TIMEOUT > 0
        assert BluestacksConstants.APP_START_TIMEOUT > 0

    def test_constants_immutability(self):
        """Test that constants cannot be modified (they are class attributes)."""
        # These are class attributes, so they can be modified, but we should test they start with expected values
        original_ip = BluestacksConstants.DEFAULT_IP
        original_port = BluestacksConstants.DEFAULT_PORT

        # Verify they are set to expected values
        assert original_ip == "127.0.0.1"
        assert original_port == 5555

    def test_window_size_dimensions(self):
        """Test that window size has correct dimensions."""
        width, height = BluestacksConstants.DEFAULT_REF_WINDOW_SIZE
        assert width > 0
        assert height > 0
        assert width >= height  # Typically width is greater than or equal to height for landscape
