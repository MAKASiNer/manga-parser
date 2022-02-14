import sys
import json
import click
from pathvalidate import sanitize_filename

from core.tools import *
from core.module import *
from core.packer import *
from core.config import *
from core.settings import *


@click.group()
@click.option('-m', '--module', default=DEFAULT_MODULE, help="Specify the default module.")
@click.option('-p', '--packer', default=DEFAULT_PACKER, help="Specify the default packer.")
@click.pass_context
def app(context, module, packer):
    context.ensure_object(dict)

    if not INSTALED_MODULES:
        click.echo(f"No modules installed.")
        sys.exit()
    if module not in INSTALED_MODULES:
        click.echo(f"Module '{module}' is not defined.")
        sys.exit()
    else:
        context.obj["MODULE"] = module

    if not INSTALED_PACKERS:
        click.echo(f"No packers installed.")
        sys.exit()
    if packer not in INSTALED_PACKERS:
        click.echo(f"Packer '{packer}' is not defined.")
        sys.exit()
    else:
        context.obj["PACKER"] = packer


@app.command(help="Shows the installed parsing modules.")
@click.option('-d', '--default', is_flag=True, help="Show default module.")
@click.pass_context
def modules_list(context, default) -> list[list[str]]:
    result = _modules_list(context, default)
    for m in result:
        click.echo(
            "{}\t {}\t search: {}\t preload-tile: {}\t preload-chapter: {}".format(*m))
    return result


def _modules_list(context, default) -> list[list[str]]:
    if INSTALED_MODULES:
        max_name_len = len(max(INSTALED_MODULES, key=lambda x: len(x)))
    if MODULES:
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
        module = modules[i]

        name = instaled_modules[i].ljust(max_name_len)
        server = module.server.ljust(max_server_len)
        search = str(module.search_defined).ljust(5)
        preload_tile = str(module.preload_tile_defined).ljust(5)
        preload_chapter = str(module.preload_chapter_defined).ljust(5)

        result.append([name, server, search, preload_tile, preload_chapter])
    return result


@app.command(help="Shows the installed storage packer.")
@click.option('-d', '--default', is_flag=True, help="Show default packer.")
@click.pass_context
def packers_list(context, default) -> list[list[str]]:
    result = _packers_list(context, default)
    for p in result:
        click.echo("{}\t *.{}\t save: {}\t join: {}".format(*p))
    return result


def _packers_list(context, default) -> list[list[str]]:
    if INSTALED_PACKERS:
        max_name_len = len(max(INSTALED_PACKERS, key=lambda x: len(x)))
    if PACKERS:
        max_extension_len = len(
            max(PACKERS, key=lambda x: len(x.extension)).extension)

    if default:
        i = INSTALED_PACKERS.index(context.obj["PACKER"])
        packers = [PACKERS[i]]
        instaled_packers = [INSTALED_PACKERS[i]]
    else:
        packers = PACKERS
        instaled_packers = INSTALED_PACKERS

    result = list()
    for i in range(len(packers)):
        packer = packers[i]

        name = instaled_packers[i].ljust(max_name_len)
        extension = packer.extension.ljust(max_extension_len)
        save = str(packer.save_defined).ljust(5)
        join = str(packer.join_defined).ljust(5)

        result.append([name, extension, save, join])
    return result


@app.command(help="Scans packer files.")
@click.option('-d', '--directory', default=PACK_FOLDER, help=f"Directory to scan. By default {PACK_FOLDER}")
@click.pass_context
def scan(context, directory) -> list[str]:
    result = _scan(context, directory)
    click.echo()
    click.echo('\n'.join(result))
    return result


def _scan(context, directory) -> list[str]:
    i = INSTALED_PACKERS.index(context.obj["PACKER"])
    packer = PACKERS[i]
    return packer.scan(directory)


@app.command(help="Search using the module.")
@click.option('-q', '--query', required=True, help="Search query.")
@click.option('-t', '--timeout', default=8.0, help="Timeout in seconds.")
@click.option('--offset', default=1, help="Мaximum number of results.")
@click.pass_context
def search(context, query, offset, timeout) -> list[TileInfo]:
    result = _search(context, query, offset, timeout)

    if result:
        max_title_len = len(max(result, key=lambda x: len(x.title)).title)
    for tile_info in result:
        title = tile_info.title.ljust(max_title_len, ".")
        url = tile_info.url
        click.echo(f"{title}... {url}")

    return result


def _search(context, query, offset, timeout) -> list[TileInfo]:
    i = INSTALED_MODULES.index(context.obj["MODULE"])
    module = MODULES[i]

    if not module.search_defined:
        click.echo(
            f"The module '{INSTALED_MODULES[i]}' is unable to execute this command.")
        return []

    result = module.search(q=query, offset=offset, timeout=timeout)

    return result


@app.command(help="Upload information about tile.")
@click.option('-u', '--url', required=True, help="Tile address.")
@click.option('-a', '--auto', is_flag=True, help="Automatically select module.")
@click.option('-s', '--show', is_flag=True, help="Show execution result.")
@click.option('-t', '--timeout', default=8.0, help="Timeout in seconds.")
@click.pass_context
def preload_tile(context, url, auto, show, timeout) -> TileInfo:
    result = _preload_tile(context, url, auto, timeout)
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

    if not module.preload_tile_defined:
        click.echo(
            f"The module '{INSTALED_MODULES[i]}' is unable to execute this command.")
        return TileInfo()

    return module.preload_tile(url=url, timeout=timeout)


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

    if not module.preload_chapter_defined:
        click.echo(
            f"The module '{INSTALED_MODULES[i]}' is unable to execute this command.")
        return TileInfo()

    return module.preload_chapter(url=url, timeout=timeout)


@app.command(help="Save content")
@click.option('-c', '--content', multiple=True, required=True, help="Content list.")
@click.option('-o', '--output', required=True, help="Output file name.")
@click.option('-s', '--show', is_flag=True, help="Show execution result.")
@click.pass_context
def save(context, content, output, show) -> str:
    result = _save(context, content, output)
    if show:
        click.echo()
        click.echo(result)
    return result


def _save(context, content, output) -> str:
    i = INSTALED_PACKERS.index(context.obj["PACKER"])
    packer = PACKERS[i]

    if not packer.save_defined:
        click.echo(
            f"The packer '{INSTALED_PACKERS[i]}' is unable to execute this command.")
        return str()

    path = packer.save(output, content)
    return path


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

    chapters = list(tile.chapters.items())
    if len(chapters) >= begin:
        chapters = chapters[begin - 1:]
    if len(chapters) > offset:
        chapters = chapters[:offset]

    paths = list()
    for i, chapter in chapters:
        click.echo(f"The preloading of '{chapter.url}' has started")
        chapter = _preload_chapter(context, chapter.url, auto, timeout)
        click.echo(f"Preloading has finished")

        click.echo(f"The loading of has started")
        contents = LOADER.load_auto(chapter.pages)
        click.echo(f"Loading has finished")

        name = sanitize_filename(chapter.title)
        path = os.path.join(output, sanitize_filename(tile.title), i)
        os.makedirs(path, exist_ok=True)
        paths += [_save(context, contents, os.path.join(path, name))]
    return paths


if __name__ == "__main__":
    app(obj={})
    # try:
    #    app(obj={})
    # except BaseException as err:
    #    click.echo(err)

    SESSION.close()
    LOOP.close()
