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
    sys.exit()

print("resolving dependencies...")
print("looking for conflicting packages...")

build_packages: list[aur.AURPackage] = []
remove_packages: list[str] = []

for package in not_utd_packages:
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
        remove_packages.append(e.args[0])
    build_packages.append(package)

print(build_packages)
print(remove_packages)
