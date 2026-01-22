import os
from typing import cast
from company_identity import CompanyIdentity
from crawl4ai import (AsyncWebCrawler, CrawlerRunConfig,
                      DefaultMarkdownGenerator, LLMConfig, LLMExtractionStrategy, PruningContentFilter, CacheMode)
from crawl4ai.models import CrawlResult


class FileWriteError(RuntimeError):
    pass


async def crawl_url(URL_TO_CRAWL: str = ""):
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
            url=URL_TO_CRAWL,
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


async def crawl_url_with_llm(URL_TO_CRAWL: str = ""):
    crawl_config = CrawlerRunConfig(
        # cache_mode=CacheMode.ENABLED,
        word_count_threshold=1,
        extraction_strategy=LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY")
            ),
            schema=CompanyIdentity.model_json_schema(),
            extraction_type="schema",
            instruction="Analyze the markdown and extract the core business identity."
        ),
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(),
            options={
                "ignore_links": True,

            }
        )
    )
    async with AsyncWebCrawler() as web_crawler:
        result = cast(CrawlResult, await web_crawler.arun(
            url=URL_TO_CRAWL,
            config=crawl_config
        ))
        if result.extracted_content:
            print(f"Content Size: {len(result.extracted_content)}")
            return result.extracted_content
        return None


def write_to_file(content, path):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except Exception as ex:
        raise FileWriteError(f"Failed to write to {path}")
