import os


DEBUG = False


LOG_FOLDER = os.path.abspath("logs")
PACK_FOLDER = os.path.abspath("downloads")


INSTALED_MODULES = [
    "ReadMangaIo",
    "MintMangaLive",
    "MangaMammyRu",
]
DEFAULT_MODULE = INSTALED_MODULES[0] if INSTALED_MODULES else None


INSTALED_PACKERS = [
    "pdf",
]
DEFAULT_PACKER = INSTALED_PACKERS[0] if INSTALED_PACKERS else None


PROXYIES = {
    # "http": ...,
    # "https": ...,
    # "ftp": ...,
}
ONLY_PROXYIES = False
