from subprocess import Popen
from pty import openpty
from os import close, read
from shutil import get_terminal_size
from struct import pack
from fcntl import ioctl
from termios import TIOCSWINSZ

def call(
    _action: str,
    _package_list: list[str],
    _skip: int
) -> int:
    """
    Calls `pacman` (in a PTY for colors) with the specified _action and _package_list, skipping _skip first lines.

    Parameters:
        _action: "S", "R" or "U".
        _package_list: The package list.
        _skip: How many lines to skip.

    Returns:
        int.
    """

    _master, _slave = openpty()
    _cols, _rows = get_terminal_size()
    ioctl(
        _slave,
        TIOCSWINSZ,
        pack(
            "HHHH",
            _rows,
            _cols,
            0,
            0
        )
    ); _proc: Popen = Popen(
        ["sudo", "pacman", f"-{_action}", "--noconfirm", "--noprogressbar", "--disable-download-timeout"] + _package_list,
        stdout=_slave,
        stderr=_slave,
        stdin=_slave,
        close_fds=True
    ); close(_slave)
    _skipped = 0
    _buffer = b""
    while True:
        try:
            data = read(
                _master,
                1024
            )
            if not data:
                break
            _buffer += data
            while b"\n" in _buffer:
                line, _buffer = _buffer.split(b"\n", 1)
                if _skipped < _skip:
                    _skipped += 1
                    continue
                print(
                    f"{line.decode(errors='ignore')}\n",
                    end=""
                )
        except OSError:
            break
    _proc.wait()
    return _proc.returncode
