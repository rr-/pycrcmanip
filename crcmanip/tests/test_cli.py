import argparse
import typing as T
from pathlib import Path

import pytest

from crcmanip.cli import main


def test_calc_command(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "file.txt"
    input_path.write_text("hello")

    main(["calc", str(input_path)])
    captured = capsys.readouterr()

    assert captured.out == "3610A686\n"


def test_calc_command_different_alg(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "file.txt"
    input_path.write_text("hello")

    main(["-a", "CRC16IBM", "calc", str(input_path)])
    captured = capsys.readouterr()

    assert captured.out == "34D2\n"


@pytest.mark.parametrize(
    "extra_args,expected_output",
    [
        ([], b"hello\x45\x7E\x34\x30"),
        (["-P", "-1"], b"hell\x56\x4D\xF6\x31o"),
        (["-P", "0"], b"\xA1\x40\x7F\x60hello"),
        (["-P", "1"], b"h\x54\x05\xD8\x8Aello"),
        (["-P", "2"], b"he\x3F\xD8\x54\x34llo"),
        (["-P", "3"], b"hel\x96\x54\x56\x9Elo"),
        (["-P", "4"], b"hell\x56\x4D\xF6\x31o"),
        (["-P", "5"], b"hello\x45\x7E\x34\x30"),
        (["-O"], b"h\x24\xDE\x4F\x97"),
        (["-O", "-P", "-1"], b"hell\x20\xD8\xA2\x1A"),
        (["-O", "-P", "0"], b"\xB5\x4D\x70\x2Do"),
        (["-O", "-P", "1"], b"h\x24\xDE\x4F\x97"),
        (["-O", "-P", "2"], b"he\x44\xBE\x01\xD7"),
        (["-O", "-P", "3"], b"hel\xD8\x29\x2F\xE3"),
        (["-O", "-P", "4"], b"hell\x20\xD8\xA2\x1A"),
        (["-O", "-P", "5"], b"hello\x45\x7E\x34\x30"),
    ],
)
def test_patch_command(
    tmp_path: Path, extra_args: T.List[str], expected_output: bytes
) -> None:
    input_path = tmp_path / "file.txt"
    input_path.write_text("hello")

    main(["patch", str(input_path), "DEADBEEF", *extra_args])

    assert input_path.read_bytes() == expected_output


def test_patch_command_different_alg(tmp_path: Path) -> None:
    input_path = tmp_path / "file.txt"
    input_path.write_text("hello")

    main(["-a", "CRC16IBM", "patch", str(input_path), "DEADBEEF"])

    assert input_path.read_bytes() == b"hello\xBA\x9D"


def test_patch_command_invalid_pos(tmp_path: Path) -> None:
    input_path = tmp_path / "file.txt"
    input_path.write_text("123")

    with pytest.raises(ValueError):
        main(["patch", str(input_path), "DEADBEEF", "-P", "6"])

    main(["patch", str(input_path), "DEADBEEF", "-O"])
    assert input_path.read_bytes() == b"\xC3\xD8\x24\x06"


def test_patch_command_output_file(tmp_path: Path) -> None:
    input_path = tmp_path / "input.txt"
    input_path.write_text("hello")
    output_path = tmp_path / "output.txt"

    main(["patch", str(input_path), "DEADBEEF", "-o", str(output_path)])

    assert input_path.read_bytes() == b"hello"
    assert output_path.read_bytes() == b"hello\x45\x7E\x34\x30"


def test_patch_command_backup(tmp_path: Path) -> None:
    input_path = tmp_path / "input.txt"
    input_path.write_text("hello")
    backup_path = tmp_path / "input.txt.bak"

    main(["patch", str(input_path), "DEADBEEF", "-b"])

    assert input_path.read_bytes() == b"hello\x45\x7E\x34\x30"
    assert backup_path.read_bytes() == b"hello"