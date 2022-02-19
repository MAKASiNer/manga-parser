from PIL import Image
from PyPDF2 import PdfFileMerger

from core.config import *
from core.module import *
from core.packer import *


class Packer(BasePacker):
    extension = "pdf"

    @LOGGER.logging
    def save(self, name: str, contents: list) -> str:
        name = self.correct_path(name)

        imgs = []
        for content in contents:
            if isinstance(content, (Image.Image)):
                imgs += [content.convert("RGB")]
            else:
                pass

        if imgs:
            imgs[0].save(name, save_all=True, append_images=imgs[1:])
            return name

        return str()

    @LOGGER.logging
    def join(self, name: str, paths: list[str]) -> str:
        book = PdfFileMerger()
        [book.append(path) for path in paths]
        book.write(self.correct_path(name))
        book.close()