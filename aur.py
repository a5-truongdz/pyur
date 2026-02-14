from typing import NamedTuple, Any
from pyalpm import Handle, vercmp
import requests

class AURPackage(NamedTuple):
    name: str
    version: str
    dependencies: list[str]
    conflicts: list[str]

from local import is_locally_installed, get_version

class NotExists(Exception):
    pass

class AURRPCRequests:
    """
    Creates with the RPC API of the package when initialized.

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
            dependencies = self._requests["results"][0].get("Depends", []),
            conflicts = self._requests["results"][0].get("Conflicts", [])
        )

def is_up_to_date(
    _handler: Handle,
    _package: AURPackage
) -> bool:
    """
    Checks if a local package is up-to-date with the provided AUR package.

    Parameters:
        _handler: A handler created from local.create_handler().
        _package: The AUR package.

    Returns:
        bool.
    """

    _local_version: str = ""
    if is_locally_installed(
        _handler,
        _package.name
    ):
        _local_version = get_version(
            _handler,
            _package.name
        ); _cmp: int = vercmp(
            _local_version,
            _package.version
        )
        if _cmp == 0:
            return True
    return False
