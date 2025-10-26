"""
Unit tests for BluePyll controller module.
"""

from unittest.mock import MagicMock, patch

import pytest

from bluepyll.app import BluePyllApp
from bluepyll.constants import BluestacksConstants
from bluepyll.controller import BluePyllController
from bluepyll.state_machine import AppLifecycleState, BluestacksState


class TestBluePyllControllerInitialization:
    """Test BluePyllController initialization."""

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_controller_initialization(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test BluePyllController initialization."""
        # Setup mocks
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker

        mock_elements = MagicMock()
        mock_elements_class.return_value = mock_elements

        # Mock process_iter to return empty list (no existing processes)
        mock_process_iter.return_value = []

        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "test content"

            controller = BluePyllController()

            # Verify initialization
            assert controller.img_txt_checker == mock_checker
            assert controller._ref_window_size == BluestacksConstants.DEFAULT_REF_WINDOW_SIZE
            assert controller._filepath is not None
            assert controller.running_apps == []
            assert controller.bluestacks_state.current_state == BluestacksState.LOADING

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    @patch('bluepyll.controller.os.path.exists')
    def test_controller_custom_parameters(self, mock_exists, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test BluePyllController initialization with custom parameters."""
        # Setup mocks
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker

        mock_elements = MagicMock()
        mock_elements_class.return_value = mock_elements

        mock_process_iter.return_value = []
        mock_exists.return_value = True

        custom_ip = "192.168.1.100"
        custom_port = "6000"
        custom_window_size = (1280, 720)

        controller = BluePyllController(
            ip=custom_ip,
            port=custom_port,
            ref_window_size=custom_window_size
        )

        assert controller._ref_window_size == custom_window_size

    def test_validate_and_convert_int_valid(self):
        """Test _validate_and_convert_int with valid inputs."""
        controller = BluePyllController.__new__(BluePyllController)

        # Test integer input
        result = controller._validate_and_convert_int(42, "test_param")
        assert result == 42

        # Test string input
        result = controller._validate_and_convert_int("42", "test_param")
        assert result == 42

    def test_validate_and_convert_int_invalid(self):
        """Test _validate_and_convert_int with invalid inputs."""
        controller = BluePyllController.__new__(BluePyllController)

        # Test invalid string
        with pytest.raises(ValueError, match="Error in test_param"):
            controller._validate_and_convert_int("invalid", "test_param")


class TestBluePyllControllerProperties:
    """Test BluePyllController properties."""

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_ref_window_size_property(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test ref_window_size property."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        original_size = controller.ref_window_size

        # Test getting property
        assert controller.ref_window_size == original_size

        # Test setting property with tuple
        new_size = (1280, 720)
        controller.ref_window_size = new_size
        assert controller.ref_window_size == new_size

        # Test setting property with strings
        controller.ref_window_size = ("1600", "900")
        assert controller.ref_window_size == (1600, 900)

    def test_ref_window_size_setter_validation(self):
        """Test ref_window_size setter validation."""
        controller = BluePyllController.__new__(BluePyllController)
        controller._ref_window_size = BluestacksConstants.DEFAULT_REF_WINDOW_SIZE

        # Test invalid width
        with pytest.raises(ValueError, match="Provided width must be positive integers"):
            controller.ref_window_size = (-100, 1080)

        with pytest.raises(ValueError, match="Provided width must be integer or the string representation"):
            controller.ref_window_size = ("invalid", 1080)

        # Test invalid height
        with pytest.raises(ValueError, match="Provided height must be positive integers"):
            controller.ref_window_size = (1920, 0)

        with pytest.raises(ValueError, match="Provided height must be integer or the string representation"):
            controller.ref_window_size = (1920, "invalid")

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_filepath_property(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test filepath property."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        original_filepath = controller.filepath

        # Test getting property
        assert controller.filepath == original_filepath

        # Test setting valid filepath
        test_path = "C:\\Program Files\\BlueStacks\\HD-Player.exe"
        with patch('bluepyll.controller.os.path.exists', return_value=True):
            controller.filepath = test_path
            assert controller.filepath == test_path

    def test_filepath_setter_validation(self):
        """Test filepath setter validation."""
        controller = BluePyllController.__new__(BluePyllController)

        # Test non-string input
        with pytest.raises(ValueError, match="Provided filepath must be a string"):
            controller.filepath = 123

        # Test non-existent path
        with patch('bluepyll.controller.os.path.exists', return_value=False):
            with pytest.raises(ValueError, match="Provided filepath does not exist"):
                controller.filepath = "nonexistent/path.exe"


class TestBluePyllControllerFilepath:
    """Test BluePyllController filepath detection."""

    @patch('bluepyll.controller.os.path.exists')
    @patch('bluepyll.controller.os.environ.get')
    def test_autoset_filepath_standard_path(self, mock_get, mock_exists):
        """Test _autoset_filepath finds standard installation path."""
        controller = BluePyllController.__new__(BluePyllController)

        # Mock environment variables
        mock_get.side_effect = lambda key, default="": {
            "ProgramFiles": "C:\\Program Files",
            "ProgramFiles(x86)": "C:\\Program Files (x86)"
        }.get(key, default)

        # Mock file existence - only the standard path exists
        def mock_exists_side_effect(path):
            return path == "C:\\Program Files\\BlueStacks_nxt\\HD-Player.exe"

        mock_exists.side_effect = mock_exists_side_effect

        controller._autoset_filepath()

        assert controller._filepath == "C:\\Program Files\\BlueStacks_nxt\\HD-Player.exe"

    @patch('bluepyll.controller.os.path.exists')
    @patch('bluepyll.controller.os.environ.get')
    def test_autoset_filepath_alternative_path(self, mock_get, mock_exists):
        """Test _autoset_filepath finds alternative installation path."""
        controller = BluePyllController.__new__(BluePyllController)

        # Mock environment variables
        mock_get.side_effect = lambda key, default="": {
            "ProgramFiles": "C:\\Program Files",
            "ProgramFiles(x86)": "C:\\Program Files (x86)"
        }.get(key, default)

        # Mock file existence - only alternative path exists
        def mock_exists_side_effect(path):
            return path == "C:\\Program Files (x86)\\BlueStacks\\HD-Player.exe"

        mock_exists.side_effect = mock_exists_side_effect

        controller._autoset_filepath()

        assert controller._filepath == "C:\\Program Files (x86)\\BlueStacks\\HD-Player.exe"

    @patch('bluepyll.controller.os.path.exists')
    @patch('bluepyll.controller.os.environ.get')
    def test_autoset_filepath_broad_search(self, mock_get, mock_exists):
        """Test _autoset_filepath broad search functionality."""
        controller = BluePyllController.__new__(BluePyllController)

        # Mock environment variables
        mock_get.side_effect = lambda key, default="": {
            "ProgramFiles": "C:\\Program Files",
            "ProgramFiles(x86)": "C:\\Program Files (x86)"
        }.get(key, default)

        # Mock file existence - no standard paths exist
        mock_exists.return_value = False

        # Mock os.walk to find file in custom location
        with patch('bluepyll.controller.os.walk') as mock_walk:
            mock_walk.return_value = [
                ("C:\\Custom\\BlueStacks", [], ["HD-Player.exe"])
            ]

            controller._autoset_filepath()

            assert controller._filepath == "C:\\Custom\\BlueStacks\\HD-Player.exe"

    @patch('bluepyll.controller.os.path.exists')
    @patch('bluepyll.controller.os.environ.get')
    def test_autoset_filepath_not_found(self, mock_get, mock_exists):
        """Test _autoset_filepath when file is not found."""
        controller = BluePyllController.__new__(BluePyllController)

        # Mock environment variables
        mock_get.side_effect = lambda key, default="": {
            "ProgramFiles": "C:\\Program Files",
            "ProgramFiles(x86)": "C:\\Program Files (x86)"
        }.get(key, default)

        # Mock file existence - no files exist
        mock_exists.return_value = False

        # Mock os.walk to not find file
        with patch('bluepyll.controller.os.walk') as mock_walk:
            mock_walk.return_value = []

            with pytest.raises(FileNotFoundError, match="Could not find HD-Player.exe"):
                controller._autoset_filepath()


class TestBluePyllControllerStateManagement:
    """Test BluePyllController state management."""

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_open_bluestacks_closed_state(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test open_bluestacks from CLOSED state."""
        # Setup mocks
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker

        mock_elements = MagicMock()
        mock_elements_class.return_value = mock_elements

        # Mock process_iter to return empty initially, then with process
        process_mock = MagicMock()
        process_mock.name.return_value = "HD-Player.exe"

        def process_iter_side_effect(attrs=None):
            if attrs is None:
                return [process_mock]
            return [process_mock]

        mock_process_iter.side_effect = process_iter_side_effect

        with patch('bluepyll.controller.time.time') as mock_time, \
             patch('bluepyll.controller.time.sleep'):

            mock_time.side_effect = [0, 1, 2]  # Start time, check time, end time

            controller = BluePyllController()

            # Verify state transition
            assert controller.bluestacks_state.current_state == BluestacksState.LOADING

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_open_bluestacks_already_loading(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test open_bluestacks when already in LOADING state."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.LOADING

        # Should return early without doing anything
        controller.open_bluestacks()
        assert controller.bluestacks_state.current_state == BluestacksState.LOADING

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_open_bluestacks_already_ready(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test open_bluestacks when already in READY state."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.READY

        # Should return early without doing anything
        controller.open_bluestacks()
        assert controller.bluestacks_state.current_state == BluestacksState.READY

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_kill_bluestacks_ready_state(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test kill_bluestacks from READY state."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.READY

        # Mock process for killing
        process_mock = MagicMock()
        with patch('bluepyll.controller.psutil.process_iter') as mock_iter:
            mock_iter.return_value = [process_mock]

            with patch.object(controller, 'disconnect_adb', return_value=True):
                result = controller.kill_bluestacks()

                assert result is True
                assert controller.bluestacks_state.current_state == BluestacksState.CLOSED
                process_mock.kill.assert_called_once()

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_kill_bluestacks_already_closed(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test kill_bluestacks when already in CLOSED state."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.CLOSED

        result = controller.kill_bluestacks()

        assert result is True
        assert controller.bluestacks_state.current_state == BluestacksState.CLOSED


class TestBluePyllControllerAppManagement:
    """Test BluePyllController app management."""

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_open_app_success(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test open_app successfully opens an app."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.READY

        app = BluePyllApp("TestApp", "com.test.app")

        with patch.object(controller, 'connect_adb', return_value=True), \
             patch.object(controller, 'is_app_running', return_value=True):

            controller.open_app(app)

            assert app in controller.running_apps
            assert app.app_state.current_state == AppLifecycleState.LOADING

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_open_app_bluestacks_not_ready(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test open_app when Bluestacks is not ready."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.CLOSED

        app = BluePyllApp("TestApp", "com.test.app")

        controller.open_app(app)

        # Should not add app to running apps
        assert app not in controller.running_apps
        assert app.app_state.current_state == AppLifecycleState.CLOSED

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_close_app_success(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test close_app successfully closes an app."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.READY

        app = BluePyllApp("TestApp", "com.test.app")
        controller.running_apps = [app]

        with patch.object(controller, 'connect_adb', return_value=True), \
             patch.object(controller, 'is_app_running', return_value=False):

            controller.close_app(app)

            assert app not in controller.running_apps
            assert app.app_state.current_state == AppLifecycleState.CLOSED

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_is_app_running_ready_state(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test is_app_running when Bluestacks is ready."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.READY

        app = BluePyllApp("TestApp", "com.test.app")

        with patch.object(controller, 'connect_adb', return_value=True):
            with patch('bluepyll.controller.time.sleep'):
                # Mock shell command to return output indicating app is running
                with patch.object(controller, 'shell', return_value="mCurrentFocus") as mock_shell:
                    result = controller.is_app_running(app)

                    assert result is True
                    mock_shell.assert_called()

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_is_app_running_not_ready(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test is_app_running when Bluestacks is not ready."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.CLOSED

        app = BluePyllApp("TestApp", "com.test.app")

        result = controller.is_app_running(app)

        # Should return None (falsy) when not ready
        assert not result


class TestBluePyllControllerInputMethods:
    """Test BluePyllController input methods."""

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_go_home_ready_state(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test go_home when Bluestacks is ready."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.READY

        with patch.object(controller, 'connect_adb', return_value=True):
            controller.go_home()

            # Verify shell was called with home command
            controller.shell.assert_called_with("input keyevent 3", timeout_s=30)

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_type_text_ready_state(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test type_text when Bluestacks is ready."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.READY

        with patch.object(controller, 'connect_adb', return_value=True):
            controller.type_text("Hello World")

            # Verify shell was called with text command
            controller.shell.assert_called_with("input text Hello World", timeout_s=30)

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_press_enter_ready_state(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test press_enter when Bluestacks is ready."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.READY

        with patch.object(controller, 'connect_adb', return_value=True):
            controller.press_enter()

            # Verify shell was called with enter command
            controller.shell.assert_called_with("input keyevent 66", timeout_s=30)

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_press_esc_ready_state(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test press_esc when Bluestacks is ready."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.READY

        with patch.object(controller, 'connect_adb', return_value=True):
            controller.press_esc()

            # Verify shell was called with esc command
            controller.shell.assert_called_with("input keyevent 4", timeout_s=30)

    @patch('bluepyll.controller.ImageTextChecker')
    @patch('bluepyll.controller.BluePyllElements')
    @patch('bluepyll.controller.os.startfile')
    @patch('bluepyll.controller.psutil.process_iter')
    def test_show_recent_apps_ready_state(self, mock_process_iter, mock_startfile, mock_elements_class, mock_checker_class):
        """Test show_recent_apps when Bluestacks is ready."""
        mock_process_iter.return_value = []

        controller = BluePyllController()
        controller.bluestacks_state.current_state = BluestacksState.READY

        controller.show_recent_apps()

        # Verify shell was called with recent apps command
        controller.shell.assert_called_with("input keyevent KEYCODE_APP_SWITCH", timeout_s=30)
