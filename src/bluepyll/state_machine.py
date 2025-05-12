from enum import Enum, auto
from dataclasses import dataclass, field
from collections.abc import Callable


class BluestacksState(Enum):
    CLOSED = auto()
    LOADING = auto()
    READY = auto()
    
    @classmethod
    def get_transitions(cls) -> dict:
        """
        Define valid state transitions for the BlueStacks state machine.
        
        Returns:
            dict: A dictionary mapping current states to their allowed next states
        """
        return {
            cls.CLOSED: [cls.LOADING],
            cls.LOADING: [cls.CLOSED, cls.READY],
            cls.READY: [cls.CLOSED, cls.LOADING]
        }

class AppLifecycleState(Enum):
    CLOSED = auto()
    LOADING = auto()
    READY = auto() 

    @classmethod
    def get_transitions(cls) -> dict:
        """
        Define valid state transitions for the App state machine.
        
        Returns:
            dict: A dictionary mapping current states to their allowed next states
        """
        return {
            cls.CLOSED: [cls.LOADING],
            cls.LOADING: [cls.CLOSED, cls.READY],
            cls.READY: [cls.CLOSED, cls.LOADING]
        }

@dataclass
class StateMachine:
    current_state: Enum
    transitions: dict[Enum, list[Enum]] = field(default_factory=dict)
    state_handlers: dict[Enum, dict[str, Callable[[], None] | None]] = field(default_factory=dict)

    def transition_to(self, new_state: Enum) -> Enum:
        """
        Transition to a new state with validation and optional handlers
        
        Args:
            new_state (Enum): The state to transition to
        
        Raises:
            ValueError: If the transition is not valid
        
        Returns:
            Enum: The previous state
        """
        # Validate transition
        if new_state not in self.transitions.get(self.current_state, []):
            raise ValueError(f"Invalid state transition from {self.current_state} to {new_state}")
        
        # Exit current state handler
        exit_handler = self.state_handlers.get(self.current_state, {}).get('on_exit')
        if exit_handler:
            exit_handler()
        
        # Change state
        previous_state = self.current_state
        self.current_state = new_state
        
        # Enter new state handler
        enter_handler = self.state_handlers.get(new_state, {}).get('on_enter')
        if enter_handler:
            enter_handler()
        
        return previous_state

    def register_handler(
        self, 
        state: Enum, 
        on_enter: Callable[[], None] | None = None, 
        on_exit: Callable[[], None] | None = None
    ) -> None:
        """
        Register enter and exit handlers for a specific state
        
        Args:
            state (Enum): The state to register handlers for
            on_enter (Callable[[], None] | None, optional): Handler called when entering the state
            on_exit (Callable[[], None] | None, optional): Handler called when exiting the state
        """
        handlers = {}
        if on_enter:
            handlers['on_enter'] = on_enter
        if on_exit:
            handlers['on_exit'] = on_exit
        
        if handlers:
            self.state_handlers[state] = handlers

    def __str__(self) -> str:
        """
        String representation of the state machine
        
        Returns:
            str: Current state as a string
        """
        return f"StateMachine(current_state={self.current_state})"

    def __repr__(self) -> str:
        """
        Detailed representation of the state machine
        
        Returns:
            str: Detailed state machine information
        """
        return (
            f"StateMachine(current_state={self.current_state}, "
            f"transitions={self.transitions}, "
            f"state_handlers={list(self.state_handlers.keys())})"
        )
