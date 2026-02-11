from typing import Any
from langchain_core.messages import AIMessage

from schema.state import ResearchState
from utils.prompts import TRIGGER_ANALYZER_QUERY_PROMPT
from .base import BaseResearcher

class TriggersResearcher(BaseResearcher):
    def __init__(self) -> None:
        super().__init__()
        self.analyst_type = "trigger_analyzer"

    async def analyze(self, state: ResearchState):
        """Analyze recent news, and other developments and yield events"""
        company = state.get('company', 'Unknown Company')
        
        # Generate search queries and yield events
        queries = []
        async for event in self.generate_queries(state, TRIGGER_ANALYZER_QUERY_PROMPT):
            yield event
            if event.get("type") == "queries_complete":
                queries = event.get("queries", [])
        
        # Log subqueries
        subqueries_msg = "🔍 Subqueries for trigger analysis:\n" + "\n".join([f"• {query}" for query in queries])
        state.setdefault('messages', []).append(AIMessage(content=subqueries_msg).model_dump())
        
        # Start with site scrape data
        trigger_data = dict[str, Any](state.get('site_scrape', {}))
        
        # Search and merge documents, yielding events
        documents = {}
        async for event in self.search_documents(state, queries):
            yield event
            if event.get("type") == "search_complete":
                documents = event.get("merged_docs", {})
        
        trigger_data.update(documents)
        
        # Update state
        completion_msg = f"Triggers Scanner found {len(trigger_data)} documents for {company}"
        state.setdefault('messages', []).append(AIMessage(content=completion_msg).model_dump())
        state['trigger_data'] = trigger_data
        
        yield {"type": "analysis_complete", "data_type": "trigger_data", "count": len(trigger_data)}
        yield {'message': [completion_msg], 'trigger_data': trigger_data}

    async def run(self, state: ResearchState):
        """Run analysis and yield all events"""
        result = None
        async for event in self.analyze(state):
            # yield event
            if "message" in event or "trigger_data" in event:
                result = event
            else:
                print(f"[{event['type']}]")
        return result or {}