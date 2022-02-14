import asyncio
import requests_html
from core.settings import *


LOOP = asyncio.get_event_loop()
SESSION = requests_html.HTMLSession()


from core.logger import Logger
LOGGER = Logger(LOG_FOLDER, DEBUG)


from core.loader import Loader
LOADER = Loader(LOOP)


from importlib import import_module
from core.module import BaseModule

MODULES: list[BaseModule] = []
for m in INSTALED_MODULES:
    try:
        module = import_module(f"modules.{m}").Module()
    except (ModuleNotFoundError, ValueError) as err:
        LOGGER.log(err)
        module = BaseModule()  
    MODULES.append(module)

from core.packer import BasePacker
PACKERS: list[BasePacker] = []
for p in INSTALED_PACKERS:
    try:
        packer = import_module(f"packers.{p}").Packer()
    except (ModuleNotFoundError, ValueError) as err:
        LOGGER.log(err)
        packer = BasePacker()  
    PACKERS.append(packer)