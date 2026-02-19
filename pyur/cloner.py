from pyur.aur import AURPackage
from enum import Enum
from pyur.cosmetics import info

import git
import os

class RepoAction(Enum):
    NONE = 0
    CLONE = 1
    UPDATE = 2

def is_repo_up_to_date(
    _repo: git.Repo
) -> bool:
    """
    Checks if a repository is up-to-date.

    Parameters;
        _repo: The repository.

    Returns:
        bool.
    """

    _repo.remotes.origin.fetch()
    return _repo.head.commit == _repo.active_branch.tracking_branch().commit    # type: ignore

def is_a_valid_git_repo(
    _path: str
) -> bool:
    """
    Checks if the path specified is a valid Git repository.

    Parameters;
        _path: The path.

    Returns:
        bool.
    """
    
    try:
        git.Repo(_path)
    except git.InvalidGitRepositoryError:
        return False
    return True

def get_repo_action(
    _package_name: str,
    _cache_path: str
) -> RepoAction:
    """
    Plans the action for the package.

    Parameters:
        _package_name: The package name.
        _cache_path: The cache path.

    Returns:
        RepoAction.*.
    """

    _path: str = f"{_cache_path}/{_package_name}"
    if os.path.exists(_path):
        if is_a_valid_git_repo(_path):
            _repo: git.Repo = git.Repo(_path)
            if is_repo_up_to_date(_repo):
                return RepoAction.NONE
            return RepoAction.UPDATE
    return RepoAction.CLONE


def apply_repo_action(
    _package_name: str,
    _cache_path: str,
    _action: RepoAction
) -> None:
    """
    Apply the action to the package.

    Parameters:
        _package_name: The package name.
        _cache_path: The cache path.
        _action: The action.
    """

    _path: str = f"{_cache_path}/{_package_name}"
    if _action == RepoAction.UPDATE:
        _repo: git.Repo = git.Repo(_path)
        _repo.remotes.origin.pull()
    elif _action == RepoAction.CLONE:
        git.Repo.clone_from(
            f"https://aur.archlinux.org/{_package_name}.git",
            _path
        )

def retrieve_pkgbuilds(
    _package_list: list[AURPackage],
    _cache_path: str
) -> None | list[AURPackage]:
    """
    Retrieves PKGBUILDs with proper `pacman`-like output.

    Parameters:
        _package_list: The package list.
        _cache_path: The cache path.

    Returns:
        None | list[AURPackage].
    """

    _plan: list[tuple[AURPackage, RepoAction]] = []
    for _package in _package_list:
        _action = get_repo_action(
            _package.name,
            _cache_path
        )
        if _action != RepoAction.NONE:
            _plan.append((_package, _action))
    if not _plan:
        return
    print(info("Retrieving PKGBUILDs..."))
    for _package, _action in _plan:
        print(f" {_package.name}-{_package.version} downloading...")
        apply_repo_action(
            _package.name,
            _cache_path,
            _action
        )
    return [package[0] for package in _plan]
