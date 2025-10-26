"""
Unit tests for BluePyllApp class.
"""

import pytest
from unittest.mock import Mock, patch

from bluepyll.app import BluePyllApp
from bluepyll.exceptions import AppError
from bluepyll.state_machine import AppLifecycleState


class TestBluePyllApp:
    """Test cases for BluePyllApp class."""

    def test_app_creation_valid(self):
        """Test successful app creation with valid parameters."""
        app = BluePyllApp("TestApp", "com.test.app")

        assert app.app_name == "TestApp"
        assert app.package_name == "com.test.app"
        assert app.app_state.current_state == AppLifecycleState.CLOSED

    def test_app_creation_empty_app_name(self):
        """Test app creation fails with empty app name."""
        with pytest.raises(AppError, match="app_name must be a non-empty string"):
            BluePyllApp("", "com.test.app")

    def test_app_creation_empty_package_name(self):
        """Test app creation fails with empty package name."""
        with pytest.raises(AppError, match="package_name must be a non-empty string"):
            BluePyllApp("TestApp", "")

    def test_app_creation_whitespace_app_name(self):
        """Test app creation fails with whitespace-only app name."""
        with pytest.raises(AppError, match="app_name must be a non-empty string"):
            BluePyllApp("   ", "com.test.app")

    def test_app_creation_whitespace_package_name(self):
        """Test app creation fails with whitespace-only package name."""
        with pytest.raises(AppError, match="package_name must be a non-empty string"):
            BluePyllApp("TestApp", "   ")

    def test_app_equality_same(self):
        """Test app equality with identical apps."""
        app1 = BluePyllApp("TestApp", "com.test.app")
        app2 = BluePyllApp("TestApp", "com.test.app")

        assert app1 == app2

    def test_app_equality_different_app_name(self):
        """Test app equality with different app names."""
        app1 = BluePyllApp("TestApp1", "com.test.app")
        app2 = BluePyllApp("TestApp2", "com.test.app")

        assert app1 != app2

    def test_app_equality_different_package_name(self):
        """Test app equality with different package names."""
        app1 = BluePyllApp("TestApp", "com.test.app1")
        app2 = BluePyllApp("TestApp", "com.test.app2")

        assert app1 != app2

    def test_app_equality_different_states(self):
        """Test app equality with different states."""
        app1 = BluePyllApp("TestApp", "com.test.app")
        app2 = BluePyllApp("TestApp", "com.test.app")

        # Transition one app to different state
        app1.app_state.transition_to(AppLifecycleState.LOADING)

        assert app1 != app2

    def test_app_hash_consistency(self):
        """Test that equal apps have equal hashes."""
        app1 = BluePyllApp("TestApp", "com.test.app")
        app2 = BluePyllApp("TestApp", "com.test.app")

        assert hash(app1) == hash(app2)

    def test_app_hash_different_apps(self):
        """Test that different apps have different hashes."""
        app1 = BluePyllApp("TestApp1", "com.test.app")
        app2 = BluePyllApp("TestApp2", "com.test.app")

        assert hash(app1) != hash(app2)

    def test_app_string_representation(self):
        """Test app string representation."""
        app = BluePyllApp("TestApp", "com.test.app")
        expected = "BluePyllApp(app_name=TestApp, package_name=com.test.app, state=AppLifecycleState.CLOSED)"

        assert str(app) == expected

    def test_app_string_representation_different_state(self):
        """Test app string representation with different state."""
        app = BluePyllApp("TestApp", "com.test.app")
        app.app_state.transition_to(AppLifecycleState.READY)

        expected = "BluePyllApp(app_name=TestApp, package_name=com.test.app, state=AppLifecycleState.READY)"
        assert str(app) == expected

    def test_app_with_special_characters(self):
        """Test app creation with special characters in names."""
        app = BluePyllApp("Test-App 2.0", "com.test.app.special")
        assert app.app_name == "Test-App 2.0"
        assert app.package_name == "com.test.app.special"

    @patch('bluepyll.app.StateMachine')
    def test_app_state_machine_initialization(self, mock_state_machine):
        """Test that app properly initializes state machine."""
        mock_state_machine_instance = Mock()
        mock_state_machine.return_value = mock_state_machine_instance

        app = BluePyllApp("TestApp", "com.test.app")

        # Verify StateMachine was created with correct parameters
        mock_state_machine.assert_called_once()
        call_args = mock_state_machine.call_args
        assert call_args[1]['current_state'] == AppLifecycleState.CLOSED
        assert 'transitions' in call_args[1]

        # Verify the app stores the state machine
        assert app.app_state == mock_state_machine_instance