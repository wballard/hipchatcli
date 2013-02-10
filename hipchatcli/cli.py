"""Hipchat CLI

Usage:
    hipchat [options] rooms list [PATTERN]

Commands:
    rooms list      List all available rooms, with an optional pattern on name

Options:
    -i --id-only    Return just the ID, useful to pipe along with xargs

Hipchat looks for an environment variable HIPCHAT_API_KEY that is uses
to authenticate. Set it before doing anything else.

Parameters:
    PATTERN         Python style regex matches against all available fields
"""

from docopt import docopt
from hipchatcli.version import __package_version__, __package_name__
import sys
import os
import select
import requests
import json
from clint.textui import colored
from clint.textui import puts, indent, columns
import re

def handle_error(response):
    """
    Handle hipchat API errors, bailing out.
    """
    data = json.loads(response.text)
    if response.status_code == 200:
        return data
    if 'error' in data:
        print(data)
        puts(colored.red('Error {0}:{1}'.format(
            data['error']['code'],
            data['error']['type'])))
        puts(data['error']['message'])
        sys.exit(1)


def rooms(arguments):

    def list():
        r = requests.get('https://api.hipchat.com/v1/rooms/list?format=json&auth_token={0}'.format(os.getenv('HIPCHAT_API_KEY', '')))
        r = handle_error(r)
        pattern = re.compile(arguments['PATTERN'] or '.*', re.IGNORECASE)

        for room in r['rooms']:
            if pattern.search(room['name'] + room['topic']):
                if arguments['--id-only']:
                    puts(str(room['room_id']))
                else:
                    puts(columns(
                        [str(room['room_id']), 9],
                        [room['name'], 40],
                        [room['topic'], None]
                        ))



    for key in arguments.keys():
        if key in locals() and arguments[key]:
            locals()[key]()

def main():
    arguments = docopt(__doc__, version="{0} {1}".format(__package_name__, __package_version__))
    #if select.select([sys.stdin,],[],[],0.0)[0]:
    for key in arguments.keys():
        if key in globals() and arguments[key]:
            globals()[key](arguments)
