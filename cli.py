import argparse
from pathlib import Path
import sys
import tempfile
import subprocess
import os
import time
import requests

def get_api_token():
    app_dir = Path.home() / '.stashable'
    app_dir.mkdir(parents=True, exist_ok=True)
    credentials_file = app_dir / 'credentials'
    try:
        with open(credentials_file, "r") as f:
            api_token = f.readline()
            return api_token
    except:
        return None


def set_api_token(api_token):
    app_dir = Path.home() / '.stashable'
    app_dir.mkdir(parents=True, exist_ok=True)
    credentials_file = app_dir / 'credentials'
    with open(credentials_file, "w") as f:
        f.write(api_token)


def configure():
    api_token = get_api_token()
    if api_token is not None:
        confirm = input(
            "A token already exists. Would you like to overwrite? [y/N]: ")
        if confirm.lower() != "y":
            return
    api_token = input("Enter your Stashable.io API Token: ")
    set_api_token(api_token)


def create_snippet(stage):
    api_token = get_api_token()
    if api_token is None:
        configure()
        api_token = get_api_token()
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
        editor = os.environ.get('EDITOR', 'vi')
        process = subprocess.Popen([editor, '-w', f.name])
        process.wait()
        f.seek(0)
        lines = f.readlines()
        title = lines[3].decode().strip()
        tags = [word.strip() for word in lines[7].decode().split(',')]
        if tags[0] == '':
            tags = []
        snippet = ''.join([line.decode() for line in lines[11:]])

    data = {
        'apiToken': api_token,
        'type': 'snippet',
        'title': title,
        'tags': tags,
        'content': snippet,
    }
    r = requests.post(f'https://api.stashable.io/{stage}/external/create_resource', json=data)
    r.raise_for_status()

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
