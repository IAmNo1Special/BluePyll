from typing import Optional, Any, Hashable
from .constants import AppConstants


class BluePyllApp:
    """
    Represents an Android app running in BlueStacks.
    
    This class handles:
    - App state tracking
    - App-specific operations
    - Package management
    
    Attributes:
        app_name (str): Name of the app
        package_name (str): Package name of the app
        is_app_loading (bool): Current loading state of the app
        is_app_open (bool): Current open state of the app
    """
    
    def __init__(self, app_name: str, package_name: str) -> None:
        """
        Initialize a new BluePyllApp instance.
        
        Args:
            app_name (str): Name of the app
            package_name (str): Package name of the app
        
        Raises:
            ValueError: If invalid parameters are provided
        """
        if not app_name or not package_name:
            raise ValueError("app_name and package_name must be non-empty strings")
        
        self.app_name: str = app_name
        self.package_name: str = package_name
        self.is_app_loading: bool = False
        self.is_app_open: bool = False

    @property
    def state(self) -> str:
        """
        Get the current state of the app.
        
        Returns:
            str: Current state (loading, open, or closed)
        """
        if self.is_app_loading:
            return AppConstants.State.LOADING
        elif self.is_app_open:
            return AppConstants.State.OPEN
        return AppConstants.State.CLOSED

    def __str__(self) -> str:
        """
        Return a string representation of the app.
        
        Returns:
            str: String representation of the app
        """
        return f"BluePyllApp(app_name={self.app_name}, package_name={self.package_name})"
    
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
        return self.app_name == other.app_name and self.package_name == other.package_name

    def __hash__(self) -> int:
        """
        Get the hash value of the app.
        
        Returns:
            int: Hash value of the app
        """
        return hash((self.app_name, self.package_name, self.is_app_loading, self.is_app_open))

    def __repr__(self) -> str:
        """
        Return a string representation of the app.
        
        Returns:
            str: String representation of the app
        """
        return f"BluePyllApp(app_name={self.app_name}, package_name={self.package_name})"