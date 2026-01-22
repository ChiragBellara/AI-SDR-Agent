import asyncio
from scrapper import crawl_url, crawl_url_with_llm, write_to_file
from processor import IdentityProcessor
from pathlib import Path

FILE_PATH = Path("../data/output.txt")
FILE_PATH_WITH_LLM_EXTRACTION = Path("../data/output_llm.txt")
URL_TO_CRAWL = "https://www.anthropic.com/company"

site_content = asyncio.run(crawl_url_with_llm(URL_TO_CRAWL))
if site_content:
    print(site_content)
    write_to_file(site_content, FILE_PATH_WITH_LLM_EXTRACTION)

if not FILE_PATH.is_file():
    site_content = asyncio.run(crawl_url(URL_TO_CRAWL))
    if site_content:
        print("\nWriting content to file")
        write_to_file(site_content, FILE_PATH)

test = IdentityProcessor(provider="gpt-4o-mini", file_to_read=FILE_PATH)
outcome = test._call_llm()
print(outcome)
