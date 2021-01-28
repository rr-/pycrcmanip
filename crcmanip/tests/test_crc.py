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
    "crc,test_string,expected_digest",
    [
        (CRC32, b"123456789", 0xCBF43926),
        (CRC32POSIX, b"123456789", 0x377A6011),
        (CRC16CCITT, b"123456789", 0x2189),
        (CRC16XMODEM, b"123456789", 0x31C3),
        (CRC16IBM, b"123456789", 0xBB3D),
    ],
)
def test_computing(
    crc: BaseCRC, test_string: bytes, expected_digest: int
) -> None:
    assert crc().update(test_string).digest() == expected_digest
