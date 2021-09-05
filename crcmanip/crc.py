import typing as T
from functools import lru_cache

from crcmanip.fastcrc import crc_next, crc_prev
from crcmanip.utils import get_polynomial_reverse, swap_endian


@lru_cache
def create_lookup_table(
    poly: int, num_bits: int, big_endian: bool
) -> T.Tuple[int, ...]:
    poly_rev = get_polynomial_reverse(poly, num_bits)
    mask = 1 << (num_bits - 1)
    table = [0] * 0x100

    for num in range(0x100):
        val = num
        if big_endian:
            val = swap_endian(val, num_bits)
        for _bit in range(8):
            if big_endian:
                val = (val << 1) ^ poly if val & mask else (val << 1)
            else:
                val = (val >> 1) ^ poly_rev if val & 1 else (val >> 1)
        table[num] = val & ((1 << num_bits) - 1)

    return tuple(table)


@lru_cache
def create_reverse_lookup_table(
    poly: int, num_bits: int, big_endian: bool
) -> T.Tuple[int, ...]:
    poly_rev = get_polynomial_reverse(poly, num_bits)
    mask = 1 << (num_bits - 1)
    table = [0] * 0x100

    for num in range(0x100):
        val = num
        if not big_endian:
            val = swap_endian(val, num_bits)
        for _bit in range(8):
            if big_endian:
                val = ((val ^ poly) >> 1) | mask if val & 1 else (val >> 1)
            else:
                val = ((val ^ poly_rev) << 1) | 1 if val & mask else (val << 1)
        if big_endian:
            val ^= swap_endian(num, num_bits)
        table[num] = val & ((1 << num_bits) - 1)

    return tuple(table)


class BaseCRC:
    num_bits: int = NotImplemented
    polynomial: int = NotImplemented
    initial_xor: int = 0
    final_xor: int = 0
    big_endian: bool = False
    use_file_size: bool = False

    def __init__(self) -> None:
        assert self.num_bits % 8 == 0
        self.num_bytes = self.num_bits // 8

        self.lookup_table = create_lookup_table(
            self.polynomial, self.num_bits, self.big_endian
        )
        self.lookup_table_reverse = create_reverse_lookup_table(
            self.polynomial, self.num_bits, self.big_endian
        )

        self._value = self.initial_xor
        self._consumed = 0

    def reset(self, raw_value: T.Optional[int] = None) -> "BaseCRC":
        self._value = raw_value if raw_value is not None else self.initial_xor
        self._consumed = 0
        return self

    def update(self, source: bytes) -> "BaseCRC":
        self._value = self.get_next_value(source, self._value) & (
            (1 << self.num_bits) - 1
        )
        self._consumed += len(source)
        return self

    def update_reverse(self, source: bytes) -> "BaseCRC":
        self._value = self.get_prev_value(source, self._value) & (
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
            value = self.get_next_value(bytes(patch), value)

        value ^= self.final_xor
        value &= (1 << self.num_bits) - 1
        return value

    def hex_digest(self) -> str:
        return "%0*X" % (self.num_bytes * 2, self.digest())

    def get_prev_value(self, source: bytes, value: int) -> int:
        return T.cast(int, crc_prev(self, source, value))

    def get_next_value(self, source: bytes, value: int) -> int:
        return T.cast(int, crc_next(self, source, value))

    @property
    def raw_value(self) -> int:
        return self._value


class CRC32(BaseCRC):
    num_bits = 32
    polynomial = 0x04C11DB7
    initial_xor = 0xFFFFFFFF
    final_xor = 0xFFFFFFFF


class CRC32POSIX(BaseCRC):
    num_bits = 32
    polynomial = 0x04C11DB7
    final_xor = 0xFFFFFFFF
    big_endian = True
    use_file_size = True


class CRC16CCITT(BaseCRC):
    num_bits = 16
    polynomial = 0x1021


class CRC16XMODEM(BaseCRC):
    num_bits = 16
    polynomial = 0x1021
    big_endian = True


class CRC16IBM(BaseCRC):
    num_bits = 16
    polynomial = 0x8005
