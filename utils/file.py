"""
File related functions
"""
import json
import os
from pathlib import Path
from typing import Union

from utils import error


def find_parent_of_folder(filepath: str, folder: str) -> Union[str, None]:
    """
    Find the parent of the ``folder`` in ``filepath``

    Args
        filepath (str): path to search
        folder (str): folder to find parent of

    Returns
        Union[str, None]: path to parent or None if not found
    """
    parent = None
    source_path = Path(filepath).resolve()
    parts = source_path.parts

    folder = folder.lower()
    for idx in range(len(parts) - 1, -1, -1):
        if parts[idx].lower() == folder:
            if idx >= 1:
                parent = str(Path(*parts[0:idx]))
            break

    return parent


def load_json_file(filepath: str) -> Union[dict, None]:
    """
    Load json from a file

    Args:
        filepath (str): path to file

    Returns:
        Union[dict, None]: json dict or None if error
    """
    data = None

    try:
        with open(filepath, encoding='utf-8') as file_handle:
            data = json.load(file_handle)
            file_handle.close()
    except FileNotFoundError:
        error(f'File not found: {filepath}')
    except json.decoder.JSONDecodeError:
        error(f'JSON decode error: {filepath}')

    return data


def load_json_string(json_string: str) -> Union[dict, None]:
    """
    Load json from a string

    Args:
        json_string (str): serialised json

    Returns:
        Union[dict, None]: json dict or None if error
    """
    data = None

    try:
        data = json.loads(json_string)
    except json.decoder.JSONDecodeError:
        error('JSON decode error: unable to deserialise string')

    return data


def save_json_file(filepath: str, data: object):
    """
    Save json to a file

    Args:
        filepath (str): path to file
        data (object): json data
    """
    path, _ = os.path.split(filepath)
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    try:
        with open(filepath, mode='w', encoding='utf-8') as file_handle:
            json.dump(data, file_handle, indent=4)
            file_handle.close()
    except OSError:
        error(f'Unable to save file: {filepath}')

    return data
