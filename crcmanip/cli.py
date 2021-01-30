import io
import typing as T
from pathlib import Path

import click

from crcmanip.algorithm import apply_patch, consume
from crcmanip.crc import BaseCRC
from crcmanip.utils import disable_progressbars

CRC_FACTORY = {cls.__name__: cls() for cls in BaseCRC.__subclasses__()}


class PathPath(click.Path):
    """A Click path argument that returns a pathlib Path, not a string."""

    def convert(self, value: T.Any, param: T.Any, ctx: T.Any) -> T.Any:
        return Path(super().convert(value, param, ctx))


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option(
    "-a",
    "--algorithm",
    type=click.Choice(CRC_FACTORY.keys(), case_sensitive=False),
    default=list(CRC_FACTORY.keys())[0],
    help="Checksum type.",
)
@click.option("-q", "--quiet", help="Disable progressbars.", is_flag=True)
@click.argument("path", type=PathPath(exists=True, dir_okay=False))
def calc(algorithm: str, quiet: bool, path: Path) -> None:
    """Print the checksum of a given PATH to the standard output."""
    if quiet:
        disable_progressbars()
    crc = CRC_FACTORY[algorithm]
    with path.open("rb") as handle:
        consume(crc, handle)
    click.echo(crc.hex_digest())


@cli.command()
@click.option(
    "-a",
    "--algorithm",
    type=click.Choice(CRC_FACTORY.keys(), case_sensitive=False),
    default=list(CRC_FACTORY.keys())[0],
    help="Checksum type.",
)
@click.option("-q", "--quiet", help="Disable progressbars.", is_flag=True)
@click.argument("input_path", type=PathPath(exists=True, dir_okay=False))
@click.argument("target_checksum", type=lambda x: int(x, 16))
@click.option(
    "-o",
    "--output",
    "output_path",
    type=PathPath(exists=False, writable=True, dir_okay=False),
    help="Path to the output file.",
)
@click.option(
    "-b",
    "--backup",
    is_flag=True,
    help="Create a backup of the original file.",
)
@click.option(
    "-O",
    "--overwrite",
    is_flag=True,
    help="Overwrite existing bytes in the path.",
)
@click.option(
    "-P",
    "--pos",
    "target_pos",
    type=int,
    help="Position to apply the patch at.",
)
def patch(
    algorithm: str,
    quiet: bool,
    input_path: Path,
    target_checksum: int,
    output_path: T.Optional[Path],
    backup: bool,
    overwrite: bool,
    target_pos: T.Optional[int],
) -> None:
    """Patch the INPUT_PATH so that its checksum becomes TARGET_CHECKSUM.

    TARGET_CHECKSUM must be a valid hexadecimal value.
    """
    crc = CRC_FACTORY[algorithm]
    output_path_provided = output_path is not None
    if not output_path_provided:
        output_path = input_path.with_suffix(input_path.suffix + ".tmp")

    assert input_path
    assert output_path
    with input_path.open("rb") as input_handle, output_path.open(
        "wb"
    ) as output_handle:
        input_handle.seek(0, io.SEEK_END)
        file_size = input_handle.tell()

        if target_pos is None:
            target_pos = file_size
            if overwrite:
                target_pos -= crc.num_bytes
                if target_pos < 0:
                    target_pos = 0
        while target_pos < 0:
            target_pos += file_size

        apply_patch(
            crc,
            target_checksum,
            input_handle,
            output_handle,
            target_pos=target_pos,
            overwrite=overwrite,
        )

    if not output_path_provided:
        if backup:
            input_path.rename(
                input_path.with_suffix(input_path.suffix + ".bak")
            )
        else:
            input_path.unlink()
        output_path.rename(input_path)
