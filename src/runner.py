import argparse
import asyncio
import json
import time
from scrapper import CrawlURLs, FilterAndCrawlPages
from pathlib import Path
from analyzer import get_or_create_lead_card, rank_companies
from storage_manager import _load_all_icps
from typing import List
from dotenv import load_dotenv
from schema.LeadCard import LeadCard
from logger.universal_logger import setup_logger

# Tavily Test
from nodes.grounding import GroundingNode
from schema.state import InputState

logger = setup_logger('AI_SDR.Runner')
STORAGE_PATH = Path("../storage/personas/")
load_dotenv()


def _classify_all_urls(source_path: str):
    logger.info("Starting Classification")
    # crawler = CrawlURLs()
    urlfilter = FilterAndCrawlPages()
    start_time = time.perf_counter()
    with open(source_path, 'r') as source_file:
        sources = json.load(source_file)
        for src in sources:
            company_name, company_url = src['name'], src['url']
            logger.info(f"Extracting data for {company_name}")
            bfs_links = urlfilter.filter_crawl_pages(company_name, company_url)
            with open(STORAGE_PATH / f'{company_name}_links.json', 'w', encoding='utf-8') as file:
                json.dump(bfs_links, file, indent=4)
            # site_content = crawler.handler(company_url, company_query)
            # if site_content:
            #     crawler.write_to_file(
            #         site_content, STORAGE_PATH / f"{company_name}.json"
            #     )

    logger.info("Extraction Complete.")
    logger.info(f"Number of websites crawled: {len(sources)}")
    logger.info(
        f"Total time taken: {round((time.perf_counter() - start_time) * 1000, 2)}")


def _crawl_urls():
    logger.info("Starting Extraction")
    crawler = CrawlURLs()
    with open('../storage/identities/AppliedIntuition_links.json', 'r') as source_file:
        sources = json.load(source_file)
        urls = [x["url"] for x in sources]
        results = asyncio.run(crawler._crawl_shortlisted_urls(urls))
        if results:
            crawler.write_to_file(
                results, STORAGE_PATH / f"AppliedIntuition.json"
            )


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


def create_initial_state():
    return InputState(
        company="Snorkel",
        company_url="https://snorkel.ai/"
    )

if __name__ == "__main__":
    # _classify_all_urls("sources.json")
    # _crawl_urls()
    state = create_initial_state()
    grounding = GroundingNode()
    content = asyncio.run(grounding.run(state))
    path = Path("../storage/personas/snorkel.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2), encoding="utf-8")