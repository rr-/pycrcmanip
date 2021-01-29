import argparse
import sys
from pathlib import Path

from crcmanip.crc import BaseCRC
from crcmanip.algorithm import consume

CRC_FACTORY = {cls.__name__: cls() for cls in BaseCRC.__subclasses__()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "-a",
        "--algorithm",
        choices=list(CRC_FACTORY.keys()),
        default=list(CRC_FACTORY.keys())[0],
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    crc = CRC_FACTORY[args.algorithm]

    with args.path.open("rb") as handle:
        consume(crc, handle)

    print(crc.hex_digest())


if __name__ == "__main__":
    main()
