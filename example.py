from pathvalidate import sanitize_filename
from core.tools import *
from core.module import *
from core.packer import *
from core.config import *
from core.settings import *

import re

regex = re.compile(
    r"(http|ftp|https):\/\/[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+")

server = regex.match("https://animego.org/anime/memuary-vanitasa-1803")[0]
print(server)