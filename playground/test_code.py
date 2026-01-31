import re
import asyncio
import json
from pathlib import Path
from typing import cast
from crawl4ai import (AsyncWebCrawler, CrawlerRunConfig,
                      DefaultMarkdownGenerator, PruningContentFilter,  SeedingConfig, AsyncUrlSeeder, AsyncLogger)
from crawl4ai.models import CrawlResult

ALLOW = re.compile(r"/(products|solutions|industries|customers|case-studies|pricing|integrations|api|security|trust|careers)(/|$)", re.I)
DENY  = re.compile(r"/(login|signup|register|privacy|terms|press|events|webinars|shop?)(/|$)|/blog/", re.I)
DENY_SUBDOMAIN = re.compile(
    r"^https?://shop\.",
    re.I
)
DENY_LOCALE = re.compile(
    r"/(fr|de|es|it|pt|nl|sv|no|da|fi|pl|cz|sk|hu|ro|bg|ru|tr|ar|he|jp|ja|ko|zh|cn|tw|ca|gb|au|in|au|mx|uk|gr)(/|$)"
    r"|/(en-gb|en-au|en-ca|en-in|fr-ca)(/|$)"
    r"|[?&](lang|locale|country)=",
    re.I
)

ALLOWED_PATTERNS = (
    "*(product|solution|industrie|customer|pricing|security|integration|about|contact|investor|resource|company|careers|mission|blog|sitemap)*"
)
QUERY = "product platform features integrate API dashboard solutions reduce cost improve efficiency visibility compliance safety industries fleet construction logistics manufacturing energy customers case study ROI reduced saved hours fleet pricing plans enterprise contact sales quote SOC 2 ISO 27001 GDPR security trust center integrations API developers documentation webhooks careers hiring roles sales ops revops data engineer"

class FileWriteError(RuntimeError):
    pass


def keep(url: str) -> bool:
    return bool(ALLOW.search(url)) and not bool(DENY.search(url)) and not bool(DENY_LOCALE.search(url)) and not (bool(DENY_SUBDOMAIN.search(url)))

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
            print(
                f"Raw markdown content size: {len(result.markdown.raw_markdown)}")
            print(
                f"Content size after pruning: {len(result.markdown.fit_markdown)}")
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


async def _get_all_urls(base_url: str):
    config = SeedingConfig(
        source="sitemap+cc",
        max_urls=5000,
        hits_per_sec=5,
        concurrency=100,
        force=True,
        verbose=True,
    )

    async with AsyncUrlSeeder(logger=AsyncLogger(verbose=True)) as seeder:
        urls = await seeder.urls(base_url, config)

    return urls

# with open('test-js.json', 'r') as source_file:
#         sources = json.load(source_file)
#         for src in sources:
#             company_name, company_url = src['name'], src['url']
#             links = asyncio.run(_get_all_urls(company_url))
#             filtered_urls = [url for url in links if keep(url['url'])]

#             with open(f'{company_name}_links.json', 'w', encoding='utf-8') as file:
#                 json.dump(filtered_urls, file, indent=4)

with open(f'../storage/identities/Samsara_links.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    print(len(data))