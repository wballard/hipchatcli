"""Hipchat CLI

Usage:
    hipchat [options] users show USER
    hipchat [options] rooms create USER NAME
    hipchat [options] rooms list [PATTERN]
    hipchat [options] rooms delete ID
    hipchat [options] rooms message ROOM USER

Commands:
    rooms message   This will read the message body from stdin by default.


Options:
    -i --id-only    Return just the ID, useful to pipe along with xargs

Hipchat looks for an environment variable HIPCHAT_API_KEY that is uses
to authenticate. Set it before doing anything else.

Parameters:
    PATTERN         Python style regex matches against all available fields
    ID              Integer ID used inside Hipchat for various objects
    USER            Integer ID or email address of a user
    NAME            String used to name an object
    ROOM            Name or integer ID of a chat room
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

def input_content():
    if select.select([sys.stdin,],[],[],0.0)[0]:
        return sys.stdin.read()

def forward(scope, arguments):
    for key in arguments.keys():
        if key in scope and arguments[key]:
            scope[key](arguments)
    return scope

def api_key(arguments):
    ret =  os.getenv('HIPCHAT_API_KEY', '')
    assert ret, 'You must export HIPCHAT_API_KEY'
    return ret

def user(arguments, stripped=False):
    if stripped:
        return arguments['USER'].split('@')[0][0:15]
    else:
        return arguments['USER']

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

def users(arguments):

    def show(arguments, silent=False):
        r = requests.get('https://api.hipchat.com/v1/users/show?format=json&auth_token={0}&user_id={1}'.
                format(api_key(arguments), arguments['USER']))
        r = handle_error(r)
        if not silent:
            if arguments['--id-only']:
                puts(str(r['user']['user_id']))
            else:
                puts(columns(
                    [str(r['user']['user_id']), 10],
                    [str(r['user']['name']), 25],
                    [str(r['user']['email']), 25],
                    [str(r['user']['title']), 10],
                    ))
        return r['user']

    return forward(locals(), arguments)

def rooms(arguments):

    def list(arguments):
        r = requests.get('https://api.hipchat.com/v1/rooms/list?format=json&auth_token={0}'.format(api_key(arguments)))
        r = handle_error(r)
        pattern = re.compile(arguments['PATTERN'] or '.*', re.IGNORECASE)

        for room in r['rooms']:
            if pattern.search(room['name'] + room['topic']):
                if arguments['--id-only']:
                    puts(str(room['room_id']))
                else:
                    puts(columns(
                        [str(room['room_id']), 10],
                        [room['name'], 40],
                        [room['topic'], None]
                        ))

    def delete(arguments):
        r = requests.post(
            'https://api.hipchat.com/v1/rooms/delete?format=json&auth_token={0}'.format(api_key(arguments)),
            data={'room_id': arguments['ID']}
            )
        r = handle_error(r)

    def create(arguments):
        #chain along to get the owner
        user = users(arguments)['show'](arguments, silent=True)
        r = requests.post(
            'https://api.hipchat.com/v1/rooms/create?format=json&auth_token={0}'.format(api_key(arguments)),
            data={'owner_user_id': user['user_id'], 'name': arguments['NAME']}
            )
        r = handle_error(r)

    def message(arguments):
        r = requests.post(
            'https://api.hipchat.com/v1/rooms/message?format=json&auth_token={0}'.format(api_key(arguments)),
            data={
                'room_id': arguments['ROOM'],
                'from': user(arguments, stripped=True),
                'message': input_content()
            }
            )
        r = handle_error(r)

    return forward(locals(), arguments)


def main():
    arguments = docopt(__doc__, version="{0} {1}".format(__package_name__, __package_version__))
    forward(globals(), arguments)
