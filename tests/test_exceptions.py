"""
Unit tests for BluePyll exceptions module.
"""

from bluepyll.exceptions import (
    AppError,
    BluePyllError,
    ConnectionError,
    EmulatorError,
    StateError,
    TimeoutError,
)


class TestBluePyllError:
    """Test the base BluePyllError exception."""

    def test_bluepyll_error_inheritance(self):
        """Test that BluePyllError inherits from Exception."""
        assert issubclass(BluePyllError, Exception)

    def test_bluepyll_error_instantiation(self):
        """Test that BluePyllError can be instantiated."""
        error = BluePyllError()
        assert isinstance(error, BluePyllError)
        assert isinstance(error, Exception)

    def test_bluepyll_error_with_message(self):
        """Test that BluePyllError can be instantiated with a message."""
        message = "Test error message"
        error = BluePyllError(message)
        assert str(error) == message


class TestEmulatorError:
    """Test the EmulatorError exception."""

    def test_emulator_error_inheritance(self):
        """Test that EmulatorError inherits from BluePyllError."""
        assert issubclass(EmulatorError, BluePyllError)
        assert issubclass(EmulatorError, Exception)

    def test_emulator_error_instantiation(self):
        """Test that EmulatorError can be instantiated."""
        error = EmulatorError()
        assert isinstance(error, EmulatorError)
        assert isinstance(error, BluePyllError)
        assert isinstance(error, Exception)

    def test_emulator_error_with_message(self):
        """Test that EmulatorError can be instantiated with a message."""
        message = "Emulator connection failed"
        error = EmulatorError(message)
        assert str(error) == message


class TestAppError:
    """Test the AppError exception."""

    def test_app_error_inheritance(self):
        """Test that AppError inherits from BluePyllError."""
        assert issubclass(AppError, BluePyllError)
        assert issubclass(AppError, Exception)

    def test_app_error_instantiation(self):
        """Test that AppError can be instantiated."""
        error = AppError()
        assert isinstance(error, AppError)
        assert isinstance(error, BluePyllError)
        assert isinstance(error, Exception)

    def test_app_error_with_message(self):
        """Test that AppError can be instantiated with a message."""
        message = "App installation failed"
        error = AppError(message)
        assert str(error) == message


class TestStateError:
    """Test the StateError exception."""

    def test_state_error_inheritance(self):
        """Test that StateError inherits from BluePyllError."""
        assert issubclass(StateError, BluePyllError)
        assert issubclass(StateError, Exception)

    def test_state_error_instantiation(self):
        """Test that StateError can be instantiated."""
        error = StateError()
        assert isinstance(error, StateError)
        assert isinstance(error, BluePyllError)
        assert isinstance(error, Exception)

    def test_state_error_with_message(self):
        """Test that StateError can be instantiated with a message."""
        message = "Invalid state transition"
        error = StateError(message)
        assert str(error) == message


class TestConnectionError:
    """Test the ConnectionError exception."""

    def test_connection_error_inheritance(self):
        """Test that ConnectionError inherits from BluePyllError."""
        assert issubclass(ConnectionError, BluePyllError)
        assert issubclass(ConnectionError, Exception)

    def test_connection_error_instantiation(self):
        """Test that ConnectionError can be instantiated."""
        error = ConnectionError()
        assert isinstance(error, ConnectionError)
        assert isinstance(error, BluePyllError)
        assert isinstance(error, Exception)

    def test_connection_error_with_message(self):
        """Test that ConnectionError can be instantiated with a message."""
        message = "ADB connection timeout"
        error = ConnectionError(message)
        assert str(error) == message


class TestTimeoutError:
    """Test the TimeoutError exception."""

    def test_timeout_error_inheritance(self):
        """Test that TimeoutError inherits from BluePyllError."""
        assert issubclass(TimeoutError, BluePyllError)
        assert issubclass(TimeoutError, Exception)

    def test_timeout_error_instantiation(self):
        """Test that TimeoutError can be instantiated."""
        error = TimeoutError()
        assert isinstance(error, TimeoutError)
        assert isinstance(error, BluePyllError)
        assert isinstance(error, Exception)

    def test_timeout_error_with_message(self):
        """Test that TimeoutError can be instantiated with a message."""
        message = "Operation timed out"
        error = TimeoutError(message)
        assert str(error) == message


class TestExceptionHierarchy:
    """Test the exception hierarchy."""

    def test_all_exceptions_inherit_from_bluepyll_error(self):
        """Test that all specific exceptions inherit from BluePyllError."""
        assert issubclass(EmulatorError, BluePyllError)
        assert issubclass(AppError, BluePyllError)
        assert issubclass(StateError, BluePyllError)
        assert issubclass(ConnectionError, BluePyllError)
        assert issubclass(TimeoutError, BluePyllError)

    def test_exception_independence(self):
        """Test that exceptions don't inherit from each other (except through BluePyllError)."""
        # Each exception should be independent except through the base class
        assert not issubclass(EmulatorError, AppError)
        assert not issubclass(AppError, StateError)
        assert not issubclass(StateError, ConnectionError)
        assert not issubclass(ConnectionError, TimeoutError)
