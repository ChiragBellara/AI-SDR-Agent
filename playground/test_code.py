import asyncio
from crawl4ai import AsyncWebCrawler


async def run_crawler():
    async with AsyncWebCrawler() as web_crawler:
        result = await web_crawler.arun(
            url="https://www.anthropic.com",
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(run_crawler())
