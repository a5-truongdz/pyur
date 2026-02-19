from colorama import Fore, Style
from pyur.aur import AURPackage

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

def info(_message: str) -> str:
    """
    Returns a `pacman`-like info.

    Parameter:
        _message: The message.

    Returns:
        str.
    """

    return f"{Style.BRIGHT}{Fore.BLUE}::{Fore.WHITE} {_message}{Style.RESET_ALL}"

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

    return info(f"{_aur_package.name}-\033[38;5;243m{_aur_package.version}{Style.RESET_ALL} and {_conflict_package_name}-\033[38;5;243m{_conflict_package_version}{Style.RESET_ALL} are in conflict. Remove {_conflict_package_name}? [y/N] ")

def VerbosePkgList(
    _build_order: list[AURPackage],
    _sync_order: list[tuple[str, str]],
    _remove_packages: set[str]
) -> list[str]:
    """
    Returns a `pacman`-like VerbosePkgList.

    Parameters:
        _build_order: The build order.
        _sync_order: The sync order.

    Returns:
        list[str].
    """

    _total_package_count: int = len(_build_order) + len(_sync_order) + len(_remove_packages)
    _output: list[str] = ["", f"{Style.BRIGHT}Package ({_total_package_count}){Style.RESET_ALL}", ""]

    for package in _remove_packages:
        _output.append(package)
    for package in _sync_order:
        _output.append(f"{package[0]}/{package[1]}")
    for package in _build_order:
        _output.append(f"aur/{package.name}")
    _output.append("")
    return _output
