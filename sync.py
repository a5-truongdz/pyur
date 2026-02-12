from pyalpm import Handle, DB

class NotExists(Exception):
    pass

def is_exists_in_repo(
    _package_name: str,
    _repo: DB
) -> bool:
    """
    Checks if the package exists in any repo.

    Parameters:
        _package_name: The package name.
        _repo: A alpm.DB object pointing to the repo.

    Returns:
        bool.
    """

    if _repo.get_pkg(_package_name) is not None:
        return True
    return False

def get_repo(
    _handler: Handle,
    _package_name: str
) -> str:
    """
    Returns the repository of the package.

    Parameters:
        _handler: A handler created from local.create_handler().
        _package_name: The package name.

    Returns:
        str.

    Raises:
        sync.NotExists: When the package doesn't exists in any repository.
    """

    for database in _handler.get_syncdbs():
        if is_exists_in_repo(
            _package_name,
            database
        ):
            return database.name
    raise NotExists()
