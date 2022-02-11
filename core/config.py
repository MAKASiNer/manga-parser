import asyncio
import requests_html
from core.settings import *


LOOP = asyncio.get_event_loop()
SESSION = requests_html.HTMLSession()


from core.logger import Logger
LOGGER = Logger(LOG_FOLDER, DEBUG)


from core.packer import Packer
PACKER = Packer(PACK_FOLDER)


from core.loader import Loader
LOADER = Loader(LOOP)


from importlib import import_module
from core.module import BaseModule
MODULES = []
for m in INSTALED_MODULES:
    try:
        module = import_module(f"modules.{m}").Module()
    except ModuleNotFoundError:
        module = BaseModule()
    MODULES.append(module)