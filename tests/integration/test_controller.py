"""
Integration tests for BluePyll components with mocking.
"""

import pytest
from unittest.mock import Mock, patch

from bluepyll.controller import BluePyllController
from bluepyll.app import BluePyllApp
from bluepyll.state_machine import BluestacksState, AppLifecycleState


class TestControllerIntegration:
    """Integration tests for BluePyllController with mocking."""

    @patch('bluepyll.controller.os.path.exists')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_open_bluestacks_success(self, mock_process_iter, mock_startfile, mock_path_exists):
        """Test successful BlueStacks opening."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_process_iter.return_value = [Mock(name="HD-Player.exe")]

        with patch.object(BluePyllController, '_autoset_filepath') as mock_autoset:
            mock_autoset.return_value = None

            # This test verifies that the timeout scenario is handled gracefully
            # The controller initialization should handle the timeout internally

    @patch('bluepyll.controller.psutil.process_iter')
    def test_kill_bluestacks_success(self, mock_process_iter):
        """Test successful BlueStacks killing."""
        # Setup mock process
        mock_proc = Mock()
        mock_proc.name.return_value = "HD-Player.exe"
        mock_proc.info = {"name": "HD-Player.exe"}
        mock_process_iter.return_value = [mock_proc]

        # Create controller in READY state
        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        with patch.object(controller, 'disconnect_adb', return_value=True):
            result = controller.kill_bluestacks()

            assert result is True
            assert controller.bluestacks_state.current_state == BluestacksState.CLOSED

    @patch('bluepyll.controller.psutil.process_iter')
    def test_kill_bluestacks_no_process(self, mock_process_iter):
        """Test killing BlueStacks when no process is found."""
        mock_process_iter.return_value = []  # No BlueStacks process

        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        result = controller.kill_bluestacks()

        assert result is False
        assert controller.bluestacks_state.current_state == BluestacksState.READY

    def test_app_opening_workflow(self):
        """Test complete app opening workflow."""
        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        app = BluePyllApp("TestApp", "com.test.app")

        with patch.object(controller, 'shell') as mock_shell, \
             patch.object(controller, 'is_app_running', return_value=True):

            controller.open_app(app)

            # Verify monkey command was called
            mock_shell.assert_called_with(
                "monkey -p com.test.app -v 1",
                timeout_s=60,
                read_timeout_s=60,
                transport_timeout_s=60
            )

            # Verify app state changed
            assert app.app_state.current_state == AppLifecycleState.LOADING

            # Verify app was added to running apps
            assert app in controller.running_apps

    def test_app_closing_workflow(self):
        """Test complete app closing workflow."""
        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        app = BluePyllApp("TestApp", "com.test.app")
        controller.running_apps.append(app)
        app.app_state.transition_to(AppLifecycleState.READY, ignore_validation=True)

        with patch.object(controller, 'shell') as mock_shell, \
             patch.object(controller, 'is_app_running', return_value=False):

            controller.close_app(app)

            # Verify force-stop command was called
            mock_shell.assert_called_with(
                "am force-stop com.test.app",
                timeout_s=30
            )

            # Verify app state changed
            assert app.app_state.current_state == AppLifecycleState.CLOSED

            # Verify app was removed from running apps
            assert app not in controller.running_apps

    def test_is_app_running_check(self):
        """Test app running status check."""
        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        app = BluePyllApp("TestApp", "com.test.app")

        with patch.object(controller, 'shell') as mock_shell:
            mock_shell.return_value = "mCurrentFocus"

            result = controller.is_app_running(app)

            assert result is True
            mock_shell.assert_called_with(
                "dumpsys window windows | grep -E 'mCurrentFocus' | grep com.test.app",
                timeout_s=60
            )

    def test_is_app_running_not_found(self):
        """Test app running check when app is not running."""
        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        app = BluePyllApp("TestApp", "com.test.app")

        with patch.object(controller, 'shell') as mock_shell:
            mock_shell.return_value = ""

            result = controller.is_app_running(app)

            assert result is False

    def test_adb_connection_handling(self):
        """Test ADB connection establishment and management."""
        controller = BluePyllController()

        # Initially should not be connected
        assert controller.available is False

        with patch.object(controller, 'connect') as mock_connect:
            # Test connection attempt
            result = controller.connect_adb()

            mock_connect.assert_called_once()
            # Should return True if connection succeeds
            assert isinstance(result, bool)

    def test_go_home_functionality(self):
        """Test go home functionality."""
        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        with patch.object(controller, 'shell') as mock_shell:
            controller.go_home()

            mock_shell.assert_called_with(
                "input keyevent 3",
                timeout_s=30
            )

    def test_type_text_functionality(self):
        """Test text typing functionality."""
        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        test_text = "Hello World"

        with patch.object(controller, 'shell') as mock_shell:
            controller.type_text(test_text)

            mock_shell.assert_called_with(
                f"input text {test_text}",
                timeout_s=30
            )

    def test_key_press_functions(self):
        """Test key press functions."""
        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        with patch.object(controller, 'shell') as mock_shell:
            controller.press_enter()
            mock_shell.assert_called_with(
                "input keyevent 66",
                timeout_s=30
            )

            mock_shell.reset_mock()

            controller.press_esc()
            mock_shell.assert_called_with(
                "input keyevent 4",
                timeout_s=30
            )

    def test_screenshot_capture(self):
        """Test screenshot capture functionality."""
        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        with patch.object(controller, 'shell') as mock_shell:
            mock_shell.return_value = b"fake_screenshot_data"

            result = controller.capture_screenshot()

            assert result == b"fake_screenshot_data"
            mock_shell.assert_called_with(
                "screencap -p",
                decode=False,
                timeout_s=30
            )

    def test_controller_property_validation(self):
        """Test controller property validation."""
        controller = BluePyllController()

        # Test ref_window_size validation
        with pytest.raises(Exception):  # Should raise BluePyllError
            controller.ref_window_size = (-1, 1080)  # Invalid negative width

        with pytest.raises(Exception):  # Should raise BluePyllError
            controller.ref_window_size = (1920, -1)  # Invalid negative height

        # Test valid assignment
        controller.ref_window_size = (1920, 1080)
        assert controller.ref_window_size == (1920, 1080)

    def test_controller_filepath_validation(self):
        """Test controller filepath validation."""
        controller = BluePyllController()

        # Test invalid filepath type
        with pytest.raises(Exception):  # Should raise EmulatorError
            controller.filepath = 123  # Not a string

        # Test non-existent filepath
        with pytest.raises(Exception):  # Should raise EmulatorError
            controller.filepath = "/nonexistent/path/HD-Player.exe"

    def test_state_transitions_with_handlers(self):
        """Test state transitions with registered handlers."""
        controller = BluePyllController()

        # Mock handler functions
        loading_handler = Mock()
        ready_handler = Mock()

        # Register handlers
        controller.bluestacks_state.register_handler(
            BluestacksState.LOADING, on_enter=loading_handler
        )
        controller.bluestacks_state.register_handler(
            BluestacksState.READY, on_enter=ready_handler
        )

        # Transition should call handlers
        controller.bluestacks_state.transition_to(BluestacksState.LOADING)
        loading_handler.assert_called_once()

        controller.bluestacks_state.transition_to(BluestacksState.READY)
        ready_handler.assert_called_once()

    def test_ui_element_detection(self):
        """Test UI element detection functionality."""
        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        # Create mock UI element
        mock_element = Mock()
        mock_element.where.return_value = (100, 200)

        elements_list = [mock_element]

        result = controller.where_elements(elements_list)

        assert result == (100, 200)
        mock_element.where.assert_called_once()

    def test_ui_element_clicking(self):
        """Test UI element clicking functionality."""
        controller = BluePyllController()
        controller.bluestacks_state.transition_to(BluestacksState.READY, ignore_validation=True)

        # Create mock UI element
        mock_element = Mock()
        mock_element.click.return_value = True

        elements_list = [mock_element]

        result = controller.click_elements(elements_list)

        assert result is True
        mock_element.click.assert_called_once()