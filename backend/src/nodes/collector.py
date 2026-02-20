import logging
from langchain_core.messages import AIMessage
from schema.state import ResearchState
from logger.universal_logger import setup_logger

logger = setup_logger(__name__)

class CollectorNode:
    """Collects and organizes all research data before curation."""

    async def collect(self, state: ResearchState) -> ResearchState:
        """Collect and verify all research data is present."""
        company = state.get('company', 'Unknown Company')
        msg = [f"📦 Collecting research data for {company}:"]
        
        # Check each type of research data
        research_types = {
            'news_data': '📰 News',
            'trigger_data': '🫆 Triggers',
            'offering_data': '🧧 Offerings',
            'customer_data': '👨🏻‍💻 Customers',
            'readiness_data': '✅ Readiness'
        }
        
        for data_field, label in research_types.items():
            data = state.get(data_field, {})
            if data:
                msg.append(f"• {label}: {len(data)} documents collected")
            else:
                msg.append(f"• {label}: No data found")
        
        # Update state with collection message
        state.setdefault('messages', []).append(AIMessage(content="\n".join(msg)))
        
        return state

    async def run(self, state: ResearchState) -> ResearchState:
        return await self.collect(state)