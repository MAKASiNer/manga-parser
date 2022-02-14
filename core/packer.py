import os
from glob import glob
from itertools import chain
from pathvalidate import sanitize_filename

from core.module import *


class BasePacker:

    extension: str = str()
    '''file extension'''

    def __init__(self):
        if sanitize_filename(self.extension) != self.extension:
            raise ValueError(f"Incorrect file extension '.{self.extension}'")

    def scan(self, directory: str) -> list[str]:
        '''
        It scans a directory and returns a list of all the files in that directory.
        
        Args:
          directory (str): The directory to scan.
        
        Returns:
          A list of all the files in the given directory.
        '''
        result = (chain.from_iterable(
            glob(os.path.join(x[0], f"*.{self.extension}")) for x in os.walk(directory)))
        return [os.path.abspath(r) for r in result]

    def correct_path(self, path: str) -> str:
        '''
        Add the file extension to the file name
        
        Args:
          path (str): The path to the file.
        
        Returns:
          The path to the file with the correct extension.
        '''
        if f".{self.extension}" not in os.path.split(path)[-1]:
            path += f".{self.extension}"
        return path

    @property
    def save_defined(self) -> bool:
        return not is_empty_function(self.save)

    @property
    def join_defined(self) -> bool:
        return not is_empty_function(self.join)

    # --------------------------------------------------------
    def save(self, name: str, contents: list) -> str:
        '''
        Save the contents to the files

        Args:
            name (str): The name of the files to be saved.
            contents (list): List of content.

        Returns:
            Absolute paths to saved file.
        '''

    def join(self, name: str, paths: list[str]) -> str:
        '''
        This function joins a files together

        Args:
            name (str): The name of the final result.
            paths (list[str]): A list of files paths to join.

        Returns:
            Absolute path to the saved file.
        '''
    # --------------------------------------------------------
