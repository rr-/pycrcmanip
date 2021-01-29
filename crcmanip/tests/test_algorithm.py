import io
import typing as T

import pytest

from crcmanip.algorithm import consume
from crcmanip.crc import CRC32


@pytest.mark.parametrize("start_pos", [None, 1, 2, 8, 9])
@pytest.mark.parametrize("end_pos", [None, 1, 2, 8, 9])
def test_consume(start_pos: T.Optional[int], end_pos: T.Optional[int]) -> None:
    test_string = b"123456789"
    crc = CRC32()
    with io.BytesIO() as handle:
        handle.write(test_string)
        consume(crc, handle, start_pos, end_pos)

        if (
            start_pos is not None
            and end_pos is not None
            and start_pos > end_pos
        ):
            start_pos, end_pos = end_pos, start_pos

        assert (
            crc.digest()
            == CRC32().update(test_string[start_pos:end_pos]).digest()
        )
