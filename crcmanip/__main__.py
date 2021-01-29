import argparse

from crcmanip.cli import BaseCommand, DictAction
from crcmanip.crc import BaseCRC

CRC_FACTORY = {cls.__name__: cls() for cls in BaseCRC.__subclasses__()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--algorithm",
        action=DictAction,
        choices=CRC_FACTORY,
        default=CRC_FACTORY[list(CRC_FACTORY.keys())[0]],
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
