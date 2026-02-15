import aur
from pyalpm import Handle, find_satisfier, Package, DB
from local import is_locally_installed

def better_find_satisfier(
    _handler: Handle,
    _query: str
) -> tuple[str, str]:
    """
    Returns the package provided the query.

    Parameters:
        _handler: A handler created from local.create_handler()
        _query: The query
    """

    for database in _handler.get_syncdbs():
        _package: Package | None = find_satisfier(
            database.pkgcache,
            _query
        )
        if _package is not None:
            return (database.name, _package.name)
    return ("", "")    # Unreachable, i believe in ALPM =D

def build_order(
    _handler: Handle,
    _package: aur.AURPackage,
    _seen: set[str],
    _build_order: list[aur.AURPackage],
    _sync_dependencies: set[tuple[str, str]]
) -> None:
    """
    Generates a build order for an AUR package.

    Parameters:
        _handler: A handler created from local.create_handler().
        _package: The AUR package.
        _seen: A set of seen packages.
        _build_order: The build order.
        _sync_dependencies: The sync dependencies.
    """

    if _package.name in _seen:
        return
    _seen.add(_package.name)
    for dependency in _package.dependencies:
        try:
            _dependency_package: aur.AURPackage = aur.AURRPCRequests(dependency).construct_package()
        except aur.NotExists:
            _name: tuple[str, str] = better_find_satisfier(
                _handler,
                dependency
            )
            if not is_locally_installed(
                _handler,
                _name[1]
            ):
                _sync_dependencies.add(_name)
            continue
        build_order(
            _handler,
            _dependency_package,
            _seen,
            _build_order,
            _sync_dependencies
        )
    _build_order.append(_package)

def get_database(
    _handler: Handle,
    _database_name: str
) -> DB:
    """
    Find the database with the name given.

    Parameters:
        _handler: A handler created from local.create_handler().
        _database_name: The database name.

    Returns:
        alpm.DB.
    """

    for database in _handler.get_syncdbs():
        if database.name == _database_name:
            return database

def sync_order(
    _handler: Handle,
    _package: tuple[str, str],
    _seen: set[str],
    _sync_order: list[tuple[str, str]]
) -> None:
    """
    Recursively find sync dependencies and build install order.

    Parameters:
        _handler: A handler created from local.create_handler().
        _package: The package.
        _seen: A set of seen packages.
        _sync_order: The sync order.
    """

    db_name, pkg_name = _package

    if pkg_name in _seen:
        return
    _seen.add(pkg_name)
    db = get_database(
        _handler,
        db_name
    ); pkg = db.get_pkg(pkg_name)
    for dependency in pkg.depends:
        if is_locally_installed(
            _handler,
            dependency
        ):
            continue
        provider = better_find_satisfier(
            _handler,
            dependency
        )
        if not is_locally_installed(
            _handler,
            provider[1]
        ):
            sync_order(
                _handler,
                provider,
                _seen,
                _sync_order
            )

    _sync_order.append(_package)
