import aur
from pyalpm import Handle, find_satisfier, Package
from local import is_locally_installed

def better_find_satisfier(
    _handler: Handle,
    _query: str
) -> str:
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
            return _package.name
    return ""    # Unreachable, i believe in ALPM =D

def build_order(
    _handler: Handle,
    _package: aur.AURPackage,
    _seen: set[str],
    _build_order: list[aur.AURPackage],
    _sync_dependencies: set[str]
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
            _name: str = better_find_satisfier(
                _handler,
                dependency
            )
            if not is_locally_installed(
                _handler,
                _name
            ):
                _sync_dependencies.add(dependency)
            continue
        build_order(
            _handler,
            _dependency_package,
            _seen,
            _build_order,
            _sync_dependencies
        )
    _build_order.append(_package)

