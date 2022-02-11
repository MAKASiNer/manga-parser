from imp import reload
from core.module import *
from core.config import LOGGER, SESSION


class Module(BaseModule):
    server = "https://readmanga.io"
    session = SESSION

    @LOGGER.logging
    def search(self, q: str, offset: int = 1, timeout=8.0) -> list[TileInfo]:
        script = """
            () => {
                data = [];
                $("div.tile").each(function () {
                    elm = $("div.desc > h3 > a", $(this))[0]
                    href = elm.getAttribute("href");
                    title = elm.textContent
                    data.push({"href": href, "title": title});
                });
                return data;
            }
        """

        with self.session.post(self.server + "/search", {"q": q}) as response:
            data = response.html.render(
                script=script, reload=False, timeout=timeout)
            if len(data) > offset:
                data = data[:offset]

        def f(item):
            url = (
                self.server if "://" not in item['href'] else '') + item['href']
            title = item['title']
            return TileInfo(url=url, title=title)

        return [f(i) for i in data]

    @LOGGER.logging
    def preload_tile(self, url: str, timeout=8.0) -> TileInfo:
        script = """
            () => {
                data = {};
                data["title"] = $("meta[itemprop='name']")[0].getAttribute("content");
                data["chapters"] = Object();
                i = 0;
                rm_h.chapters.changeOrder();
                $(".item-title").each(function () {
                    elm = $("a", $(this)[0])[0];
                    href = elm.getAttribute("href");
                    title = elm.textContent;
                    data["chapters"][String(i++)] = {"href": href, "title": title};
                });
                return data;
            }
        """

        with self.session.get(url, params={"mtr": 1}) as response:
            data = response.html.render(script=script, timeout=timeout)

        def f(item):
            i = item[0]
            chapter = item[1]
            return (i, ChapterInfo(url=self.server + chapter["href"], title=chapter["title"].strip()))

        return TileInfo(
            url=url,
            title=data["title"].strip(),
            chapters=dict([f(i) for i in data["chapters"].items()])
        )

    @LOGGER.logging
    def preload_chapter(self, url: str, timeout=8.0) -> ChapterInfo:
        script = """
            () => {
                data = {};
                elm = $("#mangaBox > h1")[0];
                data["title"] = elm.innerText.replace($("a", elm)[0].text, '');
                data["pages"] = rm_h.pics;
                return data;
            }
        """

        with self.session.get(url, params={"mtr": 1}) as response:
            data = response.html.render(script=script, timeout=timeout)

        return ChapterInfo(
            url=url,
            title=data["title"].strip(),
            pages=[p["url"] for p in data["pages"]],
        )
