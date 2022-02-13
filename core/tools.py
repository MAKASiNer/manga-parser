from core.module import *
from core.config import *


def select_module(for_url: str) -> BaseModule:
    '''
    Given a URL, return the module that can handle it

    Args:
        for_url (str): The URL for which to select the module.

    Returns:
        The module that matches the URL.
    '''
    for model in MODULES:
        if model.server in for_url:
            return model
    return BaseModule()


def ChapterInfo_to_dict(chapter: ChapterInfo) -> dict:
    '''
    Convert a ChapterInfo object to a dictionary

    Args:
        chapter (ChapterInfo): ChapterInfo

    Returns:
        A dictionary of the chapter info.
    '''
    return chapter.__dict__


def TileInfo_to_dict(tile: TileInfo) -> dict:
    '''
    Convert a TileInfo object to a dictionary

    Args:
        tile (TileInfo): The tile object to convert to a dictionary.

    Returns:
        A dictionary of the tile info.
    '''
    chapters = {}
    for i, chapter in tile.chapters.items():
        chapters[i] = ChapterInfo_to_dict(chapter)

    return TileInfo(url=tile.url,
                    title=tile.title,
                    tags=tile.tags,
                    chapters=chapters).__dict__
