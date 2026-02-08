import os
from tavily import TavilyClient
from dotenv import load_dotenv
from pathlib import Path
import json

load_dotenv()
TVLY_API_KEY = os.getenv("TAVILY_API_KEY", "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")
url = "https://www.tesla.com/"
instruction = "Find any pages that will help us understand the company's offering, customers, market, positioning, buyers, maturity, motion, momentum, compliance, integrability, and readiness."
tavily_client = TavilyClient(api_key=TVLY_API_KEY)

response = tavily_client.crawl(
    url = url, 
    instructions=instruction,
    max_depth=1, 
    max_breadth=50, 
    extract_depth="advanced"
)
path = Path("../playground/tesla.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(response, indent=2), encoding="utf-8")

for item in response.get("results", []):
    if item.get("raw_content"):
        page_url = item.get("url", url)
        response[page_url] = {
            'raw_content': item.get('raw_content'),
            'source': 'company_website'
        }