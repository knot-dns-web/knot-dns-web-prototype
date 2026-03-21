import pytest
from beartype import beartype
from beartype.claw import beartype_packages

packages_with_strong_typing = [
    'src.app'
]

def pytest_sessionstart(session):
    import src.backend.src.knot_wrapper.implementation.synchronous
    beartype_packages(packages_with_strong_typing)

def pytest_pyfunc_call(pyfuncitem):
    pyfuncitem.obj = beartype(pyfuncitem.obj)
    return None