import asyncio
from scrapper import CrawlURLs
from pathlib import Path
import json

crawler = CrawlURLs()
with open('./sources.json', 'r') as source_file:
    sources = json.load(source_file)

    for src in sources:
        print(f"Working on extracting data for {src["name"]}")
        site_content = asyncio.run(crawler._crawl_url(src["url"]))
        if site_content:
            crawler.write_to_file(site_content, Path(src["storage_path"]))
