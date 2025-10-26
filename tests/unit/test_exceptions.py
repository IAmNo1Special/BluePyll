"""
Unit tests for custom exceptions.
"""

import pytest

from bluepyll.exceptions import (
    BluePyllError,
    EmulatorError,
    AppError,
    StateError,
    ConnectionError,
    TimeoutError
)


class TestCustomExceptions:
    """Test cases for custom exception classes."""

    def test_bluepyll_error_base_class(self):
        """Test BluePyllError is proper base exception."""
        # Should be able to catch BluePyllError when its subclasses are raised
        with pytest.raises(BluePyllError):
            raise EmulatorError("Test error")

        with pytest.raises(BluePyllError):
            raise AppError("Test error")

        with pytest.raises(BluePyllError):
            raise StateError("Test error")

        with pytest.raises(BluePyllError):
            raise ConnectionError("Test error")

        with pytest.raises(BluePyllError):
            raise TimeoutError("Test error")

    def test_emulator_error_inheritance(self):
        """Test EmulatorError properly inherits from BluePyllError."""
        assert issubclass(EmulatorError, BluePyllError)
        assert issubclass(EmulatorError, Exception)

        error = EmulatorError("Emulator startup failed")
        assert isinstance(error, BluePyllError)
        assert isinstance(error, Exception)
        assert str(error) == "Emulator startup failed"

    def test_app_error_inheritance(self):
        """Test AppError properly inherits from BluePyllError."""
        assert issubclass(AppError, BluePyllError)
        assert issubclass(AppError, Exception)

        error = AppError("App installation failed")
        assert isinstance(error, BluePyllError)
        assert isinstance(error, Exception)
        assert str(error) == "App installation failed"

    def test_state_error_inheritance(self):
        """Test StateError properly inherits from BluePyllError."""
        assert issubclass(StateError, BluePyllError)
        assert issubclass(StateError, Exception)

        error = StateError("Invalid state transition")
        assert isinstance(error, BluePyllError)
        assert isinstance(error, Exception)
        assert str(error) == "Invalid state transition"

    def test_connection_error_inheritance(self):
        """Test ConnectionError properly inherits from BluePyllError."""
        assert issubclass(ConnectionError, BluePyllError)
        assert issubclass(ConnectionError, Exception)

        error = ConnectionError("ADB connection failed")
        assert isinstance(error, BluePyllError)
        assert isinstance(error, Exception)
        assert str(error) == "ADB connection failed"

    def test_timeout_error_inheritance(self):
        """Test TimeoutError properly inherits from BluePyllError."""
        assert issubclass(TimeoutError, BluePyllError)
        assert issubclass(TimeoutError, Exception)

        error = TimeoutError("Operation timed out")
        assert isinstance(error, BluePyllError)
        assert isinstance(error, Exception)
        assert str(error) == "Operation timed out"

    def test_exception_with_cause(self):
        """Test exceptions can carry cause information."""
        original_error = ValueError("Original error")
        emulator_error = EmulatorError(f"Emulator failed: {original_error}")

        assert "Emulator failed" in str(emulator_error)
        assert "Original error" in str(emulator_error)

    def test_exception_chaining(self):
        """Test exception chaining works properly."""
        try:
            raise ValueError("Original error")
        except ValueError as e:
            emulator_error = EmulatorError("Emulator failed")
            emulator_error.__cause__ = e

            assert emulator_error.__cause__ is e
            assert str(emulator_error.__cause__) == "Original error"