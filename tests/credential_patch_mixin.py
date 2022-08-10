"""
Credentials related functions
"""
from pathlib import Path
from typing import Union

from utils import GOOGLE_CREDS_PATH_ENV, YAHOO_FINANCE_CREDS_PATH_ENV


class CredentialPatchMixin:
    """
    Mixin to get patch for credentials
    """

    @staticmethod
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

    @staticmethod
    def get_credential_patch(filepath: str):
        """
        Get the credentials patch to apply to the correct environment variables

        Args
            filepath (str): path to search

        Returns
            dict: patch
        """
        # project root is parent of 'tests'
        project_root = CredentialPatchMixin.find_parent_of_folder(
            filepath, 'tests')
        assert project_root is not None

        return {
            GOOGLE_CREDS_PATH_ENV: project_root,
            YAHOO_FINANCE_CREDS_PATH_ENV: project_root
        }
