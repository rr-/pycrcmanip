import typing as T


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


def num_to_bytes(val: int, num_bytes: T.Optional[int] = None) -> bytes:
    ret: T.List[int] = []
    if num_bytes:
        for _i in range(num_bytes):
            ret.append(val & 0xFF)
            val >>= 8
    else:
        while val:
            ret.append(val & 0xFF)
            val >>= 8
    return bytes(ret)
