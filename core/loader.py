import re
import asyncio
import requests
from PIL import Image
from io import BytesIO

from core.settings import *


class Loader():
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop

    def load(self, urls: list[str]) -> list[requests.Response]:
        '''
        It uses the asyncio library to load a list of URLs asynchronously.

        Args:
            urls (list[str]): list of URLs

        Returns:
            A list of requests.Response objects.
        '''
        async def aload(urls: list[str]):
            def get(url, params):
                return requests.get(url, params=params, proxies=PROXYIES)

            futures = [
                self.loop.run_in_executor(None, get, url, {}) for url in urls if is_url(url)
            ]
            await asyncio.wait(futures)
            return [f.result() for f in futures]

        return self.loop.run_until_complete(aload(urls))

    def load_imgs(self, urls: list[str]) -> list[Image.Image]:
        '''
        It loads a list of images from a list of urls.

        Args:
            urls (list[str]): A list of URLs to download.

        Returns:
            A list of PIL images.
        '''
        return [Image.open(BytesIO(r.content)) for r in self.load(urls)]

    def load_auto(self, urls: list[str]) -> list[Image.Image, bytes]:
        '''
        Loads a list of URLs and returns a list of images or bytes

        Args:
          urls (list[str]): A list of URLs to download.

         Returns:
            A list of PIL images or bytes.
        '''
        result = list()
        for r in self.load(urls):
            if r.status_code != 200:
                result += [None]
                continue

            try:
                result += [Image.open(BytesIO(r.content))]
            except BaseException:
                result += [r.content]
        
        return result


def is_url(url: str) -> bool:
    '''
    Given a string, return True if it is a valid url, else return False

    Args:
      url (str): The URL to check.
    '''
    pattern = r"(http|ftp|https):\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    return bool(re.fullmatch(pattern, url))
