import os
from PIL import Image
from core.module import *


class Packer:
    def __init__(self, folder: str):
        self.folder = None
        if os.path.isdir(folder):
            self.folder = folder
        else:
            raise FileNotFoundError("Incorrect packer folder")

    def save_pdf(self, name: str, imgs: list[Image.Image]) -> str:
        if ".pdf" not in name.lower():
            name += ".pdf"

        for i in range(len(imgs)):
            imgs[i] = imgs[i].convert("RGB")

        path = os.path.join(self.folder, name)
        imgs[0].save(path, save_all=True, append_images=imgs[1:])
        return path

    def save_img(self, name: str, imgs: list[Image.Image], ext: str = "png") -> list[str]:
        paths = list()
        for i in range(len(imgs)):
            img = imgs[i].convert("RGB")
            paths += [os.path.join(self.folder, f"{name}_{i}.{ext}")]
            img.save(paths[-1])

        return paths

    def save_text(self, name: str, texts: list[str]) -> str:
        from xml.etree import ElementTree

        html = ElementTree.Element('html')

        head = ElementTree.Element('head')
        meta = ElementTree.Element('meta', attrib={'charset': 'UTF-8'})
        head.append(meta)

        body = ElementTree.Element('body')
        for text in texts:
            div = ElementTree.Element('div',
                                      attrib={"style": "page-break-after:always;"})
            div.text = text
            body.append(div)

        html.append(head)
        html.append(body)

        name += '.html' if '.html' not in name.lower() else ''
        path = os.path.join(self.folder, name)
        ElementTree.ElementTree(html).write(path)
        return path

    def scan(self, ext="pdf") -> list[str]:
        '''
        This function scans the folder for files and returns a list of their paths

        Args:
            ext: The file extension to search for. Defaults to pdf.

        Returns:
            A list of strings.
        '''
        pdfs = []
        for f in os.listdir(self.folder):
            if f".{ext}" in f.lower():
                pdfs.append(os.path.join(self.folder, f))
        return pdfs

    @staticmethod
    def join(name: str, pdfs: list[str]):
        '''
        It joins pdfs into one pdf.

        Args:
          name (str): The name of the file to be created.
          pdfs (list[str]): list of pdf files.
        '''
        from PyPDF2 import PdfFileMerger

        book = PdfFileMerger()
        [book.append(pdf) for pdf in pdfs]
        book.write(name + ".pdf" if ".pdf" not in name.lower() else "")
        book.close()
