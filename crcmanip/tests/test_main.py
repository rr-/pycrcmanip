from unittest.mock import patch

import pytest

from crcmanip import __main__


def test_init() -> None:
    with patch.object(__main__, "cli") as mock_cli, patch.object(
        __main__, "__name__", "__main__"
    ):
        __main__.init()
        mock_cli.assert_called_with()
