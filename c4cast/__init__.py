# -*- coding: utf-8 -*-

import argparse
import pkg_resources
import sys

version = pkg_resources.resource_string('c4cast', 'version.txt')
version = version.decode('utf-8').strip()
"""Package version (as a dotted string)."""

cli = argparse.ArgumentParser(description='Cash flow forecast.')
cli.add_argument('--version', action='version', version=version,
                 help="Print version and exit.")

def main(arguments=None):
    if arguments is None:
        arguments = sys.argv[1:]
    arguments = cli.parse_args(arguments)
