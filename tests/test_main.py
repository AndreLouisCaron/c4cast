# -*- coding: utf-8 -*-

import pytest

from unittest import mock

from c4cast import main, version

@mock.patch('sys.argv', ['c4cast', '--version'])
def test_version(capsys):
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.args[0] == 0
    stdout, _ = capsys.readouterr()
    assert stdout.strip() == version

def test_main_explicit_args(capsys):
    with pytest.raises(SystemExit) as error:
        main(['--version'])
    assert error.value.args[0] == 0
    stdout, _ = capsys.readouterr()
    assert stdout.strip() == version
