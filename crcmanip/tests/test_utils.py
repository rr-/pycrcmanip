import io
import typing as T

import pytest

from crcmanip.crc import CRC32
from crcmanip.utils import compute_checksum


@pytest.mark.parametrize(
    "start_pos,end_pos", [(0, None), (1, None), (0, 9), (0, 8)]
)
def test_compute_checksum(start_pos: int, end_pos: T.Optional[int]) -> None:
    test_string = b"123456789"
    crc = CRC32()
    with io.BytesIO() as handle:
        handle.write(test_string)
        assert (
            compute_checksum(crc, handle, start_pos, end_pos)
            == CRC32().update(test_string[start_pos:end_pos]).digest()
        )
