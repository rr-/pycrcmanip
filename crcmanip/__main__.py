import argparse
import sys
import typing as T
from pathlib import Path

from crcmanip.algorithm import consume
from crcmanip.crc import BaseCRC

CRC_FACTORY = {cls.__name__: cls() for cls in BaseCRC.__subclasses__()}


class BaseCommand:
    names: T.List[str] = NotImplemented
    description: str = NotImplemented

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        pass

    def run(self, args: argparse.Namespace) -> None:
        raise NotImplementedError("not implemented")


class CalcCommand(BaseCommand):
    names = ["calc"]
    description = "calculate CRC checksum"

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("path", type=Path)

    def run(self, args: argparse.Namespace) -> None:
        crc = CRC_FACTORY[args.algorithm]
        with args.path.open("rb") as handle:
            consume(crc, handle)
        print(crc.hex_digest())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--algorithm",
        choices=list(CRC_FACTORY.keys()),
        default=list(CRC_FACTORY.keys())[0],
    )

    subparsers = parser.add_subparsers(dest="command")
    for command_cls in BaseCommand.__subclasses__():
        command = command_cls()
        subparser = subparsers.add_parser(
            command.names[0],
            aliases=command.names[1:],
            help=command.description,
        )
        subparser.set_defaults(command_cls=command)
        command.decorate_arg_parser(subparser)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.command_cls.run(args)


if __name__ == "__main__":
    main()
