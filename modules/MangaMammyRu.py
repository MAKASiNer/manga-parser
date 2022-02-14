from core.module import *
from core.config import *


class Module(BaseModule):
    server = "https://mangamammy.ru"
    session = SESSION
    proxies = PROXYIES

    @LOGGER.logging
    def preload_tile(self, url: str, timeout=8) -> TileInfo:
        script1 = """
            () => {
                data = {};
                data["title"] = document.querySelector('div.post-title').textContent;
                data["tags"] = document.querySelector('div.genres-content').textContent;
                return data;
            }
        """

        script2 = """
            () => {
                chapters = {};
                i = 0;
                document.querySelectorAll('li.wp-manga-chapter').forEach((elm) => {
                    href = elm.children[0].href;
                    title = elm.children[0].textContent;
                    chapters[String(i++)] = {"href": href, "title": title};
                });
                return chapters;
            }
        """

        with self.get(url) as response:
            data = response.html.render(
                script=script1, reload=False, timeout=timeout)

        with self.post(url + "ajax/chapters/") as response:
            chapters: dict = response.html.render(
                script=script2, reload=False, timeout=timeout)
            data["chapters"] = dict(
                zip(chapters.keys(), reversed(chapters.values())))

        def f(item):
            i = item[0]
            chapter = item[1]
            return (i, ChapterInfo(url=chapter["href"], title=chapter["title"].strip()))

        return TileInfo(
            url=url,
            title=data["title"].strip(),
            tags=[s.strip() for s in data["tags"].split(',')],
            chapters=dict([f(i) for i in data["chapters"].items()])
        )

    @LOGGER.logging
    def preload_chapter(self, url: str, timeout=8) -> ChapterInfo:
        script1 = """
            () => {
                data = {};
                data["title"] = document.querySelector("#chapter-heading").textContent;
                data["pages"] = [];
                data["links"] = [];
                document.querySelectorAll("div.footer .select-pagination option").forEach((elm) => {
                    data["links"].push(elm.getAttribute("data-redirect"));
                });

                return data;
            }
        """

        script2 = """
            () => {
                pages = [];
                document.querySelectorAll(".reading-content img").forEach((elm) => {
                    pages.push(elm.src);
                });
                return pages;
            }
        """

        with self.get(url) as response:
            data = response.html.render(
                script=script1, reload=False, timeout=timeout)

        for link in data["links"]:
            with self.get(link) as response:
                data["pages"] += response.html.render(
                    script=script2, reload=False, timeout=timeout)

        return ChapterInfo(
            url=url,
            title=data["title"].strip(),
            pages=data["pages"],
        )
