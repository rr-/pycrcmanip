import argparse
import io
import typing as T
from pathlib import Path

from crcmanip.algorithm import apply_patch, consume
from crcmanip.crc import BaseCRC
from crcmanip.utils import disable_progressbars

CRC_FACTORY = {cls.__name__: cls() for cls in BaseCRC.__subclasses__()}


class DictAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: T.Any,
        option_string: T.Optional[str] = None,
    ) -> None:
        assert isinstance(self.choices, dict)
        setattr(namespace, self.dest, self.choices.get(values, self.default))


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
        parser.add_argument(
            "path", type=Path, help="file to calculate the checksum for"
        )

    def run(self, args: argparse.Namespace) -> None:
        crc = args.algorithm
        with args.path.open("rb") as handle:
            consume(crc, handle)
        print(crc.hex_digest())


class PatchCommand(BaseCommand):
    names = ["patch"]
    description = "patch CRC checksum"

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "input_path", metavar="PATH", type=Path, help="input file to patch"
        )
        parser.add_argument(
            "target_checksum",
            metavar="CHECKSUM",
            type=lambda x: int(x, 16),
            help="target checksum in hex",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-o",
            "--output",
            dest="output_path",
            metavar="PATH",
            type=Path,
            help="path to the output file",
        )
        group.add_argument(
            "-b",
            "--backup",
            action="store_true",
            help="create a backup of the original file",
        )
        parser.add_argument(
            "-O",
            "--overwrite",
            action="store_true",
            help="overwrite existing bytes in the path",
        )
        parser.add_argument(
            "-P",
            "--pos",
            dest="target_pos",
            metavar="POS",
            type=int,
            help="position to apply the patch at",
        )

    def run(self, args: argparse.Namespace) -> None:
        crc = args.algorithm
        input_path = args.input_path
        output_path = (
            args.output_path
            if args.output_path
            else input_path.with_suffix(input_path.suffix + ".tmp")
        )

        with input_path.open("rb") as input_handle, output_path.open(
            "wb"
        ) as output_handle:
            input_handle.seek(0, io.SEEK_END)
            file_size = input_handle.tell()

            if args.target_pos is not None:
                target_pos = args.target_pos
            else:
                target_pos = file_size
                if args.overwrite:
                    target_pos -= crc.num_bytes
                    if target_pos < 0:
                        target_pos = 0
            while target_pos < 0:
                target_pos += file_size

            apply_patch(
                crc,
                args.target_checksum,
                input_handle,
                output_handle,
                target_pos=target_pos,
                overwrite=args.overwrite,
            )

        if not args.output_path:
            if args.backup:
                input_path.rename(
                    input_path.with_suffix(input_path.suffix + ".bak")
                )
            else:
                input_path.unlink()
            output_path.rename(input_path)


def parse_args(args: T.Optional[T.List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--algorithm",
        action=DictAction,
        choices=CRC_FACTORY,
        default=CRC_FACTORY[list(CRC_FACTORY.keys())[0]],
    )
    parser.add_argument(
        "-q", "--quiet", help="disable progressbars", action="store_true"
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

    return parser.parse_args(args)


def main(args: T.Optional[T.List[str]] = None) -> None:
    parsed_args = parse_args(args)
    if parsed_args.quiet:
        disable_progressbars()
    parsed_args.command_cls.run(parsed_args)
