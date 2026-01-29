import os
import json
import time
import asyncio
from typing import cast, List, Dict, Any
from urllib.parse import urlparse
from schema.LeadCard import LeadCard
from crawl4ai import (AsyncWebCrawler, CrawlerRunConfig,
                      DefaultMarkdownGenerator, LLMConfig, LLMExtractionStrategy, PruningContentFilter)
from crawl4ai.models import CrawlResult
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from logger.universal_logger import setup_logger
from utils.json_utils import _parse_first_json, _merge_lead_cards
from discovery import Discovery
from utils.prompts import CRAWL_INSTRUCTION

logger = setup_logger('AI_SDR.Scrapper')


class CrawlURLs:
    def __init__(self, model="openai"):
        self.discover = Discovery()
        self.model = model
        self.instruction = CRAWL_INSTRUCTION

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

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

    async def _shortlist_urls_to_crawl(self, URL_TO_CRAWL: str = ""):
        config = CrawlerRunConfig(
            only_text=True,
            excluded_tags=['meta', 'noscript', 'style'],
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=3,
                include_external=False,
                max_pages=18,
            ),
            scraping_strategy=LXMLWebScrapingStrategy(),
            verbose=True,
            prettiify=True
        )

        async with AsyncWebCrawler() as web_crawler:
            results = await web_crawler.arun(
                url=URL_TO_CRAWL,
                config=config
            )
        all_links = [
            crawl_result.url for container in results for crawl_result in container]
        return all_links

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

    def _identify_target_urls(self, crawl_url: str = ""):
        all_urls = asyncio.run(self._shortlist_urls_to_crawl(crawl_url))
        if all_urls:
            selected_sdr_links = self.discover._select_sdr_pages(all_urls)
            return selected_sdr_links
        logger.error("No URLS to classify")
        return []

    def handler(self, URL_TO_CRAWL: str = ""):
        selected_links = self._identify_target_urls(
            URL_TO_CRAWL)
        if selected_links:
            outcome = asyncio.run(self._crawl_shortlisted_urls(selected_links))
            return outcome
        return None
