import typing as T

from crcmanip.fastcrc import crc_next
from crcmanip.utils import get_polynomial_reverse, swap_endian


def compute_lookup_table(
    polynomial: int, num_bits: int, big_endian: bool
) -> T.Tuple[int, ...]:
    polynomial_reverse = get_polynomial_reverse(polynomial, num_bits)
    mask = 1 << (num_bits - 1)
    table = [0] * 0x100

    for num in range(0x100):
        value = num
        if big_endian:
            value = swap_endian(value, num_bits)
        for _bit in range(8):
            if big_endian:
                value = (
                    (value << 1) ^ polynomial if value & mask else (value << 1)
                )
            else:
                value = (
                    (value >> 1) ^ polynomial_reverse
                    if value & 1
                    else (value >> 1)
                )
        table[num] = value & ((1 << num_bits) - 1)

    return tuple(table)


def compute_reverse_lookup_table(
    polynomial: int, num_bits: int, big_endian: bool
) -> T.Tuple[int, ...]:
    polynomial_reverse = get_polynomial_reverse(polynomial, num_bits)
    mask = 1 << (num_bits - 1)
    table = [0] * 0x100

    for num in range(0x100):
        value = num
        if not big_endian:
            value = swap_endian(value, num_bits)
        for _bit in range(8):
            if big_endian:
                value = (
                    ((value ^ polynomial) >> 1) | mask
                    if value & 1
                    else (value >> 1)
                )
            else:
                value = (
                    ((value ^ polynomial_reverse) << 1) | 1
                    if value & mask
                    else (value << 1)
                )
        if big_endian:
            value ^= swap_endian(num, num_bits)
        table[num] = value & ((1 << num_bits) - 1)

    return tuple(table)


class BaseCRC:
    def __init__(
        self,
        num_bits: int,
        polynomial: int,
        initial_xor: int = 0,
        final_xor: int = 0,
        big_endian: bool = False,
        use_file_size: bool = False,
    ) -> None:
        self.polynomial = polynomial
        self.polynomial_reverse = get_polynomial_reverse(polynomial, num_bits)
        self.initial_xor = initial_xor
        self.final_xor = final_xor
        self.big_endian = big_endian
        self.use_file_size = use_file_size

        self.num_bits = num_bits
        assert num_bits % 8 == 0
        self.num_bytes = num_bits // 8

        self.lookup_table = compute_lookup_table(
            polynomial, num_bits, big_endian
        )
        self.lookup_table_reverse = compute_reverse_lookup_table(
            polynomial, num_bits, big_endian
        )

        self._value = self.initial_xor
        self._consumed = 0

    def update(self, source: bytes) -> "BaseCRC":
        self._value = self._update(source, self._value) & (
            (1 << self.num_bits) - 1
        )
        self._consumed += len(source)
        return self

    def digest(self) -> int:
        value = self._value

        if self.use_file_size:
            patch = []
            tmp = self._consumed
            while tmp:
                patch.append(tmp & 0xFF)
                tmp >>= 8
            value = self._update(bytes(patch), value)

        value ^= self.final_xor
        value &= (1 << self.num_bits) - 1
        return value

    def hex_digest(self) -> str:
        return "%0*X" % (self.num_bytes * 2, self.digest())

    def _update(self, source: bytes, value: int) -> int:
        return crc_next(self, source, value)


class CRC32(BaseCRC):
    def __init__(self) -> None:
        super().__init__(
            num_bits=32,
            polynomial=0x04C11DB7,
            initial_xor=0xFFFFFFFF,
            final_xor=0xFFFFFFFF,
        )


class CRC32POSIX(BaseCRC):
    def __init__(self) -> None:
        super().__init__(
            num_bits=32,
            polynomial=0x04C11DB7,
            final_xor=0xFFFFFFFF,
            big_endian=True,
            use_file_size=True,
        )


class CRC16CCITT(BaseCRC):
    def __init__(self) -> None:
        super().__init__(num_bits=16, polynomial=0x1021)


class CRC16XMODEM(BaseCRC):
    def __init__(self) -> None:
        super().__init__(num_bits=16, polynomial=0x1021, big_endian=True)


class CRC16IBM(BaseCRC):
    def __init__(self) -> None:
        super().__init__(num_bits=16, polynomial=0x8005)
