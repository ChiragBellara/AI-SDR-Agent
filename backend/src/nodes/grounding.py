import os
from tavily import AsyncTavilyClient
from langchain_core.messages import AIMessage

from schema.state import InputState, ResearchState
from logger.universal_logger import setup_logger

logger = setup_logger(__name__)

class GroundingNode:
    """Gathers initial information about the company"""

    def __init__(self) -> None:
        self.tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    async def _initial_search(self, initial_state: InputState):
        """Initial search and yield events"""
        company = initial_state.get("company", "No Company Name")
        message = f"Initializing search for {company}..."
        yield {
            "type": "research_init",
            "company": company,
            "message": f"Initializing search for {company}...",
            "step": "Initialization"
        }

        site_scrape = {}
        if url := initial_state.get("company_url"):
            message += f"\nCrawling company website: {url}"
            logger.info(f"Starting website analysis for {url}")
            yield {
                "type": "crawl_start",
                "url": url,
                "message": f"Crawling company website: {url}",
                "step": "Website Crawl"
            }

            try:
                logger.info("Initializing Tavily crawl")
                site_content = await self.tavily_client.crawl(
                    url = url,
                    instructions="Find the most important official pages that explain the company's business, products or platform, services, customers or use cases, pricing or packaging, and company overview. Prefer core product and solution pages over blogs or news.",
                    max_depth=2,
                    max_breadth=50,
                    extract_depth="advanced"
                )

                site_scrape = {}
                for item in site_content.get("results", []):
                    if item.get("raw_content"):
                        page_url = item.get("url", url)
                        site_scrape[page_url] = {
                            'raw_content': item.get('raw_content'),
                            'source': 'company_website'
                        }

                if site_scrape:
                    logger.info(f"Successfully crawled {len(site_scrape)} pages from website")
                    message += f"\nSuccessfully crawled {len(site_scrape)} pages from website"
                    yield {
                        "type": "crawl_success",
                        "pages_found": len(site_scrape),
                        "message": f"Successfully crawled {len(site_scrape)} pages from website",
                        "step": "Initial Site Scrape"
                    }
                else:
                    logger.warning("No content found in crawl results")
                    message += "\nNo content found in website crawl"
                    yield {
                        "type": "crawl_warning",
                        "message": "No content found in provided URL",
                        "step": "Initial Site Scrape"
                    }

            except Exception as ex:
                error_str = str(ex)
                logger.error(f"Website crawl error: {error_str}", exc_info=True)
                error_msg = f"Error crawling website content: {error_str}"
                message += f"\n{error_msg}"
                yield {
                    "type": "crawl_error",
                    "error": error_str,
                    "message": error_msg,
                    "step": "Initial Site Scrape",
                    "continue_research": True
                }
        else:
            message += "\nNo company URL provided, proceeding directly to research phase"
            yield {
                "type": "no_url",
                "message": "No company URL provided, proceeding directly to research phase",
                "step": "Initializing"
            }

        # Initialize ResearchState with input information
        research_state = {
            # Copy input fields
            "company": initial_state.get('company'),
            "company_url": initial_state.get('company_url'),
            "hq_location": initial_state.get('hq_location'),
            "industry": initial_state.get('industry'),
            # Initialize research fields
            "messages": [AIMessage(content=message)],
            "site_scrape": site_scrape
        }
        if "Error crawling website content:" in message:
            research_state["error"] = error_str

        yield {"type": "grounding_complete", "site_pages": len(site_scrape)}
        yield research_state

    async def run(self, state: InputState) -> ResearchState:
        """Run grounding"""
        result = {}
        async for event in self._initial_search(state):
            if isinstance(event, dict) and "type" not in event:
                result = event
            else:
                print(f"[{event['type']}]")
        return result