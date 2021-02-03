import typing as T
from pathlib import Path
from unittest import mock

import pytest
from click.testing import CliRunner

from crcmanip.cli import calc, cli, patch


@pytest.fixture(scope="module")
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def src_file(tmp_path: Path) -> Path:
    ret = tmp_path / "file.txt"
    ret.write_text("hello")
    return ret


def test_cli_command(runner: CliRunner) -> None:
    result = runner.invoke(cli, [])

    assert result.exit_code == 0
    assert "Usage: " in result.output

    assert cli.callback() is None  # to boost the coverage


def test_calc_command(src_file: Path, runner: CliRunner) -> None:
    result = runner.invoke(calc, [str(src_file)])

    assert result.exit_code == 0
    assert result.output == "3610A686\n"


def test_calc_command_quiet(src_file: Path, runner: CliRunner) -> None:
    with mock.patch(
        "crcmanip.cli.disable_progressbars"
    ) as mock_disable_progressbars:
        runner.invoke(calc, [str(src_file), "-q"])

    mock_disable_progressbars.assert_called_once()


def test_calc_command_different_alg(src_file: Path, runner: CliRunner) -> None:
    result = runner.invoke(calc, ["-a", "CRC16IBM", str(src_file)])

    assert result.exit_code == 0
    assert result.output == "34D2\n"


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
    src_file: Path,
    extra_args: T.List[str],
    expected_output: bytes,
    runner: CliRunner,
) -> None:
    result = runner.invoke(patch, [str(src_file), "DEADBEEF", *extra_args])

    assert result.exit_code == 0
    assert result.output == ""
    assert src_file.read_bytes() == expected_output


def test_patch_command_quiet(src_file: Path, runner: CliRunner) -> None:
    with mock.patch(
        "crcmanip.cli.disable_progressbars"
    ) as mock_disable_progressbars:
        runner.invoke(patch, [str(src_file), "DEADBEEF", "-q"])

    mock_disable_progressbars.assert_called_once()


def test_patch_command_different_alg(
    src_file: Path, runner: CliRunner
) -> None:
    result = runner.invoke(patch, ["-a", "CRC16IBM", str(src_file), "BEEF"])

    assert result.exit_code == 0
    assert result.output == ""
    assert src_file.read_bytes() == b"hello\xBA\x9D"


def test_patch_command_invalid_pos(src_file: Path, runner: CliRunner) -> None:
    src_file.write_text("123")

    result = runner.invoke(patch, [str(src_file), "DEADBEEF", "-P", "6"])
    assert result.exit_code == 1

    result = runner.invoke(patch, [str(src_file), "DEADBEEF", "-O"])
    assert result.exit_code == 0
    assert result.output == ""
    assert src_file.read_bytes() == b"\xC3\xD8\x24\x06"


def test_patch_command_dst_file(src_file: Path, runner: CliRunner) -> None:
    dst_file = src_file.parent / "output.txt"

    result = runner.invoke(
        patch, [str(src_file), "DEADBEEF", "-o", str(dst_file)]
    )

    assert result.exit_code == 0
    assert result.output == ""
    assert src_file.read_bytes() == b"hello"
    assert dst_file.read_bytes() == b"hello\x45\x7E\x34\x30"


def test_patch_command_backup(src_file: Path, runner: CliRunner) -> None:
    backup_file = src_file.with_suffix(src_file.suffix + ".bak")

    result = runner.invoke(patch, [str(src_file), "DEADBEEF", "-b"])

    assert result.exit_code == 0
    assert result.output == ""
    assert src_file.read_bytes() == b"hello\x45\x7E\x34\x30"
    assert backup_file.read_bytes() == b"hello"
