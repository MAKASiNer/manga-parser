import json
from core.tools import *
from core.module import *
from core.packer import *
from core.config import *
from core.settings import *
from pathvalidate import sanitize_filename


url = "https://mintmanga.live/vasilisk"

module = select_module(for_url=url)
tile = module.preload_tile(url)
# tile.title = sanitize_filename(tile.title)

# os.makedirs(os.path.join(PACK_FOLDER, tile.title), exist_ok=True)
# packer = Packer(os.path.join(PACK_FOLDER, tile.title))

# paths = []
# for i, chapter in list(tile.chapters.items()):
#     chapter = module.preload_chapter(chapter.url)
#     chapter.title = sanitize_filename(chapter.title)
#     print(f"PRELOADING '{chapter.title}' IS COMPLETED")
#     pages = LOADER.load_imgs(chapter.pages)
#     print(f"LOADING '{chapter.title}' IS COMPLETED")
#     paths += [packer.save_pdf(chapter.title, pages)]

# packer.join(tile.title, paths[::-1])

print(json.dumps(TileInfo_to_dict(tile), indent=2))
