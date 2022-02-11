import asyncio
import requests
from PIL import Image
from io import BytesIO


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
            futures = [
                self.loop.run_in_executor(None, requests.get, url) for url in urls
            ]
            await asyncio.wait(futures)
            return [f.result() for f in futures]

        return self.loop.run_until_complete(aload(urls))

    def load_imgs(self, urls: list[str]) -> list[Image.Image]:
        '''
        It loads a list of images from a list of urls.
        
        Args:
            urls (list[str]): list[str]
        
        Returns:
            A list of PIL images.
        '''
        return [Image.open(BytesIO(r.content)) for r in self.load(urls)]
