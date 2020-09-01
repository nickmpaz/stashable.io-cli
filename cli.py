import argparse
from pathlib import Path
import sys
import tempfile
import subprocess
import os
import time
import requests
import json

from simple_term_menu import TerminalMenu
app_dir = Path.home() / '.stashable'
config_file = app_dir / 'config'
editors = [
    {
        'name': 'Vim',
        'command': ['vim', '-f']
    }, {
        'name': 'VS Code',
        'command': ['code', '-w']
    }
]


def set_config(config):
    app_dir.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w") as f:
        f.write(json.dumps(config))


def get_config():
    app_dir.mkdir(parents=True, exist_ok=True)
    try:
        with open(config_file, "r") as f:
            config = json.loads(f.readline())
            return config
    except:
        return None


def configure():
    config = get_config()
    if config is not None and config.get('api_token'):
        api_token = input(f"Enter your Stashable.io API Token [{config.get('api_token')}]: ")
        if api_token == "":
            api_token = config.get('api_token')
    else:
        api_token = input("Enter your Stashable.io API Token: ")
    print('Choose your editor:')
    select_editor_menu = TerminalMenu([editor['name'] for editor in editors])
    editor = select_editor_menu.show()

    set_config({'api_token': api_token, 'editor': editor})


def create_snippet(stage):
    config = get_config()
    if config is None:
        configure()
        config = get_config()
    api_token = config['api_token']

    snippet_template = b"""#####################
# Enter title below #
#####################

##############################################
# Enter tags below as a comma separated list #
##############################################

############################
# Enter code snippet below #
############################
"""
    with tempfile.NamedTemporaryFile() as f:
        f.write(snippet_template)
        f.seek(0)
        process = subprocess.Popen(editors[config['editor']]['command'] + [f.name])
        process.wait()
        f.seek(0)
        lines = f.readlines()
        title = lines[3].decode().strip()
        tags = [word.strip() for word in lines[7].decode().split(',')]
        if tags[0] == '':
            tags = []
        snippet = ''.join([line.decode() for line in lines[11:]])

        if title == '' and snippet == '' and tags == []:
            print('No changes made, aborting.')
            return

    data = {
        'apiToken': api_token,
        'type': 'snippet',
        'title': title,
        'tags': tags,
        'content': snippet,
    }
    r = requests.post(
        f'https://api.stashable.io/{stage}/external/create_resource', json=data)
    r.raise_for_status()
    print(f"Created snippet: {title}")


if __name__ == "__main__":
    category_choices = ['configure', 'snippet']
    stage_choices = ['prod', 'dev', 'local']

    parser = argparse.ArgumentParser(
        description='Stashable.io command line interface',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'category',
        metavar='category',
        type=str,
        choices=category_choices,
        help=f'{category_choices}'
    )
    parser.add_argument(
        '--stage',
        metavar='stage',
        type=str,
        default=stage_choices[0],
        choices=stage_choices,
        help=f'{stage_choices}'
    )
    args = parser.parse_args()

    if args.category == "configure":
        configure()
    elif args.category == "snippet":
        create_snippet(args.stage)
