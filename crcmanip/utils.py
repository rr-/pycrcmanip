def get_polynomial_reverse(polynomial: int, num_bits: int) -> int:
    result = 0
    for _i in range(num_bits):
        result <<= 1
        result |= polynomial & 1
        polynomial >>= 1
    return result


def swap_endian(crc: int, num_bits: int) -> int:
    result = 0
    assert num_bits % 8 == 0
    num_bytes = num_bits // 8
    for _i in range(num_bytes):
        result <<= 8
        result |= crc & 0xFF
        crc >>= 8
    return result
