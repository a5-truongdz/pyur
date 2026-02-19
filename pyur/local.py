from pycman.config import init_with_config
from pyalpm import Handle
from pyur.aur import AURPackage

class Conflicts(Exception):
    def __init__(
        self,
        _name: str,
        _version: str
    ) -> None:
        self._name: str = _name
        self._version: str = _version
        super().__init__(
            _name,
            _version
        )

def create_handler() -> Handle:
    """
    Creates a handle with the config in /etc/pacman.conf.

    Returns:
        pyalpm.Handle.
    """
    return init_with_config("/etc/pacman.conf")

def is_locally_installed(
    _handler: Handle,
    _package_name: str
) -> bool:
    """
    Checks if a package is locally-installed.

    Parameter:
        _handler: A handler created from create_handler().
        _package_name: The package

    Returns:
        bool.
    """
    if _handler.get_localdb().get_pkg(_package_name) is not None:
        return True
    return False

def check_for_conflicts(
    _handler: Handle,
    _aur_package: AURPackage
) -> None:
    """
    Checks if the AUR package conflicts with any locally-installed packages.

    Parameters:
        _handler: A handler created from create_handler()
        _aur_package: The AUR package

    Raises:
        local.Conflicts: If the AUR package conflicts.
    """

    for package in _aur_package.conflicts:
        if is_locally_installed(
            _handler,
            package
        ):
            raise Conflicts(package, _handler.get_localdb().get_pkg(package).version)

def get_version(
    _handler: Handle,
    _package_name: str
) -> str:
    """
    Gets the version of a package.

    Parameters:
        _handler: A handler created from create_handler().
        _package_name: The package.

    Returns:
        str.
    """

    return str(_handler.get_localdb().get_pkg(_package_name).version)
