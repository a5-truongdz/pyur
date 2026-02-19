from argparse import ArgumentParser, Namespace
from pyur.cosmetics import error
import sys

def parse_arguments() -> list[str]:
    """
    Parses the argument(s) as package(s), and returns a list of parsed package(s).

    Behaviours:
        When -h/--help is provided:
            Print custom help page, then exit.

        When no package/argument is provided:
            Print an error and exit with a non-zero exit code.

    Returns:
        list[str].
    """

    _parser: ArgumentParser = ArgumentParser(add_help = False)
    _parser.add_argument(
        "packages",
        nargs = "*",
        type = str
    ); _parser.add_argument(
        "-h", "--help",
        action = "store_true"
    ); _parser.add_argument(
        "-v", "--version",
        action = "store_true"
    ); _args: Namespace = _parser.parse_args()
    
    if _args.version:
        print("v1.1")
        sys.exit()

    if _args.help:
        print("""usage:  pyur [operation] <package(s)>
operation:
    pyur {-h --help}"

use 'pyur {-h --help}' with an operation for available options"""
        ); sys.exit()

    if not _args.packages:
        print(
            error("no targets specified (use -h for help)"),
            file = sys.stderr
        ); sys.exit(1)

    return _args.packages
