"""
Unit tests for StateMachine class.
"""

import pytest
from unittest.mock import Mock

from bluepyll.state_machine import StateMachine, BluestacksState, AppLifecycleState
from bluepyll.exceptions import StateError


class TestStateMachine:
    """Test cases for StateMachine class."""

    def test_state_machine_creation(self):
        """Test state machine creation with initial state."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        assert state_machine.current_state == BluestacksState.CLOSED
        assert isinstance(state_machine.transitions, dict)
        assert BluestacksState.CLOSED in state_machine.transitions

    def test_valid_state_transition(self):
        """Test valid state transition."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        previous_state = state_machine.transition_to(BluestacksState.LOADING)

        assert state_machine.current_state == BluestacksState.LOADING
        assert previous_state == BluestacksState.CLOSED

    def test_invalid_state_transition(self):
        """Test invalid state transition raises StateError."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        with pytest.raises(StateError, match="Invalid state transition"):
            state_machine.transition_to(BluestacksState.READY)

    def test_state_transition_ignore_validation(self):
        """Test state transition with validation ignored."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        # This should work even though it's not a valid transition
        previous_state = state_machine.transition_to(BluestacksState.READY, ignore_validation=True)

        assert state_machine.current_state == BluestacksState.READY
        assert previous_state == BluestacksState.CLOSED

    def test_state_handler_registration(self):
        """Test state handler registration."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        # Mock handlers
        on_enter = Mock()
        on_exit = Mock()

        state_machine.register_handler(BluestacksState.LOADING, on_enter=on_enter, on_exit=on_exit)

        assert BluestacksState.LOADING in state_machine.state_handlers
        assert state_machine.state_handlers[BluestacksState.LOADING]["on_enter"] == on_enter
        assert state_machine.state_handlers[BluestacksState.LOADING]["on_exit"] == on_exit

    def test_state_handler_registration_partial(self):
        """Test state handler registration with only one handler."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        on_enter = Mock()
        state_machine.register_handler(BluestacksState.LOADING, on_enter=on_enter)

        assert BluestacksState.LOADING in state_machine.state_handlers
        assert state_machine.state_handlers[BluestacksState.LOADING]["on_enter"] == on_enter
        assert "on_exit" not in state_machine.state_handlers[BluestacksState.LOADING]

    def test_state_transition_calls_handlers(self):
        """Test that state transition calls appropriate handlers."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        on_exit = Mock()
        on_enter = Mock()

        # Register handlers for both states
        state_machine.register_handler(BluestacksState.CLOSED, on_exit=on_exit)
        state_machine.register_handler(BluestacksState.LOADING, on_enter=on_enter)

        state_machine.transition_to(BluestacksState.LOADING)

        # Verify handlers were called
        on_exit.assert_called_once()
        on_enter.assert_called_once()

    def test_state_machine_string_representation(self):
        """Test state machine string representation."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        expected = "StateMachine(current_state=BluestacksState.CLOSED)"
        assert str(state_machine) == expected

    def test_state_machine_repr(self):
        """Test state machine detailed representation."""
        state_machine = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions()
        )

        repr_str = repr(state_machine)
        assert "StateMachine(" in repr_str
        assert "current_state=BluestacksState.CLOSED" in repr_str
        assert "transitions=" in repr_str
        assert "state_handlers=" in repr_str

    def test_bluestacks_state_transitions(self):
        """Test BlueStacks state transitions are correctly defined."""
        transitions = BluestacksState.get_transitions()

        assert transitions[BluestacksState.CLOSED] == [BluestacksState.LOADING]
        assert transitions[BluestacksState.LOADING] == [BluestacksState.CLOSED, BluestacksState.READY]
        assert transitions[BluestacksState.READY] == [BluestacksState.CLOSED, BluestacksState.LOADING]

    def test_app_lifecycle_state_transitions(self):
        """Test AppLifecycle state transitions are correctly defined."""
        transitions = AppLifecycleState.get_transitions()

        assert transitions[AppLifecycleState.CLOSED] == [AppLifecycleState.LOADING]
        assert transitions[AppLifecycleState.LOADING] == [AppLifecycleState.CLOSED, AppLifecycleState.READY]
        assert transitions[AppLifecycleState.READY] == [AppLifecycleState.CLOSED, AppLifecycleState.LOADING]

    def test_multiple_transitions_from_loading_state(self):
        """Test multiple valid transitions from LOADING state."""
        state_machine = StateMachine(
            current_state=BluestacksState.LOADING,
            transitions=BluestacksState.get_transitions()
        )

        # Should be able to transition to CLOSED
        state_machine.transition_to(BluestacksState.CLOSED)
        assert state_machine.current_state == BluestacksState.CLOSED

        # Transition back to LOADING
        state_machine.transition_to(BluestacksState.LOADING)
        assert state_machine.current_state == BluestacksState.LOADING

        # Should be able to transition to READY
        state_machine.transition_to(BluestacksState.READY)
        assert state_machine.current_state == BluestacksState.READY