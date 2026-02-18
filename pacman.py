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
    _skip: int    # if it works, dont touch it
) -> int:
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
        ["sudo", "pacman", f"-{_action}", "--noconfirm"] + _package_list,
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
