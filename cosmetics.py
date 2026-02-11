from colorama import Fore, Style
from aur import AURPackage

def error(_message: str) -> str:
    """
    Returns a `pacman`-like error.

    Parameter:
        message: The message.

    Returns:
        str.
    """

    return f"{Style.BRIGHT}{Fore.RED}error:{Style.RESET_ALL} {_message}"

def warning(_message: str) -> str:
    """
    Returns a `pacman`-like warning.

    Parameter:
        _message: The message.

    Returns:
        str.
    """

    return f"{Style.BRIGHT}{Fore.YELLOW}warning:{Style.RESET_ALL} {_message}"

def conflict(
    _aur_package: AURPackage,
    _conflict_package_name: str,
    _conflict_package_version: str
) -> str:
    """
    Returns a `pacman`-like conflict message.

    Parameters:
        _aur_package: The AUR package.
        _conflict_package_name: The conflict package name.
        _conflict_package_version: The conflict package version.

    Returns:
        str.
    """

    return f"{Style.BRIGHT}{Fore.BLUE}:: {Fore.WHITE}{_aur_package.name}-\033[38;5;243m{_aur_package.version}{Style.RESET_ALL} and {_conflict_package_name}-\033[38;5;243m{_conflict_package_version}{Style.RESET_ALL} are in conflict. Remove {_conflict_package_name}? [y/N] "
