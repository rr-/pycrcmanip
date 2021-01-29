import typing as T

import pytest

from crcmanip.crc import (
    CRC16CCITT,
    CRC16IBM,
    CRC16XMODEM,
    CRC32,
    CRC32POSIX,
    BaseCRC,
)


@pytest.mark.parametrize(
    "crc_cls,test_string,expected_digest",
    [
        (CRC32, b"123456789", 0xCBF43926),
        (CRC32POSIX, b"123456789", 0x377A6011),
        (CRC16CCITT, b"123456789", 0x2189),
        (CRC16XMODEM, b"123456789", 0x31C3),
        (CRC16IBM, b"123456789", 0xBB3D),
    ],
)
def test_update(
    crc_cls: T.Type[BaseCRC], test_string: bytes, expected_digest: int
) -> None:
    actual_digest = crc_cls().update(test_string).digest()
    assert actual_digest == expected_digest


@pytest.mark.parametrize(
    "crc_cls,test_string,expected_digest",
    [
        (CRC32, b"123456789", 0x9A7AC8DB),
        (CRC32POSIX, b"123456789", 0x6041BEBA),
        (CRC16CCITT, b"123456789", 0xF84B),
        (CRC16XMODEM, b"123456789", 0x8544),
        (CRC16IBM, b"123456789", 0x1372),
    ],
)
def test_reverse_update(
    crc_cls: T.Type[BaseCRC], test_string: bytes, expected_digest: int
) -> None:
    actual_digest = crc_cls().update_reverse(test_string).digest()
    assert actual_digest == expected_digest
