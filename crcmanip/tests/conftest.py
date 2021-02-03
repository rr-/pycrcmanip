import pytest

from crcmanip.crc import BaseCRC


@pytest.fixture
def any_crc() -> BaseCRC:
    return BaseCRC.__subclasses__()[0]()
