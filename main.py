"""
pyur: An AUR helper that tries to replicate exactly how `pacman` output.
"""

from arguments import parse_arguments
from cosmetics import error, warning, conflict
from pyalpm import Handle
from colorama import Fore, Style
import aur
import sys
import local

packages = parse_arguments()

constructed_packages: list[aur.AURPackage] = []
for package in packages:
    try:
        constructed_packages.append(aur.AURRPCRequests(package).construct_package())
    except aur.NotExists:
        print(
            error(f"target not found: {package}"),
            file = sys.stderr
        ); sys.exit(1)

handler: Handle = local.create_handler()
install_packages: list[aur.AURPackage] = []

for package in constructed_packages:
    if local.is_locally_installed(
        handler,
        package.name
    ):
        version: str = local.get_version(
            handler,
            package.name
        )
        if version == package.version:
            print(warning(f"{package.name}-{version} is up to date -- skipping"))
            continue
    install_packages.append(package)

if not install_packages:
    print(" there is nothing to do")
    sys.exit()

print("resolving dependencies...")
print("looking for conflicting packages...")

for package in install_packages:
    try:
        local.check_for_conflicts(
            handler,
            package
        )
    except local.Conflicts as e:
        choice: str = input(conflict(
            package,
            e.args[0],
            e.args[1]
        )).lower()
        if choice != "y":
            print(
                error("unresolvable package conflicts detected"),
                file = sys.stderr
            ); print(
                error("failed to prepare transaction (conflicting dependencies)"),
                file = sys.stderr
            ); print(f"{Style.BRIGHT}{Fore.BLUE}::{Fore.WHITE} {package.name}-{package.version} and {e.args[0]}-{e.args[1]} are in conflict")
            sys.exit(1)
