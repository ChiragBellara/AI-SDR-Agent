import os
from typing import cast
from company_identity import CompanyIdentity
from crawl4ai import (AsyncWebCrawler, CrawlerRunConfig,
                      DefaultMarkdownGenerator, LLMConfig, LLMExtractionStrategy, PruningContentFilter)
from crawl4ai.models import CrawlResult


class FileWriteError(RuntimeError):
    pass


class CrawlURLs:
    def __init__(self, model="openai"):
        self.model = model

    def _get_llm_config(self):
        # Add functionality for the user to choose their model from a dropdown and update the LLM Config accordingly
        return LLMConfig(
            provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY")
        )

    def _get_mardown_generator(self):
        return DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(),
            options={
                "ignore_links": True,
            }
        )

    def _get_extraction_stratergy(self):
        return LLMExtractionStrategy(
            llm_config=self._get_llm_config(),
            schema=CompanyIdentity.model_json_schema(),
            extraction_type="schema",
            instruction="Analyze the markdown and extract the core business identity."
        ),

    async def _crawl_url(self, URL_TO_CRAWL: str = ""):
        crawl_config = CrawlerRunConfig(
            markdown_generator=self._get_mardown_generator(),
            extraction_strategy=self._get_extraction_stratergy()[0]
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

    def write_to_file(self, content, path):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except Exception as ex:
            raise FileWriteError(f"Failed to write to {path}")
