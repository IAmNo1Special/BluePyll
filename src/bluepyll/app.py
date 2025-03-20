class BluePyllApp:
    def __init__(self, app_name: str, package_name: str) -> None:
        self.app_name: str = app_name
        self.package_name: str = package_name
        self.is_app_loading: bool = False
        self.is_app_open: bool = False

    def __str__(self) -> str:
        return f"BluePyllApp(app_name={self.app_name}, package_name={self.package_name})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BluePyllApp):
            return False
        return self.app_name == other.app_name and self.package_name == other.package_name

    def __hash__(self) -> int:
        return hash((self.app_name, self.package_name, self.is_app_loading, self.is_app_open))

    def __repr__(self) -> str:
        return f"BluePyllApp(app_name={self.app_name}, package_name={self.package_name})"