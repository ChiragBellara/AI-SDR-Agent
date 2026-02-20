from typing import Any
from langchain_core.messages import AIMessage

from schema.state import ResearchState
from utils.prompts import CUSTOMER_ANALYZER_QUERY_PROMPT
from .base import BaseResearcher


class CustomersResearcher(BaseResearcher):
    def __init__(self) -> None:
        super().__init__()
        self.analyst_type = "customers_analyzer"

    async def analyze(self, state: ResearchState):
        """Analyze the company's customers and yield events"""
        company = state.get('company', 'Unknown Company')

        # Generate search queries and yield events
        queries = []
        async for event in self.generate_queries(state, CUSTOMER_ANALYZER_QUERY_PROMPT):
            yield event
            if event.get("type") == "queries_complete":
                queries = event.get("queries", [])

        # Log subqueries
        subqueries_msg = "🔍 Subqueries for customer analysis:\n" + \
            "\n".join([f"• {query}" for query in queries])
        state.setdefault('messages', []).append(
            AIMessage(content=subqueries_msg).model_dump())

        # Start with site scrape data
        customer_data = dict[str, Any](state.get('site_scrape', {}))

        # Search and merge documents, yielding events
        documents = {}
        async for event in self.search_documents(state, queries):
            yield event
            if event.get("type") == "search_complete":
                documents = event.get("merged_docs", {})

        customer_data.update(documents)

        # Update state
        completion_msg = f"Customers Scanner found {len(customer_data)} documents for {company}"
        state.setdefault('messages', []).append(
            AIMessage(content=completion_msg).model_dump())
        state['customer_data'] = customer_data

        yield {"type": "analysis_complete", "data_type": "customer_data", "count": len(customer_data)}
        yield {'message': [completion_msg], 'customer_data': customer_data}

    async def run(self, state: ResearchState):
        """Run analysis and yield all events"""
        result = None
        async for event in self.analyze(state):
            # yield event
            if "message" in event or "customers_data" in event:
                result = event
        return result or {}
