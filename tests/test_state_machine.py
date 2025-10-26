"""
Unit tests for BluePyll state machine module.
"""

import pytest

from bluepyll.exceptions import StateError
from bluepyll.state_machine import AppLifecycleState, BluestacksState, StateMachine


class TestBluestacksState:
    """Test the BluestacksState enum."""

    def test_bluestacks_state_enum_values(self):
        """Test that BluestacksState has correct enum values."""
        assert BluestacksState.CLOSED.name == "CLOSED"
        assert BluestacksState.LOADING.name == "LOADING"
        assert BluestacksState.READY.name == "READY"

    def test_bluestacks_state_enum_order(self):
        """Test that BluestacksState enum has correct values."""
        assert BluestacksState.CLOSED.value == 1
        assert BluestacksState.LOADING.value == 2
        assert BluestacksState.READY.value == 3

    def test_bluestacks_state_transitions(self):
        """Test that BluestacksState get_transitions returns correct transitions."""
        transitions = BluestacksState.get_transitions()

        assert isinstance(transitions, dict)
        assert len(transitions) == 3

        # Test CLOSED state transitions
        assert BluestacksState.CLOSED in transitions
        assert BluestacksState.LOADING in transitions[BluestacksState.CLOSED]
        assert len(transitions[BluestacksState.CLOSED]) == 1

        # Test LOADING state transitions
        assert BluestacksState.LOADING in transitions
        assert BluestacksState.CLOSED in transitions[BluestacksState.LOADING]
        assert BluestacksState.READY in transitions[BluestacksState.LOADING]
        assert len(transitions[BluestacksState.LOADING]) == 2

        # Test READY state transitions
        assert BluestacksState.READY in transitions
        assert BluestacksState.CLOSED in transitions[BluestacksState.READY]
        assert BluestacksState.LOADING in transitions[BluestacksState.READY]
        assert len(transitions[BluestacksState.READY]) == 2

    def test_bluestacks_state_invalid_transition(self):
        """Test that invalid transitions are not allowed."""
        transitions = BluestacksState.get_transitions()

        # READY cannot transition to READY
        assert BluestacksState.READY not in transitions[BluestacksState.READY]
        # CLOSED cannot transition to READY directly
        assert BluestacksState.READY not in transitions[BluestacksState.CLOSED]


class TestAppLifecycleState:
    """Test the AppLifecycleState enum."""

    def test_app_lifecycle_state_enum_values(self):
        """Test that AppLifecycleState has correct enum values."""
        assert AppLifecycleState.CLOSED.name == "CLOSED"
        assert AppLifecycleState.LOADING.name == "LOADING"
        assert AppLifecycleState.READY.name == "READY"

    def test_app_lifecycle_state_enum_order(self):
        """Test that AppLifecycleState enum has correct values."""
        assert AppLifecycleState.CLOSED.value == 1
        assert AppLifecycleState.LOADING.value == 2
        assert AppLifecycleState.READY.value == 3

    def test_app_lifecycle_state_transitions(self):
        """Test that AppLifecycleState get_transitions returns correct transitions."""
        transitions = AppLifecycleState.get_transitions()

        assert isinstance(transitions, dict)
        assert len(transitions) == 3

        # Test CLOSED state transitions
        assert AppLifecycleState.CLOSED in transitions
        assert AppLifecycleState.LOADING in transitions[AppLifecycleState.CLOSED]
        assert len(transitions[AppLifecycleState.CLOSED]) == 1

        # Test LOADING state transitions
        assert AppLifecycleState.LOADING in transitions
        assert AppLifecycleState.CLOSED in transitions[AppLifecycleState.LOADING]
        assert AppLifecycleState.READY in transitions[AppLifecycleState.LOADING]
        assert len(transitions[AppLifecycleState.LOADING]) == 2

        # Test READY state transitions
        assert AppLifecycleState.READY in transitions
        assert AppLifecycleState.CLOSED in transitions[AppLifecycleState.READY]
        assert AppLifecycleState.LOADING in transitions[AppLifecycleState.READY]
        assert len(transitions[AppLifecycleState.READY]) == 2

    def test_app_lifecycle_state_invalid_transition(self):
        """Test that invalid transitions are not allowed."""
        transitions = AppLifecycleState.get_transitions()

        # READY cannot transition to READY
        assert AppLifecycleState.READY not in transitions[AppLifecycleState.READY]
        # CLOSED cannot transition to READY directly
        assert AppLifecycleState.READY not in transitions[AppLifecycleState.CLOSED]


