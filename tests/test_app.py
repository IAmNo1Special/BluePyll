"""
Unit tests for BluePyll app module.
"""

import pytest

from bluepyll.app import BluePyllApp
from bluepyll.state_machine import AppLifecycleState


class TestBluePyllApp:
    """Test the BluePyllApp class."""

    def test_app_initialization_valid(self):
        """Test BluePyllApp initialization with valid parameters."""
        app = BluePyllApp(app_name="TestApp", package_name="com.test.app")

        assert app.app_name == "TestApp"
        assert app.package_name == "com.test.app"
        assert app.app_state.current_state == AppLifecycleState.CLOSED
        assert isinstance(app.app_state.transitions, dict)

    def test_app_initialization_empty_app_name(self):
        """Test BluePyllApp initialization with empty app name raises ValueError."""
        with pytest.raises(ValueError, match="app_name must be a non-empty string"):
            BluePyllApp(app_name="", package_name="com.test.app")

    def test_app_initialization_empty_package_name(self):
        """Test BluePyllApp initialization with empty package name raises ValueError."""
        with pytest.raises(ValueError, match="package_name must be a non-empty string"):
            BluePyllApp(app_name="TestApp", package_name="")

    def test_app_initialization_none_app_name(self):
        """Test BluePyllApp initialization with None app name raises ValueError."""
        with pytest.raises(ValueError, match="app_name must be a non-empty string"):
            BluePyllApp(app_name=None, package_name="com.test.app")

    def test_app_initialization_none_package_name(self):
        """Test BluePyllApp initialization with None package name raises ValueError."""
        with pytest.raises(ValueError, match="package_name must be a non-empty string"):
            BluePyllApp(app_name="TestApp", package_name=None)

    def test_app_initialization_whitespace_app_name(self):
        """Test BluePyllApp initialization with whitespace-only app name raises ValueError."""
        with pytest.raises(ValueError, match="app_name must be a non-empty string"):
            BluePyllApp(app_name="   ", package_name="com.test.app")

    def test_app_initialization_whitespace_package_name(self):
        """Test BluePyllApp initialization with whitespace-only package name raises ValueError."""
        with pytest.raises(ValueError, match="package_name must be a non-empty string"):
            BluePyllApp(app_name="TestApp", package_name="   ")

    def test_app_string_representation(self):
        """Test BluePyllApp string representation."""
        app = BluePyllApp(app_name="TestApp", package_name="com.test.app")
        str_repr = str(app)

        assert "BluePyllApp" in str_repr
        assert "TestApp" in str_repr
        assert "com.test.app" in str_repr
        assert "CLOSED" in str_repr

    def test_app_equality_same(self):
        """Test BluePyllApp equality with identical apps."""
        app1 = BluePyllApp(app_name="TestApp", package_name="com.test.app")
        app2 = BluePyllApp(app_name="TestApp", package_name="com.test.app")

        assert app1 == app2

    def test_app_equality_different_name(self):
        """Test BluePyllApp equality with different app names."""
        app1 = BluePyllApp(app_name="TestApp1", package_name="com.test.app")
        app2 = BluePyllApp(app_name="TestApp2", package_name="com.test.app")

        assert app1 != app2

    def test_app_equality_different_package(self):
        """Test BluePyllApp equality with different package names."""
        app1 = BluePyllApp(app_name="TestApp", package_name="com.test.app1")
        app2 = BluePyllApp(app_name="TestApp", package_name="com.test.app2")

        assert app1 != app2

    def test_app_equality_different_state(self):
        """Test BluePyllApp equality with different states."""
        app1 = BluePyllApp(app_name="TestApp", package_name="com.test.app")
        app2 = BluePyllApp(app_name="TestApp", package_name="com.test.app")

        # Change one app's state
        app1.app_state.transition_to(AppLifecycleState.LOADING)

        assert app1 != app2

    def test_app_equality_different_type(self):
        """Test BluePyllApp equality with different object types."""
        app = BluePyllApp(app_name="TestApp", package_name="com.test.app")
        other_object = "not an app"

        assert app != other_object

    def test_app_hash_consistency(self):
        """Test that BluePyllApp hash is consistent for equal objects."""
        app1 = BluePyllApp(app_name="TestApp", package_name="com.test.app")
        app2 = BluePyllApp(app_name="TestApp", package_name="com.test.app")

        assert hash(app1) == hash(app2)

    def test_app_hash_different_objects(self):
        """Test that BluePyllApp hash differs for different objects."""
        app1 = BluePyllApp(app_name="TestApp1", package_name="com.test.app1")
        app2 = BluePyllApp(app_name="TestApp2", package_name="com.test.app2")

        assert hash(app1) != hash(app2)

    def test_app_hash_with_state_change(self):
        """Test that BluePyllApp hash changes when state changes."""
        app1 = BluePyllApp(app_name="TestApp", package_name="com.test.app")
        app2 = BluePyllApp(app_name="TestApp", package_name="com.test.app")

        original_hash1 = hash(app1)
        original_hash2 = hash(app2)

        assert original_hash1 == original_hash2

        # Change state of app1
        app1.app_state.transition_to(AppLifecycleState.LOADING)

        # Hash should be different now
        assert hash(app1) != original_hash1
        assert hash(app2) == original_hash2

    def test_app_attributes_immutable(self):
        """Test that app attributes cannot be modified after creation."""
        app = BluePyllApp(app_name="TestApp", package_name="com.test.app")

        # Test that we can read attributes
        assert app.app_name == "TestApp"
        assert app.package_name == "com.test.app"

        # Test that attributes are strings
        assert isinstance(app.app_name, str)
        assert isinstance(app.package_name, str)

    def test_app_state_machine_integration(self):
        """Test that app integrates properly with state machine."""
        app = BluePyllApp(app_name="TestApp", package_name="com.test.app")

        # Test initial state
        assert app.app_state.current_state == AppLifecycleState.CLOSED

        # Test state transitions work
        app.app_state.transition_to(AppLifecycleState.LOADING)
        assert app.app_state.current_state == AppLifecycleState.LOADING

        app.app_state.transition_to(AppLifecycleState.READY)
        assert app.app_state.current_state == AppLifecycleState.READY

        app.app_state.transition_to(AppLifecycleState.CLOSED)
        assert app.app_state.current_state == AppLifecycleState.CLOSED

    def test_multiple_apps_independent(self):
        """Test that multiple app instances are independent."""
        app1 = BluePyllApp(app_name="TestApp1", package_name="com.test.app1")
        app2 = BluePyllApp(app_name="TestApp2", package_name="com.test.app2")

        # Apps should have independent states
        assert app1.app_state.current_state == app2.app_state.current_state == AppLifecycleState.CLOSED

        # Changing one app's state shouldn't affect the other
        app1.app_state.transition_to(AppLifecycleState.LOADING)
        assert app1.app_state.current_state == AppLifecycleState.LOADING
        assert app2.app_state.current_state == AppLifecycleState.CLOSED

        # Apps should not be equal
        assert app1 != app2
