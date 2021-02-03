import pytest

from crcmanip import utils


@pytest.mark.parametrize(
    "polynomial,num_bits,expected_polynomial_reverse",
    [
        (0x04C11DB7, 32, 0xEDB88320),
        (0x1021, 16, 0x8408),
        (0x8005, 16, 0xA001),
    ],
)
def test_get_polynomial_reverse(
    polynomial: int, num_bits: int, expected_polynomial_reverse: int
) -> None:
    assert (
        utils.get_polynomial_reverse(polynomial, num_bits)
        == expected_polynomial_reverse
    )


@pytest.mark.parametrize(
    "value,num_bits,expected_value",
    [
        (0b1, 8, 0b1),
        (0b10000000, 8, 0b10000000),
        (0b11100011_11111100, 16, 0b11111100_11100011),
        (0b11100011_11111100_10101010, 24, 0b10101010_11111100_11100011),
    ],
)
def test_swap_endian(value: int, num_bits: int, expected_value: int) -> None:
    assert utils.swap_endian(value, num_bits) == expected_value


@pytest.mark.parametrize(
    "value,num_bytes,expected_bytes",
    [
        (1, 1, bytes([0x01])),
        (500, 1, bytes([500 & 0xFF])),
        (500, 2, bytes([500 & 0xFF, 500 // 0xFF])),
        (500, 0, bytes([500 & 0xFF, 500 // 0xFF])),
    ],
)
def test_num_to_bytes(
    value: int, num_bytes: int, expected_bytes: bytes
) -> None:
    assert utils.num_to_bytes(value, num_bytes) == expected_bytes


def test_disable_progressbars() -> None:
    assert utils.PROGRESSBARS_ENABLED is True
    utils.disable_progressbars()
    assert utils.PROGRESSBARS_ENABLED is False
