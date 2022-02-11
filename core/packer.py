import os
from PIL import Image
from PyPDF2 import PdfFileMerger
from numpy import save

from core.module import *


class Packer:
    def __init__(self, folder: str):
        self.folder = None
        if os.path.isdir(folder):
            self.folder = folder
        else:
            raise FileNotFoundError("Incorrect packer folder")

    def save_pdf(self, name: str, imgs: list[Image.Image]) -> str:
        '''
        Save a list of images as a PDF
        
        Args:
          name (str): The name of the PDF file.
          imgs (list[Image.Image]): list[Image.Image]
        
        Returns:
          The path to the saved PDF.
        '''
        if ".pdf" not in name.lower():
            name += ".pdf"

        for i in range(len(imgs)):
            imgs[i] = imgs[i].convert("RGB")

        path = os.path.join(self.folder, name)
        imgs[0].save(path, save_all=True, append_images=imgs[1:])
        return path

    def save(self, name: str, imgs: list[Image.Image], ext: str = "png") -> list[str]:
        '''
        Save a list of images to disk
        
        Args:
          name (str): The name of the image. Each image will be saved with name {name}.{index}.{ext}.
          imgs (list[Image.Image]): list[Image.Image]
          ext (str): str = "png". Defaults to png
        
        Returns:
          A list of paths to the saved images.
        '''
        paths = list()
        for i in range(len(imgs)):
            img = imgs[i].convert("RGB")
            paths += [os.path.join(self.folder, f"{name}_{i}.{ext}")]
            img.save(paths[-1])
        
        return paths

    def scan(self) -> list[str]:
        '''
        This function returns a list of all the files in the folder that have the extension ".pdf"

        Returns:
          A list of strings.
        '''
        pdfs = []
        for f in os.listdir(self.folder):
            if ".pdf" in f.lower():
                pdfs.append(os.path.join(self.folder, f))
        return pdfs

    @staticmethod
    def join(name: str, pdfs: list[str]):
        merger = PdfFileMerger()
        [merger.append(pdf) for pdf in pdfs]
        merger.write(name + ".pdf" if ".pdf" not in name.lower() else "")
        merger.close()
