from typing import Any
from langchain_core.messages import AIMessage

from schema.state import ResearchState
from utils.prompts import NEWS_SCANNER_QUERY_PROMPT
from .base import BaseResearcher


class NewsResearcher(BaseResearcher):
    def __init__(self) -> None:
        super().__init__()
        self.analyst_type = "news_analyzer"

    async def analyze(self, state: ResearchState):
        """Analyze news and yield events"""
        company = state.get('company', 'Unknown Company')

        # Generate search queries and yield events
        queries = []
        async for event in self.generate_queries(state, NEWS_SCANNER_QUERY_PROMPT):
            yield event
            if event.get("type") == "queries_complete":
                queries = event.get("queries", [])

        # Log subqueries
        subqueries_msg = "🔍 Subqueries for news analysis:\n" + \
            "\n".join([f"• {query}" for query in queries])
        state.setdefault('messages', []).append(
            AIMessage(content=subqueries_msg).model_dump())

        # Start with site scrape data
        news_data = dict[str, Any](state.get('site_scrape', {}))

        # Search and merge documents, yielding events
        documents = {}
        async for event in self.search_documents(state, queries):
            yield event
            if event.get("type") == "search_complete":
                documents = event.get("merged_docs", {})

        news_data.update(documents)

        # Update state
        completion_msg = f"📰 News Scanner found {len(news_data)} documents for {company}"
        state.setdefault('messages', []).append(
            AIMessage(content=completion_msg).model_dump())
        state['news_data'] = news_data

        yield {"type": "analysis_complete", "data_type": "news_data", "count": len(news_data)}
        yield {'message': [completion_msg], 'news_data': news_data}

    async def run(self, state: ResearchState):
        """Run analysis and yield all events"""
        result = None
        async for event in self.analyze(state):
            # yield event
            if "message" in event or "news_data" in event:
                result = event
        return result or {}


"""
2026-02-09 21:43:25 | INFO | nodes.research_nodes.base | Final queries for news_analyzer: ['Snorkel recent company announcements February 2026', 'Snorkel press releases new product launches 2025 2026', 'Snorkel Enterprise AI new partnerships and collaborations 2024 2026', 'Snorkel funding updates leadership changes strategic initiatives 2024 2026']
"""
