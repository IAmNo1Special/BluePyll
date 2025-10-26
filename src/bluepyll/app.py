from .exceptions import AppError
from .state_machine import AppLifecycleState, StateMachine


class BluePyllApp:
    def __init__(self, app_name: str, package_name: str) -> None:
        if not app_name:
            raise AppError("app_name must be a non-empty string")
        if not package_name:
            raise AppError("package_name must be a non-empty string")

        self.app_name: str = app_name
        self.package_name: str = package_name

        self.app_state = StateMachine(
            current_state=AppLifecycleState.CLOSED,
            transitions=AppLifecycleState.get_transitions(),
        )

    def __str__(self) -> str:
        """
        Return a string representation of the app.

        Returns:
            str: String representation of the app
        """
        return f"BluePyllApp(app_name={self.app_name}, package_name={self.package_name}, state={self.app_state.current_state})"

    def __eq__(self, other: object) -> bool:
        """
        Check if two apps are equal based on their name and package name.

        Args:
            other (object): Object to compare with

        Returns:
            bool: True if apps are equal, False otherwise
        """
        if not isinstance(other, BluePyllApp):
            return False
        return (
            self.app_name == other.app_name
            and self.package_name == other.package_name
            and self.app_state.current_state == other.app_state.current_state
        )

    def __hash__(self) -> int:
        """
        Get the hash value of the app.

        Returns:
            int: Hash value of the app
        """
        return hash((self.app_name, self.package_name, self.app_state.current_state))