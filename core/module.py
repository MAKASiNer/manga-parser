import re
import dis
import requests_html
from functools import *

from core.settings import *


class ChapterInfo():
    def __init__(
        self,
        url: str = None,
        title: str = None,
        pages: list[str] = [],
    ) -> None:
        '''      
        Args:
            url (str): The url of the chapter.
            title (str): The title of the chapter.
            pages (list[str]): Images URLs or text of each pages.
        '''
        self.url = url
        self.title = title
        self.pages = pages

    def __str__(self) -> str:
        return str(self.__dict__)


class TileInfo():
    def __init__(

        self,
        url: str = None,
        title: str = None,
        tags: list[str] = [],
        chapters: dict[int, ChapterInfo] = {},
    ) -> None:
        '''
        Args:
            url (str): The URL of the manga.
            title (str): The title of the manga.
            tags (list[str]): A list of strings that are tags for the tile.
            chapters (dict[int: ChapterInfo]): A dictionary of chapter numbers to ChapterInfo objects.
        '''
        self.url = url
        self.title = title
        self.tags = tags
        self.chapters = chapters

    def __str__(self) -> str:
        return str(self.__dict__)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = value
        if value is not None:
            self.server = "/".join(value.split("/")[:3])
        else:
            self.server = None


class BaseModule:
    server: str = "undefined"
    ''' site domain '''
    session: requests_html.HTMLSession = None
    ''' request_html session '''
    proxies: dict = None
    ''' proxies '''

    def __init__(self) -> None:
        protocol_pattern = r"(http|ftp|https):\/\/"
        domain_pattern = r"[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+"

        if self.server in ("undefined", ..., None):
            pass

        elif not re.match(protocol_pattern + domain_pattern, self.server):
            raise ValueError(
                f"Incorrect server '{self.server}' (must contain protocol and domain)")

    def get(self, url, params=None):
        return self.session.get(url, params=params, proxies=self.proxies)

    def post(self, url, params=None):
        return self.session.post(url, data=params, proxies=self.proxies)

    @property
    def search_defined(self) -> bool:
        return not is_empty_function(self.search)

    @property
    def preload_chapter_defined(self) -> bool:
        return not is_empty_function(self.preload_chapter)

    @property
    def preload_tile_defined(self) -> bool:
        return not is_empty_function(self.preload_tile)

    # --------------------------------------------------------------------------
    def search(self, q: str, offset: int = 1, timeout=8.0) -> list[TileInfo]:
        '''
        This function searches for tiles that match the given query

        Args:
          q (str): The search query.
          offset (int): The offset of the first result. Defaults to 1
          timeout (int): The timeout in seconds. Defaults to 8

        Returns:
          A list of TileInfo objects.
        '''

    def preload_tile(self, url: str, timeout=8.0) -> TileInfo:
        '''
        This function is used to preload a tile

        Args:
            url (str): The URL of the tile to be loaded.
            timeout (int): The timeout in seconds. Defaults to 8

        Returns:
            TileInfo object
        '''

    def preload_chapter(self, url: str, timeout=8.0) -> ChapterInfo:
        '''
        This function is used to preload chapter pages

        Args:
            url (str): The URL of the chapter.
            timeout (int): The timeout in seconds. Defaults to 8

        Returns:
            ChapterInfo object
        '''
    # --------------------------------------------------------------------------


def is_empty_function(function) -> bool:
    '''
    Checking the function

    Args:
      function: The function to check.

    Returns:
      Returns True if the function is empty, False otherwise.
    '''
    instructions = dis.get_instructions(function)
    instr = next(instructions, None)
    if (instr is None) or (instr.opname != 'LOAD_CONST') or (instr.argrepr != 'None'):
        return False
    instr = next(instructions, None)
    return instr and (instr.opname == 'RETURN_VALUE')
