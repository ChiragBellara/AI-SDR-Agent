import argparse
import asyncio
from scrapper import CrawlURLs
from pathlib import Path
import json
from analyzer import get_or_create_lead_card, rank_companies
from storage_manager import _load_all_icps
from typing import List, Any
from schema.LeadCard import LeadCard


def _crawl_urls():
    crawler = CrawlURLs()
    with open('./sources.json', 'r') as source_file:
        sources = json.load(source_file)

        for src in sources:
            print(f"Working on extracting data for {src["name"]}")
            site_content = asyncio.run(crawler._crawl_url(src["url"]))
            if site_content:
                crawler.write_to_file(
                    site_content[0], Path(src["storage_path"]))


def get_companies():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", type=str, required=True,
                    help="Sales goal (e.g., which company needs a cybersecurity tool?)")
    args = ap.parse_args()

    stored = _load_all_icps()
    if not stored:
        print("No saved ICPs found in storage/identities. Run extraction first.")
        return

    cards: List[LeadCard] = []
    for s in stored:
        cards.append(get_or_create_lead_card(s))

    result = rank_companies(args.goal, cards)

    print("\n=== Ranked Leads ===")
    for i, item in enumerate(result.ranked, start=1):
        print(f"{i}. {item.company_name} — {item.fit_score_0_to_100}/100")
        print(f"   {item.reason}\n")


if __name__ == "__main__":
    get_companies()
    # _crawl_urls()
