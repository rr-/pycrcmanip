import io
import typing as T

from crcmanip.crc import BaseCRC

DEFAULT_CHUNK_SIZE = 1024 * 1024


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
    handle.seek(start_pos or 0, io.SEEK_SET)
    while True:
        if handle.tell() >= end_pos:
            break
        chunk_size = min(chunk_size, end_pos - handle.tell())
        chunk = handle.read(chunk_size)
        if not chunk:
            break
        crc.update(chunk)
