import argparse
import asyncio
import json
import time
from scrapper import CrawlURLs
from pathlib import Path
from analyzer import get_or_create_lead_card, rank_companies
from storage_manager import _load_all_icps
from typing import List
from dotenv import load_dotenv
from schema.LeadCard import LeadCard
from logger.universal_logger import setup_logger

logger = setup_logger('AI_SDR.Runner')
STORAGE_PATH = Path("../storage/identities/")
load_dotenv()


def _classify_all_urls(sources):
    logger.info("Starting Classification")
    crawler = CrawlURLs()
    start_time = time.perf_counter()
    # with open('./sources.json', 'r') as source_file:
    #     sources = json.load(source_file)
    for src in sources:
        company_name, company_url = src['name'], src['url']
        logger.info(f"Extracting data for {company_name}")
        site_content = crawler.handler(company_url)
        if site_content:
            crawler.write_to_file(
                site_content, STORAGE_PATH / f"{company_name}.json"
            )

    logger.info("Extraction Complete.")
    logger.info(f"Number of websites crawled: {len(sources)}")
    logger.info(
        f"Total time taken: {round((time.perf_counter() - start_time) * 1000, 2)}")


def _crawl_urls():
    logger.info("Starting Extraction")
    crawler = CrawlURLs()
    start_time = time.perf_counter()
    with open('./sources.json', 'r') as source_file:
        sources = json.load(source_file)

        for src in sources:
            logger.info(f"Extracting data for {src['name']}")
            site_content = asyncio.run(crawler._crawl_url(src["url"]))
            if site_content:
                crawler.write_to_file(
                    site_content[0], Path(src["storage_path"]))
        logger.info("Extraction Complete.")
        logger.info(f"Number of websites crawled: {len(sources)}")
        logger.info(
            f"Total time taken: {round((time.perf_counter() - start_time) * 1000, 2)}")


def get_companies():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", type=str, required=True,
                    help="Sales goal (e.g., which company needs a cybersecurity tool?)")
    args = ap.parse_args()

    stored = _load_all_icps()
    if not stored:
        logger.warning(
            "No saved ICPs found in storage/identities. Run extraction first.")
        return

    cards: List[LeadCard] = []
    for s in stored:
        cards.append(get_or_create_lead_card(s))

    result = rank_companies(args.goal, cards)

    print("\n=== Ranked Leads ===")
    for i, item in enumerate(result.ranked, start=1):
        print(f"{i}. {item.company_name} — {item.fit_score_0_to_100}/100")
        print(f"is_competitor: {item.is_competitor}")
        print(f"{item.reason}")
        print(f"can reach out to: {item.top_outreach_roles}\n\n")
