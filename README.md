**WARNING: This is a personal (and fun) project. Bugs will get un-fixed. If it works for me, i will ignore it.**

# pyur
An AUR helper that tries to replicate exactly how `pacman` output.

# Installation
```
$ cd ~
$ git clone https://github.com/a5-truongdz/pyur.git
$ cd pyur
$ pip install --user .
```

# Usage
1. Installing packages:
```
$ python main.py [packages]
```
2. Uninstalling packages: Please use `pacman -R` itself.
3. Clear cache:
```
$ rm -r ~/.cache/pyur
```

# TODO
- Update/Upgrade
- Performance improve
