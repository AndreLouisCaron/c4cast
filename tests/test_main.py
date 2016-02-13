# -*- coding: utf-8 -*-

# TODO: validate asset links with BeautifulSoup.

import asyncio
import bs4
import functools
import os
import pytest
import signal
import unittest.mock
import urllib.parse

from c4cast import main, version

def ctrl_c():
    os.kill(os.getpid(), signal.SIGINT)

async def fetch_http(client, url):
    response = await client.get(url)
    assert response.status == 200
    body = await response.read()
    return body.strip()

@unittest.mock.patch('sys.argv', ['c4cast', '--version'])
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

def forward(target, source):
    try:
        target.set_result(source.result())
    except Exception as error:
        target.set_exception(error)

async def check_index(client):
    body = await fetch_http(client, 'http://127.0.0.1:9000/index.html')
    soup = bs4.BeautifulSoup(body, 'html.parser')
    for link in soup.find_all('link'):
        assert await fetch_http(
            client, urllib.parse.urljoin(
                'http://127.0.0.1:9000/', link.get('href'),
            ),
        )
    for script in soup.find_all('script'):
        if not script.get('src'):
            continue
        assert await fetch_http(
            client, urllib.parse.urljoin(
                'http://127.0.0.1:9000/', script.get('src'),
            ),
        )

def test_main_ctrl_c(capsys, event_loop, client):
    def fetch_index(f):
        t = event_loop.create_task(check_index(client))
        t.add_done_callback(functools.partial(forward, f))

    # Query the page contents once the server is running.
    f = asyncio.Future()
    event_loop.call_later(0.5, fetch_index, f)

    # Automatically trigger CTRL-C after we're sure the query is complete.
    event_loop.call_later(1.0, ctrl_c)

    # Run the server (until CTRL-C is fired).
    main([
        '--host=127.0.0.1',
        '--port=9000',
    ])

    # Error log should be empty.
    stdout, stderr = capsys.readouterr()
    assert stdout.strip() == ''
    assert stderr.strip() == ''

    # There should be no broken links.
    assert f.result() is None
