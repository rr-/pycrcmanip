import io
import typing as T

from crcmanip.crc import BaseCRC


def compute_checksum(
    crc: BaseCRC,
    handle: T.IO[bytes],
    start_pos: int,
    end_pos: T.Optional[int],
    chunk_size=1024 * 1024,
) -> int:
    handle.seek(start_pos, io.SEEK_SET)
    while True:
        if end_pos is not None:
            if handle.tell() >= end_pos:
                break
            chunk_size = min(chunk_size, end_pos - handle.tell())
        chunk = handle.read(chunk_size)
        if not chunk:
            break
        crc.update(chunk)
    return crc.digest()
