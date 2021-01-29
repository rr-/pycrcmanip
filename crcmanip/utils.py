import typing as T

from tqdm import tqdm

PROGRESSBARS_ENABLED = True


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


def disable_progressbars() -> None:
    global PROGRESSBARS_ENABLED
    PROGRESSBARS_ENABLED = False


def track_progress(*args: T.Any, **kwargs: T.Any) -> tqdm:
    global PROGRESSBARS_ENABLED
    return tqdm(
        *args,
        disable=None if PROGRESSBARS_ENABLED else True,
        unit="B",
        unit_divisor=1024,
        unit_scale=True,
        bar_format=(
            "{desc:<10} {percentage:3.0f}%|{bar:25}| "
            "{n_fmt}{unit}/{total_fmt}{unit} [{elapsed}<{remaining}]"
        ),
        **kwargs,
    )
