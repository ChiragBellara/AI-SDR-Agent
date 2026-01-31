import os
import json
import time
import asyncio
from typing import cast, List, Dict, Any
from urllib.parse import urlparse
from schema.LeadCard import LeadCard
from crawl4ai import (AsyncWebCrawler, CrawlerRunConfig,
                      DefaultMarkdownGenerator, LLMConfig, LLMExtractionStrategy, PruningContentFilter, SeedingConfig, AsyncUrlSeeder)
from crawl4ai.models import CrawlResult
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from logger.universal_logger import setup_logger
from utils.json_utils import _parse_first_json, _merge_lead_cards
from utils.url_utils import CheckUrlDomain
from discovery import Discovery
from utils.prompts import CRAWL_INSTRUCTION
import logging

logging.basicConfig(
    filename="crawl4ai.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
file_logger = logging.getLogger("crawl4ai")
logger = setup_logger('AI_SDR.Scrapper')


class FilterAndCrawlPages:
    def __init__(self) -> None:
        pass

    async def _get_all_urls(self):
        config = SeedingConfig(
            source="sitemap+cc", 
            max_urls=5000, 
            hits_per_sec=5, 
            concurrency=100, 
            force=True, 
            verbose=True
        ) 
        async with AsyncUrlSeeder() as seeder: 
            urls = await seeder.urls(self.homepage, config)
        logger.info(f"Initial seeding identified {len(urls)} for {self.company}.")
        return urls
    
    def filter_crawl_pages(self, company, base_url):
        self.company = company
        self.homepage = base_url
        self.check_url = CheckUrlDomain(base_url)
        all_urls = asyncio.run(self._get_all_urls())
        logger.info("Proceeding to shortlist and rank.")
        return self.check_url._select_top_k_urls(all_urls, k = 100)

class CrawlURLs:
    def __init__(self, model="openai"):
        self.model = model
        self.instruction = CRAWL_INSTRUCTION

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
            schema=LeadCard.model_json_schema(),
            extraction_type="schema",
            instruction=self.instruction
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
                logger.info(f"Content Size: {len(result.extracted_content)}")
                data = json.loads(result.extracted_content)
                return data
        return None

    async def _crawl_shortlisted_urls(self, selected_urls: List[Any]):
        crawl_config = CrawlerRunConfig(
            markdown_generator=self._get_mardown_generator(),
            extraction_strategy=self._get_extraction_stratergy()[0]
        )
        logger.info(f"Crawling shortlisted URLs | count={len(selected_urls)}")
        async with AsyncWebCrawler() as web_crawler:
            t0 = time.perf_counter()
            results = await web_crawler.arun_many(
                urls=selected_urls,
                config=crawl_config
            )
            latency_ms = (time.perf_counter() - t0) * 1000

        if not results:
            logger.warning("No crawl results returned")
            return None
        logger.info(
            f"Crawl complete | results={len(results)} | latency_ms={latency_ms}")

        per_page_cards: List[Dict[str, Any]] = []
        for res in results:
            url = getattr(res, "url", None)
            status = getattr(res, "success", True)
            extracted = getattr(res, "extracted_content", None)

            if not extracted:
                logger.warning(
                    f"No extracted_content | url={url} | ok={status}")
                continue

            logger.info(
                f"Extracted content | url={url} | size={len(extracted)}")

            obj = _parse_first_json(extracted)
            if not obj:
                logger.warning(f"Failed to parse JSON | url={url}")
                continue

            # Optionally: tag the source URL so your merger has provenance
            obj.setdefault("source_notes", [])
            obj["source_notes"].append(f"from {url}")

            per_page_cards.append(obj)
        if not per_page_cards:
            logger.warning(
                "No valid LeadCards parsed from shortlisted URLs")
            return None

        # Merge page-level LeadCards into one site-level LeadCard
        merged = _merge_lead_cards(per_page_cards)
        return merged

    def write_to_file(self, content, path):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(content, indent=2), encoding="utf-8")
        except Exception:
            logger.exception(f"File Write Error. Failed to write to {path}")
