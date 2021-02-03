import io
import re
import typing as T

import pytest

from crcmanip.algorithm import (
    InvalidPositionError,
    apply_patch,
    compute_patch,
    consume,
    consume_reverse,
)
from crcmanip.crc import BaseCRC


@pytest.mark.parametrize("crc_cls", BaseCRC.__subclasses__())
@pytest.mark.parametrize("start_pos", [None, 1, 2, 8, 9])
@pytest.mark.parametrize("end_pos", [None, 1, 2, 8, 9])
@pytest.mark.parametrize("chunk_size", [1, 2, 8, 9, 100])
def test_consume(
    crc_cls: T.Type[BaseCRC],
    start_pos: T.Optional[int],
    end_pos: T.Optional[int],
    chunk_size: int,
) -> None:
    test_string = b"123456789"
    crc = crc_cls()
    with io.BytesIO() as handle:
        handle.write(test_string)
        consume(crc, handle, start_pos, end_pos, chunk_size=chunk_size)

        if start_pos and end_pos and start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos
        expected_digest = (
            crc_cls().update(test_string[start_pos:end_pos]).digest()
        )

        assert crc.digest() == expected_digest


@pytest.mark.parametrize("crc_cls", BaseCRC.__subclasses__())
@pytest.mark.parametrize("start_pos", [None, 1, 2, 8, 9])
@pytest.mark.parametrize("end_pos", [None, 1, 2, 8, 9])
@pytest.mark.parametrize("chunk_size", [1, 2, 8, 9, 100])
def test_consume_reverse(
    crc_cls: T.Type[BaseCRC],
    start_pos: T.Optional[int],
    end_pos: T.Optional[int],
    chunk_size: int,
) -> None:
    test_string = b"123456789"
    crc = crc_cls()
    with io.BytesIO() as handle:
        handle.write(test_string)
        consume_reverse(crc, handle, start_pos, end_pos, chunk_size=chunk_size)

        if start_pos and end_pos and start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos
        expected_digest = (
            crc.reset().update_reverse(test_string[start_pos:end_pos]).digest()
        )

        assert crc.digest() == expected_digest


@pytest.mark.parametrize("crc_cls", BaseCRC.__subclasses__())
@pytest.mark.parametrize("overwrite", (False, True))
@pytest.mark.parametrize("target_pos", [0, 100, 896, 897, 898, 899, 900])
def test_apply_patch_digest(
    crc_cls: T.Type[BaseCRC],
    overwrite: bool,
    target_pos: int,
) -> None:
    test_string = b"123456789" * 100
    test_digest = 0xDEADBEEF & ((1 << crc_cls.num_bits) - 1)

    with io.BytesIO() as input_handle, io.BytesIO() as output_handle:
        input_handle.write(test_string)

        apply_patch(
            crc_cls(),
            test_digest,
            input_handle,
            output_handle,
            target_pos=target_pos,
            overwrite=overwrite,
        )

        output_handle.seek(0)
        actual_digest = crc_cls().update(output_handle.read()).digest()
        assert actual_digest == test_digest


@pytest.mark.parametrize("crc_cls", BaseCRC.__subclasses__())
@pytest.mark.parametrize("overwrite", (False, True))
@pytest.mark.parametrize("target_pos", [0, 100, 896, 897, 898, 899, 900])
def test_apply_patch_output(
    crc_cls: T.Type[BaseCRC], overwrite: bool, target_pos: int
) -> None:
    test_string = b"123456789" * 100
    test_digest = 0

    with io.BytesIO() as input_handle, io.BytesIO() as output_handle:
        input_handle.write(test_string)

        apply_patch(
            crc_cls(),
            test_digest,
            input_handle,
            output_handle,
            target_pos=target_pos,
            overwrite=overwrite,
        )

        expected_output_re = (
            test_string[:target_pos]
            + b"." * (crc_cls.num_bits // 8)
            + test_string[
                target_pos + crc_cls.num_bits // 8
                if overwrite
                else target_pos :
            ]
        )

        output_handle.seek(0, io.SEEK_SET)
        actual_output = output_handle.read()

        assert re.match(expected_output_re, actual_output, flags=re.DOTALL)


def test_compute_patch_invalid_pos(any_crc: BaseCRC) -> None:
    with io.BytesIO() as handle:
        handle.write(b"123")
        with pytest.raises(InvalidPositionError):
            compute_patch(any_crc, handle, 0x00000000, -1, False)
        with pytest.raises(InvalidPositionError):
            compute_patch(any_crc, handle, 0x00000000, 4, False)


def test_apply_patch_invalid_pos(any_crc: BaseCRC) -> None:
    with io.BytesIO() as input_handle, io.BytesIO() as output_handle:
        input_handle.write(b"123")
        with pytest.raises(InvalidPositionError):
            apply_patch(
                any_crc, 0x00000000, input_handle, output_handle, -1, False
            )
        with pytest.raises(InvalidPositionError):
            apply_patch(
                any_crc, 0x00000000, input_handle, output_handle, 4, False
            )
