import asyncio
from pathlib import Path
from typing import cast
from crawl4ai import (AsyncWebCrawler, CrawlerRunConfig,
                      DefaultMarkdownGenerator, PruningContentFilter, CacheMode)
from crawl4ai.models import CrawlResult


class FileWriteError(RuntimeError):
    pass


async def main():
    crawl_config = CrawlerRunConfig(
        # cache_mode=CacheMode.ENABLED,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(),
            options={
                "ignore_links": True,

            }
        ),
    )
    async with AsyncWebCrawler() as web_crawler:
        result = cast(CrawlResult, await web_crawler.arun(
            url="https://www.anthropic.com",
            config=crawl_config
        ))
        if result.markdown:
            print(len(result.markdown.raw_markdown))
            print(len(result.markdown.fit_markdown))
            if result.markdown.fit_markdown:
                return result.markdown.fit_markdown
        return None


def write_to_file(content, file_to_write):
    try:
        path = Path(file_to_write)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except Exception as ex:
        raise FileWriteError(f"Failed to write to {path}")


if __name__ == "__main__":
    site_content = asyncio.run(main())
    if site_content:
        write_to_file(site_content, "../data/output.txt")
