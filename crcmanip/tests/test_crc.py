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
    "crc_cls,test_string,expected_digest,expected_raw_value",
    [
        (CRC32, b"123456789", "CBF43926", 0x340BC6D9),
        (CRC32POSIX, b"123456789", "377A6011", 0x89A1897F),
        (CRC16CCITT, b"123456789", "2189", 0x2189),
        (CRC16XMODEM, b"123456789", "31C3", 0x31C3),
        (CRC16IBM, b"123456789", "BB3D", 0xBB3D),
    ],
)
def test_update(
    crc_cls: T.Type[BaseCRC],
    test_string: bytes,
    expected_digest: str,
    expected_raw_value: int,
) -> None:
    crc = crc_cls()
    crc.update(test_string)
    assert crc.digest() == int(expected_digest, 16)
    assert crc.hex_digest() == expected_digest
    assert crc.raw_value == expected_raw_value


def test_reset(any_crc: BaseCRC) -> None:
    test_string = b"123"
    any_crc.update(test_string)
    initial_checksum = any_crc.digest()
    any_crc.update(test_string)
    assert any_crc.digest() != initial_checksum
    any_crc.reset()
    any_crc.update(test_string)
    assert any_crc.digest() == initial_checksum


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
