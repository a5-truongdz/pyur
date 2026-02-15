"""
pyur: An AUR helper that tries to replicate exactly how `pacman` output.
"""

from arguments import parse_arguments
from cosmetics import error, warning, conflict
from pyalpm import Handle
from colorama import Fore, Style
from dependencies import build_order, sync_order
import aur
import sys
import local

def main() -> int:
    packages = parse_arguments()

    constructed_packages: list[aur.AURPackage] = []
    for package in packages:
        try:
            constructed_packages.append(aur.AURRPCRequests(package).construct_package())
        except aur.NotExists:
            print(
                error(f"target not found: {package}"),
                file = sys.stderr
            ); return 1

    handler: Handle = local.create_handler()
    not_utd_packages: list[aur.AURPackage] = []

    for package in constructed_packages:
        if aur.is_up_to_date(
            handler,
            package
        ):
            print(warning(f"{package.name}-{package.version} is up to date -- skipping"))
            continue
        not_utd_packages.append(package)

    if not not_utd_packages:
        print(" there is nothing to do")
        return 0

    print("resolving dependencies...")
    print("looking for conflicting packages...")

    build_packages: list[aur.AURPackage] = []
    remove_packages: set[str] = set()

    for package in not_utd_packages:
        try:
            local.check_for_conflicts(
                handler,
                package
            )
        except local.Conflicts as e:
            choice: str = input(conflict(
                package,
                e._name,
                e._version
            )).lower()
            if choice != "y":
                print(
                    error("unresolvable package conflicts detected"),
                    file = sys.stderr
                ); print(
                    error("failed to prepare transaction (conflicting dependencies)"),
                    file = sys.stderr
                ); print(f"{Style.BRIGHT}{Fore.BLUE}::{Fore.WHITE} {package.name}-{package.version} and {e._name}-{e._version} are in conflict")
                return 1
            remove_packages.add(e._name)
        build_packages.append(package)

    aur_seen: set[str] = set()
    _build_order: list[aur.AURPackage] = []
    sync_dependencies: set[tuple[str, str]] = set()

    for package in build_packages:
        print(package)
        build_order(
            handler,
            package,
            aur_seen,
            _build_order,
            sync_dependencies
        )
    
    sync_seen: set[str] = set()
    _sync_order: list[tuple[str, str]] = []
    for package in sync_dependencies:
        print(package)
        sync_order(
            handler,
            package,
            sync_seen,
            _sync_order
        )

    print(_build_order)
    print(_sync_order)

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupt signal received")
        sys.exit(130)
