from typing import NamedTuple, Any
import requests

class AURPackage(NamedTuple):
    name: str
    version: str
    dependencies: list[str]
    conflicts: list[str]

class NotExists(Exception):
    pass

class AURRPCRequests:
    """
    Create a response with the RPC API of the package when initialized.

    Parameters:
        _package_name: The name of the package.
    
    Raises:
        aur.NotExists: If the package doesn't exists.
    """

    def __init__(
        self,
        _package_name: str
    ) -> None:
        self._package_name: str = _package_name
        self._requests: dict[str, Any] = requests.get(f"https://aur.archlinux.org/rpc/v5/info/{_package_name}").json()
        if self._requests["resultcount"] == 0:
            raise NotExists()    # Will catch it in main.py

    def construct_package(self) -> AURPackage:
        return AURPackage(
            name = self._package_name,
            version = self._requests["results"][0]["Version"],
            dependencies = self._requests["results"][0].get("Depends", []),    # Avoid packages with no dependency (rare).
            conflicts = self._requests["results"][0].get("Conflicts", [])
        )