class TestStateMachine:
    """Test the StateMachine class."""

    def test_state_machine_initialization(self):
        """Test StateMachine initialization."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        assert state_machine.current_state == BluestacksState.CLOSED
        assert isinstance(state_machine.transitions, dict)
        assert isinstance(state_machine.state_handlers, dict)

    def test_state_machine_transition_valid(self):
        """Test valid state transitions."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        previous_state = state_machine.transition_to(BluestacksState.LOADING)
        assert previous_state == BluestacksState.CLOSED
        assert state_machine.current_state == BluestacksState.LOADING

    def test_state_machine_transition_invalid(self):
        """Test invalid state transitions raise StateError."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        # READY is not a valid transition from CLOSED
        with pytest.raises(StateError):
            state_machine.transition_to(BluestacksState.READY)

    def test_state_machine_transition_ignore_validation(self):
        """Test state transitions with validation ignored."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        # This should work even though it's invalid when validation is ignored
        previous_state = state_machine.transition_to(BluestacksState.READY, ignore_validation=True)
        assert previous_state == BluestacksState.CLOSED
        assert state_machine.current_state == BluestacksState.READY

    def test_state_machine_register_handler(self):
        """Test registering state handlers."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        def on_enter_handler():
            pass

        def on_exit_handler():
            pass

        # Register handlers
        state_machine.register_handler(
            BluestacksState.LOADING,
            on_enter=on_enter_handler,
            on_exit=on_exit_handler
        )

        assert BluestacksState.LOADING in state_machine.state_handlers
        assert state_machine.state_handlers[BluestacksState.LOADING]["on_enter"] == on_enter_handler
        assert state_machine.state_handlers[BluestacksState.LOADING]["on_exit"] == on_exit_handler

    def test_state_machine_register_handler_partial(self):
        """Test registering only some handlers."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        def on_enter_handler():
            pass

        # Register only enter handler
        state_machine.register_handler(BluestacksState.LOADING, on_enter=on_enter_handler)

        assert BluestacksState.LOADING in state_machine.state_handlers
        assert state_machine.state_handlers[BluestacksState.LOADING]["on_enter"] == on_enter_handler
        assert "on_exit" not in state_machine.state_handlers[BluestacksState.LOADING]

    def test_state_machine_handler_execution_on_transition(self):
        """Test that handlers are executed during transitions."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        exit_called = False
        enter_called = False

        def on_exit():
            nonlocal exit_called
            exit_called = True

        def on_enter():
            nonlocal enter_called
            enter_called = True

        # Register handlers
        state_machine.register_handler(BluestacksState.CLOSED, on_exit=on_exit)
        state_machine.register_handler(BluestacksState.LOADING, on_enter=on_enter)

        # Transition and check handlers were called
        state_machine.transition_to(BluestacksState.LOADING)

        assert exit_called
        assert enter_called

    def test_state_machine_string_representation(self):
        """Test StateMachine string representation."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        str_repr = str(state_machine)
        assert "StateMachine" in str_repr
        assert "CLOSED" in str_repr

    def test_state_machine_repr_representation(self):
        """Test StateMachine repr representation."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        repr_str = repr(state_machine)
        assert "StateMachine" in repr_str
        assert "CLOSED" in repr_str
        assert "transitions" in repr_str
        assert "state_handlers" in repr_str

    def test_state_machine_multiple_transitions(self):
        """Test multiple state transitions."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        # CLOSED -> LOADING -> READY
        state_machine.transition_to(BluestacksState.LOADING)
        assert state_machine.current_state == BluestacksState.LOADING

        state_machine.transition_to(BluestacksState.READY)
        assert state_machine.current_state == BluestacksState.READY

        # READY -> LOADING -> CLOSED
        state_machine.transition_to(BluestacksState.LOADING)
        assert state_machine.current_state == BluestacksState.LOADING

        state_machine.transition_to(BluestacksState.CLOSED)
        assert state_machine.current_state == BluestacksState.CLOSED
