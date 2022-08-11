"""
Help related functions
"""
from pathlib import Path
from utils import (
    get_env_setting, DEFAULT_HELP_PATH, error, display_paginated,
    find_parent_of_folder, Spacing
)


def display_help():
    """ Display help """
    help_file = get_env_setting('HELP_PATH', DEFAULT_HELP_PATH)
    path = Path(help_file)
    if not path.is_absolute():
        # project root is parent of 'process'
        parent = find_parent_of_folder(__file__, 'process')
        path = Path(parent, help_file)

    error_msg = None
    if not path.exists():
        error_msg = f'Help file not found: {help_file}'
    elif not path.is_file():
        error_msg = f'Not a file: {help_file}'

    if error_msg:
        error(error_msg)
    else:
        display_paginated(file_reader(path), pre_spc=Spacing.LARGE,
                          post_spc=Spacing.SMALL)


def file_reader(filepath: str):
    """
    Generator to read a file
    
    Args:
        filepath (str): path to file
    """
    for row in open(filepath, "r"):
        yield row

