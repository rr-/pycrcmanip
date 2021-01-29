import io
import typing as T

from crcmanip.crc import BaseCRC
from crcmanip.utils import num_to_bytes, swap_endian

DEFAULT_CHUNK_SIZE = 1024 * 1024


class InvalidPositionError(ValueError):
    def __init__(self) -> None:
        super().__init__("patch position is located outside available input")


def fix_start_end_pos(
    start_pos: T.Optional[int], end_pos: T.Optional[int], handle: T.IO[bytes]
) -> T.Tuple[int, int]:
    if start_pos is None:
        start_pos = 0
    if end_pos is None:
        old_pos = handle.tell()
        handle.seek(0, io.SEEK_END)
        end_pos = handle.tell()
        handle.seek(old_pos, io.SEEK_SET)

    if start_pos > end_pos:
        end_pos, start_pos = start_pos, end_pos
    assert start_pos >= 0
    assert end_pos >= 0
    assert start_pos <= end_pos
    return start_pos, end_pos


def consume(
    crc: BaseCRC,
    handle: T.IO[bytes],
    start_pos: T.Optional[int] = None,
    end_pos: T.Optional[int] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> None:
    start_pos, end_pos = fix_start_end_pos(start_pos, end_pos, handle)
    if start_pos == end_pos:
        return

    handle.seek(start_pos, io.SEEK_SET)
    remaining = end_pos - start_pos
    while remaining:
        chunk_size = min(chunk_size, remaining)
        chunk = handle.read(chunk_size)
        crc.update(chunk)
        remaining -= chunk_size


def consume_reverse(
    crc: BaseCRC,
    handle: T.IO[bytes],
    start_pos: T.Optional[int],
    end_pos: T.Optional[int],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> None:
    start_pos, end_pos = fix_start_end_pos(start_pos, end_pos, handle)
    if start_pos == end_pos:
        return

    remaining = end_pos - start_pos
    while remaining:
        chunk_size = min(chunk_size, remaining)
        handle.seek(start_pos + remaining - chunk_size, io.SEEK_SET)
        chunk = handle.read(chunk_size)
        crc.update_reverse(chunk)
        remaining -= chunk_size


def compute_patch(
    crc: BaseCRC,
    handle: T.IO[bytes],
    target_checksum: int,
    target_pos: int,
    overwrite: bool,
) -> int:
    handle.seek(0, io.SEEK_END)
    orig_file_size = handle.tell()
    if target_pos < 0 or target_pos > orig_file_size:
        raise InvalidPositionError

    if overwrite:
        target_file_size = orig_file_size
        if target_pos + crc.num_bytes > orig_file_size:
            target_file_size = target_pos + crc.num_bytes
    else:
        target_file_size = orig_file_size + crc.num_bytes

    target_checksum ^= crc.final_xor
    if crc.use_file_size:
        target_checksum = crc.get_prev_value(
            num_to_bytes(target_file_size), target_checksum
        )

    pos_start = 0
    pos_before_patch = target_pos
    pos_after_patch = target_pos + (crc.num_bytes if overwrite else 0)
    pos_end = orig_file_size

    crc.reset(raw_value=crc.initial_xor)
    consume(crc, handle, pos_start, pos_before_patch)
    checksum1 = crc.raw_value

    crc.reset(raw_value=target_checksum)
    consume_reverse(crc, handle, pos_end, pos_after_patch)
    checksum2 = crc.raw_value

    if crc.big_endian:
        checksum1 = swap_endian(checksum1, crc.num_bits)

    patch = crc.get_prev_value(
        num_to_bytes(checksum1, crc.num_bytes), checksum2
    )
    if crc.big_endian:
        patch = swap_endian(patch, crc.num_bits)

    return patch


def apply_patch(
    crc: BaseCRC,
    target_checksum: int,
    input_handle: T.IO[bytes],
    output_handle: T.IO[bytes],
    target_pos: int,
    overwrite: bool,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> None:
    patch = compute_patch(
        crc, input_handle, target_checksum, target_pos, overwrite=overwrite
    )

    input_handle.seek(0, io.SEEK_END)
    end_pos = input_handle.tell()
    input_handle.seek(0, io.SEEK_SET)
    pos = input_handle.tell()

    if target_pos < 0 or target_pos > end_pos:
        raise InvalidPositionError

    # output first half
    while pos < target_pos:
        chunk_size = min(chunk_size, target_pos - input_handle.tell())
        chunk = input_handle.read(chunk_size)
        output_handle.write(chunk)
        pos += chunk_size

    # output patch
    output_handle.write(num_to_bytes(patch, crc.num_bytes))
    if overwrite:
        pos += crc.num_bytes
        input_handle.seek(pos, io.SEEK_SET)

    # output second half
    while pos < end_pos:
        chunk_size = min(chunk_size, end_pos - input_handle.tell())
        chunk = input_handle.read(chunk_size)
        output_handle.write(chunk)
        pos += chunk_size
