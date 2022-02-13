import sys
import json
from unittest import result
import click
from pathvalidate import sanitize_filename

from core.tools import *
from core.module import *
from core.packer import *
from core.config import *
from core.settings import *


@click.group()
@click.option('-m', '--module', default=DEFAULT_MODULE, help="Explicitly specify the module used.")
@click.pass_context
def app(context, module):
    context.ensure_object(dict)
    context.obj["MODULE"] = module

    if module not in INSTALED_MODULES:
        click.echo(f"Module '{module}' is not defined.")
        sys.exit()


@app.command(name="list", help="Shows the installed parsing modules.")
@click.option('-d', '--default', is_flag=True, help="Show default module.")
@click.pass_context
def modules(context, default) -> list[list[str]]:
    return _modules(context, default)


def _modules(context, default) -> list[list[str]]:
    max_name_len = len(max(INSTALED_MODULES, key=lambda x: len(x)))
    max_server_len = len(max(MODULES, key=lambda x: len(x.server)).server)

    if default:
        i = INSTALED_MODULES.index(context.obj["MODULE"])
        modules = [MODULES[i]]
        instaled_modules = [INSTALED_MODULES[i]]
    else:
        modules = MODULES
        instaled_modules = INSTALED_MODULES

    result = list()
    for i in range(len(modules)):
        name = instaled_modules[i].ljust(max_name_len)
        server = modules[i].server.ljust(max_server_len)
        search = str(modules[i].search_defined()).ljust(5)
        preload_tile = str(modules[i].preload_tile_defined()).ljust(5)
        preload_chapter = str(modules[i].preload_chapter_defined()).ljust(5)

        click.echo("{}\t {}\t search: {}\t preload-tile: {}\t preload-chapter: {}".format(
            name, server, search, preload_tile, preload_chapter))

        result.append([name, server, search, preload_tile, preload_chapter])
    return result


@app.command(help="Search using the module.")
@click.option('-q', '--query', required=True, help="Search query.")
@click.option('--offset', default=1, help="Мaximum number of results.")
@click.option('-t', '--timeout', default=8.0, help="Timeout in seconds.")
@click.pass_context
def search(context, query, offset, timeout) -> list[TileInfo]:
    result = _search(context, query, offset, timeout)

    max_title_len = len(max(result, key=lambda x: len(x.title)).title)
    for tile_info in result:
        title = tile_info.title.ljust(max_title_len, ".")
        url = tile_info.url
        click.echo(f"{title}... {url}")

    return result


def _search(context, query, offset, timeout) -> list[TileInfo]:
    i = INSTALED_MODULES.index(context.obj["MODULE"])
    module = MODULES[i]

    if not module.search_defined():
        click.echo(
            f"The module '{INSTALED_MODULES[i]}' is unable to execute this command.")
        return []

    try:
        result = module.search(q=query, offset=offset, timeout=timeout)
    except BaseException as err:
        click.echo(f"{err} exception occurred.")

    return result


@app.command(help="Upload information about tile.")
@click.option('-u', '--url', required=True, help="Tile address.")
@click.option('-a', '--auto', is_flag=True, help="Automatically select module.")
@click.option('-s', '--show', is_flag=True, help="Show execution result.")
@click.option('-t', '--timeout', default=8.0, help="Timeout in seconds.")
@click.pass_context
def preload_tile(context, url, auto, show, timeout) -> TileInfo:
    result = _preload_tile(context, url, auto, show, timeout)

    if show:
        click.echo(json.dumps(TileInfo_to_dict(result), indent=4))

    return result


def _preload_tile(context, url, auto, timeout) -> TileInfo:
    if auto:
        module = select_module(for_url=url)
        i = MODULES.index(module)
    else:
        i = INSTALED_MODULES.index(context.obj["MODULE"])
        module = MODULES[i]

    if not module.preload_tile_defined():
        click.echo(
            f"The module '{INSTALED_MODULES[i]}' is unable to execute this command.")
        return TileInfo()

    try:
        tile_info = module.preload_tile(url=url, timeout=timeout)
    except BaseException as err:
        click.echo(f"{err} exception occurred.")

    return tile_info


@app.command(help="Upload information about chapter.")
@click.option('-u', '--url', required=True, help="Chapter address.")
@click.option('-a', '--auto', is_flag=True, help="Automatically select module.")
@click.option('-s', '--show', is_flag=True, help="Show execution result.")
@click.option('-t', '--timeout', default=8.0, help="Timeout in seconds.")
@click.pass_context
def preload_chapter(context, url, auto, show, timeout) -> ChapterInfo:
    result = _preload_chapter(context, url, auto, timeout)

    if show:
        click.echo(json.dumps(ChapterInfo_to_dict(result), indent=4))

    return result


def _preload_chapter(context, url, auto, timeout) -> ChapterInfo:
    if auto:
        module = select_module(for_url=url)
        i = MODULES.index(module)
    else:
        i = INSTALED_MODULES.index(context.obj["MODULE"])
        module = MODULES[i]

    if not module.preload_chapter_defined():
        click.echo(
            f"The module '{INSTALED_MODULES[i]}' is unable to execute this command.")
        return TileInfo()

    try:
        chapter_info = module.preload_chapter(url=url, timeout=timeout)
    except BaseException as err:
        click.echo(f"{err} exception occurred.")

    return chapter_info


@app.command(help="Loads chapters and saves them.")
@click.option('-u', '--url', required=True, help="Tile address.")
@click.option('-a', '--auto', is_flag=True, help="Automatically select module.")
@click.option('-s', '--show', is_flag=True, help="Show execution result.")
@click.option('-t', '--timeout', default=8.0, help="Timeout in seconds.")
@click.option('-o', '--output', default=PACK_FOLDER, help="Folder to save.")
@click.option('--begin', default=1, help="The number of the first chapter. Starts with 1.")
@click.option('--offset', default=9999, help="Мaximum number of chapters.")
@click.pass_context
def load(context, url, auto, show, timeout, output, begin, offset) -> list[str]:
    result = _load(context, url, auto, timeout, output, begin, offset)

    if show:
        click.echo()
        click.echo('\n'.join(result))

    return result


def _load(context, url, auto, timeout, output, begin, offset) -> list[str]:
    tile = _preload_tile(context, url, auto, timeout)

    os.makedirs(output, exist_ok=True)
    packer = Packer(output)

    chapters = list(tile.chapters.items())
    if len(chapters) > begin:
        chapters = chapters[begin:]
    if len(chapters) > offset:
        chapters = chapters[:offset]

    paths = list()
    for i, chapter in chapters:
        click.echo(f"The preloading of '{chapter.url}' has started")
        chapter = _preload_chapter(context, chapter.url, auto, timeout)
        click.echo(f"Preloading has finished")

        click.echo(f"The loading of has started")
        pages = LOADER.load_imgs(chapter.pages)
        click.echo(f"Loading has finished")

        name = sanitize_filename(chapter.title)
        paths += [packer.save_pdf(name, pages)]

    return paths


if __name__ == "__main__":
    app(obj={})
    SESSION.close()
    LOOP.close()