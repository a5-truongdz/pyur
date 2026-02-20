"""
pyur: An AUR helper that tries to replicate exactly how `pacman` output.
"""

import sys
import os

# Putting root check here to avoid uninstalled pip packages globally
# Which leads to ImportError
if os.getuid() == 0:
    print(
        "error: you cannot perform this operation unless you are not root.",
        file = sys.stderr
    ); sys.exit(1)


from pyur.arguments import parse_arguments
from pyur.cosmetics import error, warning, conflict, VerbosePkgList, info
from pyalpm import Handle
from pyur.dependencies import build_order, sync_order
from pyur.cloner import retrieve_pkgbuilds

import pyur.aur
import pyur.local
import pyur.pacman
import subprocess
import glob

CACHE_PATH: str = os.path.expanduser("~/.cache/pyur")

def main() -> int:
    packages = parse_arguments()

    constructed_packages: list[pyur.aur.AURPackage] = []
    for package in packages:
        try:
            constructed_packages.append(pyur.aur.AURRPCRequests(package).construct_package())
        except pyur.aur.NotExists:
            print(
                error(f"target not found: {package}"),
                file = sys.stderr
            ); return 1

    handler: Handle = pyur.local.create_handler()
    not_utd_packages: list[pyur.aur.AURPackage] = []

    for package in constructed_packages:
        if pyur.aur.is_up_to_date(
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

    build_packages: list[pyur.aur.AURPackage] = []
    remove_packages: set[str] = set()

    for package in not_utd_packages:
        try:
            pyur.local.check_for_conflicts(
                handler,
                package
            )
        except pyur.local.Conflicts as e:
            choice: str = input(conflict(
                package,
                e._name,
                e._version
            )).strip().lower()
            if choice and choice != "y":
                print(
                    error("unresolvable package conflicts detected"),
                    file = sys.stderr
                ); print(
                    error("failed to prepare transaction (conflicting dependencies)"),
                    file = sys.stderr
                    ); print(info(f"{package.name}-{package.version} and {e._name}-{e._version} are in conflict"))
                return 1
            remove_packages.add(e._name)
        build_packages.append(package)

    aur_seen: set[str] = set()
    _build_order: list[pyur.aur.AURPackage] = []
    sync_dependencies: set[tuple[str, str]] = set()

    for package in build_packages:
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
        sync_order(
            handler,
            package,
            sync_seen,
            _sync_order
        )

    for line in VerbosePkgList(
        _build_order,
        _sync_order,
        remove_packages
    ):
        print(line)

    confirm: str = input(info(f"Proceed with installation? [Y/n] ")).strip().lower()
    if confirm and confirm != "y":
        return 1

    if remove_packages:
        return_code: int = pyur.pacman.call(
            "R",
            list(remove_packages),
            8 + len(remove_packages)
        )
        if return_code != 0:
            return return_code

    if _sync_order:
        return_code: int = pyur.pacman.call(
            "S",
            [f"{i[0]}/{i[1]}" for i in _sync_order],
            10 + len(_sync_order)
        )
        if return_code != 0:
            return return_code

    os.makedirs(
        CACHE_PATH,
        exist_ok = True
    )

    plan: list[str] = retrieve_pkgbuilds(
        _build_order,
        CACHE_PATH
    )

    print(info(f"Building and installing PKGBUILDs..."))
    for package in _build_order:
        compiled_packages: list[str] = glob.glob(f"{CACHE_PATH}/{package.name}/{package.name}*.pkg.tar.zst")
        if not compiled_packages or package.name in plan:
            print(f"building {package.name}...")
            proc: subprocess.CompletedProcess = subprocess.run(
                ["makepkg", "--noconfirm"],
                cwd = f"{CACHE_PATH}/{package.name}"
            )
            if proc.returncode != 0:
                return proc.returncode
            compiled_packages: list[str] = glob.glob(f"{CACHE_PATH}/{package.name}/{package.name}*.pkg.tar.zst")
        return_code: int = pyur.pacman.call(
            "U",
            compiled_packages,
            10 + len(compiled_packages)
        )
        if return_code != 0:
            return return_code

    return 0

def _launch() -> None:
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupt signal received")
        sys.exit(130)

if __name__ == "__main__":
    _launch()
