import sys
import json
import click

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


@app.command(help="Shows the installed parsing module.")
@click.option('-e', '--each', is_flag=True, help="Show each of all modules.")
@click.pass_context
def modules(context, each) -> list[list[str]]:
    max_name_len = len(max(INSTALED_MODULES, key=lambda x: len(x)))
    max_server_len = len(max(MODULES, key=lambda x: len(x.server)).server)

    if each:
        modules = MODULES
        instaled_modules = INSTALED_MODULES
    else:
        i = INSTALED_MODULES.index(context.obj["MODULE"])
        modules = [MODULES[i]]
        instaled_modules = [INSTALED_MODULES[i]]

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
@click.option('--timeout', default=8.0, help="Timeout in seconds.")
@click.pass_context
def search(context, query, offset, timeout) -> list[TileInfo]:
    i = INSTALED_MODULES.index(context.obj["MODULE"])
    module = MODULES[i]

    if not module.search_defined():
        click.echo(
            f"The module '{INSTALED_MODULES[i]}' is unable to execute this command.")
        return []

    result = module.search(q=query, offset=offset, timeout=timeout)

    max_title_len = len(max(result, key=lambda x: len(x.title)).title)
    for tile_info in result:
        title = tile_info.title.ljust(max_title_len, ".")
        url = tile_info.url
        click.echo(f"{title}... {url}")

    return result


@app.command(help="Upload information about tile.")
@click.option('-u', '--url', required=True, help="Tile address.")
@click.option('-a', '--auto', is_flag=True, help="Automatically select module.")
@click.option('-p', '--preview', is_flag=True, help="Show execution result.")
@click.option('--timeout', default=8.0, help="Timeout in seconds.")
@click.pass_context
def preload_tile(context, url, auto, preview, timeout) -> TileInfo:
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

    tile_info = module.preload_tile(url=url, timeout=timeout)

    if preview:
        click.echo(json.dumps(TileInfo_to_dict(tile_info), indent=4))

    return tile_info


@app.command(help="Upload information about chapter.")
@click.option('-u', '--url', required=True, help="Chapter address.")
@click.option('-a', '--auto', is_flag=True, help="Automatically select module.")
@click.option('-p', '--preview', is_flag=True, help="Show execution result.")
@click.option('--timeout', default=8.0, help="Timeout in seconds.")
@click.pass_context
def preload_chapter(context, url, auto, preview, timeout) -> TileInfo:
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

    chapter_info = module.preload_chapter(url=url, timeout=timeout)

    if preview:
        click.echo(json.dumps(ChapterInfo_to_dict(chapter_info), indent=4))

    return chapter_info


app(obj={})
SESSION.close()